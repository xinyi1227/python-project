import sys
import os
import json
import socket
import datetime
import requests
import webbrowser
import subprocess
import platform
import random
from bs4 import BeautifulSoup
from advisor import SmartHealthAdvisor
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QStackedWidget, QMessageBox, 
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, 
    QFrame, QDialog, QTextEdit, QScrollArea, QSizePolicy, QGraphicsDropShadowEffect,
    QAbstractItemView, QTabWidget, QTabBar, QDateEdit, QSpinBox, QDoubleSpinBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QRect, QThread, QTimer
from PyQt5.QtGui import QColor, QFont, QPixmap, QIcon, QPalette, QBrush, QPainter, QPainterPath
from PyQt5.QtCore import QUrl
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib

# Set Font for Matplotlib to support Chinese
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'Microsoft YaHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

# Configuration
SERVER_IP = '127.0.0.1'
SERVER_PORT = 9999

COLORS = {
    'sidebar_bg': '#001529',
    'sidebar_fg': '#a6adb4',
    'sidebar_active': '#1890ff',
    'sidebar_hover': '#000c17', # Added missing color
    'header_bg': '#ffffff',
    'main_bg': '#f0f2f5',
    'primary': '#409EFF',
    'success': '#67C23A',
    'danger': '#F56C6C',
    'text_main': '#303133',
    'text_regular': '#606266',
    'text_light': '#909399',
    'warning': '#E6A23C',
    'border': '#EBEEF5',
    'white': '#ffffff'
}

FONT_FAMILY = "Microsoft YaHei"

class NetworkClient:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((SERVER_IP, SERVER_PORT))
        except ConnectionRefusedError:
            # We can't use QMessageBox here easily without a window, but we'll try
            print(f"无法连接到服务器 {SERVER_IP}:{SERVER_PORT}")
            sys.exit(1)

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

class RoundedButton(QPushButton):
    def __init__(self, text, bg_color=COLORS['primary'], width=None, height=40, font_size=14, radius=None):
        super().__init__(text)
        self.setCursor(Qt.PointingHandCursor)
        if width:
            self.setFixedWidth(width)
        self.setFixedHeight(height)
        
        r = radius if radius else height // 2
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: white;
                border-radius: {r}px;
                font-family: "{FONT_FAMILY}";
                font-size: {font_size}px;
                border: none;
                font-weight: bold;
            }}
            QPushButton:hover {{
                opacity: 0.9;
            }}
            QPushButton:pressed {{
                background-color: {bg_color};
            }}
        """)

class RoundedEntry(QLineEdit):
    def __init__(self, placeholder="", width=None, password=False):
        super().__init__()
        self.setPlaceholderText(placeholder)
        if width:
            self.setFixedWidth(width)
        self.setFixedHeight(40)
        if password:
            self.setEchoMode(QLineEdit.Password)
            
        self.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {COLORS['border']};
                border-radius: 20px;
                padding: 0 15px;
                font-family: "{FONT_FAMILY}";
                font-size: 14px;
                background-color: white;
                color: {COLORS['text_main']};
            }}
            QLineEdit:focus {{
                border: 1px solid {COLORS['primary']};
            }}
        """)

class CardFrame(QFrame):
    """白色圆角卡片容器"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        # Shadow effect - slightly softer
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 15))
        self.setGraphicsEffect(shadow)

class ModernTable(QTableWidget):
    """美化版表格组件"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.verticalHeader().setVisible(False)
        self.setFrameShape(QFrame.NoFrame)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers) # Read-only by default
        
        # Header Style
        self.horizontalHeader().setFixedHeight(45)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # Set Stylesheet
        self.setStyleSheet(f"""
            QTableWidget {{
                background-color: white;
                alternate-background-color: #fafafa;
                border: none;
                gridline-color: {COLORS['border']};
                selection-background-color: #e6f7ff;
                selection-color: {COLORS['text_main']};
                font-family: "{FONT_FAMILY}";
                font-size: 14px;
                padding: 10px;
            }}
            QHeaderView::section {{
                background-color: #fafafa;
                color: {COLORS['text_regular']};
                padding-left: 15px;
                border: none;
                border-bottom: 1px solid {COLORS['border']};
                font-weight: bold;
                font-family: "{FONT_FAMILY}";
                font-size: 14px;
                height: 45px;
            }}
            QTableWidget::item {{
                padding-left: 15px;
                border-bottom: 1px solid {COLORS['border']};
                color: {COLORS['text_main']};
                height: 50px;
            }}
            QTableWidget::item:selected {{
                background-color: #e6f7ff;
                color: {COLORS['primary']};
            }}
            /* Scrollbar Styling */
            QScrollBar:vertical {{
                border: none;
                background: #f0f2f5;
                width: 8px;
                margin: 0px 0px 0px 0px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: #c0c4cc;
                min-height: 20px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #909399;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)

class LoginWindow(QWidget):
    def __init__(self, app_manager):
        super().__init__()
        self.app_manager = app_manager
        self.initUI()

    def initUI(self):
        self.setWindowTitle("HealthGuard - 登录")
        self.resize(1280, 800)
        
        # Background
        self.bg_label = QLabel(self)
        self.bg_label.resize(1280, 800)
        self.bg_label.setScaledContents(True)
        
        # Try load image
        bg_path = "theme.png"
        if not os.path.exists(bg_path):
            bg_path = "assets/theme.png"
        
        if os.path.exists(bg_path):
            self.bg_label.setPixmap(QPixmap(bg_path))
        else:
            self.bg_label.setStyleSheet(f"background-color: {COLORS['sidebar_bg']};")

        # Center Card
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        card = QFrame()
        card.setFixedSize(420, 460)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
            }}
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(20)
        
        title = QLabel("HealthGuard")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"font-family: '{FONT_FAMILY}'; font-size: 32px; font-weight: bold; color: {COLORS['primary']}; background: transparent;")
        
        subtitle = QLabel("个人健康管理系统")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(f"font-family: '{FONT_FAMILY}'; font-size: 16px; color: {COLORS['text_regular']}; background: transparent;")
        
        self.user_input = RoundedEntry("请输入账号")
        self.pwd_input = RoundedEntry("请输入密码", password=True)
        
        login_btn = RoundedButton("登  录", width=340, height=45)
        login_btn.clicked.connect(self.handle_login)
        
        reg_btn = QPushButton("还没有账号？点击注册")
        reg_btn.setCursor(Qt.PointingHandCursor)
        reg_btn.setStyleSheet(f"border: none; color: {COLORS['primary']}; background: transparent; font-family: '{FONT_FAMILY}';")
        reg_btn.clicked.connect(lambda: self.app_manager.show_register())
        
        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.user_input)
        card_layout.addWidget(self.pwd_input)
        card_layout.addSpacing(10)
        card_layout.addWidget(login_btn)
        card_layout.addWidget(reg_btn)
        card_layout.addStretch()
        
        layout.addWidget(card)

    def handle_login(self):
        u = self.user_input.text()
        p = self.pwd_input.text()
        if not u or not p:
            QMessageBox.warning(self, "提示", "请输入账号和密码")
            return
            
        resp = self.app_manager.network.send_request("login", {"username": u, "password": p})
        if resp["status"] == "success":
            self.app_manager.current_user = resp["data"]
            self.app_manager.show_main()
        else:
            QMessageBox.critical(self, "错误", resp.get("message", "登录失败"))

    def resizeEvent(self, event):
        self.bg_label.resize(self.size())
        super().resizeEvent(event)

class RegisterWindow(QWidget):
    def __init__(self, app_manager):
        super().__init__()
        self.app_manager = app_manager
        self.initUI()

    def initUI(self):
        self.setWindowTitle("HealthGuard - 注册")
        self.resize(1280, 800)
        
        # Reuse bg logic (simplified)
        self.bg_label = QLabel(self)
        self.bg_label.resize(1280, 800)
        self.bg_label.setScaledContents(True)
        if os.path.exists("theme.png"): self.bg_label.setPixmap(QPixmap("theme.png"))
        else: self.bg_label.setStyleSheet(f"background-color: {COLORS['sidebar_bg']};")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        card = QFrame()
        card.setFixedSize(420, 550)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
            }}
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(15)
        
        title = QLabel("注册新用户")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"font-family: '{FONT_FAMILY}'; font-size: 28px; font-weight: bold; color: {COLORS['text_main']}; background: transparent;")
        
        self.user_input = RoundedEntry("用户名")
        self.pwd_input = RoundedEntry("密码", password=True)
        self.age_input = RoundedEntry("年龄")
        
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["男", "女"])
        self.gender_combo.setFixedHeight(40)
        self.gender_combo.setStyleSheet(f"""
            QComboBox {{
                border: 1px solid {COLORS['border']};
                border-radius: 20px;
                padding: 0 15px;
                background: white;
            }}
        """)
        
        reg_btn = RoundedButton("立即注册", bg_color=COLORS['success'], width=340, height=45)
        reg_btn.clicked.connect(self.handle_register)
        
        back_btn = QPushButton("返回登录")
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setStyleSheet(f"border: none; color: {COLORS['text_regular']}; background: transparent;")
        back_btn.clicked.connect(lambda: self.app_manager.show_login())
        
        card_layout.addWidget(title)
        card_layout.addSpacing(20)
        card_layout.addWidget(self.user_input)
        card_layout.addWidget(self.pwd_input)
        card_layout.addWidget(self.age_input)
        card_layout.addWidget(self.gender_combo)
        card_layout.addSpacing(10)
        card_layout.addWidget(reg_btn)
        card_layout.addWidget(back_btn)
        card_layout.addStretch()
        
        layout.addWidget(card)

    def handle_register(self):
        u = self.user_input.text()
        p = self.pwd_input.text()
        a = self.age_input.text()
        g = self.gender_combo.currentText()
        
        if not u or not p:
            QMessageBox.warning(self, "提示", "信息不完整")
            return
            
        resp = self.app_manager.network.send_request("register", {"username": u, "password": p, "age": a, "gender": g})
        if resp["status"] == "success":
            QMessageBox.information(self, "成功", "注册成功")
            self.app_manager.show_login()
        else:
            QMessageBox.warning(self, "失败", resp["message"])
            
    def resizeEvent(self, event):
        self.bg_label.resize(self.size())
        super().resizeEvent(event)

class MainWindow(QMainWindow):
    def __init__(self, app_manager):
        super().__init__()
        self.app_manager = app_manager
        self.setWindowTitle("HealthGuard - 个人健康管理系统")
        self.resize(1280, 800)
        
        # Central Widget
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.setup_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Main Content Area
        content_area = QWidget()
        content_area.setStyleSheet(f"background-color: {COLORS['main_bg']};")
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Header
        self.setup_header()
        content_layout.addWidget(self.header)
        
        # Pages Stack
        self.pages = QStackedWidget()
        self.pages.setContentsMargins(20, 20, 20, 20)
        content_layout.addWidget(self.pages)
        
        main_layout.addWidget(content_area)
        
        self.init_pages()

    def setup_sidebar(self):
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(240)
        self.sidebar.setStyleSheet(f"background-color: {COLORS['sidebar_bg']}; border: none;")
        
        layout = QVBoxLayout(self.sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Logo
        logo = QLabel("HealthGuard")
        logo.setFixedHeight(80)
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet(f"color: white; font-size: 24px; font-weight: bold; font-family: '{FONT_FAMILY}';")
        layout.addWidget(logo)
        
        # Menu Items
        self.menu_layout = QVBoxLayout()
        self.menu_layout.setSpacing(8) # Increased spacing
        self.menu_layout.setContentsMargins(15, 15, 15, 15)
        
        # 1. Dashboard (Index 0)
        self.add_menu_btn("📊  仪表盘", 0)
        
        role = self.app_manager.current_user['role']
        if role == 'user':
            # 2. Health News (Index 1)
            self.add_menu_btn("📰  健康资讯", 1)
            self.add_menu_btn("📝  健康打卡", 2)
            self.add_menu_btn("👤  健康档案", 3)
            self.add_menu_btn("💊  用药管理", 4)
            self.add_menu_btn("🎯  健康目标", 5)
            self.add_menu_btn("🍎  饮食记录", 6)
            self.add_menu_btn("⏰  提醒中心", 7)
        else:
            self.add_menu_btn("👥  用户管理", 8)
            
        layout.addLayout(self.menu_layout)
        layout.addStretch()

    def add_menu_btn(self, text, index):
        btn = QPushButton(text)
        btn.setFixedHeight(50)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                color: {COLORS['sidebar_fg']};
                background-color: transparent;
                border: none;
                text-align: left;
                padding-left: 20px;
                font-size: 16px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['sidebar_hover']};
                color: white;
            }}
            QPushButton:checked {{
                background-color: {COLORS['sidebar_active']};
                color: white;
            }}
        """)
        btn.setCheckable(True)
        btn.setAutoExclusive(True)
        if index == 0: btn.setChecked(True)
        btn.clicked.connect(lambda: self.on_menu_click(index, text))
        self.menu_layout.addWidget(btn)

    def on_menu_click(self, index, text):
        self.pages.setCurrentIndex(index)
        # Extract name cleanly
        clean_text = text.split()[-1] 
        if hasattr(self, 'header_title'):
            self.header_title.setText(f"首页 / {clean_text}")

    def setup_header(self):
        self.header = QFrame()
        self.header.setFixedHeight(60)
        self.header.setStyleSheet(f"background-color: {COLORS['header_bg']}; border-bottom: 1px solid {COLORS['border']};")
        
        layout = QHBoxLayout(self.header)
        layout.setContentsMargins(30, 0, 30, 0)
        
        self.header_title = QLabel("首页 / 仪表盘")
        self.header_title.setStyleSheet(f"color: {COLORS['text_regular']}; font-size: 16px;")
        layout.addWidget(self.header_title)
        
        layout.addStretch()
        
        user_label = QLabel(f"欢迎, {self.app_manager.current_user['username']}")
        user_label.setStyleSheet(f"color: {COLORS['text_main']}; font-size: 14px;")
        layout.addWidget(user_label)
        
        logout_btn = RoundedButton("注销", bg_color=COLORS['danger'], width=80, height=30, font_size=12)
        logout_btn.clicked.connect(self.app_manager.show_login)
        layout.addWidget(logout_btn)

    def init_pages(self):
        # 0: Dashboard (Swapped back to 0)
        if self.app_manager.current_user['role'] == 'user':
            self.pages.addWidget(UserChartsPage(self.app_manager))
        else:
            self.pages.addWidget(AdminStatsPage(self.app_manager))

        # 1: Health News (Swapped to 1)
        self.pages.addWidget(HealthNewsPage(self.app_manager))
        
        # Others remain same indices relative to base
        if self.app_manager.current_user['role'] == 'user':
            # indices 2-7
            self.pages.addWidget(DataEntryPage(self.app_manager))
            self.pages.addWidget(ProfilePage(self.app_manager))
            self.pages.addWidget(MedicationPage(self.app_manager))
            self.pages.addWidget(GoalsPage(self.app_manager))
            self.pages.addWidget(DietPage(self.app_manager))
            self.pages.addWidget(RemindersPage(self.app_manager))
        else:
            # admin logic
            # Placeholder pages for admin to align index if needed or just add AdminUserPage
            # UserChartsPage(0) is taken by AdminStatsPage
            # News is (1)
            # Need to fill 2-7 with empty or whatever
            for _ in range(6): self.pages.addWidget(QWidget()) 
            self.pages.addWidget(AdminUserPage(self.app_manager))

# --- Page Widgets ---

class NewsWorker(QThread):
    finished = pyqtSignal(list)

    def run(self):
        news_list = []
        visited_links = set()

        def scrape_sina():
            try:
                url = "https://health.sina.com.cn/"
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                resp = requests.get(url, headers=headers, timeout=5)
                resp.encoding = resp.apparent_encoding
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                # Sina Health generic link search
                # Focus on news content areas if possible, or just all valid news links
                # Strategy: Look for links with meaningful titles and url patterns
                count = 0
                for a in soup.find_all('a'):
                    if count >= 15: break
                    title = a.get_text().strip()
                    link = a.get('href')
                    
                    if not link or not title: continue
                    if link in visited_links: continue
                    
                    # Basic filters for Sina
                    if len(title) < 10: continue
                    if '注册' in title or '登录' in title or '关于我们' in title: continue
                    if not link.startswith('http'): continue
                    
                    # URL pattern check for news articles (heuristic)
                    # Sina news often has /news/ or date in path or is an article page
                    is_news = False
                    if 'health.sina.com.cn' in link or 'k.sina.cn' in link:
                         if '/news/' in link or '/doc-' in link or 'article_' in link:
                             is_news = True
                    
                    if is_news:
                        news_list.append({'title': title, 'link': link, 'source': '新浪健康'})
                        visited_links.add(link)
                        count += 1
            except Exception as e:
                print(f"Sina scrape error: {e}")

        def scrape_39():
            try:
                url = "http://news.39.net/"
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                resp = requests.get(url, headers=headers, timeout=5)
                resp.encoding = resp.apparent_encoding
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                items = soup.select('.newslist li a, .art_list li a, .textlist li a')
                count = 0
                for item in items:
                    if count >= 5: break
                    title = item.get_text().strip()
                    link = item.get('href')
                    
                    if link and title and len(title) > 8:
                        if not link.startswith('http'): continue
                        if link in visited_links: continue
                        
                        news_list.append({'title': title, 'link': link, 'source': '39健康网'})
                        visited_links.add(link)
                        count += 1
            except Exception as e:
                print(f"39.net scrape error: {e}")

        # Execute scrapers
        scrape_sina()
        if len(news_list) < 10:
            scrape_39()
            
        # Fallback
        if not news_list:
            news_list = [
                {'title': '【健康小贴士】保持充足睡眠有助于提高免疫力', 'link': 'https://www.who.int/zh', 'source': 'HealthGuard'},
                {'title': '【健康小贴士】每日饮水2000ml，促进新陈代谢', 'link': 'https://www.who.int/zh', 'source': 'HealthGuard'},
                {'title': '【健康小贴士】适量运动，远离亚健康状态', 'link': 'https://www.who.int/zh', 'source': 'HealthGuard'},
                {'title': '【健康小贴士】少油少盐，均衡饮食', 'link': 'https://www.who.int/zh', 'source': 'HealthGuard'},
                {'title': '【科普】世界卫生组织：关于身体活动的建议', 'link': 'https://www.who.int/zh/news-room/fact-sheets/detail/physical-activity', 'source': 'WHO'},
            ]
            
        # Randomize the order
        random.shuffle(news_list)
        
        self.finished.emit(news_list)

class HealthNewsPage(QWidget):
    def __init__(self, app_manager):
        super().__init__()
        self.app_manager = app_manager
        layout = QVBoxLayout(self)
        
        # Header
        header = CardFrame()
        # Remove border for the text box frame around "Health News" text
        header.setStyleSheet(header.styleSheet() + "QFrame { border: none; }")
        header.setFixedHeight(80)
        hl = QHBoxLayout(header)
        hl.addWidget(QLabel("📰 今日健康资讯"))
        refresh_btn = RoundedButton("🔄 刷新", width=100)
        refresh_btn.clicked.connect(self.load_news)
        hl.addStretch()
        hl.addWidget(refresh_btn)
        layout.addWidget(header)
        
        # News List
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("background: transparent;")
        
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setSpacing(15)
        self.container_layout.addStretch()
        
        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)
        
        self.load_news()

    def load_news(self):
        # Clear
        while self.container_layout.count() > 1:
            child = self.container_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        # Show loading
        loading = QLabel("加载中...")
        loading.setAlignment(Qt.AlignCenter)
        self.container_layout.insertWidget(0, loading)
        
        self.worker = NewsWorker()
        self.worker.finished.connect(lambda data: self.on_news_loaded(data, loading))
        self.worker.start()

    def on_news_loaded(self, news_list, loading_widget):
        loading_widget.deleteLater()
        for news in news_list:
            self.add_news_card(news)

    def add_news_card(self, news):
        card = CardFrame()
        # Remove border for news item cards
        card.setStyleSheet(card.styleSheet() + "QFrame { border: none; }")
        card.setFixedHeight(100)
        card.setCursor(Qt.PointingHandCursor)
        
        # Use subprocess 'open' on macOS to avoid crashes with webbrowser module or QDesktopServices
        card.mousePressEvent = lambda e, link=news['link']: self.open_link_safely(link)
        
        l = QVBoxLayout(card)
        
        title = QLabel(news['title'])
        title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLORS['text_main']};")
        title.setWordWrap(True)
        l.addWidget(title)
        
        source = QLabel(f"来源: {news['source']}")
        source.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 12px;")
        l.addWidget(source)
        
        self.container_layout.insertWidget(self.container_layout.count()-1, card)

    def open_link_safely(self, url):
        try:
            system_name = platform.system()
            if system_name == 'Darwin':
                # MacOS safe method
                subprocess.Popen(['open', url])
            elif system_name == 'Windows':
                os.startfile(url)
            else:
                # Linux
                subprocess.Popen(['xdg-open', url])
        except Exception as e:
            print(f"Failed to open link via subprocess: {e}")
            # Last resort
            try:
                webbrowser.open(url)
            except:
                pass

class UserChartsPage(QWidget):
    def __init__(self, app_manager):
        super().__init__()
        self.app_manager = app_manager
        self.advisor = SmartHealthAdvisor()
        layout = QVBoxLayout(self)
        
        # Smart Advice Section
        self.advice_layout = QVBoxLayout()
        layout.addLayout(self.advice_layout)
        
        # Weather & Advice Card
        self.advice_card = CardFrame()
        # self.advice_card.setFixedHeight(160) # Auto height
        self.advice_card.setStyleSheet(self.advice_card.styleSheet() + "QFrame { border: none; }")
        
        adv_layout = QVBoxLayout(self.advice_card)
        adv_layout.setContentsMargins(20, 20, 20, 20)
        
        # Top: Weather + Refresh
        top_h = QHBoxLayout()
        self.weather_lbl = QLabel("正在获取天气...")
        self.weather_lbl.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLORS['primary']};")
        top_h.addWidget(self.weather_lbl)
        
        top_h.addStretch()
        
        refresh_btn = RoundedButton("🔄 刷新建议", width=100, height=30, font_size=12)
        refresh_btn.clicked.connect(self.load_advice)
        top_h.addWidget(refresh_btn)
        
        adv_layout.addLayout(top_h)
        
        # Advice Text
        self.advice_text = QLabel("正在生成智能健康建议...")
        self.advice_text.setWordWrap(True)
        self.advice_text.setStyleSheet(f"font-size: 14px; line-height: 1.5; color: {COLORS['text_main']}; margin-top: 10px;")
        self.advice_text.setTextFormat(Qt.RichText)
        adv_layout.addWidget(self.advice_text)
        
        self.advice_layout.addWidget(self.advice_card)
        
        # Notifications Area
        self.notif_layout = QVBoxLayout()
        layout.addLayout(self.notif_layout)
        self.check_notifications()
        
        # Charts Area (Tab Widget)
        chart_card = CardFrame()
        chart_layout = QVBoxLayout(chart_card)
        
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border: none; }}
            QTabBar::tab {{
                background: #f0f2f5; 
                color: {COLORS['text_regular']};
                padding: 8px 20px;
                margin-right: 5px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }}
            QTabBar::tab:selected {{
                background: white;
                color: {COLORS['primary']};
                font-weight: bold;
            }}
        """)
        
        # Tab 1: Weight & Steps
        self.tab1 = QWidget()
        self.tab1_layout = QVBoxLayout(self.tab1)
        self.fig1 = Figure(figsize=(5, 3), dpi=100)
        self.canvas1 = FigureCanvas(self.fig1)
        self.tab1_layout.addWidget(self.canvas1)
        self.tabs.addTab(self.tab1, "体重 & 步数趋势")
        
        # Tab 2: Blood Pressure
        self.tab2 = QWidget()
        self.tab2_layout = QVBoxLayout(self.tab2)
        self.fig2 = Figure(figsize=(5, 3), dpi=100)
        self.canvas2 = FigureCanvas(self.fig2)
        self.tab2_layout.addWidget(self.canvas2)
        self.tabs.addTab(self.tab2, "血压变化")
        
        # Tab 3: Sleep vs Water (Scatter)
        self.tab3 = QWidget()
        self.tab3_layout = QVBoxLayout(self.tab3)
        self.fig3 = Figure(figsize=(5, 3), dpi=100)
        self.canvas3 = FigureCanvas(self.fig3)
        self.tab3_layout.addWidget(self.canvas3)
        self.tabs.addTab(self.tab3, "睡眠与饮水")
        
        chart_layout.addWidget(self.tabs)
        layout.addWidget(chart_card, stretch=3)
        
        # Table
        table_card = CardFrame()
        table_layout = QVBoxLayout(table_card)
        table_layout.addWidget(QLabel("历史记录明细"))
        
        self.table = ModernTable()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["记录日期", "体重(kg)", "步数", "血压"])
        table_layout.addWidget(self.table)
        layout.addWidget(table_card, stretch=2)
        
        self.load_data()
        QTimer.singleShot(500, self.load_advice)

    def load_advice(self):
        try:
            # Request records (already loaded in self.load_data but we might need fresh if not called together)
            # Actually load_data is async request, this is also async.
            # We can just request records again or rely on load_data if we store records. 
            # Let's request to be safe and independent.
            resp = self.app_manager.network.send_request("get_records", {"user_id": self.app_manager.current_user['id']})
            records = []
            if resp['status'] == 'success':
                records = resp['data']
            
            advice = self.advisor.generate_recommendation(records)
            self.update_advice_ui(advice)
        except Exception as e:
            print(f"Error loading advice: {e}")
            self.advice_text.setText(f"无法生成建议: {e}")

    def update_advice_ui(self, advice):
        weather = advice['raw']['weather']
        self.weather_lbl.setText(f"📍 {weather['text']}")
        self.advice_text.setText(advice['text'])

    def check_notifications(self):
        resp = self.app_manager.network.send_request("get_notifications", {"user_id": self.app_manager.current_user['id']})
        if resp['status'] == 'success' and resp['data']:
            for notif in resp['data']:
                self.create_notif_banner(notif)
                
    def create_notif_banner(self, notif):
        banner = QFrame()
        banner.setStyleSheet(f"background-color: #fdf6ec; border: 1px solid #faecd8; border-radius: 5px;")
        banner.setFixedHeight(50)
        
        bl = QHBoxLayout(banner)
        bl.setContentsMargins(15, 0, 15, 0)
        
        icon = QLabel("🔔")
        msg = QLabel(f"管理员通知: {notif['message']}")
        msg.setStyleSheet("color: #e6a23c; font-weight: bold;")
        
        close_btn = QPushButton("×")
        close_btn.setFixedSize(30, 30)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("border: none; color: #909399; font-size: 18px; font-weight: bold; background: transparent;")
        close_btn.clicked.connect(lambda: self.mark_read(notif['id'], banner))
        
        bl.addWidget(icon)
        bl.addWidget(msg)
        bl.addStretch()
        bl.addWidget(close_btn)
        
        self.notif_layout.addWidget(banner)
        
    def mark_read(self, notif_id, banner_widget):
        self.app_manager.network.send_request("mark_read", {"notif_id": notif_id})
        banner_widget.deleteLater()

    def load_data(self):
        resp = self.app_manager.network.send_request("get_records", {"user_id": self.app_manager.current_user['id']})
        if resp["status"] == "success":
            records = resp["data"]
            # Sort by date
            records.sort(key=lambda x: x['record_date'])
            
            self.table.setRowCount(len(records))
            dates = []
            weights = []
            steps = []
            sys_bps = []
            dia_bps = []
            sleeps = []
            waters = []
            
            # Fill table in reverse order (newest first)
            for i, r in enumerate(reversed(records)):
                self.table.setItem(i, 0, QTableWidgetItem(str(r['record_date'])))
                self.table.setItem(i, 1, QTableWidgetItem(str(r['weight'])))
                self.table.setItem(i, 2, QTableWidgetItem(str(r['steps'])))
                self.table.setItem(i, 3, QTableWidgetItem(f"{r['systolic_bp']}/{r['diastolic_bp']}"))
            
            for r in records:
                dates.append(r['record_date'][5:]) # Show MM-DD
                weights.append(r['weight'])
                steps.append(r['steps'])
                sys_bps.append(r['systolic_bp'])
                dia_bps.append(r['diastolic_bp'])
                sleeps.append(r.get('sleep_hours', 0))
                waters.append(r.get('water_intake', 0))
            
            # Chart 1: Weight (Line) & Steps (Bar)
            self.fig1.clear()
            ax1 = self.fig1.add_subplot(111)
            ax2 = ax1.twinx()
            
            ax1.bar(dates, steps, color='#a0cfff', alpha=0.5, label='步数')
            ax2.plot(dates, weights, marker='o', color=COLORS['primary'], linewidth=2, label='体重(kg)')
            
            ax1.set_xlabel("日期")
            ax1.set_ylabel("步数", color='#409EFF')
            ax2.set_ylabel("体重 (kg)", color=COLORS['primary'])
            ax1.set_title("近期运动与体重趋势")
            self.canvas1.draw()
            
            # Chart 2: Blood Pressure
            self.fig2.clear()
            ax = self.fig2.add_subplot(111)
            ax.plot(dates, sys_bps, marker='^', color=COLORS['danger'], linestyle='--', label='收缩压')
            ax.plot(dates, dia_bps, marker='v', color=COLORS['success'], linestyle='--', label='舒张压')
            ax.fill_between(dates, dia_bps, sys_bps, color='gray', alpha=0.1)
            ax.set_title("近期血压变化趋势")
            ax.legend()
            ax.grid(True, linestyle=':', alpha=0.6)
            self.canvas2.draw()
            
            # Chart 3: Sleep vs Water
            self.fig3.clear()
            ax = self.fig3.add_subplot(111)
            ax.scatter(sleeps, waters, s=100, c=COLORS['warning'], alpha=0.7, edgecolors='white')
            ax.set_xlabel("睡眠时长 (小时)")
            ax.set_ylabel("饮水量 (ml)")
            ax.set_title("睡眠与饮水关系分布")
            ax.grid(True, linestyle=':', alpha=0.6)
            self.canvas3.draw()

class DataEntryPage(QWidget):
    def __init__(self, app_manager):
        super().__init__()
        self.app_manager = app_manager
        
        container = CardFrame()
        # Glassmorphism / Clean Card Style
        container.setStyleSheet("""
            QFrame { 
                background-color: rgba(255, 255, 255, 0.95); 
                border: none;
                border-radius: 16px;
            }
        """)
        # Soft Shadow
        shadow = QGraphicsDropShadowEffect(container)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 8)
        container.setGraphicsEffect(shadow)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.addWidget(container)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        # Header with Title and Button
        header = QHBoxLayout()
        title = QLabel("今日健康数据")
        title.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {COLORS['text_main']};")
        header.addWidget(title)
        header.addStretch()
        
        btn = RoundedButton("提交数据", width=140, bg_color=COLORS['success']) # Emerald Green accent
        btn.clicked.connect(self.submit)
        header.addWidget(btn)
        layout.addLayout(header)
        
        # Scroll Area for Form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        
        content = QWidget()
        form_layout = QVBoxLayout(content)
        form_layout.setSpacing(30)
        form_layout.setContentsMargins(10, 10, 10, 10)
        
        self.entries = {}
        
        # Styles for Inputs
        input_style = f"""
            QDoubleSpinBox, QSpinBox, QDateEdit {{
                border: 1px solid #DCDFE6;
                border-radius: 8px;
                padding: 5px 10px;
                font-size: 14px;
                background: #FFFFFF;
                color: {COLORS['text_main']};
                min-height: 40px;
            }}
            QDoubleSpinBox:focus, QSpinBox:focus, QDateEdit:focus {{
                border: 1px solid {COLORS['primary']};
                background: #F0F9FF;
            }}
            QDoubleSpinBox::up-button, QSpinBox::up-button {{
                width: 20px;
                border-left: 1px solid #DCDFE6;
                background: transparent;
                margin: 2px;
            }}
            QDoubleSpinBox::down-button, QSpinBox::down-button {{
                width: 20px;
                border-left: 1px solid #DCDFE6;
                background: transparent;
                margin: 2px;
            }}
            /* Calendar Widget Styling */
            QCalendarWidget QWidget {{
                background-color: white; 
                border-bottom: 1px solid #EBEEF5;
            }}
            QCalendarWidget QToolButton {{
                color: {COLORS['text_main']};
                background-color: transparent;
                icon-size: 20px;
                border: none;
                margin: 5px;
            }}
            QCalendarWidget QToolButton:hover {{
                background-color: #F0F9FF;
                border-radius: 5px;
            }}
            QCalendarWidget QMenu {{
                background-color: white;
                color: {COLORS['text_main']};
            }}
            QCalendarWidget QSpinBox {{
                background-color: white;
                color: {COLORS['text_main']};
                selection-background-color: {COLORS['primary']};
                selection-color: white;
            }}
            QCalendarWidget QAbstractItemView:enabled {{
                color: {COLORS['text_main']};
                background-color: white;
                selection-background-color: {COLORS['primary']};
                selection-color: white;
                font-size: 14px;
            }}
            QCalendarWidget QAbstractItemView:disabled {{
                color: #C0C4CC;
            }}
        """
        
        fields = [
            ("基础指标", [
                ("日期", "date", "date"),
                ("体重", "weight", "double", "kg", 0, 300),
                ("体温", "temperature", "double", "°C", 30, 45),
                ("收缩压", "sys_bp", "int", "mmHg", 0, 300),
                ("舒张压", "dia_bp", "int", "mmHg", 0, 300),
                ("心率", "heart_rate", "int", "次/分", 0, 250),
                ("血糖", "blood_sugar", "double", "mmol/L", 0, 50),
            ]),
            ("生活习惯", [
                ("步数", "steps", "int", "步", 0, 100000),
                ("睡眠时长", "sleep_hours", "double", "小时", 0, 24),
                ("饮水量", "water_intake", "int", "ml", 0, 5000)
            ]),
            ("备注", [("备注", "notes", "text")])
        ]
        
        for section, items in fields:
            # Section Header
            sec_header = QLabel(section)
            sec_header.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLORS['primary']}; border-left: 4px solid {COLORS['primary']}; padding-left: 10px;")
            form_layout.addWidget(sec_header)
            
            # Grid Layout for Inputs
            grid = QVBoxLayout()
            grid.setSpacing(15)
            
            # Group items in rows of 2
            current_row = QHBoxLayout()
            count = 0
            
            for item in items:
                label_text = item[0]
                key = item[1]
                type_ = item[2]
                
                # Input Container
                item_container = QWidget()
                item_layout = QVBoxLayout(item_container)
                item_layout.setContentsMargins(0,0,0,0)
                item_layout.setSpacing(5)
                
                lbl = QLabel(label_text)
                lbl.setStyleSheet(f"color: {COLORS['text_regular']}; font-weight: 500;")
                item_layout.addWidget(lbl)
                
                widget = None
                if type_ == 'date':
                    widget = QDateEdit()
                    widget.setDisplayFormat("yyyy-MM-dd")
                    widget.setDate(datetime.date.today())
                    widget.setCalendarPopup(True)
                    widget.setStyleSheet(input_style)
                elif type_ == 'double':
                    widget = QDoubleSpinBox()
                    widget.setRange(item[4], item[5])
                    widget.setSuffix(f" {item[3]}")
                    widget.setDecimals(1)
                    widget.setStyleSheet(input_style)
                    # Set empty-ish default? No, spinbox has value. Let's set to min or reasonable default if known, else 0
                elif type_ == 'int':
                    widget = QSpinBox()
                    widget.setRange(item[4], item[5])
                    widget.setSuffix(f" {item[3]}")
                    widget.setStyleSheet(input_style)
                elif type_ == 'text':
                    widget = QTextEdit()
                    widget.setFixedHeight(80)
                    widget.setStyleSheet(f"""
                        border: 1px solid #DCDFE6;
                        border-radius: 8px;
                        padding: 10px;
                        font-size: 14px;
                    """)
                
                if widget:
                    item_layout.addWidget(widget)
                    self.entries[key] = widget
                
                # Add to grid row
                if type_ == 'text':
                    # Text area takes full width
                    if count % 2 != 0:
                        current_row.addStretch()
                        grid.addLayout(current_row)
                        current_row = QHBoxLayout()
                        count = 0
                    grid.addWidget(item_container)
                else:
                    current_row.addWidget(item_container)
                    count += 1
                    if count == 2:
                        grid.addLayout(current_row)
                        current_row = QHBoxLayout()
                        count = 0
            
            if count > 0:
                current_row.addStretch()
                grid.addLayout(current_row)
                
            form_layout.addLayout(grid)
            form_layout.addSpacing(10)
                
        form_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)

    def submit(self):
        data = {}
        for k, v in self.entries.items():
            if isinstance(v, QTextEdit):
                data[k] = v.toPlainText()
            elif isinstance(v, QDateEdit):
                data[k] = v.date().toString("yyyy-MM-dd")
            elif isinstance(v, (QSpinBox, QDoubleSpinBox)):
                val = v.value()
                # If value is 0, maybe treat as empty? Or just send 0.
                # Requirement: "Metrics input fields". 
                # Let's send as string or number. Server expects string or number.
                if val == 0 and k not in ['steps']: # steps can be 0, others unlikely if measured
                    data[k] = "" 
                else:
                    data[k] = str(val)
        
        data['user_id'] = self.app_manager.current_user['id']
        
        resp = self.app_manager.network.send_request("add_record", data)
        if resp["status"] == "success":
            QMessageBox.information(self, "成功", "数据已保存")
        else:
            QMessageBox.critical(self, "失败", resp["message"])

class AdminStatsPage(QWidget):
    def __init__(self, app_manager):
        super().__init__()
        self.app_manager = app_manager
        self.layout = QHBoxLayout(self)
        self.load_stats()
        
    def load_stats(self):
        resp = self.app_manager.network.send_request("get_sys_stats")
        if resp["status"] == "success":
            d = resp["data"]
            self.add_card("总用户数", d.get('user_count', 0), COLORS['primary'])
            self.add_card("总记录数", d.get('total_records', 0), COLORS['success'])
            self.add_card("平均体重", f"{d.get('avg_weight', 0)}kg", COLORS['danger'])
            
    def add_card(self, title, value, color):
        card = CardFrame()
        card.setFixedSize(260, 130)
        l = QVBoxLayout(card)
        
        tl = QLabel(title)
        tl.setStyleSheet("color: #909399; font-size: 14px;")
        vl = QLabel(str(value))
        vl.setStyleSheet(f"color: {COLORS['text_main']}; font-size: 32px; font-weight: bold;")
        
        l.addWidget(tl)
        l.addWidget(vl)
        
        # Colored stripe
        stripe = QFrame(card)
        stripe.setStyleSheet(f"background-color: {color};")
        stripe.setFixedWidth(5)
        stripe.move(0, 0)
        stripe.resize(5, 130)
        
        self.layout.addWidget(card)
        
# Placeholder classes for others (Profile, Medication, etc.) to save space, 
# but implementing core logic as requested.
class ProfilePage(QWidget):
    def __init__(self, app_manager):
        super().__init__()
        self.app_manager = app_manager
        layout = QVBoxLayout(self)
        
        card = CardFrame()
        layout.addWidget(card)
        
        main_layout = QVBoxLayout(card)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("个人健康档案")
        title.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {COLORS['text_main']};")
        main_layout.addWidget(title)
        main_layout.addSpacing(20)
        
        # Load profile
        resp = app_manager.network.send_request("get_profile", {"user_id": app_manager.current_user['id']})
        profile = resp.get('data', {}) if resp['status'] == 'success' else {}
        
        self.entries = {}
        fields = [
            ("身高 (cm)", "height", profile.get('height', '')),
            ("血型", "blood_type", profile.get('blood_type', '')),
            ("紧急联系人", "emergency_contact", profile.get('emergency_contact', '')),
            ("过敏史", "allergies", profile.get('allergies', '')),
            ("慢性病史", "chronic_diseases", profile.get('chronic_diseases', ''))
        ]
        
        form_layout = QVBoxLayout()
        for label, key, default in fields:
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setFixedWidth(100)
            lbl.setStyleSheet("font-size: 14px;")
            ent = RoundedEntry(width=400)
            ent.setText(str(default))
            self.entries[key] = ent
            row.addWidget(lbl)
            row.addWidget(ent)
            row.addStretch()
            form_layout.addLayout(row)
            form_layout.addSpacing(10)
            
        main_layout.addLayout(form_layout)
        main_layout.addSpacing(20)
        
        save_btn = RoundedButton("保存档案", width=160)
        save_btn.clicked.connect(self.save_profile)
        main_layout.addWidget(save_btn, alignment=Qt.AlignLeft)
        main_layout.addStretch()

    def save_profile(self):
        data = {k: v.text() for k, v in self.entries.items()}
        resp = self.app_manager.network.send_request("update_profile", {
            "user_id": self.app_manager.current_user['id'],
            "profile_data": data
        })
        if resp['status'] == 'success':
            QMessageBox.information(self, "成功", "档案已更新")
        else:
            QMessageBox.critical(self, "失败", resp['message'])

class MedicationPage(QWidget):
    def __init__(self, app_manager):
        super().__init__()
        self.app_manager = app_manager
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        add_btn = RoundedButton("➕ 添加用药", bg_color=COLORS['success'], width=120)
        add_btn.clicked.connect(self.show_add_dialog)
        header.addWidget(add_btn)
        
        del_btn = RoundedButton("删除选中", bg_color=COLORS['danger'], width=120)
        del_btn.clicked.connect(self.delete_selected)
        header.addWidget(del_btn)
        header.addStretch()
        layout.addLayout(header)
        
        # List
        card = CardFrame()
        layout.addWidget(card)
        card_layout = QVBoxLayout(card)
        
        self.table = ModernTable()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["药品名称", "剂量", "频率", "开始日期", "结束日期"])
        # self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.table.setStyleSheet("border: none;")
        # self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        card_layout.addWidget(self.table)
        
        self.load_medications()

    def load_medications(self):
        resp = self.app_manager.network.send_request("get_medications", {"user_id": self.app_manager.current_user['id']})
        if resp['status'] == 'success':
            data = resp['data']
            self.table.setRowCount(len(data))
            for i, med in enumerate(data):
                self.table.setItem(i, 0, QTableWidgetItem(med['medicine_name']))
                self.table.setItem(i, 1, QTableWidgetItem(med['dosage']))
                self.table.setItem(i, 2, QTableWidgetItem(med['frequency']))
                self.table.setItem(i, 3, QTableWidgetItem(med['start_date']))
                self.table.setItem(i, 4, QTableWidgetItem(med.get('end_date', '长期')))
                # Store ID in hidden data
                self.table.item(i, 0).setData(Qt.UserRole, med['id'])

    def show_add_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("添加用药")
        dialog.setFixedSize(400, 350)
        dialog.setStyleSheet(f"background: white;")
        
        layout = QVBoxLayout(dialog)
        entries = {}
        fields = [
            ("药品名称*", "medicine_name"),
            ("剂量", "dosage"),
            ("频率", "frequency"),
            ("开始日期", "start_date"),
            ("结束日期", "end_date"),
        ]
        
        for label, key in fields:
            layout.addWidget(QLabel(label))
            ent = RoundedEntry()
            if key == 'start_date': ent.setText(datetime.date.today().strftime("%Y-%m-%d"))
            layout.addWidget(ent)
            entries[key] = ent
            
        btn = RoundedButton("提交", bg_color=COLORS['success'])
        btn.clicked.connect(lambda: self.submit_add(dialog, entries))
        layout.addWidget(btn)
        dialog.exec_()

    def submit_add(self, dialog, entries):
        data = {k: v.text() for k, v in entries.items()}
        data['user_id'] = self.app_manager.current_user['id']
        resp = self.app_manager.network.send_request("add_medication", data)
        if resp['status'] == 'success':
            QMessageBox.information(self, "成功", "已添加")
            dialog.accept()
            self.load_medications()
        else:
            QMessageBox.warning(self, "失败", resp['message'])

    def delete_selected(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "提示", "请先选择记录")
            return
            
        med_id = self.table.item(row, 0).data(Qt.UserRole)
        resp = self.app_manager.network.send_request("delete_medication", {"med_id": med_id})
        if resp['status'] == 'success':
            self.load_medications()

class GoalsPage(QWidget):
    def __init__(self, app_manager):
        super().__init__()
        self.app_manager = app_manager
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        add_btn = RoundedButton("➕ 新建目标", bg_color=COLORS['primary'], width=120)
        add_btn.clicked.connect(self.show_add_dialog)
        header.addWidget(add_btn)
        header.addStretch()
        layout.addLayout(header)
        
        # List Container
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("background: transparent;")
        
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setSpacing(15)
        self.container_layout.addStretch()
        
        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)
        
        self.load_goals()

    def load_goals(self):
        # Clear existing
        while self.container_layout.count() > 1:
            child = self.container_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        resp = self.app_manager.network.send_request("get_goals", {"user_id": self.app_manager.current_user['id']})
        if resp['status'] == 'success':
            goals = resp['data']
            for goal in goals:
                self.add_goal_card(goal)

    def add_goal_card(self, goal):
        card = CardFrame()
        # Remove border for goal cards
        card.setStyleSheet(card.styleSheet() + "QFrame { border: none; }")
        card.setFixedHeight(120)
        l = QVBoxLayout(card)
        
        # Progress calculation based on goal type
        is_reduce_goal = any(kw in goal['goal_type'] for kw in ['减肥', '减重', '降', '瘦'])
        
        if is_reduce_goal:
            # For weight loss/reduction goals: target/current represents how close we are (100% = reached)
            # Example: Target 65, Current 70.5 -> 65/70.5 = 92.2% (Approaching 100%)
            # Example: Target 65, Current 60 -> 65/60 = 108% (Exceeded goal)
            progress = (goal['target_value'] / goal['current_value'] * 100) if goal['current_value'] > 0 else 0
        else:
            # For accumulation goals: current/target
            progress = (goal['current_value'] / goal['target_value'] * 100) if goal['target_value'] > 0 else 0
        
        # Top: Type + Progress
        top = QHBoxLayout()
        type_lbl = QLabel(f"🎯 {goal['goal_type']}")
        type_lbl.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {COLORS['text_main']};")
        prog_lbl = QLabel(f"{progress:.1f}%")
        prog_lbl.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {COLORS['primary']};")
        top.addWidget(type_lbl)
        top.addStretch()
        top.addWidget(prog_lbl)
        l.addLayout(top)
        
        # Middle: Values
        mid = QLabel(f"目标: {goal['target_value']}  |  当前: {goal['current_value']}")
        mid.setStyleSheet(f"color: {COLORS['text_regular']}; font-size: 14px;")
        l.addWidget(mid)
        
        # Bottom: Dates
        bot = QLabel(f"期限: {goal['start_date']} 至 {goal['end_date']}")
        bot.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 12px;")
        l.addWidget(bot)
        
        self.container_layout.insertWidget(self.container_layout.count()-1, card)

    def show_add_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("新建健康目标")
        dialog.setFixedSize(400, 400)
        dialog.setStyleSheet("background: white;")
        
        layout = QVBoxLayout(dialog)
        entries = {}
        fields = [
            ("目标类型 (如: 减肥)", "goal_type"),
            ("目标值", "target_value"),
            ("当前值", "current_value"),
            ("开始日期", "start_date"),
            ("结束日期", "end_date"),
        ]
        
        for label, key in fields:
            layout.addWidget(QLabel(label))
            ent = RoundedEntry()
            if 'date' in key: ent.setText(datetime.date.today().strftime("%Y-%m-%d"))
            layout.addWidget(ent)
            entries[key] = ent
            
        btn = RoundedButton("创建", bg_color=COLORS['primary'])
        btn.clicked.connect(lambda: self.submit_add(dialog, entries))
        layout.addWidget(btn)
        dialog.exec_()

    def submit_add(self, dialog, entries):
        data = {k: v.text() for k, v in entries.items()}
        data['user_id'] = self.app_manager.current_user['id']
        resp = self.app_manager.network.send_request("add_goal", data)
        if resp['status'] == 'success':
            QMessageBox.information(self, "成功", "目标已创建")
            dialog.accept()
            self.load_goals()
        else:
            QMessageBox.warning(self, "失败", resp['message'])

class DietPage(QWidget):
    def __init__(self, app_manager):
        super().__init__()
        self.app_manager = app_manager
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        add_btn = RoundedButton("➕ 记录饮食", bg_color=COLORS['success'], width=120)
        add_btn.clicked.connect(self.show_add_dialog)
        header.addWidget(add_btn)
        header.addStretch()
        layout.addLayout(header)
        
        # List
        card = CardFrame()
        layout.addWidget(card)
        card_layout = QVBoxLayout(card)
        
        self.table = ModernTable()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["日期", "餐次", "食物", "热量(kcal)"])
        # self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.table.setStyleSheet("border: none;")
        # self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        card_layout.addWidget(self.table)
        
        self.load_diet()

    def load_diet(self):
        resp = self.app_manager.network.send_request("get_diet_records", {"user_id": self.app_manager.current_user['id']})
        if resp['status'] == 'success':
            data = resp['data']
            self.table.setRowCount(len(data))
            for i, r in enumerate(data):
                self.table.setItem(i, 0, QTableWidgetItem(r['record_date']))
                self.table.setItem(i, 1, QTableWidgetItem(r['meal_type']))
                self.table.setItem(i, 2, QTableWidgetItem(r['food_description']))
                self.table.setItem(i, 3, QTableWidgetItem(str(r['calories'])))

    def show_add_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("记录饮食")
        dialog.setFixedSize(400, 350)
        dialog.setStyleSheet("background: white;")
        
        layout = QVBoxLayout(dialog)
        entries = {}
        
        layout.addWidget(QLabel("日期"))
        date_ent = RoundedEntry()
        date_ent.setText(datetime.date.today().strftime("%Y-%m-%d"))
        layout.addWidget(date_ent)
        entries['record_date'] = date_ent
        
        layout.addWidget(QLabel("餐次"))
        meal_combo = QComboBox()
        meal_combo.addItems(["早餐", "午餐", "晚餐", "加餐"])
        meal_combo.setFixedHeight(40)
        layout.addWidget(meal_combo)
        
        layout.addWidget(QLabel("食物描述"))
        food_ent = RoundedEntry()
        layout.addWidget(food_ent)
        entries['food_description'] = food_ent
        
        layout.addWidget(QLabel("热量 (kcal)"))
        cal_ent = RoundedEntry()
        layout.addWidget(cal_ent)
        entries['calories'] = cal_ent
        
        def submit():
            data = {k: v.text() for k, v in entries.items()}
            data['meal_type'] = meal_combo.currentText()
            data['user_id'] = self.app_manager.current_user['id']
            
            resp = self.app_manager.network.send_request("add_diet", data)
            if resp['status'] == 'success':
                QMessageBox.information(self, "成功", "已记录")
                dialog.accept()
                self.load_diet()
            else:
                QMessageBox.warning(self, "失败", resp['message'])
                
        btn = RoundedButton("提交", bg_color=COLORS['success'])
        btn.clicked.connect(submit)
        layout.addWidget(btn)
        dialog.exec_()

class RemindersPage(QWidget):
    def __init__(self, app_manager):
        super().__init__()
        self.app_manager = app_manager
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        add_btn = RoundedButton("➕ 新建提醒", bg_color=COLORS['primary'], width=120)
        add_btn.clicked.connect(self.show_add_dialog)
        header.addWidget(add_btn)
        header.addStretch()
        layout.addLayout(header)
        
        # List
        card = CardFrame()
        layout.addWidget(card)
        card_layout = QVBoxLayout(card)
        
        self.table = ModernTable()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["类型", "标题", "时间", "重复"])
        # self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.table.setStyleSheet("border: none;")
        # self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        card_layout.addWidget(self.table)
        
        self.load_reminders()

    def load_reminders(self):
        resp = self.app_manager.network.send_request("get_reminders", {"user_id": self.app_manager.current_user['id']})
        if resp['status'] == 'success':
            data = resp['data']
            self.table.setRowCount(len(data))
            for i, r in enumerate(data):
                self.table.setItem(i, 0, QTableWidgetItem(r['reminder_type']))
                self.table.setItem(i, 1, QTableWidgetItem(r['title']))
                self.table.setItem(i, 2, QTableWidgetItem(r['reminder_time']))
                self.table.setItem(i, 3, QTableWidgetItem(r['repeat_type']))

    def show_add_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("新建提醒")
        dialog.setFixedSize(400, 400)
        dialog.setStyleSheet("background: white;")
        
        layout = QVBoxLayout(dialog)
        entries = {}
        
        layout.addWidget(QLabel("类型"))
        type_combo = QComboBox()
        type_combo.addItems(["用药", "测量", "运动", "饮水", "其他"])
        type_combo.setFixedHeight(40)
        layout.addWidget(type_combo)
        
        layout.addWidget(QLabel("标题"))
        title_ent = RoundedEntry()
        layout.addWidget(title_ent)
        entries['title'] = title_ent
        
        layout.addWidget(QLabel("时间 (HH:MM)"))
        time_ent = RoundedEntry()
        time_ent.setText("08:00")
        layout.addWidget(time_ent)
        entries['reminder_time'] = time_ent
        
        layout.addWidget(QLabel("重复"))
        rep_combo = QComboBox()
        rep_combo.addItems(["once", "daily", "weekly"])
        rep_combo.setFixedHeight(40)
        layout.addWidget(rep_combo)
        
        def submit():
            data = {k: v.text() for k, v in entries.items()}
            data['reminder_type'] = type_combo.currentText()
            data['repeat_type'] = rep_combo.currentText()
            data['user_id'] = self.app_manager.current_user['id']
            
            resp = self.app_manager.network.send_request("add_reminder", data)
            if resp['status'] == 'success':
                QMessageBox.information(self, "成功", "已创建")
                dialog.accept()
                self.load_reminders()
            else:
                QMessageBox.warning(self, "失败", resp['message'])
                
        btn = RoundedButton("创建", bg_color=COLORS['primary'])
        btn.clicked.connect(submit)
        layout.addWidget(btn)
        dialog.exec_()

class AdminUserPage(QWidget):
    def __init__(self, app_manager):
        super().__init__()
        self.app_manager = app_manager
        layout = QVBoxLayout(self)
        
        # 1. Header with Actions
        header_card = CardFrame()
        header_card.setFixedHeight(80)
        layout.addWidget(header_card)
        
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        header_layout.addWidget(QLabel("搜索用户:"))
        self.search_input = RoundedEntry(width=200)
        header_layout.addWidget(self.search_input)
        
        search_btn = RoundedButton("🔍 查询", bg_color=COLORS['primary'], width=100)
        search_btn.clicked.connect(self.load_users)
        header_layout.addWidget(search_btn)
        
        header_layout.addStretch()
        
        msg_btn = RoundedButton("📢 发送通知", bg_color=COLORS['success'], width=120)
        msg_btn.clicked.connect(self.show_msg_dialog)
        header_layout.addWidget(msg_btn)
        
        header_layout.addSpacing(10)
        
        del_btn = RoundedButton("❌ 删除用户", bg_color=COLORS['danger'], width=120)
        del_btn.clicked.connect(self.delete_selected_user)
        header_layout.addWidget(del_btn)
        
        # 2. User List
        list_card = CardFrame()
        layout.addWidget(list_card)
        list_layout = QVBoxLayout(list_card)
        
        self.table = ModernTable()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "用户名", "性别", "年龄", "注册时间"])
        # self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents) # ID Column distinct
        # self.table.setStyleSheet("border: none;")
        # self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        list_layout.addWidget(self.table)
        
        self.load_users()

    def load_users(self):
        query = self.search_input.text().strip()
        resp = self.app_manager.network.send_request("get_all_users", {"query": query if query else None})
        
        if resp['status'] == 'success':
            self.table.setRowCount(0)
            for user in resp['data']:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(user['id'])))
                self.table.setItem(row, 1, QTableWidgetItem(str(user['username'])))
                self.table.setItem(row, 2, QTableWidgetItem(str(user['gender'])))
                self.table.setItem(row, 3, QTableWidgetItem(str(user['age'])))
                self.table.setItem(row, 4, QTableWidgetItem(str(user['created_at'])))
                # Store ID in hidden data of first column item
                self.table.item(row, 0).setData(Qt.UserRole, user['id'])
        else:
            QMessageBox.warning(self, "错误", "无法加载用户列表")

    def delete_selected_user(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "提示", "请先选择一个用户")
            return
            
        user_id = self.table.item(row, 0).data(Qt.UserRole)
        username = self.table.item(row, 1).text()
        
        reply = QMessageBox.question(self, "危险操作", 
                                   f"确定要删除用户 [{username}] 吗？\n该操作将永久删除该用户的所有数据！",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                                   
        if reply == QMessageBox.Yes:
            resp = self.app_manager.network.send_request("delete_user", {"target_id": user_id})
            if resp['status'] == 'success':
                QMessageBox.information(self, "成功", resp['message'])
                self.load_users()
            else:
                QMessageBox.warning(self, "失败", resp['message'])

    def show_msg_dialog(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "提示", "请先选择一个接收消息的用户")
            return
            
        user_id = self.table.item(row, 0).data(Qt.UserRole)
        username = self.table.item(row, 1).text()
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"发送消息给 {username}")
        dialog.setFixedSize(400, 300)
        dialog.setStyleSheet("background: white;")
        
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel("消息内容:"))
        text_area = QTextEdit()
        layout.addWidget(text_area)
        
        def submit():
            msg = text_area.toPlainText().strip()
            if not msg: return
            
            resp = self.app_manager.network.send_request("send_notification", {"target_id": user_id, "message": msg})
            if resp['status'] == 'success':
                QMessageBox.information(self, "成功", "通知已发送")
                dialog.accept()
            else:
                QMessageBox.warning(self, "失败", resp['message'])
                
        btn = RoundedButton("发送", bg_color=COLORS['primary'])
        btn.clicked.connect(submit)
        layout.addWidget(btn)
        
        dialog.exec_()

class AppManager:
    def __init__(self):
        self.app = QApplication(sys.argv)
        # Set global font
        font = QFont(FONT_FAMILY)
        self.app.setFont(font)
        
        self.network = NetworkClient()
        self.current_user = None
        
        self.login_window = LoginWindow(self)
        self.register_window = RegisterWindow(self)
        self.main_window = None 

    def show_login(self):
        if self.main_window: self.main_window.close()
        self.register_window.close()
        self.login_window.show()

    def show_register(self):
        self.login_window.close()
        self.register_window.show()

    def show_main(self):
        self.login_window.close()
        self.main_window = MainWindow(self)
        self.main_window.show()

    def run(self):
        self.show_login()
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    manager = AppManager()
    manager.run()
