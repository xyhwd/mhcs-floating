#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏核心模块
包含消除游戏的主要逻辑和算法
"""

import time
import random
import numpy as np
from itertools import product
from kivy.logger import Logger

class GameCore:
    """游戏核心类"""
    
    def __init__(self, model_manager, screen_capture, touch_controller):
        self.model_manager = model_manager
        self.screen_capture = screen_capture
        self.touch_controller = touch_controller
        
        # 游戏配置
        self.board_size = 8
        self.target_steps = 30
        self.target_score = 1000
        
        # 游戏状态
        self.steps_used = 0
        self.total_score = 0
        self.total_base_score = 0
        self.current_board = None
        
        # 食材类型
        self.common_ingredients = ["香菇", "蔬菜", "鸡腿", "蛋糕", "红肉", "鸡蛋"]
        self.special_ingredients = ["凤凰振翅", "双龙戏珠"]
        
        # 类别映射
        self.class_mapping = {
            0: "香菇",
            1: "蔬菜", 
            2: "鸡腿",
            3: "蛋糕",
            4: "红肉",
            5: "鸡蛋",
            6: "凤凰振翅",
            7: "双龙戏珠"
        }
        
        Logger.info("GameCore: 游戏核心初始化完成")
    
    def execute_one_step(self):
        """执行一步游戏逻辑"""
        try:
            # 1. 截取屏幕
            screenshot = self.screen_capture.capture()
            if screenshot is None:
                return {"message": "截图失败"}
            
            # 2. 检测棋盘
            board = self.detect_board(screenshot)
            if not board:
                return {"message": "棋盘检测失败"}
            
            self.current_board = board
            
            # 3. 寻找最佳移动
            best_move = self.get_best_move(board)
            if not best_move:
                return {"message": "未找到有效移动"}
            
            # 4. 执行移动
            success = self.execute_move(best_move)
            if success:
                self.steps_used += 1
                # 模拟计算得分（实际应该通过图像识别获取）
                score_gained = self.calculate_move_score(board, best_move)
                self.total_score += score_gained
                
                return {
                    "steps": self.steps_used,
                    "score": self.total_score,
                    "message": f"执行移动成功，得分+{score_gained}"
                }
            else:
                return {"message": "移动执行失败"}
                
        except Exception as e:
            Logger.error(f"GameCore: 执行步骤失败: {str(e)}")
            return {"message": f"执行失败: {str(e)}"}
    
    def detect_board(self, screenshot):
        """检测棋盘状态"""
        try:
            # 使用YOLO模型检测游戏元素
            results = self.model_manager.predict(screenshot)
            
            # 初始化棋盘
            board = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]
            confidence_board = [[-1 for _ in range(self.board_size)] for _ in range(self.board_size)]
            
            # 获取棋盘配置
            board_origin, cell_size = self.screen_capture.get_board_config()
            
            # 处理检测结果
            for result in results:
                if hasattr(result, 'boxes') and result.boxes is not None:
                    for box in result.boxes:
                        # 获取边界框中心点
                        x_center = (box.xyxy[0][0] + box.xyxy[0][2]) / 2
                        y_center = (box.xyxy[0][1] + box.xyxy[0][3]) / 2
                        
                        # 转换为棋盘坐标
                        rel_x = x_center - board_origin[0]
                        rel_y = y_center - board_origin[1]
                        j = int(rel_x // cell_size)
                        i = int(rel_y // cell_size)
                        
                        # 检查坐标有效性
                        if 0 <= i < self.board_size and 0 <= j < self.board_size:
                            cls = int(box.cls[0])
                            detected_class = self.class_mapping.get(cls, "未知")
                            conf = float(box.conf[0]) if hasattr(box, 'conf') else 1.0
                            
                            # 使用置信度最高的检测结果
                            if board[i][j] is None or conf > confidence_board[i][j]:
                                board[i][j] = detected_class
                                confidence_board[i][j] = conf
            
            # 填充未检测到的格子
            for i in range(self.board_size):
                for j in range(self.board_size):
                    if board[i][j] in ["未知", None]:
                        board[i][j] = self.infer_from_neighbors(board, i, j)
            
            return board
            
        except Exception as e:
            Logger.error(f"GameCore: 棋盘检测失败: {str(e)}")
            return None
    
    def infer_from_neighbors(self, board, i, j):
        """从邻居推断格子内容"""
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                ni, nj = i + dx, j + dy
                if 0 <= ni < self.board_size and 0 <= nj < self.board_size:
                    if board[ni][nj] in self.common_ingredients:
                        neighbors.append(board[ni][nj])
        
        if len(neighbors) >= 2:
            return max(set(neighbors), key=neighbors.count)
        else:
            return random.choice(self.common_ingredients)
    
    def get_best_move(self, board):
        """获取最佳移动"""
        try:
            # 生成所有可能的交换
            swaps = self.generate_swaps()
            valid_swaps = [swap for swap in swaps if self.is_valid_swap(board, swap)]
            
            if not valid_swaps:
                return None
            
            # 评估每个交换的价值
            best_swap = None
            best_score = -1
            
            for swap in valid_swaps:
                score = self.evaluate_swap(board, swap)
                if score > best_score:
                    best_score = score
                    best_swap = swap
            
            return best_swap
            
        except Exception as e:
            Logger.error(f"GameCore: 寻找最佳移动失败: {str(e)}")
            return None
    
    def generate_swaps(self):
        """生成所有可能的交换"""
        swaps = []
        for i in range(self.board_size):
            for j in range(self.board_size):
                # 水平交换
                if j < self.board_size - 1:
                    swaps.append(((i, j), (i, j + 1)))
                # 垂直交换
                if i < self.board_size - 1:
                    swaps.append(((i, j), (i + 1, j)))
        return swaps
    
    def is_valid_swap(self, board, swap):
        """检查交换是否有效（能产生消除）"""
        try:
            (i1, j1), (i2, j2) = swap
            
            # 创建临时棋盘
            temp_board = [row.copy() for row in board]
            temp_board[i1][j1], temp_board[i2][j2] = temp_board[i2][j2], temp_board[i1][j1]
            
            # 检查是否有特殊元素交换
            a, b = temp_board[i1][j1], temp_board[i2][j2]
            
            # 特殊元素交换规则
            if a == "双龙戏珠" and b == "双龙戏珠":
                return True
            if (a == "双龙戏珠" and b in self.common_ingredients) or \
               (b == "双龙戏珠" and a in self.common_ingredients):
                return True
            if (a == "凤凰振翅" and b in self.common_ingredients) or \
               (b == "凤凰振翅" and a in self.common_ingredients):
                return True
            if a == "凤凰振翅" and b == "凤凰振翅":
                return True
            if (a == "双龙戏珠" and b == "凤凰振翅") or \
               (a == "凤凰振翅" and b == "双龙戏珠"):
                return True
            
            # 检查普通消除
            for (i, j) in [(i1, j1), (i2, j2)]:
                if temp_board[i][j] not in self.common_ingredients:
                    continue
                
                h_count = self.count_line(temp_board, i, j, 0, 1)
                v_count = self.count_line(temp_board, i, j, 1, 0)
                
                if h_count >= 3 or v_count >= 3:
                    return True
            
            return False
            
        except Exception as e:
            Logger.error(f"GameCore: 检查交换有效性失败: {str(e)}")
            return False
    
    def count_line(self, board, i, j, di, dj):
        """计算某方向上连续相同元素的数量"""
        color = board[i][j]
        count = 1
        
        # 正方向
        ni, nj = i + di, j + dj
        while 0 <= ni < self.board_size and 0 <= nj < self.board_size and board[ni][nj] == color:
            count += 1
            ni += di
            nj += dj
        
        # 负方向
        ni, nj = i - di, j - dj
        while 0 <= ni < self.board_size and 0 <= nj < self.board_size and board[ni][nj] == color:
            count += 1
            ni -= di
            nj -= dj
        
        return count
    
    def evaluate_swap(self, board, swap):
        """评估交换的价值"""
        try:
            # 简化的评估函数
            (i1, j1), (i2, j2) = swap
            
            # 创建临时棋盘
            temp_board = [row.copy() for row in board]
            temp_board[i1][j1], temp_board[i2][j2] = temp_board[i2][j2], temp_board[i1][j1]
            
            score = 0
            
            # 检查消除数量
            for (i, j) in [(i1, j1), (i2, j2)]:
                if temp_board[i][j] in self.common_ingredients:
                    h_count = self.count_line(temp_board, i, j, 0, 1)
                    v_count = self.count_line(temp_board, i, j, 1, 0)
                    
                    if h_count >= 3:
                        score += h_count * 10
                    if v_count >= 3:
                        score += v_count * 10
                    
                    # L形或T形奖励
                    if h_count >= 3 and v_count >= 3:
                        score += 100
            
            # 特殊元素奖励
            a, b = temp_board[i1][j1], temp_board[i2][j2]
            if a in self.special_ingredients or b in self.special_ingredients:
                score += 50
            
            return score
            
        except Exception as e:
            Logger.error(f"GameCore: 评估交换失败: {str(e)}")
            return 0
    
    def execute_move(self, move):
        """执行移动"""
        try:
            (i1, j1), (i2, j2) = move
            
            # 获取棋盘配置
            board_origin, cell_size = self.screen_capture.get_board_config()
            
            # 计算屏幕坐标
            x1 = board_origin[0] + j1 * cell_size + cell_size // 2
            y1 = board_origin[1] + i1 * cell_size + cell_size // 2
            x2 = board_origin[0] + j2 * cell_size + cell_size // 2
            y2 = board_origin[1] + i2 * cell_size + cell_size // 2
            
            # 执行滑动操作
            success = self.touch_controller.swipe(x1, y1, x2, y2)
            
            if success:
                Logger.info(f"GameCore: 执行移动成功: ({i1},{j1}) -> ({i2},{j2})")
                time.sleep(1)  # 等待动画完成
            else:
                Logger.error(f"GameCore: 执行移动失败: ({i1},{j1}) -> ({i2},{j2})")
            
            return success
            
        except Exception as e:
            Logger.error(f"GameCore: 执行移动异常: {str(e)}")
            return False
    
    def calculate_move_score(self, board, move):
        """计算移动得分（简化版本）"""
        # 这里应该通过图像识别来获取实际得分
        # 现在使用简化的计算方法
        try:
            (i1, j1), (i2, j2) = move
            temp_board = [row.copy() for row in board]
            temp_board[i1][j1], temp_board[i2][j2] = temp_board[i2][j2], temp_board[i1][j1]
            
            score = 0
            for (i, j) in [(i1, j1), (i2, j2)]:
                if temp_board[i][j] in self.common_ingredients:
                    h_count = self.count_line(temp_board, i, j, 0, 1)
                    v_count = self.count_line(temp_board, i, j, 1, 0)
                    
                    if h_count >= 3:
                        score += h_count
                    if v_count >= 3:
                        score += v_count
            
            return max(score, 1)  # 至少返回1分
            
        except Exception as e:
            Logger.error(f"GameCore: 计算得分失败: {str(e)}")
            return 1
    
    def reset_game(self):
        """重置游戏状态"""
        self.steps_used = 0
        self.total_score = 0
        self.total_base_score = 0
        self.current_board = None
        Logger.info("GameCore: 游戏状态已重置")
