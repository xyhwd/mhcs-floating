#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手机游戏引擎 - 完整保留原版算法
包含所有原始的游戏逻辑、消除算法、评估函数等
"""

import os
import sys
import time
import random
import subprocess
import numpy as np
import cv2
from itertools import product
from kivy.logger import Logger
from kivy.utils import platform

# 尝试导入YOLO
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False

class MobileGameEngine:
    """手机游戏引擎 - 完整保留原版算法"""
    
    def __init__(self):
        # 游戏配置参数 (完全保留原版)
        self.BOARD_SIZE = 8
        self.TARGET_STEPS = 30
        self.SCORE_TARGET = 1000
        
        # 分辨率适配参数
        self.BOARD_ORIGIN = None
        self.CELL_SIZE = None
        self.SCREEN_WIDTH = None
        self.SCREEN_HEIGHT = None
        
        # 预设分辨率配置 (完全保留原版)
        self.RESOLUTION_CONFIGS = {
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
        
        # 游戏状态
        self.steps_used = 0
        self.total_score = 0
        self.total_base_score = 0
        self.running = True
        self.paused = True
        
        # 类别映射表 (完全保留原版)
        self.CLASS_MAPPING = {
            0: "香菇",
            1: "蔬菜",
            2: "鸡腿",
            3: "蛋糕",
            4: "红肉",
            5: "鸡蛋",
            6: "凤凰振翅",
            7: "双龙戏珠"
        }
        
        self.common_ingredients = ["香菇", "蔬菜", "鸡腿", "蛋糕", "红肉", "鸡蛋"]
        
        # 初始化模型
        self.model = None
        self.init_model()
        
        # 初始化设备配置
        self.init_device_config()
        
        Logger.info("MobileGameEngine: 手机游戏引擎初始化完成")
    
    def init_model(self):
        """初始化YOLO模型 (完全保留原版逻辑)"""
        try:
            if not YOLO_AVAILABLE:
                Logger.warning("MobileGameEngine: YOLO不可用，使用模拟模式")
                return
            
            # 查找模型文件
            model_paths = [
                "model/best.pt",
                "best.pt",
                os.path.join(os.path.dirname(__file__), "model", "best.pt"),
                os.path.join(os.path.dirname(__file__), "best.pt")
            ]
            
            model_path = None
            for path in model_paths:
                if os.path.exists(path):
                    model_path = path
                    break
            
            if model_path:
                Logger.info(f"MobileGameEngine: 加载模型: {model_path}")
                self.model = YOLO(model_path)
                Logger.info("MobileGameEngine: 模型加载成功")
            else:
                Logger.warning("MobileGameEngine: 未找到模型文件，使用模拟模式")
                
        except Exception as e:
            Logger.error(f"MobileGameEngine: 模型初始化失败: {str(e)}")
    
    def get_device_resolution(self):
        """获取设备分辨率 (适配手机)"""
        try:
            if platform == 'android':
                # Android平台获取分辨率
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                DisplayMetrics = autoclass('android.util.DisplayMetrics')
                Context = autoclass('android.content.Context')
                
                activity = PythonActivity.mActivity
                window_manager = activity.getSystemService(Context.WINDOW_SERVICE)
                display = window_manager.getDefaultDisplay()
                
                metrics = DisplayMetrics()
                display.getRealMetrics(metrics)
                
                return metrics.widthPixels, metrics.heightPixels
            else:
                # 桌面平台模拟
                return 1080, 1920
                
        except Exception as e:
            Logger.error(f"MobileGameEngine: 获取分辨率失败: {str(e)}")
            return 1080, 1920
    
    def calculate_adaptive_config(self, width, height):
        """根据设备分辨率计算自适应配置 (完全保留原版算法)"""
        self.SCREEN_WIDTH = width
        self.SCREEN_HEIGHT = height
        
        # 首先检查是否有完全匹配的预设配置
        if (width, height) in self.RESOLUTION_CONFIGS:
            x, y, size = self.RESOLUTION_CONFIGS[(width, height)]
            self.BOARD_ORIGIN = (x, y)
            self.CELL_SIZE = size
            Logger.info(f"MobileGameEngine: 使用预设配置: 分辨率{width}x{height}, 棋盘起点({x},{y}), 格子大小{size}")
            return
        
        # 如果没有完全匹配，尝试按比例缩放
        base_width, base_height = 1080, 1920
        base_x, base_y, base_size = 90, 680, 120
        
        # 计算缩放比例
        scale_x = width / base_width
        scale_y = height / base_height
        scale = min(scale_x, scale_y)
        
        # 计算新的配置
        new_x = int(base_x * scale_x)
        new_y = int(base_y * scale_y)
        new_size = int(base_size * scale)
        
        # 确保棋盘不会超出屏幕边界
        board_width = self.BOARD_SIZE * new_size
        board_height = self.BOARD_SIZE * new_size
        
        if new_x + board_width > width:
            new_x = width - board_width - 10
        if new_y + board_height > height:
            new_y = height - board_height - 10
        
        new_x = max(10, new_x)
        new_y = max(10, new_y)
        
        self.BOARD_ORIGIN = (new_x, new_y)
        self.CELL_SIZE = new_size
        
        Logger.info(f"MobileGameEngine: 自适应配置: 分辨率{width}x{height}, 棋盘起点({new_x},{new_y}), 格子大小{new_size}")
    
    def init_device_config(self):
        """初始化设备配置"""
        try:
            width, height = self.get_device_resolution()
            self.calculate_adaptive_config(width, height)
        except Exception as e:
            Logger.error(f"MobileGameEngine: 设备配置初始化失败: {str(e)}")
            # 使用默认配置
            self.BOARD_ORIGIN = (90, 680)
            self.CELL_SIZE = 120
    
    def take_screenshot(self):
        """截取屏幕 (适配手机)"""
        try:
            if platform == 'android':
                # Android平台截图
                result = subprocess.run(
                    ['screencap', '-p'],
                    capture_output=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    img_array = np.frombuffer(result.stdout, dtype=np.uint8)
                    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                    return img
                else:
                    Logger.error("MobileGameEngine: screencap命令失败")
                    return None
            else:
                # 桌面平台模拟截图
                img = np.zeros((self.SCREEN_HEIGHT or 1920, self.SCREEN_WIDTH or 1080, 3), dtype=np.uint8)
                img.fill(128)
                return img
                
        except Exception as e:
            Logger.error(f"MobileGameEngine: 截图失败: {str(e)}")
            return None
    
    def infer_from_neighbors(self, board, i, j):
        """从邻居推断格子内容 (完全保留原版算法)"""
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                ni, nj = i + dx, j + dy
                if 0 <= ni < self.BOARD_SIZE and 0 <= nj < self.BOARD_SIZE:
                    if board[ni][nj] in self.common_ingredients:
                        neighbors.append(board[ni][nj])
        
        if len(neighbors) >= 2:
            return max(set(neighbors), key=neighbors.count)
        
        # 否则，基于整个棋盘的当前分布选择
        food_counts = {}
        for r in range(self.BOARD_SIZE):
            for c in range(self.BOARD_SIZE):
                if board[r][c] in self.common_ingredients:
                    food_counts[board[r][c]] = food_counts.get(board[r][c], 0) + 1
        
        if food_counts:
            max_count = max(food_counts.values())
            most_common = [food for food, count in food_counts.items() if count == max_count]
            return random.choice(most_common)
        else:
            return random.choice(self.common_ingredients)
    
    def detect_board(self, img):
        """检测棋盘状态 (完全保留原版算法)"""
        try:
            if img is None:
                return [[None] * self.BOARD_SIZE for _ in range(self.BOARD_SIZE)]
            
            h, w = img.shape[:2]
            if self.BOARD_ORIGIN is None or self.CELL_SIZE is None:
                Logger.error("MobileGameEngine: 棋盘配置未初始化")
                return [[None] * self.BOARD_SIZE for _ in range(self.BOARD_SIZE)]
            
            board_area = img[
                self.BOARD_ORIGIN[1]: self.BOARD_ORIGIN[1] + self.BOARD_SIZE * self.CELL_SIZE,
                self.BOARD_ORIGIN[0]: self.BOARD_ORIGIN[0] + self.BOARD_SIZE * self.CELL_SIZE
            ]
            
            if board_area.size == 0:
                Logger.error(f"MobileGameEngine: 棋盘区域检测异常，请校准参数：BOARD_ORIGIN={self.BOARD_ORIGIN}, CELL_SIZE={self.CELL_SIZE}")
                return [[None] * self.BOARD_SIZE for _ in range(self.BOARD_SIZE)]
            
            # 使用YOLO模型检测或模拟检测
            if self.model is not None:
                results = self.model(img)
            else:
                results = self._mock_detection()
            
            board = [[None for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)]
            current_confidence = [[-1 for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)]
            
            # 处理检测结果 (完全保留原版逻辑)
            for result in results:
                if hasattr(result, 'boxes') and result.boxes is not None:
                    for box in result.boxes:
                        x_center = (box.xyxy[0][0] + box.xyxy[0][2]) / 2
                        y_center = (box.xyxy[0][1] + box.xyxy[0][3]) / 2
                        rel_x = x_center - self.BOARD_ORIGIN[0]
                        rel_y = y_center - self.BOARD_ORIGIN[1]
                        j = int(rel_x // self.CELL_SIZE)
                        i = int(rel_y // self.CELL_SIZE)
                        
                        if 0 <= i < self.BOARD_SIZE and 0 <= j < self.BOARD_SIZE:
                            cls = int(box.cls[0])
                            detected_class = self.CLASS_MAPPING.get(cls, "未知")
                            conf = float(box.conf[0]) if hasattr(box, 'conf') else 1.0
                            
                            if board[i][j] is None or conf > current_confidence[i][j]:
                                board[i][j] = detected_class
                                current_confidence[i][j] = conf
            
            # 填充未检测到的格子
            for i in range(self.BOARD_SIZE):
                for j in range(self.BOARD_SIZE):
                    if board[i][j] in ["未知", None]:
                        board[i][j] = self.infer_from_neighbors(board, i, j)
            
            return board
            
        except Exception as e:
            Logger.error(f"MobileGameEngine: 棋盘检测失败: {str(e)}")
            return [[None] * self.BOARD_SIZE for _ in range(self.BOARD_SIZE)]
    
    def _mock_detection(self):
        """模拟检测结果 (用于测试)"""
        class MockBox:
            def __init__(self, x1, y1, x2, y2, cls, conf):
                self.xyxy = [[x1, y1, x2, y2]]
                self.cls = [cls]
                self.conf = [conf]
        
        class MockResult:
            def __init__(self, engine):
                self.boxes = []

                # 生成随机检测框
                if engine.BOARD_ORIGIN and engine.CELL_SIZE:
                    for i in range(engine.BOARD_SIZE):
                        for j in range(engine.BOARD_SIZE):
                            if random.random() > 0.1:  # 90%概率生成
                                x1 = engine.BOARD_ORIGIN[0] + j * engine.CELL_SIZE + 10
                                y1 = engine.BOARD_ORIGIN[1] + i * engine.CELL_SIZE + 10
                                x2 = x1 + engine.CELL_SIZE - 20
                                y2 = y1 + engine.CELL_SIZE - 20

                                if random.random() > 0.95:  # 5%概率是特殊元素
                                    cls = random.choice([6, 7])
                                else:
                                    cls = random.choice([0, 1, 2, 3, 4, 5])

                                conf = random.uniform(0.7, 0.95)
                                box = MockBox(x1, y1, x2, y2, cls, conf)
                                self.boxes.append(box)
        
        return [MockResult(self)]

    def execute_swap(self, swap):
        """执行交换操作 (适配手机触摸)"""
        try:
            (i1, j1), (i2, j2) = swap
            x1 = self.BOARD_ORIGIN[0] + j1 * self.CELL_SIZE + self.CELL_SIZE // 2
            y1 = self.BOARD_ORIGIN[1] + i1 * self.CELL_SIZE + self.CELL_SIZE // 2
            x2 = self.BOARD_ORIGIN[0] + j2 * self.CELL_SIZE + self.CELL_SIZE // 2
            y2 = self.BOARD_ORIGIN[1] + i2 * self.CELL_SIZE + self.CELL_SIZE // 2

            if platform == 'android':
                # Android平台使用input命令
                result = subprocess.run(
                    ['input', 'swipe', str(x1), str(y1), str(x2), str(y2), '250'],
                    capture_output=True,
                    timeout=3
                )
                success = result.returncode == 0
            else:
                # 桌面平台模拟
                Logger.info(f"MobileGameEngine: 模拟交换 ({i1},{j1}) -> ({i2},{j2})")
                success = True

            if success:
                Logger.info(f"MobileGameEngine: 执行交换成功：({i1},{j1}) -> ({i2},{j2})")
                time.sleep(1)  # 等待动画完成
            else:
                Logger.error(f"MobileGameEngine: 执行交换失败：({i1},{j1}) -> ({i2},{j2})")

            return success

        except Exception as e:
            Logger.error(f"MobileGameEngine: 执行交换异常: {str(e)}")
            return False

    def generate_swaps(self):
        """生成所有可能的交换 (完全保留原版算法)"""
        swaps = []
        for i in range(self.BOARD_SIZE):
            for j in range(self.BOARD_SIZE):
                if j < self.BOARD_SIZE - 1:
                    swaps.append(((i, j), (i, j + 1)))
                if i < self.BOARD_SIZE - 1:
                    swaps.append(((i, j), (i + 1, j)))
        return swaps

    def count_line(self, board, i, j, di, dj):
        """计算某方向连续相同元素数量 (完全保留原版算法)"""
        color = board[i][j]
        cnt = 1
        ni, nj = i + di, j + dj
        while 0 <= ni < self.BOARD_SIZE and 0 <= nj < self.BOARD_SIZE and board[ni][nj] == color:
            cnt += 1
            ni += di
            nj += dj
        ni, nj = i - di, j - dj
        while 0 <= ni < self.BOARD_SIZE and 0 <= nj < self.BOARD_SIZE and board[ni][nj] == color:
            cnt += 1
            ni -= di
            nj -= dj
        return cnt

    def is_valid_swap(self, board, swap):
        """检查交换是否有效 (完全保留原版算法)"""
        try:
            temp_board = [row.copy() for row in board]
            (i1, j1), (i2, j2) = swap
            a, b = temp_board[i1][j1], temp_board[i2][j2]

            # 1. 双龙戏珠与双龙戏珠相邻直接允许
            if a == "双龙戏珠" and b == "双龙戏珠" and abs(i1 - i2) + abs(j1 - j2) == 1:
                return True

            # 2. 其它特殊消除类型直接允许
            if (a == "双龙戏珠" and b in self.common_ingredients) or (b == "双龙戏珠" and a in self.common_ingredients):
                return True
            if (a == "凤凰振翅" and b in self.common_ingredients) or (b == "凤凰振翅" and a in self.common_ingredients):
                return True
            if (a == "凤凰振翅" and b == "凤凰振翅"):
                if abs(i1 - i2) + abs(j1 - j2) == 1:
                    return True
            if (a == "双龙戏珠" and b == "凤凰振翅") or (a == "凤凰振翅" and b == "双龙戏珠"):
                return True

            # 3. 其它情况按横竖消除规则
            temp_board[i1][j1], temp_board[i2][j2] = temp_board[i2][j2], temp_board[i1][j1]
            for (i, j) in [(i1, j1), (i2, j2)]:
                if temp_board[i][j] not in self.common_ingredients:
                    continue
                h = self.count_line(temp_board, i, j, 0, 1)
                v = self.count_line(temp_board, i, j, 1, 0)
                cross = 0
                if h >= 3: cross += h - 1
                if v >= 3: cross += v - 1
                if ((h >= 3 and v >= 3 and cross + 1 >= 5) or (h >= 3 and v < 3) or (v >= 3 and h < 3)):
                    return True
            return False

        except Exception as e:
            Logger.error(f"MobileGameEngine: 检查交换有效性失败: {str(e)}")
            return False

    def find_matches(self, board):
        """查找匹配的消除组 (完全保留原版算法)"""
        matches = []
        # 横向查找
        for i in range(self.BOARD_SIZE):
            j = 0
            while j < self.BOARD_SIZE:
                run = []
                start_j = j
                while j < self.BOARD_SIZE and board[i][j] in self.common_ingredients and board[i][j] == board[i][start_j]:
                    run.append((i, j))
                    j += 1
                if len(run) >= 3:
                    matches.append(run)
                if len(run) == 0:
                    j += 1

        # 竖向查找
        for j in range(self.BOARD_SIZE):
            i = 0
            while i < self.BOARD_SIZE:
                run = []
                start_i = i
                while i < self.BOARD_SIZE and board[i][j] in self.common_ingredients and board[i][j] == board[start_i][j]:
                    run.append((i, j))
                    i += 1
                if len(run) >= 3:
                    matches.append(run)
                if len(run) == 0:
                    i += 1
        return matches

    def evaluate_swap(self, board, swap):
        """评估交换的价值 (完全保留原版算法)"""
        try:
            temp_board = [row.copy() for row in board]
            (i1, j1), (i2, j2) = swap
            a, b = temp_board[i1][j1], temp_board[i2][j2]

            # 特殊元素交换的高分奖励
            if a == "双龙戏珠" and b == "双龙戏珠":
                return 1000
            if (a == "双龙戏珠" and b in self.common_ingredients) or (b == "双龙戏珠" and a in self.common_ingredients):
                return 800
            if (a == "凤凰振翅" and b in self.common_ingredients) or (b == "凤凰振翅" and a in self.common_ingredients):
                return 600
            if a == "凤凰振翅" and b == "凤凰振翅":
                return 700
            if (a == "双龙戏珠" and b == "凤凰振翅") or (a == "凤凰振翅" and b == "双龙戏珠"):
                return 900

            # 普通消除评估
            temp_board[i1][j1], temp_board[i2][j2] = temp_board[i2][j2], temp_board[i1][j1]
            score = 0

            for (i, j) in [(i1, j1), (i2, j2)]:
                if temp_board[i][j] not in self.common_ingredients:
                    continue

                h = self.count_line(temp_board, i, j, 0, 1)
                v = self.count_line(temp_board, i, j, 1, 0)

                # 基础消除分数
                if h >= 3:
                    score += h * 10
                if v >= 3:
                    score += v * 10

                # L形或T形奖励
                if h >= 3 and v >= 3:
                    score += 100

                # 长消除奖励
                if h >= 5:
                    score += 50
                if v >= 5:
                    score += 50

            return score

        except Exception as e:
            Logger.error(f"MobileGameEngine: 评估交换失败: {str(e)}")
            return 0

    def get_best_swap(self, board):
        """获取最佳交换 (完全保留原版算法)"""
        try:
            swaps = self.generate_swaps()
            valid_swaps = [swap for swap in swaps if self.is_valid_swap(board, swap)]

            if not valid_swaps:
                return None

            best_swap = None
            best_score = -1

            for swap in valid_swaps:
                score = self.evaluate_swap(board, swap)
                if score > best_score:
                    best_score = score
                    best_swap = swap

            return best_swap

        except Exception as e:
            Logger.error(f"MobileGameEngine: 获取最佳交换失败: {str(e)}")
            return None

    def execute_one_step(self):
        """执行一步游戏逻辑 (完全保留原版算法)"""
        try:
            if self.paused or not self.running:
                return {"status": "paused"}

            # 1. 截取屏幕
            img = self.take_screenshot()
            if img is None:
                return {"status": "error", "message": "截图失败"}

            # 2. 检测棋盘
            board = self.detect_board(img)
            if not board or all(cell is None for row in board for cell in row):
                return {"status": "error", "message": "棋盘检测失败"}

            # 3. 寻找最佳交换
            best_swap = self.get_best_swap(board)
            if not best_swap:
                return {"status": "error", "message": "未找到有效交换"}

            # 4. 执行交换
            success = self.execute_swap(best_swap)
            if success:
                self.steps_used += 1
                # 简化的得分计算
                score_gained = self.evaluate_swap(board, best_swap) // 10
                self.total_score += score_gained

                return {
                    "status": "success",
                    "steps": self.steps_used,
                    "score": self.total_score,
                    "message": f"执行交换成功，得分+{score_gained}",
                    "swap": best_swap
                }
            else:
                return {"status": "error", "message": "交换执行失败"}

        except Exception as e:
            Logger.error(f"MobileGameEngine: 执行步骤失败: {str(e)}")
            return {"status": "error", "message": f"执行失败: {str(e)}"}

    def start_game(self):
        """开始游戏"""
        self.running = True
        self.paused = False
        Logger.info("MobileGameEngine: 游戏已开始")

    def pause_game(self):
        """暂停游戏"""
        self.paused = True
        Logger.info("MobileGameEngine: 游戏已暂停")

    def resume_game(self):
        """继续游戏"""
        self.paused = False
        Logger.info("MobileGameEngine: 游戏已继续")

    def stop_game(self):
        """停止游戏"""
        self.running = False
        self.paused = True
        Logger.info("MobileGameEngine: 游戏已停止")

    def reset_game(self):
        """重置游戏状态"""
        self.steps_used = 0
        self.total_score = 0
        self.total_base_score = 0
        self.paused = True
        Logger.info("MobileGameEngine: 游戏状态已重置")

    def get_game_status(self):
        """获取游戏状态"""
        return {
            "running": self.running,
            "paused": self.paused,
            "steps": self.steps_used,
            "score": self.total_score,
            "target_steps": self.TARGET_STEPS,
            "target_score": self.SCORE_TARGET,
            "board_config": {
                "origin": self.BOARD_ORIGIN,
                "cell_size": self.CELL_SIZE,
                "screen_size": (self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
            }
        }
