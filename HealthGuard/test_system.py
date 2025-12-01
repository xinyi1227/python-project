#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HealthGuard 系统功能测试脚本
用于验证数据库和服务端功能是否正常
"""

import database
import datetime

def test_database():
    """测试数据库功能"""
    print("=" * 50)
    print("开始测试数据库功能...")
    print("=" * 50)
    
    # 1. 初始化数据库
    print("\n[测试1] 初始化数据库...")
    database.init_db()
    print("✅ 数据库初始化成功")
    
    # 2. 测试用户注册
    print("\n[测试2] 测试用户注册...")
    success, msg = database.register_user("testuser", "123456", 25, "男")
    if success:
        print(f"✅ 用户注册成功: {msg}")
    else:
        print(f"ℹ️  用户可能已存在: {msg}")
    
    # 3. 测试用户登录
    print("\n[测试3] 测试用户登录...")
    success, data = database.login_user("testuser", "123456")
    if success:
        print(f"✅ 用户登录成功: {data}")
        user_id = data['id']
    else:
        print(f"❌ 登录失败: {data}")
        return
    
    # 4. 测试更新用户档案
    print("\n[测试4] 测试更新用户档案...")
    success, msg = database.update_user_profile(
        user_id,
        height=175,
        blood_type="A型",
        emergency_contact="张三 13800138000",
        allergies="花粉",
        chronic_diseases="无"
    )
    print(f"{'✅' if success else '❌'} 档案更新: {msg}")
    
    # 5. 测试添加健康记录
    print("\n[测试5] 测试添加健康记录...")
    today = datetime.date.today().strftime("%Y-%m-%d")
    success, msg = database.add_health_record(
        user_id, today, 70.5, 120, 80, 8000,
        heart_rate=72, blood_sugar=5.5, temperature=36.5,
        sleep_hours=7.5, water_intake=2000, notes="感觉良好"
    )
    print(f"{'✅' if success else '❌'} 健康记录: {msg}")
    
    # 6. 测试获取健康记录
    print("\n[测试6] 测试获取健康记录...")
    records = database.get_user_records(user_id)
    print(f"✅ 获取到 {len(records)} 条记录")
    if records:
        print(f"   最新记录: 日期={records[-1]['record_date']}, 体重={records[-1]['weight']}kg")
    
    # 7. 测试添加用药记录
    print("\n[测试7] 测试添加用药记录...")
    success, msg = database.add_medication(
        user_id, "维生素C", "1片/次", "每日1次", today, None, "饭后服用"
    )
    print(f"{'✅' if success else '❌'} 用药记录: {msg}")
    
    # 8. 测试获取用药记录
    print("\n[测试8] 测试获取用药记录...")
    meds = database.get_user_medications(user_id)
    print(f"✅ 获取到 {len(meds)} 条用药记录")
    
    # 9. 测试添加健康目标
    print("\n[测试9] 测试添加健康目标...")
    end_date = (datetime.date.today() + datetime.timedelta(days=90)).strftime("%Y-%m-%d")
    success, msg = database.add_health_goal(
        user_id, "减肥", 65.0, 70.5, today, end_date
    )
    print(f"{'✅' if success else '❌'} 健康目标: {msg}")
    
    # 10. 测试获取健康目标
    print("\n[测试10] 测试获取健康目标...")
    goals = database.get_user_goals(user_id)
    print(f"✅ 获取到 {len(goals)} 个目标")
    if goals:
        goal = goals[0]
        progress = (goal['current_value'] / goal['target_value'] * 100) if goal['target_value'] > 0 else 0
        print(f"   目标: {goal['goal_type']}, 进度: {progress:.1f}%")
    
    # 11. 测试添加提醒
    print("\n[测试11] 测试添加提醒...")
    success, msg = database.add_reminder(
        user_id, "用药", "服用维生素C", "08:00", "daily"
    )
    print(f"{'✅' if success else '❌'} 提醒: {msg}")
    
    # 12. 测试添加饮食记录
    print("\n[测试12] 测试添加饮食记录...")
    success, msg = database.add_diet_record(
        user_id, today, "早餐", "1碗燕麦粥 + 1个鸡蛋 + 1杯牛奶", 350
    )
    print(f"{'✅' if success else '❌'} 饮食记录: {msg}")
    
    # 13. 测试管理员统计
    print("\n[测试13] 测试管理员统计...")
    stats = database.get_all_stats()
    print(f"✅ 系统统计:")
    print(f"   用户总数: {stats['user_count']}")
    print(f"   记录总数: {stats['total_records']}")
    print(f"   平均体重: {stats['avg_weight']} kg")
    
    print("\n" + "=" * 50)
    print("✅ 所有数据库功能测试完成！")
    print("=" * 50)

def test_server_connection():
    """测试服务器连接"""
    print("\n" + "=" * 50)
    print("测试服务器连接...")
    print("=" * 50)
    
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect(('127.0.0.1', 9999))
        print("✅ 服务器连接成功！")
        sock.close()
    except Exception as e:
        print(f"❌ 服务器连接失败: {e}")
        print("   请确保 server.py 已启动")

if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════╗
║                                                   ║
║        HealthGuard 系统功能测试                    ║
║                                                   ║
╚═══════════════════════════════════════════════════╝
    """)
    
    # 测试数据库
    test_database()
    
    # 测试服务器连接
    test_server_connection()
    
    print("""
╔═══════════════════════════════════════════════════╗
║                                                   ║
║  测试完成！如果所有项目都显示 ✅，说明系统正常      ║
║                                                   ║
║  下一步：                                          ║
║  1. 启动服务器: python server.py                   ║
║  2. 启动客户端: python client.py                   ║
║  3. 使用 testuser/123456 登录测试                  ║
║                                                   ║
╚═══════════════════════════════════════════════════╝
    """)

