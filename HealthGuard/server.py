import socket
import threading
import json
import database

# 配置
HOST = '0.0.0.0'
PORT = 9999

def handle_client(client_socket, addr):
    """处理单个客户端连接的线程函数"""
    print(f"[NEW CONNECTION] {addr} connected.")
    
    try:
        while True:
            request_data = client_socket.recv(8192).decode('utf-8')
            if not request_data:
                break
            
            request = json.loads(request_data)
            action = request.get('action')
            payload = request.get('payload', {})
            
            response = {"status": "error", "message": "Unknown action"}
            
            # 路由分发
            if action == "login":
                success, data = database.login_user(payload['username'], payload['password'])
                response = {"status": "success" if success else "error", 
                           "data": data if success else None, 
                           "message": data if not success else "Login OK"}
                
            elif action == "register":
                success, msg = database.register_user(payload['username'], payload['password'], 
                                                     payload.get('age'), payload.get('gender'))
                response = {"status": "success" if success else "error", "message": msg}
                
            elif action == "add_record":
                success, msg = database.add_health_record(
                    payload['user_id'], payload['date'], payload.get('weight'), 
                    payload.get('sys_bp'), payload.get('dia_bp'), payload.get('steps'),
                    payload.get('heart_rate'), payload.get('blood_sugar'), 
                    payload.get('temperature'), payload.get('sleep_hours'),
                    payload.get('water_intake'), payload.get('notes')
                )
                response = {"status": "success" if success else "error", "message": msg}
                
            elif action == "get_records":
                records = database.get_user_records(payload['user_id'])
                response = {"status": "success", "data": records}
                
            elif action == "get_sys_stats":
                stats = database.get_all_stats()
                response = {"status": "success", "data": stats}
            
            # --- 新增API ---
            elif action == "update_profile":
                success, msg = database.update_user_profile(payload['user_id'], **payload.get('profile_data', {}))
                response = {"status": "success" if success else "error", "message": msg}
                
            elif action == "get_profile":
                profile = database.get_user_profile(payload['user_id'])
                response = {"status": "success", "data": profile}
                
            elif action == "add_medication":
                success, msg = database.add_medication(
                    payload['user_id'], payload['medicine_name'], payload['dosage'],
                    payload['frequency'], payload['start_date'], 
                    payload.get('end_date'), payload.get('notes')
                )
                response = {"status": "success" if success else "error", "message": msg}
                
            elif action == "get_medications":
                meds = database.get_user_medications(payload['user_id'])
                response = {"status": "success", "data": meds}
                
            elif action == "delete_medication":
                success, msg = database.delete_medication(payload['med_id'])
                response = {"status": "success" if success else "error", "message": msg}
                
            elif action == "add_goal":
                success, msg = database.add_health_goal(
                    payload['user_id'], payload['goal_type'], payload['target_value'],
                    payload['current_value'], payload['start_date'], payload['end_date']
                )
                response = {"status": "success" if success else "error", "message": msg}
                
            elif action == "get_goals":
                goals = database.get_user_goals(payload['user_id'])
                response = {"status": "success", "data": goals}
                
            elif action == "update_goal_progress":
                success, msg = database.update_goal_progress(payload['goal_id'], payload['current_value'])
                response = {"status": "success" if success else "error", "message": msg}
                
            elif action == "add_reminder":
                success, msg = database.add_reminder(
                    payload['user_id'], payload['reminder_type'], payload['title'],
                    payload['reminder_time'], payload.get('repeat_type', 'once')
                )
                response = {"status": "success" if success else "error", "message": msg}
                
            elif action == "get_reminders":
                reminders = database.get_user_reminders(payload['user_id'])
                response = {"status": "success", "data": reminders}
                
            elif action == "add_diet":
                success, msg = database.add_diet_record(
                    payload['user_id'], payload['record_date'], payload['meal_type'],
                    payload['food_description'], payload.get('calories', 0)
                )
                response = {"status": "success" if success else "error", "message": msg}
                
            elif action == "get_diet_records":
                records = database.get_user_diet_records(payload['user_id'], payload.get('date'))
                response = {"status": "success", "data": records}
            
            # 发送响应
            client_socket.send(json.dumps(response).encode('utf-8'))
            
    except Exception as e:
        print(f"[ERROR] {addr}: {e}")
    finally:
        client_socket.close()
        print(f"[DISCONNECTED] {addr} disconnected.")

def start_server():
    """启动服务器"""
    database.init_db()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[LISTENING] Server is listening on {HOST}:{PORT}")
    
    while True:
        client_sock, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_sock, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    start_server()
