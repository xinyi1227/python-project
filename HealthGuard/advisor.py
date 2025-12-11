import pandas as pd
import random
import datetime
import requests

class SmartHealthAdvisor:
    def __init__(self):
        # API 配置
        self.usda_api_key = "L7lcAcc9XGNMcR7U4FrKsQghGRYyssfkfWTjINJo"
        self.amap_api_key = "6b49895ecfde9a5f2feca33f2515c231" # 高德地图 Key
        self.cached_food_data = None
        
    def get_weather(self):
        """
        调用高德地图 API 获取实时天气
        默认城市：北京 (110000)
        返回: 包含温度、描述的字典 (不再包含 AQI)
        """
        # 默认使用北京 (110000)，实际应用中可根据 IP 定位获取 adcode
        city_code = "110000" 
        
        try:
            url = "https://restapi.amap.com/v3/weather/weatherInfo"
            params = {
                "key": self.amap_api_key,
                "city": city_code,
                "extensions": "base", # base: 实况天气, all: 预报
                "output": "json"
            }
            
            # print("Calling Amap Weather API...")
            resp = requests.get(url, params=params, timeout=5)
            
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "1" and data.get("lives"):
                    live = data["lives"][0]
                    temp = float(live.get("temperature", 25))
                    desc = live.get("weather", "晴")
                    city = live.get("city", "北京")
                    
                    # 移除了 AQI 查询和模拟逻辑

                    return {
                        "temp": temp,
                        "desc": desc,
                        "text": f"今日 {city} {desc} {temp}℃"
                    }
                else:
                    print(f"Amap API Error Response: {data}")
            else:
                print(f"Amap API Failed: {resp.status_code}")

        except Exception as e:
            print(f"Weather API Error: {e}")

        # Fallback 模拟数据
        scenarios = [
            {"temp": 35, "desc": "高温晴朗", "text": "今日 35℃ 高温"},
            {"temp": 28, "desc": "多云", "text": "今日多云 28℃"},
            {"temp": 24, "desc": "舒适", "text": "今日气候宜人 24℃"},
            {"temp": 12, "desc": "寒冷", "text": "今日气温较低 12℃"}
        ]
        return random.choice(scenarios)

    def get_food_data(self):
        """
        调用 USDA FoodData Central API 获取食物数据
        如果失败则使用本地模拟数据
        返回: Pandas DataFrame
        """
        # 如果已有缓存数据，直接返回
        if self.cached_food_data is not None:
            return self.cached_food_data

        try:
            # 搜索 "cooked" 以获取常见的熟食，包含肉类、蔬菜等
            url = "https://api.nal.usda.gov/fdc/v1/foods/search"
            params = {
                "api_key": self.usda_api_key,
                "query": "cooked", 
                "pageSize": 20,
                "dataType": ["Foundation", "SR Legacy"]
            }
            
            # print("Calling USDA API...")
            resp = requests.get(url, params=params, timeout=5)
            
            if resp.status_code == 200:
                data = resp.json()
                foods_list = []
                
                for item in data.get('foods', []):
                    name = item.get('description', 'Unknown')
                    
                    cals = 0
                    protein = 0
                    sodium = 0
                    
                    # 提取营养素
                    # Energy: 1008 (kcal), Protein: 1003 (g), Sodium: 1093 (mg)
                    for nut in item.get('foodNutrients', []):
                        nid = nut.get('nutrientId')
                        val = nut.get('value', 0)
                        if nid == 1008: cals = val       # Energy (kcal)
                        elif nid == 1003: protein = val  # Protein
                        elif nid == 1093: sodium = val   # Sodium
                    
                    # 简单过滤无效数据
                    if cals > 0:
                        foods_list.append({
                            "name": name,
                            "calories": cals,
                            "protein": protein,
                            "sodium": sodium
                        })
                
                if foods_list:
                    df = pd.DataFrame(foods_list)
                    self.cached_food_data = df
                    return df
            else:
                print(f"USDA API Failed: {resp.status_code} - {resp.text}")

        except Exception as e:
            print(f"USDA API Error: {e}")

        # Fallback 数据 (如果 API 失败)
        data = {
            "name": ["清蒸虾仁", "红烧肉", "水煮鸡胸肉", "咸鱼茄子煲", "藜麦沙拉", "麻辣火锅", "煎三文鱼", "皮蛋瘦肉粥"],
            "calories": [85, 470, 133, 180, 120, 800, 208, 150], # kcal per 100g
            "protein": [18.0, 10.0, 31.0, 4.0, 4.4, 15.0, 20.0, 8.0], # g per 100g
            "sodium": [120, 900, 60, 650, 30, 2500, 50, 400] # mg per 100g
        }
        return pd.DataFrame(data)

    def generate_recommendation(self, user_records):
        """
        核心逻辑：结合天气、健康数据（血压）和 API 数据生成建议
        """
        # 1. 分析用户健康数据 (血压)
        latest_sys = 120
        latest_dia = 80
        
        if user_records and len(user_records) > 0:
            # 假设记录是按时间排序的，取最后一条
            last_record = user_records[-1]
            try:
                # 兼容可能的数据格式差异
                if isinstance(last_record, list): # 如果是 tuple/list
                    pass
                elif isinstance(last_record, dict):
                    latest_sys = float(last_record.get('sys_bp') or 120)
                    latest_dia = float(last_record.get('dia_bp') or 80)
            except:
                pass

        is_high_bp = latest_sys > 140 or latest_dia > 90
        bp_status_text = f"血压偏高 ({int(latest_sys)}/{int(latest_dia)})" if is_high_bp else "血压正常"

        # 2. 获取环境数据
        weather = self.get_weather()
        
        # 3. 运动推荐逻辑 (基于天气描述简化版，无需 AQI 和外部 API)
        # 逻辑：如果下雨/雪 或 高温 -> 室内，否则 -> 户外
        is_bad_weather = False
        desc = weather['desc']
        temp = weather['temp']
        
        if temp > 30 or temp < 5: 
            is_bad_weather = True
        if "雨" in desc or "雪" in desc or "霾" in desc or "沙" in desc:
            is_bad_weather = True
            
        if is_bad_weather:
            weather_tip = f"{weather['text']}，建议室内运动"
            exercise_options = [
                {"name": "室内游泳", "calories_burn": 300},
                {"name": "瑜伽", "calories_burn": 150},
                {"name": "健身房力量训练", "calories_burn": 250},
                {"name": "动感单车", "calories_burn": 400}
            ]
        else:
            weather_tip = f"{weather['text']}，天气适宜"
            exercise_options = [
                {"name": "户外跑步", "calories_burn": 350},
                {"name": "晨跑", "calories_burn": 300},
                {"name": "公园快走", "calories_burn": 180},
                {"name": "户外骑行", "calories_burn": 280}
            ]
            
        chosen_ex = random.choice(exercise_options)

        # 4. 饮食推荐逻辑 (Pandas 筛选)
        df_food = self.get_food_data()
        
        # 筛选条件：
        # 如果高血压 -> 钠含量 < 500mg/100g
        if is_high_bp:
            food_condition = (df_food['sodium'] < 500)
            diet_tip = "已为您过滤高盐食物"
        else:
            food_condition = (df_food['sodium'] >= 0) # 全选
            diet_tip = "饮食均衡"
            
        suitable_foods = df_food[food_condition]
        
        # 确保不为空
        if suitable_foods.empty:
            chosen_food = df_food.sample(n=1).iloc[0]
            diet_tip = "无低盐选项，请注意摄入"
        else:
            chosen_food = suitable_foods.sample(n=1).iloc[0]
        
        # 5. 计算热量缺口逻辑
        # 假设目标缺口 500
        ex_burn = int(chosen_ex['calories_burn'])
        
        food_portion = 200 # g
        food_cals = int(chosen_food['calories'] * (food_portion / 100))
        food_protein = round(chosen_food['protein'] * (food_portion / 100), 1)
        
        recommendation_text = (
            f"💡 <b>今日建议：</b><br>"
            f"检测到{weather_tip} + {bp_status_text}。<br><br>"
            f"推荐 <b>{chosen_ex['name']}</b> 30分钟（消耗 {ex_burn} 大卡），"
            f"搭配晚餐 {food_portion}g <b>{chosen_food['name']}</b>（{diet_tip}，含蛋白质 {food_protein}g）。<br>"
            f"此组合预计产生热量差，助您达成今日健康目标。"
        )
        
        return {
            "text": recommendation_text,
            "raw": {
                "weather": weather,
                "exercise": chosen_ex,
                "food": chosen_food.to_dict(),
                "bp_high": is_high_bp
            }
        }
