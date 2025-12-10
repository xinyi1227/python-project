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

# --- 配色方案 (现代化扁平风格 - 健康医疗主题) ---
COLORS = {
    'sidebar_bg': '#001529',      # 深邃蓝夜色 (侧边栏背景)
    'sidebar_fg': '#a6adb4',      # 柔和灰 (侧边栏文字)
    'sidebar_active': '#1890ff',  # 科技蓝 (选中项背景/高亮) - 这是一个稍微鲜亮一点的蓝色，作为点缀
    'sidebar_hover': '#000c17',   # 更深的背景 (悬停)
    
    'header_bg': '#ffffff',       # 纯净白
    'main_bg': '#f0f2f5',         # 浅灰背景 (内容区)
    
    'primary': '#409EFF',         # 科技蓝 (用户指定)
    'primary_hover': '#66b1ff',   # 悬停蓝
    
    'success': '#67C23A',         # 积极绿
    'danger': '#F56C6C',          # 警示红
    'warning': '#E6A23C',         # 提示黄
    
    'text_main': '#262626',       # 主要文字 (深灰)
    'text_regular': '#595959',    # 常规文字 (中灰)
    'text_light': '#8c8c8c',      # 辅助文字 (浅灰)
    
    'border': '#d9d9d9',          # 边框色
    'input_bg': '#ffffff',        # 输入框背景
    'card_bg': '#ffffff'          # 卡片背景
}

# 全局字体配置
FONT_FAMILY = "Microsoft YaHei UI"  # 使用 UI 版本字体更美观
FONT_h1 = (FONT_FAMILY, 24, "bold")
FONT_h2 = (FONT_FAMILY, 18, "bold")
FONT_h3 = (FONT_FAMILY, 14, "bold")
FONT_body = (FONT_FAMILY, 10)
FONT_body_lg = (FONT_FAMILY, 11)
FONT_small = (FONT_FAMILY, 9)

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

# --- 自定义圆角组件 ---

def draw_rounded_rect(canvas, x1, y1, x2, y2, r, **kwargs):
    """在Canvas上绘制圆角矩形"""
    points = [
        x1+r, y1,
        x2-r, y1,
        x2, y1, x2, y1+r,
        x2, y2-r,
        x2, y2, x2-r, y2,
        x1+r, y2,
        x1, y2, x1, y2-r,
        x1, y1+r,
        x1, y1
    ]
    return canvas.create_polygon(points, **kwargs, smooth=True)

class RoundedButton(tk.Canvas):
    """自定义圆角按钮"""
    def __init__(self, parent, text, command, width=120, height=40, radius=20, 
                 bg_color='#409EFF', fg_color='white', font=("Microsoft YaHei", 10), **kwargs):
        super().__init__(parent, width=width, height=height, 
                         bg=parent['bg'], highlightthickness=0, **kwargs)
        self.command = command
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.text = text
        self.radius = radius
        self.font = font
        
        self.rect = draw_rounded_rect(self, 2, 2, width-2, height-2, radius, fill=bg_color, outline="")
        self.text_id = self.create_text(width/2, height/2, text=text, fill=fg_color, font=font)
        
        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        
    def on_click(self, event):
        if self.command:
            self.command()
            
    def on_enter(self, event):
        # 简单变亮效果
        self.itemconfig(self.rect, fill=COLORS.get('primary_hover', '#66b1ff'))
        
    def on_leave(self, event):
        self.itemconfig(self.rect, fill=self.bg_color)

class RoundedEntry(tk.Frame):
    """自定义圆角输入框"""
    def __init__(self, parent, width=30, height=40, radius=10, bg_color='white', border_color='#d9d9d9', **kwargs):
        super().__init__(parent, bg=parent['bg'])
        
        self.canvas = tk.Canvas(self, width=width*10, height=height, bg=parent['bg'], highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        # 绘制背景
        self.bg_rect = draw_rounded_rect(self.canvas, 1, 1, 5000, height-1, radius, fill=bg_color, outline=border_color)
        
        # 嵌入 Entry
        self.entry = tk.Entry(self, bg=bg_color, bd=0, highlightthickness=0, font=FONT_body, **kwargs)
        self.entry.place(x=radius, y=5, relwidth=1.0, height=height-10, width=-2*radius)
        
        # 焦点事件
        self.entry.bind("<FocusIn>", self.on_focus)
        self.entry.bind("<FocusOut>", self.on_unfocus)
        
        self.border_color = border_color
        self.active_color = COLORS['primary']

    def on_focus(self, event):
        self.canvas.itemconfig(self.bg_rect, outline=self.active_color)
        
    def on_unfocus(self, event):
        self.canvas.itemconfig(self.bg_rect, outline=self.border_color)
        
    def get(self):
        return self.entry.get()
        
    def insert(self, *args):
        self.entry.insert(*args)
        
    def delete(self, *args):
        self.entry.delete(*args)
        
    def config(self, **kwargs):
        self.entry.config(**kwargs)

class RoundedFrame(tk.Frame):
    """圆角背景容器"""
    def __init__(self, parent, bg_color='white', radius=15, padding=10, **kwargs):
        super().__init__(parent, bg=parent['bg'], **kwargs)
        self.bg_color = bg_color
        self.radius = radius
        self.padding = padding
        
        self.canvas = tk.Canvas(self, bg=parent['bg'], highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        # Inner frame for content
        self.interior = tk.Frame(self.canvas, bg=bg_color)
        
        # Use window to hold the frame
        self.win_id = self.canvas.create_window(0, 0, window=self.interior, anchor='nw')
        
        self.canvas.bind('<Configure>', self._resize)
        
    def _resize(self, event):
        w, h = event.width, event.height
        self.canvas.delete("bg")
        draw_rounded_rect(self.canvas, 0, 0, w, h, self.radius, fill=self.bg_color, outline="", tags="bg")
        self.canvas.tag_lower("bg")
        
        # Inset content slightly to clear corners
        self.canvas.coords(self.win_id, self.padding, self.padding)
        self.canvas.itemconfigure(self.win_id, width=max(1, w-2*self.padding), height=max(1, h-2*self.padding))

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
        
        # --- Treeview 样式优化 (表格) ---
        style.configure("Treeview", 
                        background="white",
                        fieldbackground="white",
                        foreground=COLORS['text_regular'],
                        rowheight=45,  # 增加行高
                        borderwidth=0,
                        font=FONT_body)
        
        style.configure("Treeview.Heading", 
                        font=FONT_body_lg,
                        background="#fafafa",
                        foreground=COLORS['text_main'],
                        borderwidth=0,
                        relief="flat")
        
        # 选中行颜色
        style.map("Treeview", 
                  background=[('selected', '#e6f7ff')], 
                  foreground=[('selected', COLORS['primary'])])

        # --- 滚动条样式 ---
        style.configure("Vertical.TScrollbar", 
                        gripcount=0,
                        background="#f0f2f5",
                        darkcolor="#f0f2f5",
                        lightcolor="#f0f2f5",
                        troughcolor="#f0f2f5",
                        bordercolor="#f0f2f5",
                        arrowcolor="#909399")
                        
        # --- Combobox 样式 ---
        style.configure("TCombobox",
                        arrowsize=12,
                        padding=5)
        style.map('TCombobox', fieldbackground=[('readonly','white')])
        style.map('TCombobox', selectbackground=[('readonly', 'white')])
        style.map('TCombobox', selectforeground=[('readonly', COLORS['text_main'])])

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
        
        # 1. 背景
        self.canvas = tk.Canvas(self, bg=COLORS['main_bg'], highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # 尝试加载背景图
        self.bg_image = None
        try:
            import os
            # 获取当前脚本所在目录，确保路径正确
            base_dir = os.path.dirname(os.path.abspath(__file__))
            
            # 优先查找脚本同级目录下的 theme.png
            possible_paths = [
                os.path.join(base_dir, "theme.png"),
                os.path.join(base_dir, "bg.png"),
                os.path.join(base_dir, "assets", "theme.png"),
                "theme.png", # Fallback for current working dir
                "bg.png"
            ]
            
            img_path = next((p for p in possible_paths if os.path.exists(p)), None)
                
            if img_path:
                # 使用 PIL (Pillow) 加载以支持更多格式和自动缩放 (如果可用)
                try:
                    from PIL import Image, ImageTk
                    pil_image = Image.open(img_path)
                    # 调整图片大小以铺满窗口 (简单适配 1280x800)
                    pil_image = pil_image.resize((1280, 800), Image.Resampling.LANCZOS)
                    self.bg_image = ImageTk.PhotoImage(pil_image)
                except ImportError:
                    # 如果没有 PIL，使用原生 PhotoImage
                    self.bg_image = tk.PhotoImage(file=img_path)
                
                self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
            else:
                # 默认装饰背景
                self.create_default_bg()
        except Exception as e:
            print(f"Background load error: {e}")
            self.create_default_bg()

    def create_default_bg(self):
        self.canvas.create_rectangle(0, 0, 3000, 350, fill=COLORS['primary'], outline="")
        self.canvas.create_oval(-100, -100, 300, 300, fill="", outline="white", width=2, stipple='gray50')
        self.canvas.create_oval(800, 50, 1200, 450, fill="", outline="white", width=2, stipple='gray25')

        # 2. 居中登录卡片
        card_width = 420
        card_height = 460
        
        # 阴影层 (使用 create_window 放入 Canvas，避免被图片覆盖)
        shadow = tk.Frame(self.canvas, bg='#e0e0e0')
        self.shadow_window = self.canvas.create_window(
            0, 0, window=shadow, anchor='center', width=card_width+4, height=card_height+4
        )
        
        # 实际卡片
        self.card = tk.Frame(self.canvas, bg='white', relief='flat')
        self.card_window = self.canvas.create_window(
            0, 0, window=self.card, anchor='center', width=card_width, height=card_height
        )
        
        # 绑定 resize 事件以居中
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        
        # 标题
        tk.Label(self.card, text="HealthGuard", font=FONT_h1, 
                 bg='white', fg=COLORS['primary']).pack(pady=(40, 5))
        tk.Label(self.card, text="个人健康管理系统", font=FONT_body, 
                 bg='white', fg=COLORS['text_light']).pack(pady=(0, 30))
        
        # 输入框容器
        form_frame = tk.Frame(self.card, bg='white')
        form_frame.pack(fill='x', padx=50)
        
        # 用户名
        self.user_entry = self.add_input_field(form_frame, "请输入账号", pady=20)
        
        # 密码
        self.pwd_entry = self.add_input_field(form_frame, "请输入密码", show="*", pady=25)
        
        # 登录按钮 (圆角)
        RoundedButton(form_frame, text="登  录", command=self.login,
                      width=320, height=45, bg_color=COLORS['primary'], 
                      font=FONT_body_lg).pack(fill='x', pady=5)
        
        # 注册链接
        link_frame = tk.Frame(self.card, bg='white')
        link_frame.pack(pady=20)
        tk.Label(link_frame, text="还没有账号？", font=FONT_small, bg='white', fg=COLORS['text_light']).pack(side=tk.LEFT)
        reg_link = tk.Label(link_frame, text="立即注册", font=FONT_small,
                 bg='white', fg=COLORS['primary'], cursor='hand2')
        reg_link.pack(side=tk.LEFT, padx=5)
        
        reg_link.bind("<Button-1>", lambda e: self.controller.show_frame("RegisterFrame"))

    def on_canvas_resize(self, event):
        # 动态居中
        w, h = event.width, event.height
        self.canvas.coords(self.shadow_window, w/2, h/2)
        self.canvas.coords(self.card_window, w/2, h/2)

    def add_input_field(self, parent, placeholder, show=None, pady=0):
        # 使用 RoundedEntry
        container = tk.Frame(parent, bg='white')
        container.pack(fill='x', pady=(0, pady))
        
        entry = RoundedEntry(container, width=30, height=45)
        entry.insert(0, placeholder)
        
        if show:
            entry.config(show=show)
            
        entry.pack(fill='x')
        
        # Placeholder 逻辑
        def on_focus(e):
            if entry.get() == placeholder:
                entry.delete(0, 'end')
                entry.config(fg='black')
                if show: entry.config(show=show)
                
        def on_unfocus(e):
            if entry.get() == "":
                entry.insert(0, placeholder)
                entry.config(fg='#8c8c8c') # Placeholder color
                entry.config(show="")

        # 重新绑定 RoundedEntry 内部 entry 的事件
        entry.entry.bind("<FocusIn>", lambda e: [entry.on_focus(e), on_focus(e)])
        entry.entry.bind("<FocusOut>", lambda e: [entry.on_unfocus(e), on_unfocus(e)])
        
        return entry

    def on_focus_in(self, entry, placeholder, show_char=None, border_frame=None):
        if border_frame: border_frame.config(bg=COLORS['primary'])
        if entry.get() == placeholder:
            entry.delete(0, 'end')
            entry.config(fg=COLORS['text_main'])
            if show_char:
                entry.config(show=show_char)

    def on_focus_out(self, entry, placeholder, border_frame=None):
        if border_frame: border_frame.config(bg=COLORS['border'])
        if entry.get() == "":
            entry.insert(0, placeholder)
            entry.config(fg=COLORS['text_light'])
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
        tk.Frame.__init__(self, parent) # 重置 init
        self.controller = controller
        
        self.canvas = tk.Canvas(self, bg=COLORS['main_bg'], highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        # 绿色背景区分 -> 改为青色统一风格但深一点
        self.canvas.create_rectangle(0, 0, 3000, 350, fill='#13c2c2', outline="") 
        
        card_width = 420
        card_height = 550 # 更高
        
        shadow = tk.Frame(self, bg='#e0e0e0')
        shadow.place(relx=0.5, rely=0.5, anchor='center', width=card_width+4, height=card_height+4)
        
        self.card = tk.Frame(self, bg='white', relief='flat')
        self.card.place(relx=0.5, rely=0.5, anchor='center', width=card_width, height=card_height)
        
        tk.Label(self.card, text="注册新用户", font=FONT_h1, 
                 bg='white', fg=COLORS['text_main']).pack(pady=(30, 20))
        
        form_frame = tk.Frame(self.card, bg='white')
        form_frame.pack(fill='x', padx=50)
        
        self.user_entry = self.add_input_field(form_frame, "用户名", pady=15)
        self.pwd_entry = self.add_input_field(form_frame, "密码", show="*", pady=15)
        self.age_entry = self.add_input_field(form_frame, "年龄", pady=15)
        
        # 性别选择框 (自定义样式 wrap)
        self.gender_combo = ttk.Combobox(form_frame, values=["男", "女"], state="readonly", font=FONT_body_lg)
        self.gender_combo.set("请选择性别")
        self.gender_combo.pack(fill='x', pady=(0, 20), ipady=3)
        
        reg_btn = tk.Button(form_frame, text="立即注册", command=self.register,
                           bg=COLORS['primary'], fg='white',
                           font=FONT_body_lg, relief='flat',
                           activebackground=COLORS['primary_hover'], activeforeground='white',
                           cursor='hand2')
        reg_btn.pack(fill='x', ipady=8)
        
        tk.Button(self.card, text="返回登录", command=lambda: controller.show_frame("LoginFrame"),
                 font=FONT_small, bg='white', fg=COLORS['text_light'], bd=0, cursor='hand2').pack(pady=15)

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
        self.sidebar = tk.Frame(self, bg=COLORS['sidebar_bg'], width=240) # 加宽侧边栏
        self.sidebar.pack(side=tk.LEFT, fill='y')
        self.sidebar.pack_propagate(False) # 固定宽度
        
        # Logo区
        logo_frame = tk.Frame(self.sidebar, bg=COLORS['sidebar_bg'], height=80)
        logo_frame.pack(fill='x')
        tk.Label(logo_frame, text="HealthGuard", font=FONT_h2, 
                 bg=COLORS['sidebar_bg'], fg='white').place(relx=0.5, rely=0.5, anchor='center')
        
        # 分隔线
        tk.Frame(self.sidebar, bg=COLORS['sidebar_active'], height=1).pack(fill='x', pady=(0, 10))
        
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
        
        # 2.1 顶部导航栏 (增加阴影线)
        self.header = tk.Frame(self.main_area, bg=COLORS['header_bg'], height=60)
        self.header.pack(fill='x')
        self.header.pack_propagate(False)
        
        # 底部边框线
        tk.Frame(self.header, bg=COLORS['border'], height=1).pack(side=tk.BOTTOM, fill='x')
        
        # 面包屑/标题
        self.header_label = tk.Label(self.header, text="首页 / 仪表盘", font=FONT_body_lg, 
                                     bg='white', fg=COLORS['text_regular'])
        self.header_label.pack(side=tk.LEFT, padx=30)
        
        # 用户信息 & 注销
        user_info = tk.Frame(self.header, bg='white')
        user_info.pack(side=tk.RIGHT, padx=30)
        tk.Label(user_info, text=f"欢迎, {controller.current_user['username']}", 
                 bg='white', fg=COLORS['text_main'], font=FONT_body).pack(side=tk.LEFT, padx=15)
        
        RoundedButton(user_info, text="注销", command=lambda: controller.show_frame("LoginFrame"),
                 bg_color=COLORS['danger'], width=80, height=30,
                 font=FONT_small).pack(side=tk.LEFT)
        
        # 2.2 内容区 (使用 Frame 容器)
        self.content_frame = tk.Frame(self.main_area, bg=COLORS['main_bg'])
        self.content_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # 初始化默认页面
        self.current_page_frame = None
        self.switch_page("dashboard")

    def create_sidebar_btn(self, text, command):
        # 增加左边框指示条容器
        btn_frame = tk.Frame(self.sidebar, bg=COLORS['sidebar_bg'])
        btn_frame.pack(fill='x', pady=2)
        
        indicator = tk.Frame(btn_frame, bg=COLORS['sidebar_bg'], width=4)
        indicator.pack(side=tk.LEFT, fill='y')
        
        btn = tk.Button(btn_frame, text=text,
                       bg=COLORS['sidebar_bg'], fg=COLORS['sidebar_fg'],
                       font=FONT_body_lg, bd=0, 
                       activebackground=COLORS['sidebar_active'],
                       activeforeground='white', 
                       anchor='w', padx=25, pady=12, 
                       cursor='hand2',
                       relief='flat')
        
        # 闭包保存状态
        def on_click():
            # 重置所有按钮样式 (这里简化处理，实际可以通过遍历 components 优化)
            command()
            
        btn.config(command=command)
        btn.pack(side=tk.LEFT, fill='x', expand=True)
        
        # 简单的 hover 效果
        def on_enter(e):
            if btn['bg'] != COLORS['sidebar_active']:
                btn['bg'] = COLORS['sidebar_hover']
        def on_leave(e):
            if btn['bg'] != COLORS['sidebar_active']:
                btn['bg'] = COLORS['sidebar_bg']
                
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

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
        chart_frame = RoundedFrame(self, bg_color='white')
        chart_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        self.canvas_frame = tk.Frame(chart_frame.interior, bg='white')
        self.canvas_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 下部分：数据表格 (Treeview)
        table_frame = RoundedFrame(self, bg_color='white')
        table_frame.pack(fill='x', ipady=10)
        
        tk.Label(table_frame.interior, text="历史记录明细", font=FONT_h3, 
                 bg='white', fg=COLORS['text_main']).pack(anchor='w', padx=15, pady=10)
        
        columns = ("date", "weight", "steps", "bp")
        self.tree = ttk.Treeview(table_frame.interior, columns=columns, show='headings', height=6)
        
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
                 bg='#fdf6ec', fg='#e6a23c', font=FONT_body).pack(side=tk.LEFT, padx=10, pady=8)
                 
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
        card = RoundedFrame(self, bg_color='white')
        card.pack(fill='both', expand=True)
        
        # 顶部操作栏
        action_bar = tk.Frame(card.interior, bg='white', height=60)
        action_bar.pack(fill='x', padx=20, pady=10)
        
        RoundedButton(action_bar, text="📝 提交今日数据", command=self.submit,
                      bg_color=COLORS['primary'], width=160, height=40).pack(side=tk.LEFT)
        
        # 创建滚动区域
        canvas = tk.Canvas(card.interior, bg='white')
        scrollbar = ttk.Scrollbar(card.interior, orient="vertical", command=canvas.yview)
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
            tk.Label(scrollable_frame, text=section_title, font=FONT_h3,
                    bg='white', fg=COLORS['primary']).pack(anchor='w', pady=(15, 10))
            
            for label, key, default in section_fields:
                row_frame = tk.Frame(scrollable_frame, bg='white')
                row_frame.pack(fill='x', pady=8)
                
                tk.Label(row_frame, text=label, width=20, anchor='e', bg='white', 
                        font=FONT_body).pack(side=tk.LEFT, padx=10)
                
                if key == 'notes':
                    ent = tk.Text(row_frame, font=FONT_body, relief='solid', 
                                 bd=1, width=40, height=3)
                    ent.pack(side=tk.LEFT) # Text 不容易做圆角，保持原样或包一层
                else:
                    ent = RoundedEntry(row_frame, width=15) # 改短 width=15
                    ent.pack(side=tk.LEFT, fill='none', expand=False)
                    if default: 
                        ent.insert(0, default)
                
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
        card = RoundedFrame(self.card_frame, bg_color='white', width=260, height=130)
        card.grid(row=0, column=col, padx=20)
        card.pack_propagate(False)
        
        # 左侧色条
        tk.Frame(card.interior, bg=color, width=5).pack(side=tk.LEFT, fill='y')
        
        content = tk.Frame(card.interior, bg='white')
        content.pack(side=tk.LEFT, fill='both', expand=True, padx=20)
        
        tk.Label(content, text=title, font=FONT_body_lg, fg='#909399', bg='white').pack(anchor='w', pady=(25, 5))
        tk.Label(content, text=str(value), font=FONT_h1, fg=COLORS['text_main'], bg='white').pack(anchor='w')

# --- 健康档案页面 ---
class ProfilePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['main_bg'])
        self.controller = controller
        
        card = RoundedFrame(self, bg_color='white')
        card.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(card.interior, text="个人健康档案", font=FONT_h2,
                bg='white', fg=COLORS['text_main']).pack(anchor='w', padx=20, pady=15)
        
        # 获取当前档案
        resp = controller.network.send_request("get_profile", {"user_id": controller.current_user['id']})
        profile = resp.get('data', {}) if resp['status'] == 'success' else {}
        
        form = tk.Frame(card.interior, bg='white')
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
            tk.Label(row, text=label, width=15, anchor='e', bg='white', font=FONT_body).pack(side=tk.LEFT, padx=10)
            ent = RoundedEntry(row, width=40)
            ent.insert(0, str(default) if default else '')
            ent.pack(side=tk.LEFT, fill='x', expand=True)
            self.entries[key] = ent
        
        RoundedButton(card.interior, text="保存档案", command=self.save_profile,
                      bg_color=COLORS['primary'], width=160, height=40).pack(pady=20)
    
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
        
        RoundedButton(action_bar, text="➕ 添加用药", command=self.add_medication,
                      bg_color=COLORS['success'], width=120, height=36).pack(side=tk.LEFT)
        
        # 用药列表
        list_card = tk.Frame(self, bg='white')
        list_card.pack(fill='both', expand=True)
        
        tk.Label(list_card, text="我的用药清单", font=FONT_h3,
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
        RoundedButton(list_card, text="删除选中", command=self.delete_selected,
                      bg_color=COLORS['danger'], width=120, height=36).pack(pady=10)
        
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
            tk.Label(dialog, text=label, bg='white', font=FONT_body).pack(anchor='w', padx=20, pady=(10, 2))
            ent = RoundedEntry(dialog, width=35)
            if key == 'start_date':
                ent.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
            ent.pack(padx=20, fill='x')
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
        
        RoundedButton(dialog, text="提交", command=submit, bg_color=COLORS['success'], width=140, height=40).pack(pady=20)
    
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
        
        RoundedButton(action_bar, text="➕ 新建目标", command=self.add_goal,
                      bg_color=COLORS['primary'], width=120, height=36).pack(side=tk.LEFT)
        
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
                        bg=COLORS['main_bg'], font=FONT_h3).pack(pady=50)
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
        
        tk.Label(content, text=f"🎯 {goal['goal_type']}", font=FONT_h3,
                bg='white').pack(anchor='w')
        tk.Label(content, text=f"目标: {goal['target_value']} | 当前: {goal['current_value']} | 进度: {progress:.1f}%",
                font=FONT_body, bg='white', fg='gray').pack(anchor='w', pady=5)
        tk.Label(content, text=f"期限: {goal['start_date']} 至 {goal['end_date']}",
                font=FONT_small, bg='white', fg='gray').pack(anchor='w')
    
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
            tk.Label(dialog, text=label, bg='white', font=FONT_body).pack(anchor='w', padx=20, pady=(10, 2))
            ent = RoundedEntry(dialog, width=35)
            if 'date' in key:
                ent.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
            ent.pack(padx=20, fill='x')
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
        
        RoundedButton(dialog, text="创建", command=submit, bg_color=COLORS['primary'], width=140, height=40).pack(pady=20)

# --- 饮食记录页面 ---
class DietPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['main_bg'])
        self.controller = controller
        
        action_bar = tk.Frame(self, bg=COLORS['main_bg'])
        action_bar.pack(fill='x', pady=(0, 10))
        
        RoundedButton(action_bar, text="➕ 记录饮食", command=self.add_diet,
                      bg_color=COLORS['success'], width=120, height=36).pack(side=tk.LEFT)
        
        list_card = tk.Frame(self, bg='white')
        list_card.pack(fill='both', expand=True)
        
        tk.Label(list_card, text="饮食记录", font=FONT_h3,
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
        
        tk.Label(dialog, text="日期", bg='white', font=FONT_body).pack(anchor='w', padx=20, pady=(10, 2))
        date_ent = RoundedEntry(dialog, width=35)
        date_ent.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        date_ent.pack(padx=20, fill='x')
        entries['record_date'] = date_ent
        
        tk.Label(dialog, text="餐次", bg='white', font=FONT_body).pack(anchor='w', padx=20, pady=(10, 2))
        meal_combo = ttk.Combobox(dialog, values=["早餐", "午餐", "晚餐", "加餐"], state="readonly", font=FONT_body, width=33)
        meal_combo.set("早餐")
        meal_combo.pack(padx=20, fill='x')
        entries['meal_type'] = meal_combo
        
        tk.Label(dialog, text="食物描述", bg='white', font=FONT_body).pack(anchor='w', padx=20, pady=(10, 2))
        food_ent = RoundedEntry(dialog, width=35)
        food_ent.pack(padx=20, fill='x')
        entries['food_description'] = food_ent
        
        tk.Label(dialog, text="热量 (kcal)", bg='white', font=FONT_body).pack(anchor='w', padx=20, pady=(10, 2))
        cal_ent = RoundedEntry(dialog, width=35)
        cal_ent.pack(padx=20, fill='x')
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
        
        RoundedButton(dialog, text="提交", command=submit, bg_color=COLORS['success'], width=140, height=40).pack(pady=20)

# --- 提醒中心页面 ---
class RemindersPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['main_bg'])
        self.controller = controller
        
        action_bar = tk.Frame(self, bg=COLORS['main_bg'])
        action_bar.pack(fill='x', pady=(0, 10))
        
        RoundedButton(action_bar, text="➕ 新建提醒", command=self.add_reminder,
                      bg_color=COLORS['primary'], width=120, height=36).pack(side=tk.LEFT)
        
        list_card = tk.Frame(self, bg='white')
        list_card.pack(fill='both', expand=True)
        
        tk.Label(list_card, text="我的提醒", font=FONT_h3,
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
        
        tk.Label(dialog, text="提醒类型", bg='white', font=FONT_body).pack(anchor='w', padx=20, pady=(10, 2))
        type_combo = ttk.Combobox(dialog, values=["用药", "测量", "运动", "饮水", "其他"], state="readonly", font=FONT_body, width=33)
        type_combo.set("用药")
        type_combo.pack(padx=20, fill='x')
        entries['reminder_type'] = type_combo
        
        tk.Label(dialog, text="提醒标题", bg='white', font=FONT_body).pack(anchor='w', padx=20, pady=(10, 2))
        title_ent = RoundedEntry(dialog, width=35)
        title_ent.pack(padx=20, fill='x')
        entries['title'] = title_ent
        
        tk.Label(dialog, text="提醒时间 (HH:MM)", bg='white', font=FONT_body).pack(anchor='w', padx=20, pady=(10, 2))
        time_ent = RoundedEntry(dialog, width=35)
        time_ent.insert(0, "08:00")
        time_ent.pack(padx=20, fill='x')
        entries['reminder_time'] = time_ent
        
        tk.Label(dialog, text="重复类型", bg='white', font=FONT_body).pack(anchor='w', padx=20, pady=(10, 2))
        repeat_combo = ttk.Combobox(dialog, values=["once", "daily", "weekly"], state="readonly", font=FONT_body, width=33)
        repeat_combo.set("daily")
        repeat_combo.pack(padx=20, fill='x')
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
        
        RoundedButton(dialog, text="创建", command=submit, bg_color=COLORS['primary'], width=140, height=40).pack(pady=20)

# --- 新增：管理员用户管理页面 ---
class AdminUserPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['main_bg'])
        self.controller = controller
        
        # 1. 顶部操作栏（搜索框）
        action_bar = tk.Frame(self, bg=COLORS['main_bg'])
        action_bar.pack(fill='x', pady=(0, 10))
        
        tk.Label(action_bar, text="搜索用户:", bg=COLORS['main_bg'], font=FONT_body).pack(side=tk.LEFT, padx=(0, 10))
        self.search_var = tk.StringVar()
        entry = RoundedEntry(action_bar, width=20, height=36)
        # 绑定 StringVar 比较麻烦，需要重写 RoundedEntry 或不用 StringVar
        # 这里为了简单，直接用 .get() 方式，不绑定 textvariable
        self.search_entry = entry 
        entry.pack(side=tk.LEFT, padx=(0, 10))
        
        RoundedButton(action_bar, text="🔍 查询", command=self.load_users,
                      bg_color=COLORS['primary'], width=100, height=36).pack(side=tk.LEFT)
                 
        RoundedButton(action_bar, text="❌ 删除选中用户", command=self.delete_selected_user,
                      bg_color=COLORS['danger'], width=140, height=36).pack(side=tk.RIGHT)
                 
        # --- 新增 ---
        RoundedButton(action_bar, text="📢 发送通知", command=self.send_msg_dialog,
                      bg_color=COLORS['success'], width=120, height=36).pack(side=tk.RIGHT, padx=10)
        
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
        query = self.search_entry.get().strip() # 使用 RoundedEntry 的 get
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
        
        tk.Label(dialog, text="消息内容:", bg='white', font=FONT_body).pack(anchor='w', padx=20, pady=(20, 5))
        
        text_area = tk.Text(dialog, height=5, width=40, font=FONT_body)
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
                
        RoundedButton(dialog, text="发送", command=submit, bg_color=COLORS['primary'], width=120, height=36).pack(pady=20)

if __name__ == "__main__":
    app = HealthApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
