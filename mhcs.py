import cv2
import numpy as np
import subprocess
import time
import random
from ultralytics import YOLO
import os
import win32api
import win32con
import threading
import msvcrt
from itertools import product
import tkinter as tk
from tkinter import messagebox
import threading
import builtins
import datetime
import sys
import queue
from tkinter import ttk
import hashlib
import uuid
import base64
import json
import re
# 移除对license_validator的导入
# from license_validator import LicenseValidator  # 导入卡密验证模块


# 内嵌LicenseValidator类到主程序
class LicenseValidator:
    def __init__(self, root=None):
        self.license_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "license.key")
        self.machine_code = self.get_machine_code()
        
        # 如果没有传入root，则创建一个新的窗口
        self.is_standalone = root is None
        if self.is_standalone:
            self.root = tk.Tk()
            self.root.title("满汉助手激活")
            self.root.geometry("450x250")
            self.root.resizable(False, False)
            # 居中显示
            self.root.update_idletasks()
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            y = (self.root.winfo_screenheight() // 2) - (height // 2)
            self.root.geometry(f'{width}x{height}+{x}+{y}')
            
            # 设置窗口图标
            icon_path = resource_path("logo.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        else:
            self.root = root
            self.root.geometry("450x250")  # 设置合适的窗口大小
            self.root.resizable(False, False)
            # 居中显示
            self.root.update_idletasks()
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            y = (self.root.winfo_screenheight() // 2) - (height // 2)
            self.root.geometry(f'{width}x{height}+{x}+{y}')
            
        self.create_ui()
        
        # 检查是否已激活
        if self.check_license():
            if self.is_standalone:
                messagebox.showinfo("提示", "软件已激活，有效期至：" + self.get_expiry_date_str())
                # 不再直接销毁窗口，而是隐藏窗口，等待主程序启动
                self.root.withdraw()
                # 延迟销毁窗口，确保主程序有时间启动
                self.root.after(1000, self.root.destroy)
                return
            else:
                # 如果作为模块被调用且已激活，关闭验证窗口
                self.root.quit()
                self.root.destroy()
                
    def create_ui(self):
        """创建UI界面"""
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 机器码显示
        tk.Label(main_frame, text="机器码:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=10)
        machine_code_frame = tk.Frame(main_frame)
        machine_code_frame.grid(row=0, column=1, sticky=tk.W, pady=10)
        
        self.machine_code_var = tk.StringVar(value=self.machine_code)
        machine_code_entry = tk.Entry(machine_code_frame, textvariable=self.machine_code_var, width=30, state="readonly")
        machine_code_entry.pack(side=tk.LEFT)
        
        copy_btn = tk.Button(machine_code_frame, text="复制", command=self.copy_machine_code)
        copy_btn.pack(side=tk.LEFT, padx=5)
        
        # 激活码输入
        tk.Label(main_frame, text="激活码:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=10)
        self.license_key_var = tk.StringVar()
        license_key_entry = tk.Entry(main_frame, textvariable=self.license_key_var, width=40)
        license_key_entry.grid(row=1, column=1, sticky=tk.W, pady=10)
        
        # 激活按钮
        btn_frame = tk.Frame(main_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        activate_btn = tk.Button(btn_frame, text="激活软件", width=15, command=self.activate_license)
        activate_btn.pack(side=tk.LEFT, padx=10)
        
        # 添加退出按钮，无论是独立运行还是作为模块被调用，都显示退出按钮
        exit_btn = tk.Button(btn_frame, text="退出", width=15, command=lambda: sys.exit(0))
        exit_btn.pack(side=tk.LEFT, padx=10)
            
        # 添加提示信息
        tip_text = "提示：请联系客服获取激活码，激活码与本机硬件绑定，不可在其他设备上使用。"
        tk.Label(main_frame, text=tip_text, fg="gray").grid(row=3, column=0, columnspan=2, pady=10)
        
    def get_machine_code(self):
        """获取机器码"""
        # 获取CPU序列号、硬盘序列号、主板序列号等硬件信息
        try:
            # 使用UUID模块获取机器唯一标识
            machine_id = str(uuid.getnode())
            # 获取计算机名
            computer_name = os.environ.get('COMPUTERNAME', '')
            # 获取用户名
            username = os.environ.get('USERNAME', '')
            
            # 组合信息生成机器码
            hardware_info = f"{machine_id}|{computer_name}|{username}"
            machine_code = hashlib.md5(hardware_info.encode()).hexdigest().upper()
            return machine_code
        except:
            # 如果获取失败，返回一个随机的机器码
            return hashlib.md5(str(uuid.uuid4()).encode()).hexdigest().upper()
            
    def copy_machine_code(self):
        """复制机器码到剪贴板"""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.machine_code)
        messagebox.showinfo("提示", "机器码已复制到剪贴板")
        
    def activate_license(self):
        """激活软件"""
        license_key = self.license_key_var.get().strip()
        if not license_key:
            messagebox.showerror("错误", "请输入激活码")
            return
            
        if self.validate_license_key(license_key):
            self.save_license_key(license_key)
            messagebox.showinfo("成功", "软件激活成功！有效期至：" + self.get_expiry_date_str())
            # 激活成功后关闭窗口
            if self.is_standalone:
                self.root.destroy()
            else:
                # 如果是作为模块被调用，关闭验证窗口并继续程序执行
                self.root.quit()
                self.root.destroy()
        else:
            messagebox.showerror("错误", "激活码无效或已过期！")
            
    def validate_license_key(self, license_key):
        """验证激活码"""
        if not license_key or len(license_key) != 40:
            return False
            
        # 解析激活码
        try:
            # 前16位是机器码的MD5前16位（大写）
            machine_part = license_key[:16]
            # 中间8位是有效期（16进制编码）
            date_part = license_key[16:24]
            # 后16位是随机字符
            
            # 验证机器码部分
            if machine_part != hashlib.md5(self.machine_code.encode()).hexdigest()[:16].upper():
                return False
                
            # 解析有效期
            year = int(date_part[:4], 16)
            month = int(date_part[4:6], 16)
            day = int(date_part[6:8], 16)
            
            expiry_date = datetime.datetime(year, month, day)
            
            # 检查是否过期
            if expiry_date < datetime.datetime.now():
                return False
                
            return True
        except:
            return False
            
    def save_license_key(self, license_key):
        """保存激活码"""
        with open(self.license_file, "w") as f:
            f.write(license_key)
            
    def check_license(self):
        """检查是否已激活"""
        try:
            if not os.path.exists(self.license_file):
                return False
                
            with open(self.license_file, "r") as f:
                license_key = f.read().strip()
                
            return self.validate_license_key(license_key)
        except:
            return False
            
    def get_expiry_date_str(self):
        """获取有效期字符串"""
        try:
            if not os.path.exists(self.license_file):
                return "未激活"
                
            with open(self.license_file, "r") as f:
                license_key = f.read().strip()
                
            # 解析有效期
            date_part = license_key[16:24]
            year = int(date_part[:4], 16)
            month = int(date_part[4:6], 16)
            day = int(date_part[6:8], 16)
            
            return f"{year}年{month}月{day}日"
        except:
            return "未知"
            
    def run(self):
        """运行激活界面"""
        if self.is_standalone:
            self.root.mainloop()

    def get_remaining_days(self):
        """获取剩余使用天数"""
        try:
            if not os.path.exists(self.license_file):
                return 0
                
            with open(self.license_file, "r") as f:
                license_key = f.read().strip()
                
            # 解析有效期
            date_part = license_key[16:24]
            year = int(date_part[:4], 16)
            month = int(date_part[4:6], 16)
            day = int(date_part[6:8], 16)
            
            expiry_date = datetime.datetime(year, month, day)
            now = datetime.datetime.now()
            
            # 计算剩余天数
            remaining_days = (expiry_date - now).days
            return max(0, remaining_days)  # 确保不返回负数
        except:
            return 0


# 获取应用程序路径
def get_app_path():
    if getattr(sys, 'frozen', False):
        # 打包后的路径
        return os.path.dirname(sys.executable)
    else:
        # 开发环境路径
        return os.path.dirname(os.path.abspath(__file__))


# 初始化APP_PATH
APP_PATH = get_app_path()


# 资源路径处理函数
def resource_path(relative_path):
    """获取资源的绝对路径，适用于开发环境和PyInstaller打包后的环境"""
    if getattr(sys, 'frozen', False):
        # 如果是打包后的环境
        base_path = sys._MEIPASS
    else:
        # 开发环境
        base_path = APP_PATH

    return os.path.join(base_path, relative_path)


# 验证卡密
def verify_license():
    # 创建一个临时的Tk窗口用于卡密验证
    root = tk.Tk()
    # 不再隐藏窗口
    # root.withdraw()  # 隐藏窗口
    
    # 设置窗口标题和大小
    root.title("满汉助手激活")
    root.geometry("1x1")  # 设置一个很小的初始大小，验证器会自己调整大小
    
    # 居中显示
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # 验证卡密，使用内嵌的LicenseValidator类
    validator = LicenseValidator(root)
    
    # 进入主循环，等待验证完成
    root.mainloop()
    
    # 检查是否验证成功
    if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "license.key")):
        # 验证成功后，确保有足够的时间启动主程序
        time.sleep(0.5)  # 添加短暂延迟，确保UI有时间响应
        return True
    return False


# 配置参数
ADB_PATHS = [
    "adb",  # 优先使用系统ADB
    os.path.join(APP_PATH, "adb", "adb.exe"),  # 其次使用程序目录下的ADB
    os.path.join(APP_PATH, "adb.exe"),  # 程序目录下的单文件ADB
    r"C:\Program Files\BlueStacks_nxt_cn\HD-Adb.exe",
    r"C:\Program Files\BlueStacks\HD-Adb.exe",
    r"D:\LDPlayer\adb.exe",
    r"D:\leidian\LDPlayer\adb.exe"
]
MODEL_PATH = resource_path(os.path.join("model", "best.pt"))  # 使用相对路径，通过resource_path解析
DEBUG_DIR = os.path.join(APP_PATH, "debug")  # 调试目录仍使用APP_PATH

# 自适应分辨率配置
BOARD_SIZE = 8  # 棋盘大小（8x8）
TARGET_STEPS = 30  # 目标步数
SCORE_TARGET = 1000  # 目标分数

# 分辨率适配参数 - 这些将在运行时根据设备分辨率自动计算
BOARD_ORIGIN = None  # 棋盘左上角顶点坐标 - 运行时计算
CELL_SIZE = None  # 每个格子的大小 - 运行时计算
SCREEN_WIDTH = None  # 屏幕宽度
SCREEN_HEIGHT = None  # 屏幕高度

# 预设的分辨率配置（基于常见手机分辨率）
RESOLUTION_CONFIGS = {
    # 分辨率: (棋盘左上角X, 棋盘左上角Y, 格子大小)
    (1080, 1920): (90, 680, 120),    # 1080p 竖屏
    (1080, 2340): (90, 850, 120),    # 19.5:9 竖屏
    (1080, 2400): (90, 900, 120),    # 20:9 竖屏
    (720, 1280): (60, 450, 80),      # 720p 竖屏
    (1440, 2560): (120, 900, 160),   # 2K 竖屏
    (1440, 2960): (120, 1100, 160),  # 2K+ 竖屏
    (1920, 1080): (454, 16, 86),     # 1080p 横屏（原配置）
    (2340, 1080): (850, 16, 86),     # 19.5:9 横屏
    (2400, 1080): (900, 16, 86),     # 20:9 横屏
}

# 全局变量
adb_path = None
model = None
paused = True  # 修改为默认暂停状态
steps_used = 0  # 已用步数
total_score = 0  # 总分数
total_base_score = 0  # 总基础分
running = True  # 控制程序运行
should_use_item = False  # 是否使用道具
item_used_count = 0  # 道具使用次数
pause_button = None  # 暂停按钮

# 类别映射表（模型输出数字 -> 实际食材名称）
CLASS_MAPPING = {
    0: "香菇",
    1: "蔬菜",
    2: "鸡腿",
    3: "蛋糕",
    4: "红肉",
    5: "鸡蛋",
    6: "凤凰振翅",  # 特殊元素（由消除生成）
    7: "双龙戏珠"  # 特殊元素（由消除生成）
}

common_ingredients = ["香菇", "蔬菜", "鸡腿", "蛋糕", "红肉", "鸡蛋"]


def get_device_resolution(device_id=None):
    """获取设备分辨率"""
    try:
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

        cmd = [adb_path, 'shell', 'wm', 'size']
        if device_id:
            cmd = ['adb', '-s', device_id, 'shell', 'wm', 'size']

        result = subprocess.run(cmd, capture_output=True, text=True, startupinfo=startupinfo)

        if result.returncode == 0:
            # 解析输出，格式通常是 "Physical size: 1080x1920"
            output = result.stdout.strip()
            if 'Physical size:' in output:
                size_str = output.split('Physical size:')[1].strip()
                width, height = map(int, size_str.split('x'))
                return width, height
            elif 'Override size:' in output:
                size_str = output.split('Override size:')[1].strip()
                width, height = map(int, size_str.split('x'))
                return width, height

        print(f"无法获取设备分辨率，使用默认值: {result.stderr}")
        return 1080, 1920  # 默认分辨率
    except Exception as e:
        print(f"获取设备分辨率时出错: {e}")
        return 1080, 1920  # 默认分辨率


def calculate_adaptive_config(width, height):
    """根据设备分辨率计算自适应配置"""
    global BOARD_ORIGIN, CELL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT

    SCREEN_WIDTH = width
    SCREEN_HEIGHT = height

    # 首先检查是否有完全匹配的预设配置
    if (width, height) in RESOLUTION_CONFIGS:
        x, y, size = RESOLUTION_CONFIGS[(width, height)]
        BOARD_ORIGIN = (x, y)
        CELL_SIZE = size
        print(f"使用预设配置: 分辨率{width}x{height}, 棋盘起点({x},{y}), 格子大小{size}")
        return

    # 如果没有完全匹配，尝试按比例缩放
    # 以1080x1920为基准进行缩放
    base_width, base_height = 1080, 1920
    base_x, base_y, base_size = 90, 680, 120

    # 计算缩放比例
    scale_x = width / base_width
    scale_y = height / base_height

    # 使用较小的缩放比例以确保棋盘完全显示
    scale = min(scale_x, scale_y)

    # 计算新的配置
    new_x = int(base_x * scale_x)
    new_y = int(base_y * scale_y)
    new_size = int(base_size * scale)

    # 确保棋盘不会超出屏幕边界
    board_width = BOARD_SIZE * new_size
    board_height = BOARD_SIZE * new_size

    if new_x + board_width > width:
        new_x = width - board_width - 10  # 留10像素边距
    if new_y + board_height > height:
        new_y = height - board_height - 10  # 留10像素边距

    # 确保坐标不为负数
    new_x = max(10, new_x)
    new_y = max(10, new_y)

    BOARD_ORIGIN = (new_x, new_y)
    CELL_SIZE = new_size

    print(f"自适应配置: 分辨率{width}x{height}, 棋盘起点({new_x},{new_y}), 格子大小{new_size}")
    print(f"缩放比例: X={scale_x:.2f}, Y={scale_y:.2f}, 使用={scale:.2f}")


def init_device_config(device_id=None):
    """初始化设备配置"""
    width, height = get_device_resolution(device_id)
    calculate_adaptive_config(width, height)
    return width, height


def init_yolo():
    global model

    # 使用绝对路径加载模型
    if not os.path.exists(MODEL_PATH):
        raise Exception(f"模型文件不存在: {MODEL_PATH}")

    print(f"加载模型: {MODEL_PATH}")
    model = YOLO(MODEL_PATH)


def take_screenshot(retries=3):
    for _ in range(retries):
        try:
            # 创建startupinfo对象以隐藏控制台窗口
            startupinfo = None
            if os.name == 'nt':  # Windows系统
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            result = subprocess.run(
                [adb_path, 'exec-out', 'screencap -p'],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10,
                startupinfo=startupinfo
            )
            img_array = np.frombuffer(result.stdout, dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            return img
        except subprocess.CalledProcessError as e:
            print(f"ADB命令失败: {e.stderr.decode()}")
        except subprocess.TimeoutExpired:
            print("ADB命令超时，正在重试...")
        except Exception as e:
            print(f"截图异常: {str(e)}")
    return None


def infer_from_neighbors(board, i, j):
    # 首先尝试从邻居推断
    neighbors = []
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            ni, nj = i + dx, j + dy
            if 0 <= ni < BOARD_SIZE and 0 <= nj < BOARD_SIZE:
                if board[ni][nj] in common_ingredients:
                    neighbors.append(board[ni][nj])

    # 如果有足够的邻居，使用最常见的邻居类型
    if len(neighbors) >= 2:
        return max(set(neighbors), key=neighbors.count)

    # 否则，基于整个棋盘的当前分布选择
    food_counts = {}
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] in common_ingredients:
                food_counts[board[r][c]] = food_counts.get(board[r][c], 0) + 1

    # 如果棋盘上有普通食材，根据分布选择
    if food_counts:
        max_count = max(food_counts.values())
        most_common = [food for food, count in food_counts.items() if count == max_count]
        return random.choice(most_common)
    else:
        # 如果没有足够信息，返回随机食材
        return random.choice(common_ingredients)


def detect_board(img, model):
    h, w = img.shape[:2]
    board_area = img[
                 BOARD_ORIGIN[1]: BOARD_ORIGIN[1] + BOARD_SIZE * CELL_SIZE,
                 BOARD_ORIGIN[0]: BOARD_ORIGIN[0] + BOARD_SIZE * CELL_SIZE
                 ]
    if board_area.size == 0:
        print(f"棋盘区域检测异常，请校准参数：BOARD_ORIGIN={BOARD_ORIGIN}, CELL_SIZE={CELL_SIZE}")
        return [[None] * BOARD_SIZE for _ in range(BOARD_SIZE)]

    results = model(img)
    board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    current_confidence = [[-1 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

    for result in results:
        for box in result.boxes:
            x_center = (box.xyxy[0][0] + box.xyxy[0][2]) / 2
            y_center = (box.xyxy[0][1] + box.xyxy[0][3]) / 2
            rel_x = x_center - BOARD_ORIGIN[0]
            rel_y = y_center - BOARD_ORIGIN[1]
            j = int(rel_x // CELL_SIZE)
            i = int(rel_y // CELL_SIZE)
            if 0 <= i < BOARD_SIZE and 0 <= j < BOARD_SIZE:
                cls = int(box.cls[0])
                detected_class = CLASS_MAPPING.get(cls, "未知")
                conf = float(box.conf[0]) if hasattr(box, 'conf') else 1.0
                if board[i][j] is None or conf > current_confidence[i][j]:
                    board[i][j] = detected_class
                    current_confidence[i][j] = conf
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] in ["未知", None]:
                board[i][j] = infer_from_neighbors(board, i, j)
    return board


def draw_debug_image(img, board):
    debug_img = img.copy()
    BOARD_TOPLEFT_X = BOARD_ORIGIN[0]
    BOARD_TOPLEFT_Y = BOARD_ORIGIN[1]
    for i in range(BOARD_SIZE + 1):
        y = BOARD_TOPLEFT_Y + i * CELL_SIZE
        cv2.line(debug_img, (BOARD_TOPLEFT_X, y), (BOARD_TOPLEFT_X + BOARD_SIZE * CELL_SIZE, y), (0, 255, 0), 2)
    for j in range(BOARD_SIZE + 1):
        x = BOARD_TOPLEFT_X + j * CELL_SIZE
        cv2.line(debug_img, (x, BOARD_TOPLEFT_Y), (x, BOARD_TOPLEFT_Y + BOARD_SIZE * CELL_SIZE), (0, 255, 0), 2)

    # 获取字体路径 - 仅使用Windows自带字体
    font_path = None
    # 尝试Windows默认路径
    windows_font = r"C:\Windows\Fonts\simhei.ttf"
    if os.path.exists(windows_font):
        font_path = windows_font
    else:
        # 如果找不到字体，使用默认字体
        print("警告: 找不到simhei.ttf字体，将使用默认字体")

    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] is not None:
                x = BOARD_TOPLEFT_X + j * CELL_SIZE + CELL_SIZE // 2 - 15
                y = BOARD_TOPLEFT_Y + i * CELL_SIZE + CELL_SIZE // 2 + 5
                from PIL import ImageFont, ImageDraw, Image
                pil_img = Image.fromarray(cv2.cvtColor(debug_img, cv2.COLOR_BGR2RGB))
                draw = ImageDraw.Draw(pil_img)

                if font_path:
                    try:
                        font = ImageFont.truetype(font_path, 14)
                    except:
                        font = ImageFont.load_default()
                else:
                    font = ImageFont.load_default()

                draw.text((x, y), board[i][j], fill=(0, 0, 255), font=font)
                debug_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    # 确保调试目录存在
    os.makedirs(DEBUG_DIR, exist_ok=True)
    cv2.imwrite(os.path.join(DEBUG_DIR, 'debug.jpg'), debug_img)


def generate_swaps():
    swaps = []
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if j < BOARD_SIZE - 1:
                swaps.append(((i, j), (i, j + 1)))
            if i < BOARD_SIZE - 1:
                swaps.append(((i, j), (i + 1, j)))
    return swaps


def count_line(board, i, j, di, dj):
    color = board[i][j]
    cnt = 1
    ni, nj = i + di, j + dj
    while 0 <= ni < BOARD_SIZE and 0 <= nj < BOARD_SIZE and board[ni][nj] == color:
        cnt += 1
        ni += di
        nj += dj
    ni, nj = i - di, j - dj
    while 0 <= ni < BOARD_SIZE and 0 <= nj < BOARD_SIZE and board[ni][nj] == color:
        cnt += 1
        ni -= di
        nj -= dj
    return cnt


def is_valid_swap(board, swap):
    temp_board = [row.copy() for row in board]
    (i1, j1), (i2, j2) = swap
    a, b = temp_board[i1][j1], temp_board[i2][j2]
    # 1. 双龙戏珠与双龙戏珠相邻直接允许（必须最前面）
    if a == "双龙戏珠" and b == "双龙戏珠" and abs(i1 - i2) + abs(j1 - j2) == 1:
        return True
    # 2. 其它特殊消除类型直接允许
    if (a == "双龙戏珠" and b in common_ingredients) or (b == "双龙戏珠" and a in common_ingredients):
        return True
    if (a == "凤凰振翅" and b in common_ingredients) or (b == "凤凰振翅" and a in common_ingredients):
        return True
    if (a == "凤凰振翅" and b == "凤凰振翅"):
        if abs(i1 - i2) + abs(j1 - j2) == 1:
            return True
    if (a == "双龙戏珠" and b == "凤凰振翅") or (a == "凤凰振翅" and b == "双龙戏珠"):
        return True
    # 3. 其它情况按横竖消除规则
    temp_board[i1][j1], temp_board[i2][j2] = temp_board[i2][j2], temp_board[i1][j1]
    for (i, j) in [(i1, j1), (i2, j2)]:
        if temp_board[i][j] not in common_ingredients:
            continue
        h = count_line(temp_board, i, j, 0, 1)
        v = count_line(temp_board, i, j, 1, 0)
        cross = 0
        if h >= 3: cross += h - 1
        if v >= 3: cross += v - 1
        if ((h >= 3 and v >= 3 and cross + 1 >= 5) or (h >= 3 and v < 3) or (v >= 3 and h < 3)):
            return True
    return False


def find_matches(board):
    matches = []
    # 横向查找
    for i in range(BOARD_SIZE):
        j = 0
        while j < BOARD_SIZE:
            run = []
            start_j = j
            while j < BOARD_SIZE and board[i][j] in common_ingredients and board[i][j] == board[i][start_j]:
                run.append((i, j))
                j += 1
            if len(run) >= 3:
                matches.append(run)
            if len(run) == 0:
                j += 1
    # 竖向查找
    for j in range(BOARD_SIZE):
        i = 0
        while i < BOARD_SIZE:
            run = []
            start_i = i
            while i < BOARD_SIZE and board[i][j] in common_ingredients and board[i][j] == board[start_i][j]:
                run.append((i, j))
                i += 1
            if len(run) >= 3:
                matches.append(run)
            if len(run) == 0:
                i += 1
    return matches


def process_elimination(board, matches, swap):
    """
    处理所有消除组，生成特殊元素，返回新棋盘、特殊元素列表、得分
    """
    elim = set()
    specials = []
    score = 0
    base_score = 0
    used_for_special = set()

    # 统计所有消除格
    for match in matches:
        for pos in match:
            elim.add(pos)

    # 统计每个点属于的横向和竖向组
    pos_to_h = dict()
    pos_to_v = dict()
    for match in matches:
        if len(match) < 3:
            continue
        if all(match[0][0] == x for x, y in match):  # 横向
            for pos in match:
                pos_to_h.setdefault(pos, []).append(match)
        elif all(match[0][1] == y for x, y in match):  # 竖向
            for pos in match:
                pos_to_v.setdefault(pos, []).append(match)

    # 1. L/T形交叉点生成双龙
    dragon_points = set()
    for pos in elim:
        h_len = max((len(m) for m in pos_to_h.get(pos, [])), default=0)
        v_len = max((len(m) for m in pos_to_v.get(pos, [])), default=0)
        if h_len >= 3 and v_len >= 3:
            dragon_points.add(pos)
    for pos in dragon_points:
        specials.append(("双龙戏珠", pos))
        used_for_special.add(pos)
        print(f"DEBUG: 在L/T形交叉点生成双龙戏珠 在位置 {pos}")

    # 2. 横/竖5连中心点生成双龙
    for match in matches:
        if len(match) == 5:
            # 横向5连
            if all(match[0][0] == x for x, y in match):
                center = match[2]  # 中心点
                if center not in used_for_special:
                    specials.append(("双龙戏珠", center))
                    used_for_special.add(center)
                    print(f"DEBUG: 在横向5连中心点生成双龙戏珠 在位置 {center}")
            # 竖向5连
            elif all(match[0][1] == y for x, y in match):
                center = match[2]  # 中心点
                if center not in used_for_special:
                    specials.append(("双龙戏珠", center))
                    used_for_special.add(center)
                    print(f"DEBUG: 在竖向5连中心点生成双龙戏珠 在位置 {center}")

    # 3. 横/竖4连生成凤凰，位置为swap[1]
    if swap:
        target = swap[1]
        h_len = max((len(m) for m in pos_to_h.get(target, [])), default=0)
        v_len = max((len(m) for m in pos_to_v.get(target, [])), default=0)
        if (h_len == 4 or v_len == 4) and target not in used_for_special:
            specials.append(("凤凰振翅", target))
            used_for_special.add(target)
            print(f"DEBUG: 在4连位置生成凤凰振翅 在位置 {target}")

    # 计分
    for (i, j) in elim:
        if board[i][j] in common_ingredients:
            score += 1
            base_score += 1
        elif board[i][j] == "凤凰振翅":
            score += 3
            base_score += 3
        elif board[i][j] == "双龙戏珠":
            score += 5  # 修改积分 - 双龙为5分而不是15分
            base_score += 5  # 修改积分 - 双龙为5分而不是15分

    # 生成新棋盘
    new_board = []
    for i in range(BOARD_SIZE):
        row = []
        for j in range(BOARD_SIZE):
            if (i, j) in elim and (i, j) not in used_for_special:
                row.append(None)
            else:
                row.append(board[i][j])
        new_board.append(row)

    # 立即在新棋盘上放置特殊元素
    for stype, (i, j) in specials:
        new_board[i][j] = stype

    return new_board, [], score, base_score  # 返回空的specials列表，因为已经放置了特殊元素


def fall_down(board):
    """
    原始下落函数，现在内部调用fall_down_with_distribution来保持行为一致
    """
    # 获取当前棋盘的食材分布
    distribution = get_board_distribution(board)

    # 调用新函数进行下落
    return fall_down_with_distribution(board, distribution)


def fall_down_with_distribution(board, distribution):
    """使用指定的食材分布进行下落填充"""
    new_board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

    for j in range(BOARD_SIZE):
        col = []
        for i in reversed(range(BOARD_SIZE)):
            if board[i][j] is not None:
                col.append(board[i][j])

        # 填充剩余位置为None，而不是生成新食材
        while len(col) < BOARD_SIZE:
            col.append(None)

        for i in range(BOARD_SIZE):
            new_board[i][j] = col[BOARD_SIZE - 1 - i]

    return new_board


def phoenix_ingredient_eliminate(board, pos1, pos2, original_distribution=None):
    """
    凤凰+普通食材：以交换后的凤凰为中心3*3范围消除，不消除双龙，保留连锁反应
    """
    # 确定哪个是凤凰，哪个是普通食材
    if board[pos1[0]][pos1[1]] == "凤凰振翅":
        phoenix_pos = pos1
        ingredient_pos = pos2  # 普通食材位置
    else:
        phoenix_pos = pos2
        ingredient_pos = pos1  # 普通食材位置

    # 确认交换的是普通食材
    if board[ingredient_pos[0]][ingredient_pos[1]] not in common_ingredients:
        # 如果不是普通食材，处理异常情况
        return board, 0, 0

    # 交换位置
    board = [row.copy() for row in board]
    board[pos1[0]][pos1[1]], board[pos2[0]][pos2[1]] = board[pos2[0]][pos2[1]], board[pos1[0]][pos1[1]]

    # 重要修复：交换后需要重新确定凤凰的位置
    # 交换后，凤凰的位置会变成原来普通食材的位置
    if phoenix_pos == pos1:
        phoenix_pos = pos2
    else:
        phoenix_pos = pos1

    # 构建消除集合，不包括双龙，只消除凤凰周围3*3区域
    elim = set()
    already_exploded = set()

    def explode_phoenix_area(center):
        """消除以中心点为中心的3×3区域，不包括双龙"""
        ci, cj = center
        # 3×3范围（中心周围1格）
        for di in range(-1, 2):
            for dj in range(-1, 2):
                ni, nj = ci + di, cj + dj
                if 0 <= ni < BOARD_SIZE and 0 <= nj < BOARD_SIZE:
                    # 不消除双龙
                    if board[ni][nj] != "双龙戏珠":
                        elim.add((ni, nj))
                        # 如果消除了其他凤凰，触发连锁反应
                        if board[ni][nj] == "凤凰振翅" and (ni, nj) != center and (ni, nj) not in already_exploded:
                            already_exploded.add((ni, nj))
                            explode_phoenix_area((ni, nj))

    # 从凤凰位置开始引爆，只消除凤凰周围的区域
    explode_phoenix_area(phoenix_pos)

    print(f"DEBUG: 凤凰+普通食材消除，凤凰位置{phoenix_pos}，消除了{len(elim)}个格子")

    # 计算分数
    score, base_score = 0, 0
    for (i, j) in elim:
        if board[i][j] in common_ingredients:
            score += 1
            base_score += 1
        elif board[i][j] == "凤凰振翅":
            score += 3
            base_score += 3

    # 生成新棋盘
    new_board = [[None if (i, j) in elim else board[i][j] for j in range(BOARD_SIZE)] for i in range(BOARD_SIZE)]

    # 使用原始分布进行填充
    if original_distribution is None:
        original_distribution = get_board_distribution(board)

    new_board = fall_down_with_distribution(new_board, original_distribution)

    return new_board, score, base_score


def phoenix_phoenix_eliminate(board, pos1, pos2, original_distribution=None):
    """
    凤凰+凤凰：以目标凤凰为中心5*5范围消除，不消除双龙
    """
    # 交换位置
    board = [row.copy() for row in board]
    board[pos1[0]][pos1[1]], board[pos2[0]][pos2[1]] = board[pos2[0]][pos2[1]], board[pos1[0]][pos1[1]]

    # 以拖动目标位置为中心5*5
    center = pos2
    elim = set()
    already_exploded = set()

    def explode_phoenix_area(center, area_size):
        """消除以中心点为中心的指定范围区域，不包括双龙"""
        ci, cj = center
        for di in range(-area_size, area_size + 1):
            for dj in range(-area_size, area_size + 1):
                ni, nj = ci + di, cj + dj
                if 0 <= ni < BOARD_SIZE and 0 <= nj < BOARD_SIZE:
                    # 不消除双龙
                    if board[ni][nj] != "双龙戏珠":
                        elim.add((ni, nj))
                        # 如果消除了其他凤凰，触发连锁反应（被引爆的凤凰只引爆3*3）
                        if board[ni][nj] == "凤凰振翅" and (ni, nj) != center and (ni, nj) not in already_exploded:
                            already_exploded.add((ni, nj))
                            explode_phoenix_area((ni, nj), 1)  # 被引爆的凤凰范围是3*3

    # 从目标凤凰位置开始引爆，范围是5*5
    explode_phoenix_area(center, 2)  # 2表示中心周围2格，形成5*5范围

    print(f"DEBUG: 凤凰+凤凰消除，目标凤凰位置{center}，消除了{len(elim)}个格子")

    score, base_score = 0, 0
    for (i, j) in elim:
        if board[i][j] in common_ingredients:
            score += 1
            base_score += 1
        elif board[i][j] == "凤凰振翅":
            score += 3
            base_score += 3

    new_board = [[None if (i, j) in elim else board[i][j] for j in range(BOARD_SIZE)] for i in range(BOARD_SIZE)]

    # 使用原始分布进行填充
    if original_distribution is None:
        original_distribution = get_board_distribution(board)

    new_board = fall_down_with_distribution(new_board, original_distribution)

    return new_board, score, base_score


def dragon_ingredient_eliminate(board, pos1, pos2, original_distribution=None):
    """
    双龙+普通食材：消除全屏所有该食材和交换的双龙本身，不消除其他双龙
    """
    # 交换位置
    board = [row.copy() for row in board]
    board[pos1[0]][pos1[1]], board[pos2[0]][pos2[1]] = board[pos2[0]][pos2[1]], board[pos1[0]][pos1[1]]

    # 确定哪个是双龙，哪个是普通食材
    if board[pos1[0]][pos1[1]] == "双龙戏珠":
        dragon_pos = pos1
        target = board[pos2[0]][pos2[1]]
    else:
        dragon_pos = pos2
        target = board[pos1[0]][pos1[1]]

    # 确保目标是普通食材
    if target not in common_ingredients:
        return board, 0, 0

    # 构建消除集合：所有目标类型的普通食材和当前交换的双龙本身
    elim = set()
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == target or (i, j) == dragon_pos:
                elim.add((i, j))

    print(f"DEBUG: 双龙+普通食材消除，双龙位置{dragon_pos}，目标食材类型:{target}，消除了{len(elim)}个格子")

    score, base_score = 0, 0
    for (i, j) in elim:
        if board[i][j] in common_ingredients:
            score += 1
            base_score += 1
        elif board[i][j] == "双龙戏珠":
            score += 5  # 修改积分 - 双龙为5分而不是15分
            base_score += 5  # 修改积分 - 双龙为5分而不是15分

    # 生成消除后的棋盘
    new_board = [[None if (i, j) in elim else board[i][j] for j in range(BOARD_SIZE)] for i in range(BOARD_SIZE)]

    # 使用原始分布进行填充
    if original_distribution is None:
        original_distribution = get_board_distribution(board)

    # 初次下落填充
    new_board = fall_down_with_distribution(new_board, original_distribution)

    # 处理可能的连锁反应 - 检查是否有L/T形或5连生成双龙
    specials = []
    match_found = True

    # 进行连锁检查，直到没有新的消除
    chain_count = 0
    while match_found:
        matches = find_matches(new_board)
        if not matches:
            match_found = False
            break

        chain_count += 1
        print(f"DEBUG: 双龙+普通食材消除后第{chain_count}次连锁反应，找到{len(matches)}组消除")

        # 分析每组消除，检查是否能生成特殊元素
        new_board, new_specials, chain_score, chain_base_score = process_elimination(new_board, matches, None)
        specials.extend(new_specials)
        score += chain_score
        base_score += chain_base_score

        print_board_text(new_board, f"连锁消除后 (本次得分:{chain_score}, 本次基础分:{chain_base_score})")

        # 执行下落
        new_board = fall_down_with_distribution(new_board, original_distribution)
        print_board_text(new_board, "下落填充后")

    # 将特殊元素放回棋盘
    for stype, (i, j) in specials:
        new_board[i][j] = stype
        print(f"DEBUG: 双龙消除食材后，检测到连锁反应生成了新的{stype}在位置({i},{j})")

    if specials:
        print_board_text(new_board, "放置特殊元素后最终状态")

    return new_board, score, base_score


def dragon_dragon_eliminate(board, pos1, pos2, original_distribution=None):
    """双龙+双龙：全屏所有格子"""
    elim = set((i, j) for i in range(BOARD_SIZE) for j in range(BOARD_SIZE))
    score, base_score = 0, 0
    for (i, j) in elim:
        if board[i][j] in common_ingredients:
            score += 2  # 双倍积分
            base_score += 2  # 双倍积分
        elif board[i][j] == "凤凰振翅":
            score += 3
            base_score += 3
        elif board[i][j] == "双龙戏珠":
            score += 5  # 修改积分 - 双龙为5分而不是15分
            base_score += 5  # 修改积分 - 双龙为5分而不是15分

    new_board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

    # 使用原始分布进行填充
    if original_distribution is None:
        original_distribution = get_board_distribution(board)

    # 修改fall_down函数的调用，传入分布信息
    new_board = fall_down_with_distribution(new_board, original_distribution)

    return new_board, score, base_score


def fall_down_with_distribution(board, distribution):
    """使用指定的食材分布进行下落填充"""
    new_board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

    for j in range(BOARD_SIZE):
        col = []
        for i in reversed(range(BOARD_SIZE)):
            if board[i][j] is not None:
                col.append(board[i][j])

        # 填充剩余位置为None，而不是生成新食材
        while len(col) < BOARD_SIZE:
            col.append(None)

        for i in range(BOARD_SIZE):
            new_board[i][j] = col[BOARD_SIZE - 1 - i]

    return new_board


# 增加两个新函数用于检测潜在的L形和T形
def check_potential_l_shapes(board, i, j):
    """检测潜在的L形状可能性，返回潜力分数"""
    if i >= BOARD_SIZE - 1 or j >= BOARD_SIZE - 1:
        return 0

    color = board[i][j]
    if color not in common_ingredients:
        return 0

    potential_score = 0

    # 检查右下角L形
    if (j + 2 < BOARD_SIZE and i + 2 < BOARD_SIZE and
            board[i][j + 1] == color and board[i][j + 2] == color and
            board[i + 1][j] == color and board[i + 2][j] == color):
        potential_score += 1

    # 检查左下角L形
    if (j - 2 >= 0 and i + 2 < BOARD_SIZE and
            board[i][j - 1] == color and board[i][j - 2] == color and
            board[i + 1][j] == color and board[i + 2][j] == color):
        potential_score += 1

    # 检查右上角L形
    if (j + 2 < BOARD_SIZE and i - 2 >= 0 and
            board[i][j + 1] == color and board[i][j + 2] == color and
            board[i - 1][j] == color and board[i - 2][j] == color):
        potential_score += 1

    # 检查左上角L形
    if (j - 2 >= 0 and i - 2 >= 0 and
            board[i][j - 1] == color and board[i][j - 2] == color and
            board[i - 1][j] == color and board[i - 2][j] == color):
        potential_score += 1

    # 检查部分形成的L形（至少有两个方向各两个相同食材）
    directions = [
        [[(0, 1), (0, 2)], [(1, 0), (2, 0)]],  # 右下
        [[(0, -1), (0, -2)], [(1, 0), (2, 0)]],  # 左下
        [[(0, 1), (0, 2)], [(-1, 0), (-2, 0)]],  # 右上
        [[(0, -1), (0, -2)], [(-1, 0), (-2, 0)]]  # 左上
    ]

    for dir_pair in directions:
        horizontal = sum(1 for dx, dy in dir_pair[0] if
                         0 <= i + dx < BOARD_SIZE and 0 <= j + dy < BOARD_SIZE and
                         board[i + dx][j + dy] == color)
        vertical = sum(1 for dx, dy in dir_pair[1] if
                       0 <= i + dx < BOARD_SIZE and 0 <= j + dy < BOARD_SIZE and
                       board[i + dx][j + dy] == color)

        # 如果一个方向已经有2个相同，另一个方向至少有1个相同
        if (horizontal == 2 and vertical >= 1) or (vertical == 2 and horizontal >= 1):
            potential_score += 0.5

    return potential_score


def check_potential_t_shapes(board, i, j):
    """检测潜在的T形状可能性，返回潜力分数"""
    if i >= BOARD_SIZE - 1 or j >= BOARD_SIZE - 1 or i <= 0 or j <= 0:
        return 0

    color = board[i][j]
    if color not in common_ingredients:
        return 0

    potential_score = 0

    # 检查T形（横杠在上）
    if (i - 1 >= 0 and j - 1 >= 0 and j + 1 < BOARD_SIZE and
            board[i - 1][j] == color and
            board[i][j - 1] == color and board[i][j + 1] == color):
        potential_score += 1

    # 检查T形（横杠在下）
    if (i + 1 < BOARD_SIZE and j - 1 >= 0 and j + 1 < BOARD_SIZE and
            board[i + 1][j] == color and
            board[i][j - 1] == color and board[i][j + 1] == color):
        potential_score += 1

    # 检查T形（横杠在中，竖杠向上）
    if (i - 1 >= 0 and i - 2 >= 0 and j - 1 >= 0 and j + 1 < BOARD_SIZE and
            board[i - 1][j] == color and board[i - 2][j] == color and
            board[i][j - 1] == color and board[i][j + 1] == color):
        potential_score += 1

    # 检查T形（横杠在中，竖杠向下）
    if (i + 1 < BOARD_SIZE and i + 2 < BOARD_SIZE and j - 1 >= 0 and j + 1 < BOARD_SIZE and
            board[i + 1][j] == color and board[i + 2][j] == color and
            board[i][j - 1] == color and board[i][j + 1] == color):
        potential_score += 1

    # 检查部分形成的T形
    # 水平三连+垂直潜力
    if (j - 1 >= 0 and j + 1 < BOARD_SIZE and board[i][j - 1] == color and board[i][j + 1] == color):
        if (i - 1 >= 0 and board[i - 1][j] == color) or (i + 1 < BOARD_SIZE and board[i + 1][j] == color):
            potential_score += 0.7

    # 垂直三连+水平潜力
    if (i - 1 >= 0 and i + 1 < BOARD_SIZE and board[i - 1][j] == color and board[i + 1][j] == color):
        if (j - 1 >= 0 and board[i][j - 1] == color) or (j + 1 < BOARD_SIZE and board[i][j + 1] == color):
            potential_score += 0.7

    return potential_score


# 添加一个辅助函数来评估单个食材的价值（基于周围相同食材数量）
def evaluate_ingredient_value(board, i, j):
    """评估一个普通食材的价值，基于周围相同食材的数量"""
    if board[i][j] not in common_ingredients:
        return 0

    color = board[i][j]
    value = 1  # 基础价值

    # 检查水平方向
    h_count = 1
    # 向左
    for dj in range(-1, -3, -1):
        nj = j + dj
        if 0 <= nj < BOARD_SIZE and board[i][nj] == color:
            h_count += 1
        else:
            break
    # 向右
    for dj in range(1, 3):
        nj = j + dj
        if 0 <= nj < BOARD_SIZE and board[i][nj] == color:
            h_count += 1
        else:
            break

    # 检查垂直方向
    v_count = 1
    # 向上
    for di in range(-1, -3, -1):
        ni = i + di
        if 0 <= ni < BOARD_SIZE and board[ni][j] == color:
            v_count += 1
        else:
            break
    # 向下
    for di in range(1, 3):
        ni = i + di
        if 0 <= ni < BOARD_SIZE and board[ni][j] == color:
            v_count += 1
        else:
            break

    # 根据连线长度增加价值
    if h_count >= 3 or v_count >= 3:
        value += 3  # 可直接消除
    elif h_count == 2 and v_count == 2:
        value += 2  # 潜在L形
    elif h_count == 2 or v_count == 2:
        value += 1  # 潜在直线

    return value


def evaluate_state(board, score):
    value = score * 2.5  # 更高的基础分权重
    phoenixes = []
    dragons = []

    # 统计特殊元素
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == "凤凰振翅":
                phoenixes.append((i, j))
                # 凤凰位于中心区域更有价值
                distance_from_center = abs(i - 3.5) + abs(j - 3.5)
                value += 8000 - distance_from_center * 500  # 大幅提高凤凰的价值

                # 评估凤凰周围3*3区域内普通食材的数量
                nearby_ingredients = 0
                nearby_high_value = 0
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        ni, nj = i + dx, j + dy
                        if 0 <= ni < BOARD_SIZE and 0 <= nj < BOARD_SIZE:
                            if board[ni][nj] in common_ingredients:
                                nearby_ingredients += 1
                                # 如果周围有更高分值的食材组合，提高价值
                                if evaluate_ingredient_value(board, ni, nj) > 1:
                                    nearby_high_value += 1

                # 根据周围普通食材数量调整价值
                value += nearby_ingredients * 500
                value += nearby_high_value * 1000

            elif board[i][j] == "双龙戏珠":
                dragons.append((i, j))
                # 大幅提高双龙价值
                value += 18000 + 5000 * (len(dragons) - 1)  # 大幅提高双龙的价值

    # 双龙之间距离评估，大幅提高奖励
    if len(dragons) >= 2:
        value += 30000  # 进一步提高双龙组合的基础奖励
        min_distance = min(
            abs(d1[0] - d2[0]) + abs(d1[1] - d2[1])
            for d1 in dragons for d2 in dragons if d1 != d2
        )
        # 距离为1时给予超高奖励（相邻）
        if min_distance == 1:
            value += 80000  # 相邻双龙给予极高奖励
        else:
            value += (8 - min_distance) * 8000  # 距离奖励

    # 双龙与凤凰的组合评估（考虑到凤凰不能消除双龙的特性，稍微降低相邻价值）
    if dragons and phoenixes:
        min_dragon_phoenix_distance = min(
            abs(d[0] - p[0]) + abs(d[1] - p[1])
            for d in dragons for p in phoenixes
        )
        # 距离为1时给予高奖励（相邻），但不如双龙相邻高
        if min_dragon_phoenix_distance == 1:
            value += 40000  # 相邻双龙和凤凰给予高奖励，但低于双龙+双龙
        else:
            value += (8 - min_dragon_phoenix_distance) * 5000  # 距离奖励

    # 检查是否有潜在的双龙生成机会（5连或特殊形状）
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] in common_ingredients:
                # 增强L形检测
                potential_l_shapes = check_potential_l_shapes(board, i, j)
                if potential_l_shapes:
                    value += 20000 * potential_l_shapes

                # 增强T形检测
                potential_t_shapes = check_potential_t_shapes(board, i, j)
                if potential_t_shapes:
                    value += 25000 * potential_t_shapes

                # 水平方向
                if j <= BOARD_SIZE - 4:
                    h_count = 1
                    for c in range(j + 1, min(j + 4, BOARD_SIZE)):
                        if board[i][c] == board[i][j]:
                            h_count += 1
                    # 提高对接近形成双龙的评估
                    if h_count == 4:  # 已有4连，只差一个
                        value += 15000
                    elif h_count == 3:  # 已有3连，差两个
                        value += 5000

                # 垂直方向
                if i <= BOARD_SIZE - 4:
                    v_count = 1
                    for r in range(i + 1, min(i + 4, BOARD_SIZE)):
                        if board[r][j] == board[i][j]:
                            v_count += 1
                    # 提高对接近形成双龙的评估
                    if v_count == 4:  # 已有4连，只差一个
                        value += 15000
                    elif v_count == 3:  # 已有3连，差两个
                        value += 5000

                # 检查T形状（中心点）
                if 1 <= i < BOARD_SIZE - 1 and 1 <= j < BOARD_SIZE - 1:
                    # 检查有没有十字形（上下左右都是相同元素）
                    cross_count = 0
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        ni, nj = i + dr, j + dc
                        if 0 <= ni < BOARD_SIZE and 0 <= nj < BOARD_SIZE and board[ni][nj] == board[i][j]:
                            cross_count += 1

                    if cross_count >= 3:  # 至少有3个方向相同，形成T形的潜力
                        value += 20000
                    elif cross_count == 2:  # 有两个方向相同，也有潜力
                        value += 3000

    # 新增：加上全局双龙生成潜力分
    value += evaluate_dragon_potential(board)

    # 步数策略调整
    remaining_steps = TARGET_STEPS - steps_used
    if remaining_steps <= 0:
        # 已超过目标步数，以稳健策略为主
        if total_base_score >= SCORE_TARGET:
            # 已达标，选择保守策略，尽量获取确定的消除
            value *= 0.7
            value += score * 3.0  # 更重视当前直接收益
        else:
            # 未达标，选择更激进的策略
            urgency_factor = 2.0 + (steps_used - TARGET_STEPS) * 0.2  # 增加紧急度
            urgency_factor = min(urgency_factor, 5.0)  # 最高不超过5倍
            value *= urgency_factor
    else:
        # 还在目标步数内
        current_avg_score = total_base_score / max(1, steps_used)
        needed_avg_score = (SCORE_TARGET - total_base_score) / max(1, remaining_steps)

        # 根据距离目标的远近调整策略激进程度
        if total_base_score < SCORE_TARGET:
            urgency_factor = needed_avg_score / max(1, current_avg_score)
            # 如果需要的平均分数高于当前平均，增加风险承受度
            if urgency_factor > 1.2:
                value *= (1 + min(urgency_factor, 6) * 0.8)

        # 接近目标步数且分数不足时，大幅提高风险偏好
        if remaining_steps < 5 and total_base_score < SCORE_TARGET * 0.9:
            value += 30000 * (5 - remaining_steps)

        # 稳健模式：已接近或超过目标时
        if total_base_score >= SCORE_TARGET * 0.95 and remaining_steps > 3:
            value *= 0.6 + 0.4 * (total_base_score / SCORE_TARGET)
            value += score * 2.0  # 更偏向直接收益

    return value


def evaluate_dragon_potential(board):
    """
    评估棋盘上所有普通食材的生成双龙潜力，越接近越高，中心位置加权更高。
    返回总潜力分。
    """
    total_potential = 0
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            color = board[i][j]
            if color not in common_ingredients:
                continue
            # 计算中心加权，越靠近中心分数越高
            center_weight = 1.0 + 0.5 * (
                    1 - (abs(i - (BOARD_SIZE - 1) / 2) + abs(j - (BOARD_SIZE - 1) / 2)) / (BOARD_SIZE - 1))
            # 检查横向、竖向、L形、T形潜力
            h_count = 1
            for dj in range(1, 5):
                nj = j + dj
                if 0 <= nj < BOARD_SIZE and board[i][nj] == color:
                    h_count += 1
                else:
                    break
            for dj in range(1, 5):
                nj = j - dj
                if 0 <= nj < BOARD_SIZE and board[i][nj] == color:
                    h_count += 1
                else:
                    break
            v_count = 1
            for di in range(1, 5):
                ni = i + di
                if 0 <= ni < BOARD_SIZE and board[ni][j] == color:
                    v_count += 1
                else:
                    break
            for di in range(1, 5):
                ni = i - di
                if 0 <= ni < BOARD_SIZE and board[ni][j] == color:
                    v_count += 1
                else:
                    break
            # 横向/竖向5连潜力
            if h_count == 5 or v_count == 5:
                total_potential += 10000 * center_weight
            elif h_count == 4 or v_count == 4:
                total_potential += 4000 * center_weight
            elif h_count == 3 or v_count == 3:
                total_potential += 1200 * center_weight
            # L形潜力
            l_score = check_potential_l_shapes(board, i, j)
            if l_score:
                total_potential += 6000 * l_score * center_weight
            # T形潜力
            t_score = check_potential_t_shapes(board, i, j)
            if t_score:
                total_potential += 8000 * t_score * center_weight
    return total_potential


def will_generate_dragon(board, swap, target_pos=None):
    """判断交换后目标点是否会生成双龙（L/T形或横/竖5连中心）"""
    temp_board = [row.copy() for row in board]
    (i1, j1), (i2, j2) = swap
    temp_board[i1][j1], temp_board[i2][j2] = temp_board[i2][j2], temp_board[i1][j1]

    # 如果没有指定目标位置，检查交换的两个位置
    if target_pos is None:
        # 检查两个交换位置是否有一个能生成双龙
        return (check_dragon_formation(temp_board, (i1, j1)) or
                check_dragon_formation(temp_board, (i2, j2)))
    else:
        # 指定位置检查
        return check_dragon_formation(temp_board, target_pos)


def check_dragon_formation(board, pos):
    """检查指定位置是否能形成双龙（辅助函数）"""
    i, j = pos
    color = board[i][j]
    if color not in common_ingredients:
        return False

    # 1. 检测横向连线
    h_count = 1
    left = 0
    for c in range(j - 1, -1, -1):
        if board[i][c] == color:
            h_count += 1
            left += 1
        else:
            break
    right = 0
    for c in range(j + 1, BOARD_SIZE):
        if board[i][c] == color:
            h_count += 1
            right += 1
        else:
            break

    # 2. 检测竖向连线
    v_count = 1
    up = 0
    for r in range(i - 1, -1, -1):
        if board[r][j] == color:
            v_count += 1
            up += 1
        else:
            break
    down = 0
    for r in range(i + 1, BOARD_SIZE):
        if board[r][j] == color:
            v_count += 1
            down += 1
        else:
            break

    # 3. L形/T形检测（横竖都≥3）
    if h_count >= 3 and v_count >= 3:
        return True

    # 4. 横向5连中心
    if h_count == 5:
        return True

    # 5. 竖向5连中心
    if v_count == 5:
        return True

    # 6. 增强型L形检测
    # 检查目标点是否为L形拐角
    if ((left >= 2 and down >= 2) or (left >= 2 and up >= 2) or
            (right >= 2 and down >= 2) or (right >= 2 and up >= 2)):
        # 确认至少一个方向有3个或以上相同元素
        if ((left >= 2 and (up >= 2 or down >= 2)) or
                (right >= 2 and (up >= 2 or down >= 2))):
            return True

    # 7. 增强型T形检测
    # 横向有3个及以上，且竖向上下都有元素
    if h_count >= 3 and up >= 1 and down >= 1:
        return True
    # 竖向有3个及以上，且横向左右都有元素
    if v_count >= 3 and left >= 1 and right >= 1:
        return True

    return False


def get_best_move(board):
    global total_base_score, steps_used
    swaps = [swap for swap in generate_swaps() if is_valid_swap(board, swap)]
    if not swaps:
        return None
    dragons = [(i, j) for i, j in product(range(BOARD_SIZE), repeat=2) if board[i][j] == "双龙戏珠"]
    phoenixes = [(i, j) for i, j in product(range(BOARD_SIZE), repeat=2) if board[i][j] == "凤凰振翅"]

    # 辅助函数：选择最佳交换（消除食材最多的）
    def select_best_swap(candidates):
        """
        从候选交换列表中选择基础分最高的交换（包含连锁消除加成分数）
        candidates: 候选交换列表
        返回: 基础分最高的交换
        """
        if not candidates:
            return None
        best_swap = None
        best_base_score = -1
        for swap in candidates:
            _, _, base_score = simulate_swap(board, swap)
            if base_score > best_base_score:
                best_base_score = base_score
                best_swap = swap
        print(f"DEBUG: 选择最高基础分({best_base_score})的交换")
        return best_swap

    # ===================== 优先级0：双龙与双龙相邻时，优先使用双龙与普通食材交换 =====================
    # 先检查是否有相邻的双龙
    adjacent_dragons = []
    for i, d1 in enumerate(dragons):
        for j, d2 in enumerate(dragons):
            if i < j and abs(d1[0] - d2[0]) + abs(d1[1] - d2[1]) == 1:
                adjacent_dragons.append((d1, d2))

    if adjacent_dragons:
        # 有相邻的双龙，寻找双龙与普通食材的交换，且不破坏双龙相邻布局
        dragon_ingredient_candidates = []

        for dragon in dragons:
            # 对每个双龙，检查与普通食材的交换
            for di, dj in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # 四个方向
                ni, nj = dragon[0] + di, dragon[1] + dj
                if 0 <= ni < BOARD_SIZE and 0 <= nj < BOARD_SIZE and board[ni][nj] in common_ingredients:
                    swap = (dragon, (ni, nj))

                    # 模拟交换
                    new_board, score, base_score = simulate_swap(board, swap)

                    # 检查交换后是否仍有相邻的双龙
                    new_dragons = [(i, j) for i, j in product(range(BOARD_SIZE), repeat=2) if
                                   new_board[i][j] == "双龙戏珠"]
                    still_has_adjacent_dragons = False

                    for i, d1 in enumerate(new_dragons):
                        for j, d2 in enumerate(new_dragons):
                            if i < j and abs(d1[0] - d2[0]) + abs(d1[1] - d2[1]) == 1:
                                still_has_adjacent_dragons = True
                                break
                        if still_has_adjacent_dragons:
                            break

                    # 注意：使用双龙与普通食材交换会消耗掉一个双龙，因此需要确保消除食材数量足够多(>=8)才值得
                    # 如果交换后仍有相邻的双龙，并且消除食材数量大于等于8个，加入候选
                    if still_has_adjacent_dragons and base_score >= 15:
                        dragon_ingredient_candidates.append((swap, base_score))

        # 如果找到符合条件的交换，选择消除食材最多的
        if dragon_ingredient_candidates:
            # 按消除食材数量排序
            dragon_ingredient_candidates.sort(key=lambda x: x[1], reverse=True)
            best_swap = dragon_ingredient_candidates[0][0]
            print(
                f"DEBUG: 找到双龙与普通食材交换，且不破坏双龙相邻布局，基础分为{dragon_ingredient_candidates[0][1]}")
            return best_swap

        # 如果没有找到合适的双龙与普通食材交换（即没有满足条件：保持双龙相邻且消除>=8个食材），
        # 则直接使用双龙与双龙交换，这样可以消除全屏所有格子
        dragon_pairs = []
        for d1, d2 in adjacent_dragons:
            dragon_pairs.append((d1, d2))

        if dragon_pairs:
            best_swap = select_best_swap(dragon_pairs)
            print(f"DEBUG: 未找到合适的双龙与普通食材交换(保持双龙相邻且消除>=8个食材)，直接使用双龙与双龙交换")
            return best_swap

    # ===================== 优先级0.5：双龙与凤凰相邻时，寻找能形成双龙相邻的交换 =====================
    # 检查是否有双龙与凤凰相邻
    dragon_phoenix_adjacent = []
    for d in dragons:
        for p in phoenixes:
            if abs(d[0] - p[0]) + abs(d[1] - p[1]) == 1:
                dragon_phoenix_adjacent.append((d, p))

    if dragon_phoenix_adjacent:
        # 有双龙与凤凰相邻，寻找所有可行交换，查找使用后能形成双龙与双龙相邻的交换
        forming_dragon_adjacent_candidates = []

        # 1. 首先检查一步交换能直接形成双龙相邻的情况
        for swap in swaps:
            # 模拟交换
            new_board, score, base_score = simulate_swap(board, swap)

            # 检查交换后是否有相邻的双龙
            new_dragons = [(i, j) for i, j in product(range(BOARD_SIZE), repeat=2) if new_board[i][j] == "双龙戏珠"]
            has_adjacent_dragons = False

            for i, d1 in enumerate(new_dragons):
                for j, d2 in enumerate(new_dragons):
                    if i < j and abs(d1[0] - d2[0]) + abs(d1[1] - d2[1]) == 1:
                        has_adjacent_dragons = True
                        break
                if has_adjacent_dragons:
                    break

            # 如果交换后有相邻的双龙，加入候选
            if has_adjacent_dragons:
                forming_dragon_adjacent_candidates.append(swap)

        # 如果找到了能直接形成双龙相邻的交换，选择消除食材最多的
        if forming_dragon_adjacent_candidates:
            best_swap = select_best_swap(forming_dragon_adjacent_candidates)
            print(f"DEBUG: 找到能直接形成双龙相邻的交换（双龙与凤凰相邻情况下）")
            return best_swap

        # 2. 如果没有找到直接形成双龙相邻的交换，尝试两步前瞻
        two_step_candidates = []
        print(f"DEBUG: 双龙与凤凰相邻情况下，开始两步前瞻搜索")

        # 检查所有可能的第一步交换
        for swap1 in swaps:  # 移除搜索范围限制，考虑所有可能的交换
            # 模拟第一步交换
            board1, score1, base_score1 = simulate_swap(board, swap1)

            # 检查第一步交换后是否已经有双龙相邻（如果有，应该已经在前面被处理）
            new_dragons1 = [(i, j) for i, j in product(range(BOARD_SIZE), repeat=2) if board1[i][j] == "双龙戏珠"]
            has_adjacent_dragons1 = False
            for i, d1 in enumerate(new_dragons1):
                for j, d2 in enumerate(new_dragons1):
                    if i < j and abs(d1[0] - d2[0]) + abs(d1[1] - d2[1]) == 1:
                        has_adjacent_dragons1 = True
                        break
                if has_adjacent_dragons1:
                    break

            # 如果第一步交换已经形成双龙相邻，跳过（应该已经在前面被处理）
            if has_adjacent_dragons1:
                continue

            # 生成第一步交换后的所有可能第二步交换
            next_swaps = [s for s in generate_swaps() if is_valid_swap(board1, s)]

            # 检查每个可能的第二步交换
            for swap2 in next_swaps:  # 移除搜索范围限制，考虑所有可能的第二步交换
                # 模拟第二步交换
                board2, score2, base_score2 = simulate_swap(board1, swap2)
                new_dragons2 = [(i, j) for i, j in product(range(BOARD_SIZE), repeat=2) if board2[i][j] == "双龙戏珠"]

                # 检查第二步交换后是否有双龙相邻
                has_adjacent_dragons2 = False
                for i, d1 in enumerate(new_dragons2):
                    for j, d2 in enumerate(new_dragons2):
                        if i < j and abs(d1[0] - d2[0]) + abs(d1[1] - d2[1]) == 1:
                            has_adjacent_dragons2 = True
                            break
                    if has_adjacent_dragons2:
                        break

                if has_adjacent_dragons2:
                    two_step_candidates.append(swap1)
                    print(f"DEBUG: 找到两步前瞻可形成双龙相邻的交换，基础分:{base_score1}")
                    break  # 只需要找到一个能形成双龙相邻的第二步交换即可

            # 移除候选数量限制
            # if len(two_step_candidates) >= 3:  # 如果已经找到足够的候选，跳出循环
            #     break

        # 如果找到了两步前瞻的交换，选择消除食材最多的
        if two_step_candidates:
            best_swap = select_best_swap(two_step_candidates)
            print(f"DEBUG: 找到两步前瞻可形成双龙相邻的交换，选择基础分最高的（双龙与凤凰相邻情况下）")
            return best_swap

        # 3. 如果没有找到能形成双龙相邻的交换，执行双龙与凤凰交换
        if dragon_phoenix_adjacent:
            best_swap = select_best_swap(dragon_phoenix_adjacent)
            print(f"DEBUG: 未找到能形成双龙相邻的交换，执行双龙与凤凰交换")
            return best_swap

    # ===================== 优先级1：查找所有可行交换，能生成双龙与双龙相邻的交换 =====================
    # 收集所有能生成双龙与双龙相邻的交换
    dragon_adjacent_candidates = []

    # 检查所有可能的交换
    for swap in swaps:
        (i1, j1), (i2, j2) = swap
        # 模拟交换
        new_board, score, base_score = simulate_swap(board, swap)
        new_dragons = [(i, j) for i, j in product(range(BOARD_SIZE), repeat=2) if new_board[i][j] == "双龙戏珠"]

        # 检查是否有双龙相邻
        has_adjacent_dragons = False
        for i, d1 in enumerate(new_dragons):
            for j, d2 in enumerate(new_dragons):
                if i < j and abs(d1[0] - d2[0]) + abs(d1[1] - d2[1]) == 1:
                    has_adjacent_dragons = True
                    break
            if has_adjacent_dragons:
                break

        if has_adjacent_dragons:
            dragon_adjacent_candidates.append(swap)

    # 如果找到了能生成双龙相邻的交换，选择最佳的
    if dragon_adjacent_candidates:
        best_swap = select_best_swap(dragon_adjacent_candidates)
        print(f"DEBUG: 找到能生成双龙相邻的交换，选择基础分最高的")
        return best_swap

    # ===================== 优先级2：查找所有可行交换，执行两次交换能形成双龙+双龙相邻的交换 =====================
    # 收集所有两步前瞻能形成双龙相邻的交换
    two_step_candidates = []
    print(f"DEBUG: 当前有{len(dragons)}个双龙，{len(phoenixes)}个凤凰，开始两步前瞻搜索")

    # 检查所有可能的第一步交换
    for swap1 in swaps:  # 移除搜索范围限制
        # 模拟第一步交换
        board1, score1, base_score1 = simulate_swap(board, swap1)

        # 检查第一步交换后是否已经有双龙相邻（如果有，应该已经在优先级1被处理）
        new_dragons1 = [(i, j) for i, j in product(range(BOARD_SIZE), repeat=2) if board1[i][j] == "双龙戏珠"]
        has_adjacent_dragons1 = False
        for i, d1 in enumerate(new_dragons1):
            for j, d2 in enumerate(new_dragons1):
                if i < j and abs(d1[0] - d2[0]) + abs(d1[1] - d2[1]) == 1:
                    has_adjacent_dragons1 = True
                    break
            if has_adjacent_dragons1:
                break

        # 如果第一步交换已经形成双龙相邻，跳过（应该已经在优先级1被处理）
        if has_adjacent_dragons1:
            continue

        # 生成第一步交换后的所有可能第二步交换
        next_swaps = [s for s in generate_swaps() if is_valid_swap(board1, s)]

        # 检查每个可能的第二步交换
        for swap2 in next_swaps:  # 移除搜索范围限制
            # 模拟第二步交换
            board2, score2, base_score2 = simulate_swap(board1, swap2)
            new_dragons2 = [(i, j) for i, j in product(range(BOARD_SIZE), repeat=2) if board2[i][j] == "双龙戏珠"]

            # 检查第二步交换后是否有双龙相邻
            has_adjacent_dragons2 = False
            for i, d1 in enumerate(new_dragons2):
                for j, d2 in enumerate(new_dragons2):
                    if i < j and abs(d1[0] - d2[0]) + abs(d1[1] - d2[1]) == 1:
                        has_adjacent_dragons2 = True
                        break
                    if has_adjacent_dragons2:
                        break

                if has_adjacent_dragons2:
                    two_step_candidates.append(swap1)
                    print(f"DEBUG: 找到两步前瞻可形成双龙相邻的交换，基础分:{base_score1}")
                    break  # 只需要找到一个能形成双龙相邻的第二步交换即可

        # 移除候选数量限制
        # if two_step_candidates:  # 如果已经找到一个候选，跳出循环
        #     break

    # 如果找到了两步前瞻的交换，选择最佳的
    if two_step_candidates:
        best_swap = select_best_swap(two_step_candidates)
        print(f"DEBUG: 找到两步前瞻可形成双龙相邻的交换，选择基础分最高的")
        return best_swap

    # ===================== 优先级3：相邻双龙与双龙直接交换 =====================
    # 收集所有双龙与双龙相邻的交换
    dragon_pairs = []
    for i, d1 in enumerate(dragons):
        for j, d2 in enumerate(dragons):
            if i < j and abs(d1[0] - d2[0]) + abs(d1[1] - d2[1]) == 1:
                dragon_pairs.append((d1, d2))

    if dragon_pairs:
        # 直接返回双龙与双龙交换，因为这是高优先级
        # 如果有多对相邻双龙，选择消除食材最多的
        best_swap = select_best_swap(dragon_pairs)
        print(f"DEBUG: 找到相邻双龙与双龙交换，选择基础分最高的")
        return best_swap

    # ===================== 优先级4：双龙与凤凰直接交换 =====================
    # 收集所有双龙与凤凰相邻的交换
    dragon_phoenix_pairs = []
    for d in dragons:
        for p in phoenixes:
            if abs(d[0] - p[0]) + abs(d[1] - p[1]) == 1:
                dragon_phoenix_pairs.append((d, p))

    # 如果找到了双龙与凤凰相邻的交换
    if dragon_phoenix_pairs:
        # 选择消除食材最多的双龙与凤凰交换
        best_swap = select_best_swap(dragon_phoenix_pairs)
        print(f"DEBUG: 找到双龙与凤凰直接交换，选择基础分最高的")
        return best_swap

    # ===================== 优先级5：查找所有交换后能形成双龙与凤凰相邻的交换 =====================
    # 收集所有交换后能形成双龙与凤凰相邻的交换
    dragon_phoenix_adjacent_candidates = []

    # 检查所有可能的交换
    for swap in swaps:
        (i1, j1), (i2, j2) = swap
        # 模拟交换
        new_board, score, base_score = simulate_swap(board, swap)
        new_dragons = [(i, j) for i, j in product(range(BOARD_SIZE), repeat=2) if new_board[i][j] == "双龙戏珠"]
        new_phoenixes = [(i, j) for i, j in product(range(BOARD_SIZE), repeat=2) if new_board[i][j] == "凤凰振翅"]

        # 检查是否有双龙与凤凰相邻
        has_dragon_phoenix_adjacent = False
        for d in new_dragons:
            for p in new_phoenixes:
                if abs(d[0] - p[0]) + abs(d[1] - p[1]) == 1:
                    has_dragon_phoenix_adjacent = True
                    break
            if has_dragon_phoenix_adjacent:
                break

        if has_dragon_phoenix_adjacent:
            dragon_phoenix_adjacent_candidates.append(swap)

    # 如果找到了能形成双龙与凤凰相邻的交换，选择最佳的
    if dragon_phoenix_adjacent_candidates:
        best_swap = select_best_swap(dragon_phoenix_adjacent_candidates)
        print(f"DEBUG: 找到能形成双龙与凤凰相邻的交换，选择基础分最高的")
        return best_swap

    # ===================== 优先级5.5：查找所有可行交换寻找能生成双龙的交换 =====================
    # 收集所有能直接生成双龙的交换
    direct_dragon_candidates = []

    # 检查所有可能的交换
    for swap in swaps:
        (i1, j1), (i2, j2) = swap
        # 模拟交换
        new_board, score, base_score = simulate_swap(board, swap)

        # 检查新棋盘中是否有新的双龙生成
        new_dragons = [(i, j) for i, j in product(range(BOARD_SIZE), repeat=2) if new_board[i][j] == "双龙戏珠"]

        # 计算新生成的双龙数量
        # 如果交换中包含双龙，需要考虑消耗的双龙
        consumed_dragons = 0
        if board[i1][j1] == "双龙戏珠" or board[i2][j2] == "双龙戏珠":
            consumed_dragons = 1

        new_dragon_count = len(new_dragons) - len(dragons) + consumed_dragons

        # 如果生成了新的双龙
        if new_dragon_count > 0:
            direct_dragon_candidates.append((swap, new_dragon_count))

    # 如果找到了能直接生成双龙的交换，按生成的双龙数量排序，选择最佳的
    if direct_dragon_candidates:
        # 按生成的双龙数量排序
        direct_dragon_candidates.sort(key=lambda x: x[1], reverse=True)
        best_dragon_count = direct_dragon_candidates[0][1]

        # 选择生成最多双龙的交换中，消除食材最多的
        best_candidates = [swap for swap, count in direct_dragon_candidates if count == best_dragon_count]
        best_swap = select_best_swap(best_candidates)

        print(f"DEBUG: 找到能直接生成{best_dragon_count}个双龙的交换，选择基础分最高的")
        return best_swap

    # ===================== 优先级6：查找所有两步交换能形成双龙+凤凰相邻的交换 =====================
    # 收集所有两步前瞻能形成双龙与凤凰相邻的交换
    two_step_dragon_phoenix_candidates = []
    print(f"DEBUG: 开始两步前瞻搜索形成双龙与凤凰相邻的交换")

    # 检查所有可能的第一步交换
    for swap1 in swaps:  # 移除搜索范围限制，考虑所有可能的交换
        # 模拟第一步交换
        board1, score1, base_score1 = simulate_swap(board, swap1)

        # 检查第一步交换后是否已经有双龙与凤凰相邻（如果有，应该已经在优先级5被处理）
        new_dragons1 = [(i, j) for i, j in product(range(BOARD_SIZE), repeat=2) if board1[i][j] == "双龙戏珠"]
        new_phoenixes1 = [(i, j) for i, j in product(range(BOARD_SIZE), repeat=2) if board1[i][j] == "凤凰振翅"]

        has_dragon_phoenix_adjacent1 = False
        for d in new_dragons1:
            for p in new_phoenixes1:
                if abs(d[0] - p[0]) + abs(d[1] - p[1]) == 1:
                    has_dragon_phoenix_adjacent1 = True
                    break
            if has_dragon_phoenix_adjacent1:
                break

        # 如果第一步交换已经形成双龙与凤凰相邻，跳过（应该已经在优先级5被处理）
        if has_dragon_phoenix_adjacent1:
            continue

        # 生成第一步交换后的所有可能第二步交换
        next_swaps = [s for s in generate_swaps() if is_valid_swap(board1, s)]

        # 检查每个可能的第二步交换
        for swap2 in next_swaps:  # 移除搜索范围限制，考虑所有可能的第二步交换
            # 模拟第二步交换
            board2, score2, base_score2 = simulate_swap(board1, swap2)
            new_dragons2 = [(i, j) for i, j in product(range(BOARD_SIZE), repeat=2) if board2[i][j] == "双龙戏珠"]
            new_phoenixes2 = [(i, j) for i, j in product(range(BOARD_SIZE), repeat=2) if board2[i][j] == "凤凰振翅"]

            # 检查第二步交换后是否有双龙与凤凰相邻
            has_dragon_phoenix_adjacent2 = False
            for d in new_dragons2:
                for p in new_phoenixes2:
                    if abs(d[0] - p[0]) + abs(d[1] - p[1]) == 1:
                        has_dragon_phoenix_adjacent2 = True
                        break
                if has_dragon_phoenix_adjacent2:
                    break

            if has_dragon_phoenix_adjacent2:
                two_step_dragon_phoenix_candidates.append(swap1)
                print(f"DEBUG: 找到两步前瞻可形成双龙与凤凰相邻的交换，基础分:{base_score1}")
                break  # 只需要找到一个能形成双龙与凤凰相邻的第二步交换即可

        # 移除候选数量限制
        # if len(two_step_dragon_phoenix_candidates) >= 3:  # 如果已经找到足够的候选，跳出循环
        #     break

    # 如果找到了两步前瞻能形成双龙与凤凰相邻的交换，选择最佳的
    if two_step_dragon_phoenix_candidates:
        best_swap = select_best_swap(two_step_dragon_phoenix_candidates)
        print(f"DEBUG: 找到两步前瞻可形成双龙与凤凰相邻的交换，选择基础分最高的")
        return best_swap

    # ===================== 优先级6.1：模拟两步所有可行交换寻找能生成双龙的交换 =====================
    # 收集所有两步前瞻能生成双龙的交换
    two_step_dragon_candidates = []
    print(f"DEBUG: 开始两步前瞻搜索生成双龙的交换")

    # 检查所有可能的第一步交换
    for swap1 in swaps:  # 移除搜索范围限制，考虑所有可能的交换
        # 模拟第一步交换
        board1, score1, base_score1 = simulate_swap(board, swap1)

        # 检查第一步交换后是否已经生成了双龙（如果有，应该已经在优先级5.5被处理）
        new_dragons1 = [(i, j) for i, j in product(range(BOARD_SIZE), repeat=2) if board1[i][j] == "双龙戏珠"]

        # 计算第一步交换后新生成的双龙数量
        consumed_dragons1 = 0
        (i1, j1), (i2, j2) = swap1
        if board[i1][j1] == "双龙戏珠" or board[i2][j2] == "双龙戏珠":
            consumed_dragons1 = 1

        new_dragon_count1 = len(new_dragons1) - len(dragons) + consumed_dragons1

        # 如果第一步已经生成了双龙，跳过（应该已经在优先级5.5被处理）
        if new_dragon_count1 > 0:
            continue

        # 生成第一步交换后的所有可能第二步交换
        next_swaps = [s for s in generate_swaps() if is_valid_swap(board1, s)]

        max_new_dragons = 0  # 记录第二步能生成的最大双龙数量

        # 检查每个可能的第二步交换
        for swap2 in next_swaps:  # 移除搜索范围限制，考虑所有可能的第二步交换
            # 模拟第二步交换
            board2, score2, base_score2 = simulate_swap(board1, swap2)
            new_dragons2 = [(i, j) for i, j in product(range(BOARD_SIZE), repeat=2) if board2[i][j] == "双龙戏珠"]

            # 计算第二步交换后新生成的双龙数量（相对于第一步）
            consumed_dragons2 = 0
            (i1, j1), (i2, j2) = swap2
            if board1[i1][j1] == "双龙戏珠" or board1[i2][j2] == "双龙戏珠":
                consumed_dragons2 = 1

            new_dragon_count2 = len(new_dragons2) - len(new_dragons1) + consumed_dragons2

            # 更新最大双龙数量
            if new_dragon_count2 > max_new_dragons:
                max_new_dragons = new_dragon_count2

        # 如果通过两步能生成双龙，将第一步交换和能生成的最大双龙数量加入候选
        if max_new_dragons > 0:
            two_step_dragon_candidates.append((swap1, max_new_dragons, base_score1))
            print(f"DEBUG: 找到两步前瞻可生成{max_new_dragons}个双龙的交换，基础分:{base_score1}")

    # 如果找到了两步前瞻能生成双龙的交换，按生成的双龙数量排序，选择最佳的
    if two_step_dragon_candidates:
        # 按生成的双龙数量排序，如果数量相同则按基础分排序
        two_step_dragon_candidates.sort(key=lambda x: (x[1], x[2]), reverse=True)
        best_dragon_count = two_step_dragon_candidates[0][1]

        # 选择生成最多双龙的交换中，消除食材最多的
        best_candidates = [swap for swap, count, _ in two_step_dragon_candidates if count == best_dragon_count]
        best_swap = select_best_swap(best_candidates)

        print(f"DEBUG: 找到两步前瞻可生成{best_dragon_count}个双龙的交换，选择基础分最高的")
        return best_swap

    # ===================== 优先级6.2：模拟三步所有可行交换寻找能生成双龙的交换 =====================
    # 收集所有三步前瞻能生成双龙的交换
    three_step_dragon_candidates = []
    print(f"DEBUG: 开始三步前瞻搜索生成双龙的交换")

    # 检查所有可能的第一步交换
    for swap1 in swaps:  # 移除搜索范围，避免计算量过大
        # 模拟第一步交换
        board1, score1, base_score1 = simulate_swap(board, swap1)

        # 检查第一步交换后是否已经生成了双龙（如果有，应该已经在优先级6被处理）
        new_dragons1 = [(i, j) for i, j in product(range(BOARD_SIZE), repeat=2) if board1[i][j] == "双龙戏珠"]

        # 计算第一步交换后新生成的双龙数量
        consumed_dragons1 = 0
        (i1, j1), (i2, j2) = swap1
        if board[i1][j1] == "双龙戏珠" or board[i2][j2] == "双龙戏珠":
            consumed_dragons1 = 1

        new_dragon_count1 = len(new_dragons1) - len(dragons) + consumed_dragons1

        # 如果第一步已经生成了双龙，跳过（应该已经在优先级6被处理）
        if new_dragon_count1 > 0:
            continue

        # 生成第一步交换后的所有可能第二步交换
        next_swaps1 = [s for s in generate_swaps() if is_valid_swap(board1, s)]

        max_dragons_in_three_steps = 0  # 记录三步能生成的最大双龙数量

        # 检查每个可能的第二步交换
        for swap2 in next_swaps1:  # 限制搜索范围
            # 模拟第二步交换
            board2, score2, base_score2 = simulate_swap(board1, swap2)
            new_dragons2 = [(i, j) for i, j in product(range(BOARD_SIZE), repeat=2) if board2[i][j] == "双龙戏珠"]

            # 计算第二步交换后新生成的双龙数量（相对于第一步）
            consumed_dragons2 = 0
            (i1, j1), (i2, j2) = swap2
            if board1[i1][j1] == "双龙戏珠" or board1[i2][j2] == "双龙戏珠":
                consumed_dragons2 = 1

            new_dragon_count2 = len(new_dragons2) - len(new_dragons1) + consumed_dragons2

            # 如果第二步已经生成了双龙，记录并继续检查其他第二步交换
            if new_dragon_count2 > max_dragons_in_three_steps:
                max_dragons_in_three_steps = new_dragon_count2

            # 生成第二步交换后的所有可能第三步交换
            next_swaps2 = [s for s in generate_swaps() if is_valid_swap(board2, s)]

            # 检查每个可能的第三步交换
            for swap3 in next_swaps2:  # 限制搜索范围
                # 模拟第三步交换
                board3, score3, base_score3 = simulate_swap(board2, swap3)
                new_dragons3 = [(i, j) for i, j in product(range(BOARD_SIZE), repeat=2) if board3[i][j] == "双龙戏珠"]

                # 计算第三步交换后新生成的双龙数量（相对于第二步）
                consumed_dragons3 = 0
                (i1, j1), (i2, j2) = swap3
                if board2[i1][j1] == "双龙戏珠" or board2[i2][j2] == "双龙戏珠":
                    consumed_dragons3 = 1

                new_dragon_count3 = len(new_dragons3) - len(new_dragons2) + consumed_dragons3

                # 更新最大双龙数量
                total_new_dragons = new_dragon_count2 + new_dragon_count3
                if total_new_dragons > max_dragons_in_three_steps:
                    max_dragons_in_three_steps = total_new_dragons

        # 如果通过三步能生成双龙，将第一步交换和能生成的最大双龙数量加入候选
        if max_dragons_in_three_steps > 0:
            three_step_dragon_candidates.append((swap1, max_dragons_in_three_steps, base_score1))
            print(f"DEBUG: 找到三步前瞻可生成{max_dragons_in_three_steps}个双龙的交换，基础分:{base_score1}")

    # 如果找到了三步前瞻能生成双龙的交换，按生成的双龙数量排序，选择最佳的
    if three_step_dragon_candidates:
        # 按生成的双龙数量排序，如果数量相同则按基础分排序
        three_step_dragon_candidates.sort(key=lambda x: (x[1], x[2]), reverse=True)
        best_dragon_count = three_step_dragon_candidates[0][1]

        # 选择生成最多双龙的交换中，消除食材最多的
        best_candidates = [swap for swap, count, _ in three_step_dragon_candidates if count == best_dragon_count]
        best_swap = select_best_swap(best_candidates)

        print(f"DEBUG: 找到三步前瞻可生成{best_dragon_count}个双龙的交换，选择基础分最高的")
        return best_swap

    # ===================== 优先级7：查找所有交换寻找基础分最高的交换 =====================
    # 收集所有交换并按基础分排序
    all_swaps_with_score = []
    for swap in swaps:
        _, _, base_score = simulate_swap(board, swap)
        all_swaps_with_score.append((swap, base_score))

    # 按基础分排序
    all_swaps_with_score.sort(key=lambda x: x[1], reverse=True)

    # 如果有基础分大于0的交换
    if all_swaps_with_score and all_swaps_with_score[0][1] > 0:
        best_swap = all_swaps_with_score[0][0]
        print(f"DEBUG: 选择基础分最高的交换，基础分:{all_swaps_with_score[0][1]}")
        return best_swap

    # ===================== 优先级8：评分最高的交换 =====================
    # 收集所有有效交换并按评分排序
    all_valid_swaps = []
    for swap in swaps:
        new_board, score, base_score = simulate_swap(board, swap)
        # 使用evaluate_state函数评估交换后的局面价值
        state_value = evaluate_state(new_board, base_score)
        all_valid_swaps.append((swap, state_value))

    # 按评分排序
    all_valid_swaps.sort(key=lambda x: x[1], reverse=True)

    # 取评分最高的交换
    if all_valid_swaps:
        best_swap = all_valid_swaps[0][0]
        print(f"DEBUG: 选择评分最高的交换")
        return best_swap

    # 如果没有找到任何有效交换
    return None


def execute_swap(board, swap):
    """执行交换操作并返回是否成功执行"""
    (i1, j1), (i2, j2) = swap
    x1 = BOARD_ORIGIN[0] + j1 * CELL_SIZE + CELL_SIZE // 2
    y1 = BOARD_ORIGIN[1] + i1 * CELL_SIZE + CELL_SIZE // 2
    x2 = BOARD_ORIGIN[0] + j2 * CELL_SIZE + CELL_SIZE // 2
    y2 = BOARD_ORIGIN[1] + i2 * CELL_SIZE + CELL_SIZE // 2
    try:
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
        subprocess.run(
            [adb_path, 'shell', 'input', 'swipe', str(x1), str(y1), str(x2), str(y2), '250'],
            check=True, timeout=3, startupinfo=startupinfo
        )
        print(f"[执行] 成功发送ADB命令：({i1},{j1}) -> ({i2},{j2})")
        # 增加等待时间到0.5秒，确保填充动画完毕
        time.sleep(1)
        return True
    except Exception as e:
        print(f"[错误] 执行交换时发生异常: {str(e)}")
        return False


# 棋盘可视化输出
def print_board(board):
    for i in range(BOARD_SIZE):
        print(f"{i}: " + ' '.join(board[i]))


def print_board_text(board, title="棋盘状态"):
    """以文本格式打印棋盘，使用不同符号表示不同食材"""
    # 只在标题包含"当前棋盘状态"或"交换后"时输出
    if "当前棋盘状态" not in title and "交换后" not in title:
        return

    # 简化符号用于纯文本输出
    text_symbols = {
        "香菇": "菇",
        "蔬菜": "菜",
        "鸡腿": "腿",
        "蛋糕": "糕",
        "红肉": "肉",
        "鸡蛋": "蛋",
        "凤凰振翅": "凤",
        "双龙戏珠": "龙",
        None: "  "
    }

    print(f"\n===== {title} =====")
    print("  " + " ".join([f"{j}" for j in range(BOARD_SIZE)]))
    print("  " + "-" * (BOARD_SIZE * 2 - 1))

    for i in range(BOARD_SIZE):
        row = []
        for j in range(BOARD_SIZE):
            row.append(text_symbols.get(board[i][j], "??"))
        print(f"{i}|" + " ".join(row))
    print("")


def boards_equal(board1, board2):
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board1[i][j] != board2[i][j]:
                return False
    return True


def check_board_stable(board):
    """检查棋盘是否稳定（没有空位）
    
    注意：此函数是为了兼容 main_loop 函数而保留的全局函数
    GameInstance 类中有同名的实例方法
    """
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] is None:
                return False
    return True


def wait_for_stable_board():
    """等待棋盘稳定后再进行下一步操作
    
    注意：此函数是为了兼容 main_loop 函数而保留的全局函数
    GameInstance 类中有同名的实例方法
    """
    max_attempts = 5
    for attempt in range(max_attempts):
        # 截取第一张图
        img1 = take_screenshot()
        if img1 is None:
            time.sleep(1)
            continue

        # 等待一秒后截取第二张图
        time.sleep(1)
        img2 = take_screenshot()
        if img2 is None:
            time.sleep(1)
            continue

        # 检测两次截图的棋盘状态
        board1 = detect_board(img1, model)
        board2 = detect_board(img2, model)

        # 检查两次截图是否相同且棋盘是否稳定（没有空位）
        if boards_equal(board1, board2) and check_board_stable(board2):
            return board2  # 返回稳定的棋盘状态

        # 如果不稳定，等待一秒后重试
        time.sleep(1)

    # 达到最大尝试次数后，返回最后一次检测的棋盘
    return board2


# 修改main_loop函数来适配GUI和步数限制
def main_loop(root):
    global steps_used, total_score, total_base_score, running, paused, TARGET_STEPS, adb_path

    # 记录上一次的棋盘状态，用于检测棋盘是否变化
    last_board = None
    unchanged_count = 0

    # 重定向print输出到GUI日志
    import builtins
    original_print = builtins.print

    def custom_print(*args, **kwargs):
        # 保留原始print功能
        original_print(*args, **kwargs)
        # 将输出添加到GUI日志
        message = " ".join(str(arg) for arg in args)
        if not message.startswith("DEBUG:"):  # 不记录DEBUG信息
            root.add_log(message)

    # 替换全局print函数
    builtins.print = custom_print

    try:
        while running:  # 移除步数限制，使循环持续运行
            if paused:
                time.sleep(0.2)
                continue

            # 检查是否达到目标步数
            if steps_used >= TARGET_STEPS:
                root.add_log(f"\n游戏结束！总得分: {total_base_score}分")
                messagebox.showinfo("游戏结束", f"已完成{TARGET_STEPS}步\n总得分: {total_base_score}分")
                # 游戏结束后自动暂停，但不退出循环
                paused = True
                continue

            # 每步都获取最新棋盘状态
            root.add_log("获取当前棋盘状态...")
            img = None
            for _ in range(3):
                img = take_screenshot()
                if img is not None:
                    break
                time.sleep(1)

            if img is None:
                root.add_log("截图失败，跳过本轮")
                continue

            # 分析当前棋盘
            board = detect_board(img, model)
            draw_debug_image(img, board)

            # 检查棋盘是否与上次相同（可能是ADB执行失败或游戏卡住）
            if last_board and boards_equal(board, last_board):
                unchanged_count += 1
                root.add_log(f"棋盘未变化，计数: {unchanged_count}/3")
                if unchanged_count >= 3:
                    root.add_log("连续3次棋盘未变化，可能是游戏卡住，跳过本轮")
                    unchanged_count = 0
                    continue
            else:
                unchanged_count = 0

            # 分析当前棋盘食材分布
            food_dist = get_board_distribution(board)
            food_dist_str = ", ".join([f"{food}:{round(prob * 100)}%" for food, prob in food_dist.items()])
            root.add_log(f"食材分布: {food_dist_str}")

            # 更新上一次的棋盘状态
            last_board = [row.copy() for row in board]

            # 分析当前局面
            dragons = sum(1 for i in range(BOARD_SIZE) for j in range(BOARD_SIZE) if board[i][j] == "双龙戏珠")
            phoenixes = sum(1 for i in range(BOARD_SIZE) for j in range(BOARD_SIZE) if board[i][j] == "凤凰振翅")
            remaining_steps = TARGET_STEPS - steps_used

            root.add_log(f"局面: 双龙:{dragons}, 凤凰:{phoenixes}, 剩余:{remaining_steps}步")
            root.add_log("基于当前布局重新模拟查找最佳交换...")

            # 每一步都基于最新布局查找最佳交换
            best_swap = get_best_move(board)
            if best_swap:
                (i1, j1), (i2, j2) = best_swap
                if is_valid_swap(board, best_swap):
                    # 只输出交换的食材信息
                    root.add_log(f"执行交换: {board[i1][j1]} <-> {board[i2][j2]}")

                    # 模拟计算预期收益
                    new_board, score, base_score = simulate_swap(board, best_swap)

                    # 尝试执行交换
                    max_retry = 5
                    retry_count = 0
                    success = False

                    while retry_count < max_retry:
                        # 执行交换操作
                        swap_success = execute_swap(board, best_swap)
                        if not swap_success:
                            retry_count += 1
                            root.add_log(f"交换失败，重试中 ({retry_count}/{max_retry})")
                            time.sleep(0.5)
                            continue

                        # 等待动画完成
                        time.sleep(1.0)

                        # 等待棋盘稳定后再进行下一步操作
                        root.add_log("等待棋盘稳定...")
                        stable_board = wait_for_stable_board()
                        if stable_board is not None:
                            board_after = stable_board
                        else:
                            # 如果等待稳定失败，尝试再次截图
                            img_after = take_screenshot()
                            if img_after is None:
                                retry_count += 1
                                root.add_log(f"交换后截图失败 ({retry_count}/{max_retry})")
                                time.sleep(0.5)
                                continue
                            board_after = detect_board(img_after, model)

                        # 比较交换前后的棋盘
                        if not boards_equal(board, board_after):
                            # 棋盘已变化，交换成功
                            root.add_log(f"消除得分: +{base_score}分")
                            total_score += score
                            total_base_score += base_score
                            steps_used += 1  # 只有棋盘变化时才计步
                            success = True
                            break
                        else:
                            # 棋盘未变化，可能交换无效或ADB执行失败
                            retry_count += 1
                            root.add_log(f"棋盘未变化，重试中 ({retry_count}/{max_retry})")
                            time.sleep(0.8)

                    # 超过最大重试次数仍未成功
                    if not success and retry_count >= max_retry:
                        root.add_log("多次重试后棋盘仍未变化，本次交换失败")

                        # 尝试最后一次
                        success = execute_swap(board, best_swap)
                        time.sleep(1.5)

                        # 截取新画面检查
                        img_after = take_screenshot()
                        if img_after is not None:
                            board_after = detect_board(img_after, model)
                            if not boards_equal(board, board_after):
                                root.add_log(f"再次执行成功，得分: +{base_score}分")
                                total_score += score
                                total_base_score += base_score
                                steps_used += 1
            else:
                root.add_log("未找到有效交换，跳过本轮")

            # 清理调试文件
            for f in os.listdir(DEBUG_DIR):
                if f.endswith(('.png', '.jpg')) and f != 'debug.jpg':
                    os.remove(os.path.join(DEBUG_DIR, f))

            # 防止循环过快
            time.sleep(0.2)
    finally:
        # 确保恢复原始print函数
        builtins.print = original_print


def is_L_T_shape(match, board):
    """判断match是否为L/T形（大于等于5个，且横竖交叉，且每个格子只算一次）"""
    if len(match) < 5:
        return False

    # 统计所有行和列
    row_set = set()
    col_set = set()
    for i, j in match:
        row_set.add(i)
        col_set.add(j)

    # 必须横竖都跨越
    if len(row_set) < 2 or len(col_set) < 2:
        return False

    # 检查是否有交点
    pos_set = set(match)

    # 构建棋盘表示
    grid = {}
    for i, j in pos_set:
        grid[(i, j)] = board[i][j]

    # 检查L形状（3x3）- 4种方向
    l_shapes = [
        # 右下L形
        [(0, 0), (0, 1), (0, 2), (1, 0), (2, 0)],
        # 左下L形
        [(0, 0), (0, -1), (0, -2), (1, 0), (2, 0)],
        # 右上L形
        [(0, 0), (0, 1), (0, 2), (-1, 0), (-2, 0)],
        # 左上L形
        [(0, 0), (0, -1), (0, -2), (-1, 0), (-2, 0)]
    ]

    # 检查T形状（3x3）- 4种方向
    t_shapes = [
        # T形（横杠在上）
        [(0, 0), (-1, 0), (0, -1), (0, 1)],
        # T形（横杠在下）
        [(0, 0), (1, 0), (0, -1), (0, 1)],
        # T形（横杠在左）
        [(0, 0), (0, -1), (-1, -1), (1, -1)],
        # T形（横杠在右）
        [(0, 0), (0, 1), (-1, 1), (1, 1)],
        # 加号型T形
        [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]
    ]

    # 检查所有可能的中心点
    for i, j in pos_set:
        # 检查L形状
        for l_pattern in l_shapes:
            matches = True
            color = None
            for di, dj in l_pattern:
                ni, nj = i + di, j + dj
                if (ni, nj) not in grid:
                    matches = False
                    break
                if color is None:
                    color = grid[(ni, nj)]
                elif grid[(ni, nj)] != color:
                    matches = False
                    break
            if matches and len(set((i + di, j + dj) for di, dj in l_pattern)) >= 5:
                return True

        # 检查T形状
        for t_pattern in t_shapes:
            matches = True
            color = None
            for di, dj in t_pattern:
                ni, nj = i + di, j + dj
                if (ni, nj) not in grid:
                    matches = False
                    break
                if color is None:
                    color = grid[(ni, nj)]
                elif grid[(ni, nj)] != color:
                    matches = False
                    break
            if matches and len(set((i + di, j + dj) for di, dj in t_pattern)) >= 5:
                return True

    # 检查横向和竖向的交点（L/T形中心）
    for i, j in pos_set:
        # 计算该点的横向和竖向连续相同颜色数量
        color = board[i][j]

        # 横向计数
        h_count = 1
        # 向左
        for dj in range(-1, -BOARD_SIZE, -1):
            nj = j + dj
            if 0 <= nj < BOARD_SIZE and (i, nj) in pos_set and board[i][nj] == color:
                h_count += 1
            else:
                break
        # 向右
        for dj in range(1, BOARD_SIZE):
            nj = j + dj
            if 0 <= nj < BOARD_SIZE and (i, nj) in pos_set and board[i][nj] == color:
                h_count += 1
            else:
                break

        # 竖向计数
        v_count = 1
        # 向上
        for di in range(-1, -BOARD_SIZE, -1):
            ni = i + di
            if 0 <= ni < BOARD_SIZE and (ni, j) in pos_set and board[ni][j] == color:
                v_count += 1
            else:
                break
        # 向下
        for di in range(1, BOARD_SIZE):
            ni = i + di
            if 0 <= ni < BOARD_SIZE and (ni, j) in pos_set and board[ni][j] == color:
                v_count += 1
            else:
                break

        # 判断是否构成L/T形
        if h_count >= 3 and v_count >= 3:
            return True

    return False


def get_board_distribution(board):
    """获取当前棋盘上普通食材的分布情况"""
    food_counts = {}
    total_cells = 0

    # 统计棋盘上各类食材的数量
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] in common_ingredients:
                food_counts[board[i][j]] = food_counts.get(board[i][j], 0) + 1
                total_cells += 1

    # 确保所有常见食材都有在分布中，即使数量为0
    for food in common_ingredients:
        if food not in food_counts:
            food_counts[food] = 0

    # 计算分布比例
    if total_cells > 0:
        food_distribution = {food: max(count, 1) / max(total_cells, 1) for food, count in food_counts.items()}

        # 如果某些食材数量为0，给它们一个小概率
        min_prob = 0.01
        for food in food_distribution:
            if food_distribution[food] < min_prob:
                food_distribution[food] = min_prob

        # 重新归一化概率
        total_prob = sum(food_distribution.values())
        food_distribution = {food: prob / total_prob for food, prob in food_distribution.items()}
    else:
        # 如果棋盘上没有普通食材，使用均匀分布
        food_distribution = {food: 1 / len(common_ingredients) for food in common_ingredients}

    return food_distribution


def simulate_swap(board, swap):
    """
    执行一次交换，返回新棋盘、得分、基础分
    """
    # 获取原始棋盘的食材分布
    original_distribution = get_board_distribution(board)

    # 调试输出交换前的棋盘
    (i1, j1), (i2, j2) = swap
    print(f"\n模拟交换 ({i1},{j1}):{board[i1][j1]} <-> ({i2},{j2}):{board[i2][j2]}")
    print_board_text(board, "交换前棋盘")

    board = [row.copy() for row in board]
    a, b = board[i1][j1], board[i2][j2]

    # 1. 双龙+双龙即时消除
    if a == "双龙戏珠" and b == "双龙戏珠":
        new_board, score, base_score = dragon_dragon_eliminate(board, (i1, j1), (i2, j2), original_distribution)
        print_board_text(new_board, f"双龙+双龙交换后 (得分:{score})")
        return new_board, score, base_score

    # 2. 双龙+普通食材即时消除
    if (a == "双龙戏珠" and b in common_ingredients) or (b == "双龙戏珠" and a in common_ingredients):
        new_board, score, base_score = dragon_ingredient_eliminate(board, (i1, j1), (i2, j2), original_distribution)
        print_board_text(new_board, f"双龙+普通食材交换后 (得分:{score})")
        return new_board, score, base_score

    # 3. 凤凰+凤凰即时消除
    if a == "凤凰振翅" and b == "凤凰振翅":
        new_board, score, base_score = phoenix_phoenix_eliminate(board, (i1, j1), (i2, j2), original_distribution)
        print_board_text(new_board, f"凤凰+凤凰交换后 (得分:{score})")
        return new_board, score, base_score

    # 4. 凤凰+普通食材即时消除
    if (a == "凤凰振翅" and b in common_ingredients) or (b == "凤凰振翅" and a in common_ingredients):
        new_board, score, base_score = phoenix_ingredient_eliminate(board, (i1, j1), (i2, j2), original_distribution)
        print_board_text(new_board, f"凤凰+普通食材交换后 (得分:{score})")
        return new_board, score, base_score

    # 5. 双龙+凤凰即时消除
    if (a == "双龙戏珠" and b == "凤凰振翅") or (a == "凤凰振翅" and b == "双龙戏珠"):
        new_board, score, base_score = dragon_phoenix_eliminate(board, (i1, j1), (i2, j2), original_distribution)
        print_board_text(new_board, f"双龙+凤凰交换后 (得分:{score})")
        return new_board, score, base_score

    # 6. 其它情况，普通交换，判断是否有连消
    board[i1][j1], board[i2][j2] = board[i2][j2], board[i1][j1]
    total_score = 0
    total_base_score = 0
    first_swap = swap

    chain_count = 0
    while True:
        matches = find_matches(board)
        if not matches:
            break

        chain_count += 1

        # 处理消除，注意特殊元素已经在process_elimination中放置到棋盘上了
        board, _, score, base_score = process_elimination(board, matches, first_swap)

        # 应用连锁消除基础分加成规则
        chain_bonus = 0
        if chain_count == 2:
            chain_bonus = 2
            print(f"DEBUG: 第{chain_count}次连锁消除，额外加{chain_bonus}基础分")
        elif chain_count == 3:
            chain_bonus = 5
            print(f"DEBUG: 第{chain_count}次连锁消除，额外加{chain_bonus}基础分")
        elif chain_count == 4:
            chain_bonus = 10
            print(f"DEBUG: 第{chain_count}次连锁消除，额外加{chain_bonus}基础分")
        elif chain_count >= 5:
            chain_bonus = 20
            print(f"DEBUG: 第{chain_count}次连锁消除，额外加{chain_bonus}基础分")

        total_score += score
        total_base_score += base_score + chain_bonus

        # 使用原始棋盘的食材分布进行填充
        board = fall_down_with_distribution(board, original_distribution)

        first_swap = None  # 只有第一次消除用swap确定特殊生成位置

    print_board_text(board, f"普通交换后 (总得分:{total_score})")

    return board, total_score, total_base_score


def dragon_dragon_eliminate(board, pos1, pos2, original_distribution=None):
    """双龙+双龙：全屏所有格子"""
    elim = set((i, j) for i in range(BOARD_SIZE) for j in range(BOARD_SIZE))
    score, base_score = 0, 0
    for (i, j) in elim:
        if board[i][j] in common_ingredients:
            score += 2  # 双倍积分
            base_score += 2  # 双倍积分
        elif board[i][j] == "凤凰振翅":
            score += 3
            base_score += 3
        elif board[i][j] == "双龙戏珠":
            score += 5  # 修改积分 - 双龙为5分而不是15分
            base_score += 5  # 修改积分 - 双龙为5分而不是15分

    new_board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

    # 使用原始分布进行填充
    if original_distribution is None:
        original_distribution = get_board_distribution(board)

    # 修改fall_down函数的调用，传入分布信息
    new_board = fall_down_with_distribution(new_board, original_distribution)

    return new_board, score, base_score


def fall_down_with_distribution(board, distribution):
    """使用指定的食材分布进行下落填充"""
    new_board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

    for j in range(BOARD_SIZE):
        col = []
        for i in reversed(range(BOARD_SIZE)):
            if board[i][j] is not None:
                col.append(board[i][j])

        # 填充剩余位置为None，而不是生成新食材
        while len(col) < BOARD_SIZE:
            col.append(None)

        for i in range(BOARD_SIZE):
            new_board[i][j] = col[BOARD_SIZE - 1 - i]

    return new_board


def explode_phoenix(board, center, area_size=1, already_exploded=None):
    """
    兼容版本的凤凰爆炸函数，确保不消除双龙
    """
    if already_exploded is None:
        already_exploded = set()
    elim = set()
    i, j = center
    for dx in range(-area_size, area_size + 1):
        for dy in range(-area_size, area_size + 1):
            ni, nj = i + dx, j + dy
            if 0 <= ni < BOARD_SIZE and 0 <= nj < BOARD_SIZE:
                if board[ni][nj] != "双龙戏珠" and (ni, nj) not in already_exploded:
                    elim.add((ni, nj))
    # 递归引爆区域内其他凤凰
    for (ni, nj) in list(elim):
        if board[ni][nj] == "凤凰振翅" and (ni, nj) not in already_exploded:
            already_exploded.add((ni, nj))
            elim |= explode_phoenix(board, (ni, nj), area_size=1, already_exploded=already_exploded)
    return elim


def dragon_phoenix_eliminate(board, pos1, pos2, original_distribution=None):
    """
    双龙+凤凰：消除全屏所有元素，包括所有双龙和凤凰
    """
    # 交换位置
    board = [row.copy() for row in board]
    board[pos1[0]][pos1[1]], board[pos2[0]][pos2[1]] = board[pos2[0]][pos2[1]], board[pos1[0]][pos1[1]]

    # 双龙与凤凰交换直接消除全屏，包括所有双龙和凤凰
    elim = set()
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            elim.add((i, j))  # 消除所有格子，包括双龙

    print(f"DEBUG: 双龙+凤凰消除，消除了{len(elim)}个格子，包括所有双龙和凤凰")

    score, base_score = 0, 0
    for (i, j) in elim:
        if board[i][j] in common_ingredients:
            score += 1
            base_score += 1
        elif board[i][j] == "凤凰振翅":
            score += 3
            base_score += 3
        elif board[i][j] == "双龙戏珠":
            score += 5  # 修改积分 - 双龙为5分而不是15分
            base_score += 5  # 修改积分 - 双龙为5分而不是15分

    new_board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

    # 使用原始分布进行填充
    if original_distribution is None:
        original_distribution = get_board_distribution(board)

    new_board = fall_down_with_distribution(new_board, original_distribution)

    return new_board, score, base_score


def categorize_dragons(dragons):
    """
    将双龙分为三类：
    1. 相同列的双龙
    2. 相邻列的双龙
    3. 独立的双龙（不与其他双龙在相同列或相邻列）
    返回这三组双龙以及相关信息
    """
    if not dragons:
        return [], [], []

    # 按列分组的双龙
    column_dragons = {}
    for i, j in dragons:
        if j not in column_dragons:
            column_dragons[j] = []
        column_dragons[j].append((i, j))

    # 找出相同列的双龙
    same_column_dragons = []
    for col, dragons_in_col in column_dragons.items():
        if len(dragons_in_col) >= 2:
            same_column_dragons.extend(dragons_in_col)

    # 找出相邻列的双龙
    adjacent_column_dragons = []
    processed_columns = set()

    for col1 in sorted(column_dragons.keys()):
        if col1 in processed_columns:
            continue

        for col2 in sorted(column_dragons.keys()):
            if col1 != col2 and abs(col1 - col2) == 1:  # 相邻列
                # 如果这两列都有双龙，则它们都属于相邻列双龙
                if col1 not in processed_columns and col2 not in processed_columns:
                    adjacent_column_dragons.extend(column_dragons[col1])
                    adjacent_column_dragons.extend(column_dragons[col2])
                    processed_columns.add(col1)
                    processed_columns.add(col2)

    # 剩余的为独立双龙
    independent_dragons = []
    for dragon in dragons:
        if dragon not in same_column_dragons and dragon not in adjacent_column_dragons:
            independent_dragons.append(dragon)

    return same_column_dragons, adjacent_column_dragons, independent_dragons


class GameInstance(threading.Thread):
    def __init__(self, device_id, model_path, status_queue):
        super().__init__()
        self.daemon = True
        self.device_id = device_id
        self.model_path = model_path
        self.status_queue = status_queue
        self.running = True
        self.steps_used = 0
        self.total_score = 0
        self.total_base_score = 0
        self.TARGET_STEPS = 30
        self.SCORE_TARGET = 1000
        # 这里可以初始化模型等资源
        self.model = None
        self.init_yolo()

    def init_yolo(self):
        from ultralytics import YOLO
        if not os.path.exists(self.model_path):
            raise Exception(f"模型文件不存在: {self.model_path}")
        self.model = YOLO(self.model_path)

    def run(self):
        while True:
            if not self.running:
                time.sleep(1)
                continue
            try:
                print('--- 调试: 开始新循环 ---')
                print('take_screenshot:', type(self.take_screenshot))
                img = self.take_screenshot()
                print('img:', type(img))
                if img is None:
                    time.sleep(1)
                    continue
                print('detect_board:', type(detect_board))
                board = detect_board(img, self.model)
                print('board:', type(board))
                print('get_best_move:', type(get_best_move))
                best_swap = get_best_move(board)
                print('best_swap:', best_swap)
                if best_swap:
                    print('execute_swap:', type(self.execute_swap))
                    self.execute_swap(board, best_swap)
                    
                    # 等待棋盘稳定后再进行下一步操作
                    print('等待棋盘稳定...')
                    stable_board = self.wait_for_stable_board()
                    
                    self.steps_used += 1
                    print('simulate_swap:', type(simulate_swap))
                    _, score, base_score = simulate_swap(board, best_swap)
                    self.total_score += score
                    self.total_base_score += base_score
                self.status_queue.put({
                    'device_id': self.device_id,
                    'steps_used': self.steps_used,
                    'total_score': self.total_score,
                    'total_base_score': self.total_base_score,
                    'status': '运行中',
                })
                time.sleep(0.5)
            except Exception as e:
                import traceback
                print('--- 调试: 捕获到异常 ---')
                traceback.print_exc()
                self.status_queue.put({
                    'device_id': self.device_id,
                    'steps_used': self.steps_used,
                    'total_score': self.total_score,
                    'total_base_score': self.total_base_score,
                    'status': f'异常: {e}',
                })
                time.sleep(2)

    def take_screenshot(self):
        # 只对指定设备截图
        try:
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            result = subprocess.run([
                'adb', '-s', self.device_id, 'exec-out', 'screencap -p'
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10, startupinfo=startupinfo)
            import numpy as np
            import cv2
            img_array = np.frombuffer(result.stdout, dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            return img
        except Exception:
            return None

    def execute_swap(self, board, swap):
        (i1, j1), (i2, j2) = swap
        x1 = BOARD_ORIGIN[0] + j1 * CELL_SIZE + CELL_SIZE // 2
        y1 = BOARD_ORIGIN[1] + i1 * CELL_SIZE + CELL_SIZE // 2
        x2 = BOARD_ORIGIN[0] + j2 * CELL_SIZE + CELL_SIZE // 2
        y2 = BOARD_ORIGIN[1] + i2 * CELL_SIZE + CELL_SIZE // 2
        try:
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            subprocess.run([
                'adb', '-s', self.device_id, 'shell', 'input', 'swipe', str(x1), str(y1), str(x2), str(y2), '250'
            ], check=True, timeout=3, startupinfo=startupinfo)
            time.sleep(2)
            return True
        except Exception as e:
            print(f"执行交换操作失败: {str(e)}")
            return False

    def stop(self):
        self.running = False

    def check_board_stable(self, board):
        """检查棋盘是否稳定（没有空位）"""
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if board[i][j] is None:
                    return False
        return True

    def wait_for_stable_board(self):
        """等待棋盘稳定后再进行下一步操作"""
        max_attempts = 5
        for attempt in range(max_attempts):
            # 截取第一张图
            img1 = self.take_screenshot()
            if img1 is None:
                time.sleep(1)
                continue

            # 等待一秒后截取第二张图
            time.sleep(1)
            img2 = self.take_screenshot()
            if img2 is None:
                time.sleep(1)
                continue

            # 检测两次截图的棋盘状态
            board1 = detect_board(img1, self.model)
            board2 = detect_board(img2, self.model)

            # 检查两次截图是否相同且棋盘是否稳定（没有空位）
            if boards_equal(board1, board2) and self.check_board_stable(board2):
                return board2  # 返回稳定的棋盘状态

            # 如果不稳定，等待一秒后重试
            time.sleep(1)

        # 达到最大尝试次数后，返回最后一次检测的棋盘
        return board2

    def last_step_action(self):
        try:
            img = self.take_screenshot()
            if img is None:
                print("截图失败")
                return

            board = detect_board(img, self.model)

            # 使用find_max_eliminate_swap函数找到最大消除交换
            best_swap, best_base_score = find_max_eliminate_swap(board)

            if best_swap:
                # 执行交换，并多等待一段时间确保动画完成
                success = self.execute_swap(board, best_swap)
                if success:
                    time.sleep(1.5)  # 等待动画完成
                    
                    # 等待棋盘稳定
                    print("等待棋盘稳定...")
                    stable_board = self.wait_for_stable_board()
                    
                    self.steps_used += 1
                    self.total_base_score += best_base_score
                    print(f"已执行最大消除交换，基础分：{best_base_score}")
                else:
                    print("执行交换失败")
            else:
                print("未找到可消除的交换")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"执行异常: {str(e)}")

    def on_closing(self):
        import os
        try:
            self.root.quit()
            self.root.destroy()
        except Exception:
            pass
        os._exit(0)


class ManagerGUI:
    def __init__(self, model_path):
        # 验证卡密
        if not verify_license():
            messagebox.showerror("错误", "软件未激活，程序将退出！")
            sys.exit(1)
            
        self.model_path = model_path
        self.instances = {}  # device_id -> GameInstance
        self.status_queue = queue.Queue()
        self.root = tk.Tk()
        self.root.title("满汉助手多开管理器")
        self.root.geometry("400x300")  # 缩小为原来的三分之一宽度
        
        # 设置窗口图标
        icon_path = resource_path("logo.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
        
        # 新增：按钮区域
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(fill=tk.X, pady=5)
        self.start_all_btn = tk.Button(self.button_frame, text="全部开始", command=self.start_all)
        self.start_all_btn.pack(side=tk.LEFT, padx=10)
        self.pause_all_btn = tk.Button(self.button_frame, text="全部暂停", command=self.pause_all)
        self.pause_all_btn.pack(side=tk.LEFT, padx=10)
        self.last_step_btn = tk.Button(self.button_frame, text="最后一步", command=self.last_step)
        self.last_step_btn.pack(side=tk.LEFT, padx=10)
        # 新增：刷新设备按钮，用于手动刷新设备列表
        self.refresh_btn = tk.Button(self.button_frame, text="刷新设备", command=self.refresh_devices_once)
        self.refresh_btn.pack(side=tk.LEFT, padx=10)

        self.tree = ttk.Treeview(self.root, columns=("设备号", "步数", "得分", "基础分", "状态"), show="headings",
                                 selectmode="extended")
        for col in ("设备号", "步数", "得分", "基础分", "状态"):
            self.tree.heading(col, text=col)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # 添加状态栏，显示剩余使用时间
        self.status_bar = tk.Frame(self.root, bd=1, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 创建状态栏左侧标签（版本信息）
        self.version_label = tk.Label(self.status_bar, text="满汉助手 v1.0", bd=1, anchor=tk.W, padx=5, pady=2)
        self.version_label.pack(side=tk.LEFT)
        
        # 创建状态栏右侧标签（剩余使用时间）
        self.license_label = tk.Label(self.status_bar, bd=1, anchor=tk.E, padx=5, pady=2, cursor="hand2")
        self.license_label.pack(side=tk.RIGHT)
        self.license_label.bind("<Button-1>", self.show_license_details)
        
        # 初始化并更新剩余使用时间显示
        self.update_license_info()
        
        # 启动时只读取一次设备列表
        self.refresh_devices_once()
        self.update_status()

        # 不再定时自动刷新设备列表
        # self.root.after(5000, self.refresh_devices)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)  # 添加窗口关闭事件处理
        self.root.mainloop()
    
    def update_license_info(self):
        """更新剩余使用时间显示"""
        validator = LicenseValidator()
        remaining_days = validator.get_remaining_days()
        expiry_date = validator.get_expiry_date_str()
        
        # 根据剩余天数设置不同的颜色
        if remaining_days <= 7:
            # 剩余7天或更少，显示红色
            fg_color = "red"
        elif remaining_days <= 30:
            # 剩余30天或更少，显示橙色
            fg_color = "orange"
        else:
            # 剩余超过30天，显示绿色
            fg_color = "green"
        
        # 更新标签文本和颜色
        self.license_label.config(
            text=f"软件有效期至: {expiry_date} (剩余 {remaining_days} 天)",
            fg=fg_color
        )
        
        # 每天更新一次（86400000毫秒 = 24小时）
        self.root.after(86400000, self.update_license_info)

    def start_all(self):
        for device_id, inst in self.instances.items():
            inst.running = True  # 恢复所有线程

    def pause_all(self):
        for device_id, inst in self.instances.items():
            inst.running = False  # 暂停所有线程

    def refresh_devices_once(self):
        """只读取一次设备列表，不再自动刷新"""
        # 自动扫描adb devices
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
        result = subprocess.run(['adb', 'devices'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                startupinfo=startupinfo)
        lines = result.stdout.decode().splitlines()
        devices = []
        for line in lines[1:]:
            if line.strip() and 'device' in line:
                device_id = line.split()[0]
                devices.append(device_id)
        # 启动新实例
        for device_id in devices:
            if device_id not in self.instances:
                inst = GameInstance(device_id, self.model_path, self.status_queue)
                inst.start()
                self.instances[device_id] = inst

        # 显示已连接的设备数量
        print(f"已连接 {len(devices)} 个设备，固定使用这些设备")
        if len(devices) == 0:
            tk.messagebox.showinfo("提示", "未检测到已连接的设备，请检查设备连接状态")

    def refresh_devices(self):
        """保留此方法以兼容原有代码，但不再自动调用"""
        # 已被refresh_devices_once替代，不再自动调用
        pass

    def update_status(self):
        # 保存当前选择的设备
        selected_items = self.tree.selection()
        selected_devices = []
        for item in selected_items:
            values = self.tree.item(item, 'values')
            if values:
                selected_devices.append(values[0])  # 设备ID在第一列

        # 清空表格
        for row in self.tree.get_children():
            self.tree.delete(row)

        # 收集所有实例状态
        status_map = {}
        while not self.status_queue.empty():
            status = self.status_queue.get()
            status_map[status['device_id']] = status

        # 更新表格
        item_map = {}  # 用于记录设备ID到表格项的映射
        for device_id, inst in self.instances.items():
            status = status_map.get(device_id, {
                'device_id': device_id,
                'steps_used': inst.steps_used,
                'total_score': inst.total_score,
                'total_base_score': inst.total_base_score,
                'status': '运行中',
            })
            item_id = self.tree.insert('', tk.END, values=(
                status['device_id'],
                status['steps_used'],
                status['total_score'],
                status['total_base_score'],
                status['status'],
            ))
            item_map[device_id] = item_id

        # 恢复之前的选择
        for device_id in selected_devices:
            if device_id in item_map:
                self.tree.selection_add(item_map[device_id])

        self.root.after(1000, self.update_status)

    def last_step(self):
        selected = self.tree.selection()
        if not selected:
            tk.messagebox.showinfo("提示", "请先选中一个或多个设备")
            return
        for sel in selected:
            device_id = self.tree.item(sel)['values'][0]
            inst = self.instances.get(device_id)
            if inst:
                inst.last_step_action()
        # 移除了结果提示对话框

    def on_closing(self):
        import os
        self.root.destroy()
        os._exit(0)

    def show_license_details(self, event=None):
        """显示详细的许可证信息"""
        validator = LicenseValidator()
        remaining_days = validator.get_remaining_days()
        expiry_date = validator.get_expiry_date_str()
        machine_code = validator.machine_code
        
        # 创建详细信息窗口
        details_window = tk.Toplevel(self.root)
        details_window.title("许可证详细信息")
        details_window.geometry("400x200")
        details_window.resizable(False, False)
        
        # 居中显示
        details_window.update_idletasks()
        width = details_window.winfo_width()
        height = details_window.winfo_height()
        x = (details_window.winfo_screenwidth() // 2) - (width // 2)
        y = (details_window.winfo_screenheight() // 2) - (height // 2)
        details_window.geometry(f'{width}x{height}+{x}+{y}')
        
        # 创建内容框架
        content_frame = tk.Frame(details_window, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 添加许可证信息
        tk.Label(content_frame, text="许可证详细信息", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        tk.Label(content_frame, text="机器码:", anchor=tk.W).grid(row=1, column=0, sticky=tk.W, pady=5)
        machine_code_var = tk.StringVar(value=machine_code)
        machine_code_entry = tk.Entry(content_frame, textvariable=machine_code_var, width=30, state="readonly")
        machine_code_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # 添加复制按钮
        copy_btn = tk.Button(content_frame, text="复制", 
                             command=lambda: self.copy_to_clipboard(machine_code, details_window))
        copy_btn.grid(row=1, column=2, padx=5, pady=5)
        
        tk.Label(content_frame, text="有效期至:", anchor=tk.W).grid(row=2, column=0, sticky=tk.W, pady=5)
        tk.Label(content_frame, text=expiry_date, anchor=tk.W).grid(row=2, column=1, sticky=tk.W, pady=5, columnspan=2)
        
        tk.Label(content_frame, text="剩余天数:", anchor=tk.W).grid(row=3, column=0, sticky=tk.W, pady=5)
        
        # 根据剩余天数设置不同的颜色
        if remaining_days <= 7:
            fg_color = "red"
        elif remaining_days <= 30:
            fg_color = "orange"
        else:
            fg_color = "green"
            
        days_label = tk.Label(content_frame, text=f"{remaining_days} 天", anchor=tk.W, fg=fg_color)
        days_label.grid(row=3, column=1, sticky=tk.W, pady=5, columnspan=2)
        
        # 添加关闭按钮
        tk.Button(content_frame, text="关闭", command=details_window.destroy, width=10).grid(row=4, column=0, columnspan=3, pady=(10, 0))
    
    def copy_to_clipboard(self, text, parent_window=None):
        """复制文本到剪贴板"""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        
        # 显示复制成功提示
        if parent_window:
            messagebox.showinfo("提示", "机器码已复制到剪贴板", parent=parent_window)
        else:
            messagebox.showinfo("提示", "机器码已复制到剪贴板")


# 1. 新增查找消除食材最多的交换的函数

def find_max_eliminate_swap(board):
    """查找基础分最高的交换（包括连锁消除加成在内）"""
    swaps = [swap for swap in generate_swaps() if is_valid_swap(board, swap)]
    if not swaps:
        return None, 0

    # 先检查特殊交换
    for swap in swaps:
        (i1, j1), (i2, j2) = swap
        a, b = board[i1][j1], board[i2][j2]

        # 双龙+双龙优先
        if a == "双龙戏珠" and b == "双龙戏珠":
            # 统计全屏消除预期得分
            total_base_score = 0
            for i in range(BOARD_SIZE):
                for j in range(BOARD_SIZE):
                    if board[i][j] in common_ingredients:
                        total_base_score += 2  # 普通食材双倍积分
                    elif board[i][j] == "凤凰振翅":
                        total_base_score += 3
                    elif board[i][j] == "双龙戏珠":
                        total_base_score += 5  # 双龙5分
            return swap, total_base_score

        # 双龙+凤凰次之
        if (a == "双龙戏珠" and b == "凤凰振翅") or (a == "凤凰振翅" and b == "双龙戏珠"):
            # 统计全屏消除预期得分
            total_base_score = 0
            for i in range(BOARD_SIZE):
                for j in range(BOARD_SIZE):
                    if board[i][j] in common_ingredients:
                        total_base_score += 1  # 普通食材正常积分
                    elif board[i][j] == "凤凰振翅":
                        total_base_score += 3
                    elif board[i][j] == "双龙戏珠":
                        total_base_score += 5  # 双龙5分
            return swap, total_base_score

    # 如果没有特殊交换，找普通消除中最高分的
    best_swap = None
    best_base_score = 0

    for swap in swaps:
        try:
            _, _, base_score = simulate_swap(board, swap)
            if base_score > best_base_score:
                best_base_score = base_score
                best_swap = swap
        except Exception as e:
            print(f"模拟交换出错: {e}")
            continue

    return best_swap, best_base_score


if __name__ == "__main__":
    try:
        # 验证卡密
        if not verify_license():
            messagebox.showerror("错误", "软件未激活，程序将退出！")
            sys.exit(1)
            
        # 卡密验证成功后，启动主程序
        print("卡密验证成功，启动主程序...")
        # 只启动多开管理器
        ManagerGUI(MODEL_PATH)
    except Exception as e:
        print(f"程序异常: {str(e)}")
        # 在没有Python环境的情况下，确保错误信息能够显示给用户
        messagebox.showerror("程序异常", f"发生错误: {str(e)}\n\n请联系技术支持。")
        import traceback
        traceback.print_exc()
