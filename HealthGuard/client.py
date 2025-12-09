import tkinter as tk
from tkinter import ttk, messagebox
import socket
import json
import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib

# 设置字体，解决中文乱码
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'Microsoft YaHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

# 配置服务器地址
SERVER_IP = '127.0.0.1'
SERVER_PORT = 9999

# --- 配色方案 (模仿 Element UI / Admin 风格) ---
COLORS = {
    'sidebar_bg': '#304156',      # 侧边栏深色背景
    'sidebar_fg': '#bfcbd9',      # 侧边栏文字颜色
    'sidebar_active': '#1f2d3d',  # 侧边栏选中背景
    'header_bg': '#ffffff',       # 顶栏白色背景
    'main_bg': '#f0f2f5',         # 内容区灰色背景
    'primary': '#409EFF',         # 主色调（蓝色）
    'success': '#67C23A',         # 成功色（绿色）
    'danger': '#F56C6C',          # 危险色（红色）
    'text_main': '#303133',       # 主要文字
    'text_regular': '#606266',    # 常规文字
    'border': '#EBEEF5'           # 边框颜色
}

class NetworkClient:
    """网络通信模块"""
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((SERVER_IP, SERVER_PORT))
        except ConnectionRefusedError:
            messagebox.showerror("连接失败", f"无法连接到服务器 {SERVER_IP}:{SERVER_PORT}\n请确认服务端已启动。")
            exit()

    def send_request(self, action, payload=None):
        request = {"action": action, "payload": payload or {}}
        try:
            self.sock.send(json.dumps(request).encode('utf-8'))
            response_data = self.sock.recv(1024*1024).decode('utf-8')
            return json.loads(response_data)
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def close(self):
        self.sock.close()

class HealthApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HealthGuard - 个人健康管理系统")
        self.geometry("1280x800")
        self.configure(bg=COLORS['main_bg'])
        
        # 样式配置
        self.setup_styles()
        
        self.network = NetworkClient()
        self.current_user = None
        
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        
        self.frames = {}
        self.show_frame("LoginFrame")
        
        self.center_window()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Treeview 样式 (表格)
        style.configure("Treeview", 
                        background="#ffffff",
                        fieldbackground="#ffffff",
                        rowheight=40,
                        font=("Microsoft YaHei", 10))
        style.configure("Treeview.Heading", 
                        font=("Microsoft YaHei", 10, "bold"),
                        background="#FAFAFA",
                        foreground=COLORS['text_regular'])
        
        # 侧边栏按钮样式
        style.configure("Sidebar.TButton",
                       background=COLORS['sidebar_bg'],
                       foreground=COLORS['sidebar_fg'],
                       borderwidth=0,
                       font=("Microsoft YaHei", 11),
                       anchor="w",
                       padding=(20, 10))
        style.map("Sidebar.TButton",
                  background=[('active', COLORS['sidebar_active'])],
                  foreground=[('active', '#409EFF')])

    def center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f'{w}x{h}+{x}+{y}')

    def show_frame(self, page_name, **kwargs):
        """切换页面逻辑"""
        # 1. 核心修复：清空容器内的所有旧页面
        for widget in self.container.winfo_children():
            widget.destroy()
            
        # 清空引用
        self.frames = {}
            
        # 2. 创建新页面
        if page_name == "LoginFrame":
            frame = LoginFrame(parent=self.container, controller=self)
        elif page_name == "RegisterFrame":
            frame = RegisterFrame(parent=self.container, controller=self)
        elif page_name == "UserDashboard":
            frame = MainLayout(parent=self.container, controller=self, role="user")
        elif page_name == "AdminDashboard":
            frame = MainLayout(parent=self.container, controller=self, role="admin")
        else:
            return

        self.frames[page_name] = frame
        frame.pack(fill="both", expand=True)

    def on_closing(self):
        self.network.close()
        self.destroy()

# --- 登录页面 (模仿图2) ---
class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # 1. 背景 (由于没有图片，使用渐变色或纯色模拟)
        # 这里使用 Canvas 绘制一个简单的背景色
        self.canvas = tk.Canvas(self, bg='#F0F2F5', highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # 绘制一些装饰背景 (模拟图片效果)
        self.canvas.create_rectangle(0, 0, 2000, 400, fill=COLORS['primary'], outline="")
        
        # 2. 居中登录卡片
        # 使用 place 绝对定位居中
        card_width = 400
        card_height = 350
        
        self.card = tk.Frame(self, bg='white', relief='raised', bd=0)
        self.card.place(relx=0.5, rely=0.5, anchor='center', width=card_width, height=card_height)
        
        # 标题
        tk.Label(self.card, text="健康管理系统", font=("Microsoft YaHei", 22, "bold"), 
                 bg='white', fg=COLORS['text_main']).pack(pady=(40, 30))
        
        # 输入框容器
        form_frame = tk.Frame(self.card, bg='white')
        form_frame.pack(fill='x', padx=40)
        
        # 用户名
        self.user_entry = self.create_input(form_frame, "请输入账号")
        self.user_entry.pack(fill='x', pady=(0, 15))
        
        # 密码
        self.pwd_entry = self.create_input(form_frame, "请输入密码", show="*")
        self.pwd_entry.pack(fill='x', pady=(0, 20))
        
        # 登录按钮 (全宽)
        login_btn = tk.Button(form_frame, text="登  录", command=self.login,
                             bg=COLORS['primary'], fg='white',
                             font=("Microsoft YaHei", 12), relief='flat',
                             activebackground='#66b1ff', activeforeground='white',
                             cursor='hand2')
        login_btn.pack(fill='x', ipady=5)
        
        # 注册链接
        tk.Label(self.card, text="还没有账号？点击注册", font=("Microsoft YaHei", 9),
                 bg='white', fg=COLORS['primary'], cursor='hand2').pack(pady=15)
        
        # 绑定点击事件去注册
        self.card.bind("<Button-1>", lambda e: controller.show_frame("RegisterFrame"))

    def create_input(self, parent, placeholder, show=None):
        entry = tk.Entry(parent, font=("Microsoft YaHei", 11), 
                        bg='#F5F7FA', relief='flat', 
                        highlightthickness=1, highlightbackground='#DCDFE6',
                        highlightcolor=COLORS['primary'])
        # 简单的 Placeholder 效果
        entry.insert(0, placeholder)
        entry.config(fg='#909399')
        if show:
            # 如果是密码框，先清空再设置 show 属性
            entry.bind("<FocusIn>", lambda e: self.on_focus_in(entry, placeholder, show))
        else:
            entry.bind("<FocusIn>", lambda e: self.on_focus_in(entry, placeholder))
            
        entry.bind("<FocusOut>", lambda e: self.on_focus_out(entry, placeholder))
        return entry

    def on_focus_in(self, entry, placeholder, show_char=None):
        if entry.get() == placeholder:
            entry.delete(0, 'end')
            entry.config(fg='black')
            if show_char:
                entry.config(show=show_char)

    def on_focus_out(self, entry, placeholder):
        if entry.get() == "":
            entry.insert(0, placeholder)
            entry.config(fg='#909399')
            entry.config(show="")

    def login(self):
        u = self.user_entry.get()
        p = self.pwd_entry.get()
        if u == "请输入账号" or p == "请输入密码":
             messagebox.showwarning("提示", "请输入用户名和密码")
             return
             
        resp = self.controller.network.send_request("login", {"username": u, "password": p})
        if resp["status"] == "success":
            self.controller.current_user = resp["data"]
            if resp["data"]["role"] == 'admin':
                self.controller.show_frame("AdminDashboard")
            else:
                self.controller.show_frame("UserDashboard")
        else:
            messagebox.showerror("错误", resp.get("message", "登录失败"))

class RegisterFrame(LoginFrame):
    """复用登录页样式，改为注册"""
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent) # 不调用 super LoginFrame，而是重写
        self.controller = controller
        
        self.canvas = tk.Canvas(self, bg='#F0F2F5', highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_rectangle(0, 0, 2000, 400, fill=COLORS['success'], outline="") # 绿色背景区分
        
        card_width = 400
        card_height = 450
        
        self.card = tk.Frame(self, bg='white', relief='raised', bd=0)
        self.card.place(relx=0.5, rely=0.5, anchor='center', width=card_width, height=card_height)
        
        tk.Label(self.card, text="注册新用户", font=("Microsoft YaHei", 22, "bold"), 
                 bg='white', fg=COLORS['text_main']).pack(pady=(30, 20))
        
        form_frame = tk.Frame(self.card, bg='white')
        form_frame.pack(fill='x', padx=40)
        
        self.user_entry = self.create_input(form_frame, "用户名")
        self.user_entry.pack(fill='x', pady=(0, 15))
        
        self.pwd_entry = self.create_input(form_frame, "密码", show="*")
        self.pwd_entry.pack(fill='x', pady=(0, 15))
        
        self.age_entry = self.create_input(form_frame, "年龄")
        self.age_entry.pack(fill='x', pady=(0, 15))
        
        self.gender_combo = ttk.Combobox(form_frame, values=["男", "女"], state="readonly", font=("Microsoft YaHei", 11))
        self.gender_combo.set("请选择性别")
        self.gender_combo.pack(fill='x', pady=(0, 20))
        
        reg_btn = tk.Button(form_frame, text="立即注册", command=self.register,
                           bg=COLORS['success'], fg='white',
                           font=("Microsoft YaHei", 12), relief='flat',
                           cursor='hand2')
        reg_btn.pack(fill='x', ipady=5)
        
        tk.Button(self.card, text="返回登录", command=lambda: controller.show_frame("LoginFrame"),
                 font=("Microsoft YaHei", 9), bg='white', fg=COLORS['text_regular'], bd=0, cursor='hand2').pack(pady=10)

    def register(self):
        u = self.user_entry.get()
        p = self.pwd_entry.get()
        a = self.age_entry.get()
        g = self.gender_combo.get()
        
        if u in ["用户名", ""] or p in ["密码", ""]:
            messagebox.showwarning("提示", "信息不完整")
            return
            
        resp = self.controller.network.send_request("register", {"username": u, "password": p, "age": a, "gender": g})
        if resp["status"] == "success":
            messagebox.showinfo("成功", "注册成功")
            self.controller.show_frame("LoginFrame")
        else:
            messagebox.showerror("失败", resp["message"])

# --- 主界面布局 (Sidebar + Header + Content) ---
class MainLayout(tk.Frame):
    def __init__(self, parent, controller, role):
        super().__init__(parent)
        self.controller = controller
        self.role = role
        
        # 1. 左侧侧边栏
        self.sidebar = tk.Frame(self, bg=COLORS['sidebar_bg'], width=220)
        self.sidebar.pack(side=tk.LEFT, fill='y')
        self.sidebar.pack_propagate(False) # 固定宽度
        
        # Logo区
        logo_frame = tk.Frame(self.sidebar, bg=COLORS['sidebar_bg'], height=60)
        logo_frame.pack(fill='x')
        tk.Label(logo_frame, text="HealthGuard", font=("Arial", 16, "bold"), 
                 bg=COLORS['sidebar_bg'], fg='white').place(relx=0.5, rely=0.5, anchor='center')
        
        # 菜单按钮
        self.create_sidebar_btn("📊  仪表盘", lambda: self.switch_page("dashboard"))
        if role == "user":
            self.create_sidebar_btn("📝  健康打卡", lambda: self.switch_page("record"))
            self.create_sidebar_btn("👤  健康档案", lambda: self.switch_page("profile"))
            self.create_sidebar_btn("💊  用药管理", lambda: self.switch_page("medication"))
            self.create_sidebar_btn("🎯  健康目标", lambda: self.switch_page("goals"))
            self.create_sidebar_btn("🍎  饮食记录", lambda: self.switch_page("diet"))
            self.create_sidebar_btn("⏰  提醒中心", lambda: self.switch_page("reminders"))
        else:
            self.create_sidebar_btn("👥  用户管理", lambda: self.switch_page("users"))
        
        # 2. 右侧主体
        self.main_area = tk.Frame(self, bg=COLORS['main_bg'])
        self.main_area.pack(side=tk.RIGHT, fill='both', expand=True)
        
        # 2.1 顶部导航栏
        self.header = tk.Frame(self.main_area, bg=COLORS['header_bg'], height=50)
        self.header.pack(fill='x')
        self.header.pack_propagate(False)
        
        # 面包屑/标题
        self.header_label = tk.Label(self.header, text="首页 / 仪表盘", font=("Microsoft YaHei", 10), 
                                     bg='white', fg=COLORS['text_regular'])
        self.header_label.pack(side=tk.LEFT, padx=20)
        
        # 用户信息 & 注销
        user_info = tk.Frame(self.header, bg='white')
        user_info.pack(side=tk.RIGHT, padx=20)
        tk.Label(user_info, text=f"欢迎, {controller.current_user['username']}", 
                 bg='white', font=("Microsoft YaHei", 10)).pack(side=tk.LEFT, padx=10)
        tk.Button(user_info, text="注销", command=lambda: controller.show_frame("LoginFrame"),
                 bg=COLORS['danger'], fg='white', bd=0, padx=10).pack(side=tk.LEFT)
        
        # 2.2 内容区 (使用 Frame 容器)
        self.content_frame = tk.Frame(self.main_area, bg=COLORS['main_bg'])
        self.content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # 初始化默认页面
        self.current_page_frame = None
        self.switch_page("dashboard")

    def create_sidebar_btn(self, text, command):
        btn = tk.Button(self.sidebar, text=text,
                       bg=COLORS['sidebar_bg'], fg=COLORS['sidebar_fg'],
                       font=("Microsoft YaHei", 11), bd=0, 
                       activebackground=COLORS['sidebar_active'],
                       activeforeground=COLORS['primary'], 
                       anchor='w', padx=20, pady=12, 
                       cursor='hand2',
                       relief='flat')
        btn.config(command=command)  # 分开设置 command
        btn.pack(fill='x', pady=2)

    def switch_page(self, page_key):
        # 销毁旧页面
        if self.current_page_frame:
            self.current_page_frame.destroy()
            self.current_page_frame = None
            
        # 创建新页面
        if page_key == "dashboard":
            self.header_label.config(text="首页 / 仪表盘")
            if self.role == 'user':
                self.current_page_frame = UserChartsPage(self.content_frame, self.controller)
            else:
                self.current_page_frame = AdminStatsPage(self.content_frame, self.controller)
                
        elif page_key == "record":
            self.header_label.config(text="首页 / 健康打卡")
            self.current_page_frame = DataEntryPage(self.content_frame, self.controller)
            
        elif page_key == "profile":
            self.header_label.config(text="首页 / 健康档案")
            self.current_page_frame = ProfilePage(self.content_frame, self.controller)
            
        elif page_key == "medication":
            self.header_label.config(text="首页 / 用药管理")
            self.current_page_frame = MedicationPage(self.content_frame, self.controller)
            
        elif page_key == "goals":
            self.header_label.config(text="首页 / 健康目标")
            self.current_page_frame = GoalsPage(self.content_frame, self.controller)
            
        elif page_key == "diet":
            self.header_label.config(text="首页 / 饮食记录")
            self.current_page_frame = DietPage(self.content_frame, self.controller)
            
        elif page_key == "reminders":
            self.header_label.config(text="首页 / 提醒中心")
            self.current_page_frame = RemindersPage(self.content_frame, self.controller)

        elif page_key == "users":
            self.header_label.config(text="首页 / 用户管理")
            self.current_page_frame = AdminUserPage(self.content_frame, self.controller)
        
        # 显示新页面（关键修复）
        if self.current_page_frame:
            self.current_page_frame.pack(fill='both', expand=True)
            self.content_frame.update()  # 强制更新显示

# --- 具体页面内容 ---

class UserChartsPage(tk.Frame):
    """用户仪表盘：显示图表和历史数据表格"""
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['main_bg'])
        self.controller = controller
        
        # --- 新增：通知区域 ---
        self.notif_frame = tk.Frame(self, bg=COLORS['main_bg'])
        self.notif_frame.pack(fill='x', pady=(0, 10))
        self.check_notifications()
        
        # 上部分：图表
        chart_frame = tk.Frame(self, bg='white', bd=1, relief='solid')
        chart_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        self.canvas_frame = tk.Frame(chart_frame, bg='white')
        self.canvas_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 下部分：数据表格 (Treeview) - 模仿图1的表格样式
        table_frame = tk.Frame(self, bg='white')
        table_frame.pack(fill='x', ipady=10)
        
        tk.Label(table_frame, text="历史记录明细", font=("Microsoft YaHei", 12, "bold"), 
                 bg='white', fg=COLORS['text_main']).pack(anchor='w', padx=15, pady=10)
        
        columns = ("date", "weight", "steps", "bp")
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=6)
        
        self.tree.heading("date", text="记录日期")
        self.tree.heading("weight", text="体重(kg)")
        self.tree.heading("steps", text="步数")
        self.tree.heading("bp", text="血压(收缩/舒张)")
        
        self.tree.column("date", anchor='center')
        self.tree.column("weight", anchor='center')
        self.tree.column("steps", anchor='center')
        self.tree.column("bp", anchor='center')
        
        self.tree.pack(fill='x', padx=15)
        
        self.load_data()
        
    def check_notifications(self):
        resp = self.controller.network.send_request("get_notifications", {"user_id": self.controller.current_user['id']})
        if resp['status'] == 'success' and resp['data']:
            for notif in resp['data']:
                self.create_notif_banner(notif)
                
    def create_notif_banner(self, notif):
        banner = tk.Frame(self.notif_frame, bg='#fdf6ec', bd=1, relief='solid') # 浅橙色背景
        banner.pack(fill='x', pady=2)
        
        tk.Label(banner, text=f"🔔 管理员通知: {notif['message']}", 
                 bg='#fdf6ec', fg='#e6a23c', font=("Microsoft YaHei", 10)).pack(side=tk.LEFT, padx=10, pady=8)
                 
        def mark_read():
            self.controller.network.send_request("mark_read", {"notif_id": notif['id']})
            banner.destroy()
            
        tk.Button(banner, text="×", command=mark_read, bd=0, bg='#fdf6ec', fg='gray', cursor='hand2').pack(side=tk.RIGHT, padx=10)

    def load_data(self):
        resp = self.controller.network.send_request("get_records", {"user_id": self.controller.current_user['id']})
        if resp["status"] == "success":
            records = resp["data"]
            
            # 填充表格
            for r in records:
                self.tree.insert("", "end", values=(r['record_date'], r['weight'], r['steps'], f"{r['systolic_bp']}/{r['diastolic_bp']}"))
            
            # 绘制图表
            if records:
                dates = [r['record_date'] for r in records]
                weights = [r['weight'] for r in records]
                
                fig = Figure(figsize=(5, 3), dpi=100)
                ax = fig.add_subplot(111)
                ax.plot(dates, weights, marker='o', color=COLORS['primary'])
                ax.set_title("近期体重趋势")
                ax.grid(True, alpha=0.3)
                
                canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill='both', expand=True)
            else:
                tk.Label(self.canvas_frame, text="暂无数据，请前往打卡页面添加", bg='white').pack(pady=50)

class DataEntryPage(tk.Frame):
    """健康打卡页面（扩展版）"""
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['main_bg'])
        self.controller = controller
        
        # 白色卡片容器
        card = tk.Frame(self, bg='white')
        card.pack(fill='both', expand=True)
        
        # 顶部操作栏
        action_bar = tk.Frame(card, bg='white', height=60)
        action_bar.pack(fill='x', padx=20, pady=10)
        
        tk.Button(action_bar, text="📝 提交今日数据", command=self.submit,
                 bg=COLORS['success'], fg='white', font=("Microsoft YaHei", 11, "bold"),
                 relief='flat', padx=20, pady=8).pack(side=tk.LEFT)
        
        # 创建滚动区域
        canvas = tk.Canvas(card, bg='white')
        scrollbar = ttk.Scrollbar(card, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=50, pady=20)
        scrollbar.pack(side="right", fill="y")
        
        # 表单区域
        self.entries = {}
        fields = [
            ("基础指标", [
                ("日期 (YYYY-MM-DD)", "date", datetime.date.today().strftime("%Y-%m-%d")),
                ("体重 (kg)", "weight", ""),
                ("收缩压 (mmHg)", "sys_bp", ""),
                ("舒张压 (mmHg)", "dia_bp", ""),
                ("心率 (次/分)", "heart_rate", ""),
                ("血糖 (mmol/L)", "blood_sugar", ""),
                ("体温 (°C)", "temperature", "")
            ]),
            ("生活习惯", [
                ("步数", "steps", ""),
                ("睡眠时长 (小时)", "sleep_hours", ""),
                ("饮水量 (ml)", "water_intake", "")
            ]),
            ("备注", [
                ("今日备注", "notes", "")
            ])
        ]
        
        for section_title, section_fields in fields:
            # 分组标题
            tk.Label(scrollable_frame, text=section_title, font=("Microsoft YaHei", 12, "bold"),
                    bg='white', fg=COLORS['primary']).pack(anchor='w', pady=(15, 10))
            
            for label, key, default in section_fields:
                row_frame = tk.Frame(scrollable_frame, bg='white')
                row_frame.pack(fill='x', pady=8)
                
                tk.Label(row_frame, text=label, width=20, anchor='e', bg='white', 
                        font=("Microsoft YaHei", 10)).pack(side=tk.LEFT, padx=10)
                
                if key == 'notes':
                    ent = tk.Text(row_frame, font=("Microsoft YaHei", 10), relief='solid', 
                                 bd=1, width=40, height=3)
                else:
                    ent = tk.Entry(row_frame, font=("Microsoft YaHei", 10), relief='solid', 
                                  bd=1, width=40)
                    if default: 
                        ent.insert(0, default)
                
                ent.pack(side=tk.LEFT)
                self.entries[key] = ent

    def submit(self):
        data = {}
        for k, v in self.entries.items():
            if isinstance(v, tk.Text):
                data[k] = v.get("1.0", "end-1c")
            else:
                data[k] = v.get()
        
        data['user_id'] = self.controller.current_user['id']
        
        resp = self.controller.network.send_request("add_record", data)
        if resp["status"] == "success":
            messagebox.showinfo("成功", "数据已保存！")
            # 清空非日期字段
            for k, v in self.entries.items():
                if k != 'date':
                    if isinstance(v, tk.Text):
                        v.delete("1.0", "end")
                    else:
                        v.delete(0, 'end')
        else:
            messagebox.showerror("失败", resp["message"])

class AdminStatsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['main_bg'])
        self.controller = controller
        
        # 统计卡片容器
        cards_container = tk.Frame(self, bg=COLORS['main_bg'])
        cards_container.pack(fill='x', pady=20)
        
        self.card_frame = tk.Frame(cards_container, bg=COLORS['main_bg'])
        self.card_frame.pack(anchor='center')
        
        self.load_stats()
        
    def load_stats(self):
        resp = self.controller.network.send_request("get_sys_stats")
        if resp["status"] == "success":
            data = resp["data"]
            self.create_card("总用户数", data.get('user_count', 0), COLORS['primary'], 0)
            self.create_card("总记录数", data.get('total_records', 0), COLORS['success'], 1)
            self.create_card("平均体重", f"{data.get('avg_weight', 0)}kg", COLORS['danger'], 2)
            
    def create_card(self, title, value, color, col):
        # 白色卡片
        card = tk.Frame(self.card_frame, bg='white', width=250, height=120)
        card.grid(row=0, column=col, padx=20)
        card.pack_propagate(False)
        
        # 左侧色条
        tk.Frame(card, bg=color, width=5).pack(side=tk.LEFT, fill='y')
        
        content = tk.Frame(card, bg='white')
        content.pack(side=tk.LEFT, fill='both', expand=True, padx=20)
        
        tk.Label(content, text=title, font=("Microsoft YaHei", 10), fg='#909399', bg='white').pack(anchor='w', pady=(20, 5))
        tk.Label(content, text=str(value), font=("Arial", 24, "bold"), fg=COLORS['text_main'], bg='white').pack(anchor='w')

# --- 健康档案页面 ---
class ProfilePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['main_bg'])
        self.controller = controller
        
        card = tk.Frame(self, bg='white')
        card.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(card, text="个人健康档案", font=("Microsoft YaHei", 16, "bold"),
                bg='white', fg=COLORS['text_main']).pack(anchor='w', padx=20, pady=15)
        
        # 获取当前档案
        resp = controller.network.send_request("get_profile", {"user_id": controller.current_user['id']})
        profile = resp.get('data', {}) if resp['status'] == 'success' else {}
        
        form = tk.Frame(card, bg='white')
        form.pack(fill='both', expand=True, padx=40, pady=20)
        
        self.entries = {}
        fields = [
            ("身高 (cm)", "height", profile.get('height', '')),
            ("血型", "blood_type", profile.get('blood_type', '')),
            ("紧急联系人", "emergency_contact", profile.get('emergency_contact', '')),
            ("过敏史", "allergies", profile.get('allergies', '')),
            ("慢性病史", "chronic_diseases", profile.get('chronic_diseases', ''))
        ]
        
        for label, key, default in fields:
            row = tk.Frame(form, bg='white')
            row.pack(fill='x', pady=8)
            tk.Label(row, text=label, width=15, anchor='e', bg='white', font=("Microsoft YaHei", 10)).pack(side=tk.LEFT, padx=10)
            ent = tk.Entry(row, font=("Microsoft YaHei", 10), relief='solid', bd=1, width=40)
            ent.insert(0, str(default) if default else '')
            ent.pack(side=tk.LEFT)
            self.entries[key] = ent
        
        tk.Button(card, text="保存档案", command=self.save_profile,
                 bg=COLORS['primary'], fg='white', font=("Microsoft YaHei", 11),
                 relief='flat', padx=30, pady=8).pack(pady=20)
    
    def save_profile(self):
        data = {k: v.get() for k, v in self.entries.items()}
        resp = self.controller.network.send_request("update_profile", {
            "user_id": self.controller.current_user['id'],
            "profile_data": data
        })
        if resp['status'] == 'success':
            messagebox.showinfo("成功", "档案已更新")
        else:
            messagebox.showerror("失败", resp['message'])

# --- 用药管理页面 ---
class MedicationPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['main_bg'])
        self.controller = controller
        
        # 顶部操作栏
        action_bar = tk.Frame(self, bg=COLORS['main_bg'])
        action_bar.pack(fill='x', pady=(0, 10))
        
        tk.Button(action_bar, text="➕ 添加用药", command=self.add_medication,
                 bg=COLORS['success'], fg='white', font=("Microsoft YaHei", 10),
                 relief='flat', padx=15, pady=5).pack(side=tk.LEFT)
        
        # 用药列表
        list_card = tk.Frame(self, bg='white')
        list_card.pack(fill='both', expand=True)
        
        tk.Label(list_card, text="我的用药清单", font=("Microsoft YaHei", 14, "bold"),
                bg='white').pack(anchor='w', padx=15, pady=10)
        
        columns = ("medicine", "dosage", "frequency", "start_date", "end_date")
        self.tree = ttk.Treeview(list_card, columns=columns, show='headings', height=12)
        
        self.tree.heading("medicine", text="药品名称")
        self.tree.heading("dosage", text="剂量")
        self.tree.heading("frequency", text="频率")
        self.tree.heading("start_date", text="开始日期")
        self.tree.heading("end_date", text="结束日期")
        
        for col in columns:
            self.tree.column(col, anchor='center', width=120)
        
        self.tree.pack(fill='both', expand=True, padx=15, pady=10)
        
        # 删除按钮
        tk.Button(list_card, text="删除选中", command=self.delete_selected,
                 bg=COLORS['danger'], fg='white', relief='flat', padx=15, pady=5).pack(pady=10)
        
        self.load_medications()
    
    def load_medications(self):
        self.tree.delete(*self.tree.get_children())
        resp = self.controller.network.send_request("get_medications", {"user_id": self.controller.current_user['id']})
        if resp['status'] == 'success':
            for med in resp['data']:
                self.tree.insert("", "end", values=(
                    med['medicine_name'], med['dosage'], med['frequency'],
                    med['start_date'], med.get('end_date', '长期')
                ), tags=(med['id'],))
    
    def add_medication(self):
        dialog = tk.Toplevel(self)
        dialog.title("添加用药")
        dialog.geometry("400x350")
        dialog.configure(bg='white')
        
        entries = {}
        fields = [
            ("药品名称*", "medicine_name"),
            ("剂量 (如: 1片/次)", "dosage"),
            ("频率 (如: 每日3次)", "frequency"),
            ("开始日期 (YYYY-MM-DD)*", "start_date"),
            ("结束日期 (可选)", "end_date"),
            ("备注", "notes")
        ]
        
        for label, key in fields:
            tk.Label(dialog, text=label, bg='white', font=("Microsoft YaHei", 10)).pack(anchor='w', padx=20, pady=(10, 2))
            ent = tk.Entry(dialog, font=("Microsoft YaHei", 10), width=35)
            if key == 'start_date':
                ent.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
            ent.pack(padx=20)
            entries[key] = ent
        
        def submit():
            data = {k: v.get() for k, v in entries.items()}
            data['user_id'] = self.controller.current_user['id']
            resp = self.controller.network.send_request("add_medication", data)
            if resp['status'] == 'success':
                messagebox.showinfo("成功", "用药记录已添加")
                dialog.destroy()
                self.load_medications()
            else:
                messagebox.showerror("失败", resp['message'])
        
        tk.Button(dialog, text="提交", command=submit, bg=COLORS['success'], fg='white',
                 relief='flat', padx=30, pady=8).pack(pady=20)
    
    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要删除的记录")
            return
        
        med_id = self.tree.item(selected[0])['tags'][0]
        resp = self.controller.network.send_request("delete_medication", {"med_id": med_id})
        if resp['status'] == 'success':
            messagebox.showinfo("成功", "已删除")
            self.load_medications()

# --- 健康目标页面 ---
class GoalsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['main_bg'])
        self.controller = controller
        
        action_bar = tk.Frame(self, bg=COLORS['main_bg'])
        action_bar.pack(fill='x', pady=(0, 10))
        
        tk.Button(action_bar, text="➕ 新建目标", command=self.add_goal,
                 bg=COLORS['primary'], fg='white', font=("Microsoft YaHei", 10),
                 relief='flat', padx=15, pady=5).pack(side=tk.LEFT)
        
        # 目标列表
        self.goals_container = tk.Frame(self, bg=COLORS['main_bg'])
        self.goals_container.pack(fill='both', expand=True)
        
        self.load_goals()
    
    def load_goals(self):
        for widget in self.goals_container.winfo_children():
            widget.destroy()
        
        resp = self.controller.network.send_request("get_goals", {"user_id": self.controller.current_user['id']})
        if resp['status'] == 'success':
            goals = resp['data']
            if not goals:
                tk.Label(self.goals_container, text="暂无目标，点击上方按钮创建",
                        bg=COLORS['main_bg'], font=("Microsoft YaHei", 12)).pack(pady=50)
            else:
                for goal in goals:
                    self.create_goal_card(goal)
    
    def create_goal_card(self, goal):
        card = tk.Frame(self.goals_container, bg='white', relief='solid', bd=1)
        card.pack(fill='x', padx=20, pady=10)
        
        # 计算进度
        progress = (goal['current_value'] / goal['target_value'] * 100) if goal['target_value'] > 0 else 0
        
        content = tk.Frame(card, bg='white')
        content.pack(fill='x', padx=20, pady=15)
        
        tk.Label(content, text=f"🎯 {goal['goal_type']}", font=("Microsoft YaHei", 13, "bold"),
                bg='white').pack(anchor='w')
        tk.Label(content, text=f"目标: {goal['target_value']} | 当前: {goal['current_value']} | 进度: {progress:.1f}%",
                font=("Microsoft YaHei", 10), bg='white', fg='gray').pack(anchor='w', pady=5)
        tk.Label(content, text=f"期限: {goal['start_date']} 至 {goal['end_date']}",
                font=("Microsoft YaHei", 9), bg='white', fg='gray').pack(anchor='w')
    
    def add_goal(self):
        dialog = tk.Toplevel(self)
        dialog.title("创建健康目标")
        dialog.geometry("400x300")
        dialog.configure(bg='white')
        
        entries = {}
        fields = [
            ("目标类型 (如: 减肥/控血压)", "goal_type"),
            ("目标值", "target_value"),
            ("当前值", "current_value"),
            ("开始日期 (YYYY-MM-DD)", "start_date"),
            ("结束日期 (YYYY-MM-DD)", "end_date")
        ]
        
        for label, key in fields:
            tk.Label(dialog, text=label, bg='white', font=("Microsoft YaHei", 10)).pack(anchor='w', padx=20, pady=(10, 2))
            ent = tk.Entry(dialog, font=("Microsoft YaHei", 10), width=35)
            if 'date' in key:
                ent.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
            ent.pack(padx=20)
            entries[key] = ent
        
        def submit():
            data = {k: v.get() for k, v in entries.items()}
            data['user_id'] = self.controller.current_user['id']
            resp = self.controller.network.send_request("add_goal", data)
            if resp['status'] == 'success':
                messagebox.showinfo("成功", "目标已创建")
                dialog.destroy()
                self.load_goals()
            else:
                messagebox.showerror("失败", resp['message'])
        
        tk.Button(dialog, text="创建", command=submit, bg=COLORS['primary'], fg='white',
                 relief='flat', padx=30, pady=8).pack(pady=20)

# --- 饮食记录页面 ---
class DietPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['main_bg'])
        self.controller = controller
        
        action_bar = tk.Frame(self, bg=COLORS['main_bg'])
        action_bar.pack(fill='x', pady=(0, 10))
        
        tk.Button(action_bar, text="➕ 记录饮食", command=self.add_diet,
                 bg=COLORS['success'], fg='white', font=("Microsoft YaHei", 10),
                 relief='flat', padx=15, pady=5).pack(side=tk.LEFT)
        
        list_card = tk.Frame(self, bg='white')
        list_card.pack(fill='both', expand=True)
        
        tk.Label(list_card, text="饮食记录", font=("Microsoft YaHei", 14, "bold"),
                bg='white').pack(anchor='w', padx=15, pady=10)
        
        columns = ("date", "meal_type", "food", "calories")
        self.tree = ttk.Treeview(list_card, columns=columns, show='headings', height=15)
        
        self.tree.heading("date", text="日期")
        self.tree.heading("meal_type", text="餐次")
        self.tree.heading("food", text="食物")
        self.tree.heading("calories", text="热量(kcal)")
        
        self.tree.pack(fill='both', expand=True, padx=15, pady=10)
        
        self.load_diet_records()
    
    def load_diet_records(self):
        self.tree.delete(*self.tree.get_children())
        resp = self.controller.network.send_request("get_diet_records", {"user_id": self.controller.current_user['id']})
        if resp['status'] == 'success':
            for record in resp['data']:
                self.tree.insert("", "end", values=(
                    record['record_date'], record['meal_type'],
                    record['food_description'], record['calories']
                ))
    
    def add_diet(self):
        dialog = tk.Toplevel(self)
        dialog.title("记录饮食")
        dialog.geometry("400x300")
        dialog.configure(bg='white')
        
        entries = {}
        
        tk.Label(dialog, text="日期", bg='white', font=("Microsoft YaHei", 10)).pack(anchor='w', padx=20, pady=(10, 2))
        date_ent = tk.Entry(dialog, font=("Microsoft YaHei", 10), width=35)
        date_ent.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        date_ent.pack(padx=20)
        entries['record_date'] = date_ent
        
        tk.Label(dialog, text="餐次", bg='white', font=("Microsoft YaHei", 10)).pack(anchor='w', padx=20, pady=(10, 2))
        meal_combo = ttk.Combobox(dialog, values=["早餐", "午餐", "晚餐", "加餐"], state="readonly", font=("Microsoft YaHei", 10), width=33)
        meal_combo.set("早餐")
        meal_combo.pack(padx=20)
        entries['meal_type'] = meal_combo
        
        tk.Label(dialog, text="食物描述", bg='white', font=("Microsoft YaHei", 10)).pack(anchor='w', padx=20, pady=(10, 2))
        food_ent = tk.Entry(dialog, font=("Microsoft YaHei", 10), width=35)
        food_ent.pack(padx=20)
        entries['food_description'] = food_ent
        
        tk.Label(dialog, text="热量 (kcal)", bg='white', font=("Microsoft YaHei", 10)).pack(anchor='w', padx=20, pady=(10, 2))
        cal_ent = tk.Entry(dialog, font=("Microsoft YaHei", 10), width=35)
        cal_ent.pack(padx=20)
        entries['calories'] = cal_ent
        
        def submit():
            data = {k: v.get() for k, v in entries.items()}
            data['user_id'] = self.controller.current_user['id']
            resp = self.controller.network.send_request("add_diet", data)
            if resp['status'] == 'success':
                messagebox.showinfo("成功", "饮食记录已添加")
                dialog.destroy()
                self.load_diet_records()
            else:
                messagebox.showerror("失败", resp['message'])
        
        tk.Button(dialog, text="提交", command=submit, bg=COLORS['success'], fg='white',
                 relief='flat', padx=30, pady=8).pack(pady=20)

# --- 提醒中心页面 ---
class RemindersPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['main_bg'])
        self.controller = controller
        
        action_bar = tk.Frame(self, bg=COLORS['main_bg'])
        action_bar.pack(fill='x', pady=(0, 10))
        
        tk.Button(action_bar, text="➕ 新建提醒", command=self.add_reminder,
                 bg=COLORS['primary'], fg='white', font=("Microsoft YaHei", 10),
                 relief='flat', padx=15, pady=5).pack(side=tk.LEFT)
        
        list_card = tk.Frame(self, bg='white')
        list_card.pack(fill='both', expand=True)
        
        tk.Label(list_card, text="我的提醒", font=("Microsoft YaHei", 14, "bold"),
                bg='white').pack(anchor='w', padx=15, pady=10)
        
        columns = ("type", "title", "time", "repeat")
        self.tree = ttk.Treeview(list_card, columns=columns, show='headings', height=15)
        
        self.tree.heading("type", text="类型")
        self.tree.heading("title", text="标题")
        self.tree.heading("time", text="提醒时间")
        self.tree.heading("repeat", text="重复")
        
        self.tree.pack(fill='both', expand=True, padx=15, pady=10)
        
        self.load_reminders()
    
    def load_reminders(self):
        self.tree.delete(*self.tree.get_children())
        resp = self.controller.network.send_request("get_reminders", {"user_id": self.controller.current_user['id']})
        if resp['status'] == 'success':
            for reminder in resp['data']:
                self.tree.insert("", "end", values=(
                    reminder['reminder_type'], reminder['title'],
                    reminder['reminder_time'], reminder['repeat_type']
                ))
    
    def add_reminder(self):
        dialog = tk.Toplevel(self)
        dialog.title("新建提醒")
        dialog.geometry("400x300")
        dialog.configure(bg='white')
        
        entries = {}
        
        tk.Label(dialog, text="提醒类型", bg='white', font=("Microsoft YaHei", 10)).pack(anchor='w', padx=20, pady=(10, 2))
        type_combo = ttk.Combobox(dialog, values=["用药", "测量", "运动", "饮水", "其他"], state="readonly", font=("Microsoft YaHei", 10), width=33)
        type_combo.set("用药")
        type_combo.pack(padx=20)
        entries['reminder_type'] = type_combo
        
        tk.Label(dialog, text="提醒标题", bg='white', font=("Microsoft YaHei", 10)).pack(anchor='w', padx=20, pady=(10, 2))
        title_ent = tk.Entry(dialog, font=("Microsoft YaHei", 10), width=35)
        title_ent.pack(padx=20)
        entries['title'] = title_ent
        
        tk.Label(dialog, text="提醒时间 (HH:MM)", bg='white', font=("Microsoft YaHei", 10)).pack(anchor='w', padx=20, pady=(10, 2))
        time_ent = tk.Entry(dialog, font=("Microsoft YaHei", 10), width=35)
        time_ent.insert(0, "08:00")
        time_ent.pack(padx=20)
        entries['reminder_time'] = time_ent
        
        tk.Label(dialog, text="重复类型", bg='white', font=("Microsoft YaHei", 10)).pack(anchor='w', padx=20, pady=(10, 2))
        repeat_combo = ttk.Combobox(dialog, values=["once", "daily", "weekly"], state="readonly", font=("Microsoft YaHei", 10), width=33)
        repeat_combo.set("daily")
        repeat_combo.pack(padx=20)
        entries['repeat_type'] = repeat_combo
        
        def submit():
            data = {k: v.get() for k, v in entries.items()}
            data['user_id'] = self.controller.current_user['id']
            resp = self.controller.network.send_request("add_reminder", data)
            if resp['status'] == 'success':
                messagebox.showinfo("成功", "提醒已创建")
                dialog.destroy()
                self.load_reminders()
            else:
                messagebox.showerror("失败", resp['message'])
        
        tk.Button(dialog, text="创建", command=submit, bg=COLORS['primary'], fg='white',
                 relief='flat', padx=30, pady=8).pack(pady=20)

# --- 新增：管理员用户管理页面 ---
class AdminUserPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['main_bg'])
        self.controller = controller
        
        # 1. 顶部操作栏（搜索框）
        action_bar = tk.Frame(self, bg=COLORS['main_bg'])
        action_bar.pack(fill='x', pady=(0, 10))
        
        tk.Label(action_bar, text="搜索用户:", bg=COLORS['main_bg'], font=("Microsoft YaHei", 10)).pack(side=tk.LEFT, padx=(0, 10))
        self.search_var = tk.StringVar()
        entry = tk.Entry(action_bar, textvariable=self.search_var, font=("Microsoft YaHei", 10), width=20)
        entry.pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(action_bar, text="🔍 查询", command=self.load_users,
                 bg=COLORS['primary'], fg='white', relief='flat', padx=15).pack(side=tk.LEFT)
                 
        tk.Button(action_bar, text="❌ 删除选中用户", command=self.delete_selected_user,
                 bg=COLORS['danger'], fg='white', relief='flat', padx=15).pack(side=tk.RIGHT)
                 
        # --- 新增 ---
        tk.Button(action_bar, text="📢 发送通知", command=self.send_msg_dialog,
                 bg=COLORS['success'], fg='white', relief='flat', padx=15).pack(side=tk.RIGHT, padx=10)
        
        # 2. 用户列表 (表格)
        list_card = tk.Frame(self, bg='white')
        list_card.pack(fill='both', expand=True)
        
        columns = ("id", "username", "gender", "age", "created_at")
        self.tree = ttk.Treeview(list_card, columns=columns, show='headings', height=20)
        
        self.tree.heading("id", text="ID")
        self.tree.column("id", width=50, anchor='center')
        
        self.tree.heading("username", text="用户名")
        self.tree.column("username", width=150)
        
        self.tree.heading("gender", text="性别")
        self.tree.column("gender", width=80, anchor='center')
        
        self.tree.heading("age", text="年龄")
        self.tree.column("age", width=80, anchor='center')
        
        self.tree.heading("created_at", text="注册时间")
        self.tree.column("created_at", width=200)
        
        self.tree.pack(fill='both', expand=True, padx=15, pady=10)
        
        # 初始加载
        self.load_users()

    def load_users(self):
        # 清空现有数据
        self.tree.delete(*self.tree.get_children())
        
        # 发送请求
        query = self.search_var.get().strip()
        resp = self.controller.network.send_request("get_all_users", {"query": query if query else None})
        
        if resp['status'] == 'success':
            for user in resp['data']:
                self.tree.insert("", "end", values=(
                    user['id'], user['username'], user['gender'], 
                    user['age'], user['created_at']
                ))
        else:
            messagebox.showerror("错误", "无法加载用户列表")

    def delete_selected_user(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("提示", "请先选择一个用户")
            return
            
        values = self.tree.item(selected_item)['values']
        user_id = values[0]
        username = values[1]
        
        # 确认对话框
        if messagebox.askyesno("危险操作", f"确定要删除用户 [{username}] 吗？\n该操作将永久删除该用户的所有健康档案、记录、用药等数据！\n此操作不可恢复！"):
            resp = self.controller.network.send_request("delete_user", {"target_id": user_id})
            
            if resp['status'] == 'success':
                messagebox.showinfo("成功", resp['message'])
                self.load_users() # 刷新列表
            else:
                messagebox.showerror("失败", resp['message'])

    def send_msg_dialog(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("提示", "请先选择一个接收消息的用户")
            return
            
        values = self.tree.item(selected_item)['values']
        user_id = values[0]
        username = values[1]
        
        dialog = tk.Toplevel(self)
        dialog.title(f"发送消息给 {username}")
        dialog.geometry("400x250")
        dialog.configure(bg='white')
        
        tk.Label(dialog, text="消息内容:", bg='white', font=("Microsoft YaHei", 10)).pack(anchor='w', padx=20, pady=(20, 5))
        
        text_area = tk.Text(dialog, height=5, width=40, font=("Microsoft YaHei", 10))
        text_area.pack(padx=20)
        
        def submit():
            msg = text_area.get("1.0", "end").strip()
            if not msg: return
            
            resp = self.controller.network.send_request("send_notification", {"target_id": user_id, "message": msg})
            if resp['status'] == 'success':
                messagebox.showinfo("成功", "通知已发送")
                dialog.destroy()
            else:
                messagebox.showerror("失败", resp['message'])
                
        tk.Button(dialog, text="发送", command=submit, bg=COLORS['primary'], fg='white', relief='flat', padx=20, pady=5).pack(pady=20)

if __name__ == "__main__":
    app = HealthApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
