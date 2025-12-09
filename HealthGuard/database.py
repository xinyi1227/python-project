import sqlite3
import hashlib
import os

DB_FILE = 'health_system.db'

def get_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # 允许通过列名访问
    return conn

def init_db():
    """初始化数据库表"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 用户表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        height REAL,
        blood_type TEXT,
        emergency_contact TEXT,
        allergies TEXT,
        chronic_diseases TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 健康数据表（扩展）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS health_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        record_date TEXT,
        weight REAL,
        systolic_bp INTEGER,
        diastolic_bp INTEGER,
        steps INTEGER,
        heart_rate INTEGER,
        blood_sugar REAL,
        temperature REAL,
        sleep_hours REAL,
        water_intake INTEGER,
        notes TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # 用药记录表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS medications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        medicine_name TEXT NOT NULL,
        dosage TEXT,
        frequency TEXT,
        start_date TEXT,
        end_date TEXT,
        notes TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # 健康目标表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS health_goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        goal_type TEXT,
        target_value REAL,
        current_value REAL,
        start_date TEXT,
        end_date TEXT,
        status TEXT DEFAULT 'active',
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # 提醒事项表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        reminder_type TEXT,
        title TEXT,
        reminder_time TEXT,
        repeat_type TEXT,
        is_active INTEGER DEFAULT 1,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # 饮食记录表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS diet_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        record_date TEXT,
        meal_type TEXT,
        food_description TEXT,
        calories INTEGER,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # --- 新增：系统通知表 ---
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,          -- 接收者ID
        message TEXT NOT NULL,    -- 消息内容
        is_read INTEGER DEFAULT 0,-- 0:未读, 1:已读
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # 初始化一个默认管理员账号 (admin/123456)
    try:
        admin_pwd = hashlib.sha256("123456".encode()).hexdigest()
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                       ("admin", admin_pwd, "admin"))
        print("默认管理员账号已创建: admin / 123456")
    except sqlite3.IntegrityError:
        pass # 管理员已存在

    conn.commit()
    conn.close()

# --- 业务逻辑函数 ---

def register_user(username, password, age, gender):
    """注册普通用户"""
    conn = get_connection()
    cursor = conn.cursor()
    pwd_hash = hashlib.sha256(password.encode()).hexdigest()
    try:
        cursor.execute("INSERT INTO users (username, password, role, age, gender) VALUES (?, ?, ?, ?, ?)",
                       (username, pwd_hash, 'user', age, gender))
        conn.commit()
        return True, "注册成功"
    except sqlite3.IntegrityError:
        return False, "用户名已存在"
    finally:
        conn.close()

def login_user(username, password):
    """用户登录校验"""
    conn = get_connection()
    cursor = conn.cursor()
    pwd_hash = hashlib.sha256(password.encode()).hexdigest()
    
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, pwd_hash))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return True, {"id": user["id"], "username": user["username"], "role": user["role"]}
    else:
        return False, "用户名或密码错误"

def add_health_record(user_id, date, weight, sys_bp, dia_bp, steps, heart_rate=None, blood_sugar=None, temperature=None, sleep_hours=None, water_intake=None, notes=None):
    """添加健康记录（扩展版）"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO health_data (user_id, record_date, weight, systolic_bp, diastolic_bp, steps, 
                                    heart_rate, blood_sugar, temperature, sleep_hours, water_intake, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, date, weight, sys_bp, dia_bp, steps, heart_rate, blood_sugar, temperature, sleep_hours, water_intake, notes))
        conn.commit()
        return True, "记录添加成功"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_user_records(user_id):
    """获取特定用户的所有记录（用于可视化）"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM health_data WHERE user_id = ? ORDER BY record_date ASC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    # 转换为列表字典返回
    return [dict(row) for row in rows]

def get_all_stats():
    """管理员功能：获取系统统计数据"""
    conn = get_connection()
    cursor = conn.cursor()
    
    stats = {}
    
    # 用户总数
    cursor.execute("SELECT COUNT(*) FROM users WHERE role='user'")
    stats['user_count'] = cursor.fetchone()[0]
    
    # 平均体重
    cursor.execute("SELECT AVG(weight) FROM health_data")
    avg_weight = cursor.fetchone()[0]
    stats['avg_weight'] = round(avg_weight, 2) if avg_weight else 0
    
    # 总记录数
    cursor.execute("SELECT COUNT(*) FROM health_data")
    stats['total_records'] = cursor.fetchone()[0]
    
    conn.close()
    return stats

# --- 用户档案管理 ---
def update_user_profile(user_id, **kwargs):
    """更新用户健康档案"""
    conn = get_connection()
    cursor = conn.cursor()
    
    allowed_fields = ['height', 'blood_type', 'emergency_contact', 'allergies', 'chronic_diseases']
    updates = []
    values = []
    
    for field in allowed_fields:
        if field in kwargs:
            updates.append(f"{field} = ?")
            values.append(kwargs[field])
    
    if not updates:
        return False, "没有可更新的字段"
    
    values.append(user_id)
    sql = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
    
    try:
        cursor.execute(sql, values)
        conn.commit()
        return True, "档案更新成功"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_user_profile(user_id):
    """获取用户完整档案"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

# --- 用药管理 ---
def add_medication(user_id, medicine_name, dosage, frequency, start_date, end_date=None, notes=None):
    """添加用药记录"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO medications (user_id, medicine_name, dosage, frequency, start_date, end_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, medicine_name, dosage, frequency, start_date, end_date, notes))
        conn.commit()
        return True, "用药记录添加成功"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_user_medications(user_id):
    """获取用户所有用药记录"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM medications WHERE user_id = ? ORDER BY start_date DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_medication(med_id):
    """删除用药记录"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM medications WHERE id = ?", (med_id,))
        conn.commit()
        return True, "删除成功"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

# --- 健康目标管理 ---
def add_health_goal(user_id, goal_type, target_value, current_value, start_date, end_date):
    """添加健康目标"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO health_goals (user_id, goal_type, target_value, current_value, start_date, end_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, goal_type, target_value, current_value, start_date, end_date))
        conn.commit()
        return True, "目标创建成功"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_user_goals(user_id):
    """获取用户所有目标"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM health_goals WHERE user_id = ? AND status = 'active' ORDER BY start_date DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_goal_progress(goal_id, current_value):
    """更新目标进度"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE health_goals SET current_value = ? WHERE id = ?", (current_value, goal_id))
        conn.commit()
        return True, "进度更新成功"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

# --- 提醒管理 ---
def add_reminder(user_id, reminder_type, title, reminder_time, repeat_type='once'):
    """添加提醒"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO reminders (user_id, reminder_type, title, reminder_time, repeat_type)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, reminder_type, title, reminder_time, repeat_type))
        conn.commit()
        return True, "提醒创建成功"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_user_reminders(user_id):
    """获取用户所有提醒"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reminders WHERE user_id = ? AND is_active = 1 ORDER BY reminder_time", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# --- 饮食记录 ---
def add_diet_record(user_id, record_date, meal_type, food_description, calories=0):
    """添加饮食记录"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO diet_records (user_id, record_date, meal_type, food_description, calories)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, record_date, meal_type, food_description, calories))
        conn.commit()
        return True, "饮食记录添加成功"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_user_diet_records(user_id, date=None):
    """获取用户饮食记录"""
    conn = get_connection()
    cursor = conn.cursor()
    if date:
        cursor.execute("SELECT * FROM diet_records WHERE user_id = ? AND record_date = ? ORDER BY id DESC", (user_id, date))
    else:
        cursor.execute("SELECT * FROM diet_records WHERE user_id = ? ORDER BY record_date DESC LIMIT 50", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# --- 新增：管理员管理接口 ---

def get_all_users(query=None):
    """管理员：获取所有用户列表（不包含密码）"""
    conn = get_connection()
    cursor = conn.cursor()
    
    sql = "SELECT id, username, role, age, gender, created_at FROM users WHERE role != 'admin'"
    params = []
    
    if query:
        sql += " AND username LIKE ?"
        params.append(f"%{query}%")
        
    sql += " ORDER BY created_at DESC"
    
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_user(user_id):
    """管理员：删除用户及其所有关联数据"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # 1. 删除关联表数据
        tables = ['health_data', 'medications', 'health_goals', 'reminders', 'diet_records', 'notifications']
        for table in tables:
            cursor.execute(f"DELETE FROM {table} WHERE user_id = ?", (user_id,))
            
        # 2. 删除用户本身
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        
        conn.commit()
        return True, "用户及其数据已彻底删除"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

# --- 新增：通知管理接口 ---

def send_notification(user_id, message):
    """管理员：发送通知给特定用户"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO notifications (user_id, message) VALUES (?, ?)", (user_id, message))
        conn.commit()
        return True, "通知发送成功"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_user_notifications(user_id, only_unread=True):
    """用户：获取通知"""
    conn = get_connection()
    cursor = conn.cursor()
    
    sql = "SELECT * FROM notifications WHERE user_id = ?"
    if only_unread:
        sql += " AND is_read = 0"
    sql += " ORDER BY created_at DESC"
    
    cursor.execute(sql, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def mark_notification_read(notif_id):
    """用户：标记通知为已读"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE notifications SET is_read = 1 WHERE id = ?", (notif_id,))
        conn.commit()
        return True, "操作成功"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()

