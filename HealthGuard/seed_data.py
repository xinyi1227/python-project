import sqlite3
import datetime
import random

DB_PATH = 'HealthGuard/health_system.db'

def seed_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Get testuser ID
    cursor.execute("SELECT id FROM users WHERE username = 'testuser'")
    user = cursor.fetchone()
    
    if not user:
        print("User 'testuser' not found. Creating...")
        cursor.execute("INSERT INTO users (username, password, role, gender, age, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                       ('testuser', '123456', 'user', '男', 25, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        user_id = cursor.lastrowid
    else:
        user_id = user[0]
        
    print(f"Seeding data for user_id: {user_id}")
    
    # 2. Generate records for last 14 days
    base_date = datetime.date.today()
    
    # Clear existing records for this user to avoid duplicates/mess
    cursor.execute("DELETE FROM health_data WHERE user_id = ?", (user_id,))
    
    for i in range(14):
        date = (base_date - datetime.timedelta(days=13-i)).strftime("%Y-%m-%d")
        
        # Random realistic data
        weight = round(70 + random.uniform(-0.5, 0.5) + (i * 0.05), 1) # Slight gain/fluctuation
        steps = random.randint(3000, 12000)
        sys_bp = random.randint(110, 130)
        dia_bp = random.randint(70, 85)
        heart_rate = random.randint(60, 90)
        sleep = round(random.uniform(6.0, 9.0), 1)
        water = random.randint(1000, 2500)
        
        cursor.execute("""
            INSERT INTO health_data 
            (user_id, record_date, weight, steps, systolic_bp, diastolic_bp, heart_rate, sleep_hours, water_intake, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, date, weight, steps, sys_bp, dia_bp, heart_rate, sleep, water, "Auto-generated data"))
        
    conn.commit()
    conn.close()
    print("Data seeded successfully!")

if __name__ == "__main__":
    seed_data()

