#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型管理器模块
负责YOLO模型的加载和推理
"""

import os
import sys
import numpy as np
from pathlib import Path
from kivy.utils import platform
from kivy.logger import Logger

# 尝试导入YOLO相关库
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    Logger.warning("ModelManager: ultralytics库未安装，将使用模拟模式")

# Android存储路径
if platform == 'android':
    from android.storage import app_storage_path, primary_external_storage_path

class ModelManager:
    """模型管理器类"""
    
    def __init__(self):
        self.model = None
        self.model_path = None
        self.is_loaded = False
        
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
        
        self.init_model()
        Logger.info("ModelManager: 模型管理器初始化完成")
    
    def init_model(self):
        """初始化模型"""
        try:
            # 查找模型文件
            model_path = self.find_model_file()
            
            if model_path and os.path.exists(model_path):
                self.model_path = model_path
                self.load_model()
            else:
                Logger.warning("ModelManager: 未找到模型文件，将使用模拟模式")
                self.setup_mock_mode()
                
        except Exception as e:
            Logger.error(f"ModelManager: 初始化模型失败: {str(e)}")
            self.setup_mock_mode()
    
    def find_model_file(self):
        """查找模型文件"""
        try:
            # 可能的模型路径
            possible_paths = []
            
            if platform == 'android':
                # Android平台路径
                app_dir = app_storage_path()
                external_dir = primary_external_storage_path()
                
                possible_paths.extend([
                    os.path.join(app_dir, "model", "best.pt"),
                    os.path.join(app_dir, "best.pt"),
                    os.path.join(external_dir, "满汉助手", "model", "best.pt"),
                    os.path.join(external_dir, "满汉助手", "best.pt"),
                    os.path.join(external_dir, "Download", "best.pt"),
                ])
            else:
                # 桌面平台路径
                current_dir = os.path.dirname(os.path.abspath(__file__))
                possible_paths.extend([
                    os.path.join(current_dir, "model", "best.pt"),
                    os.path.join(current_dir, "best.pt"),
                    os.path.join(current_dir, "..", "model", "best.pt"),
                    "model/best.pt",
                    "best.pt"
                ])
            
            # 检查每个可能的路径
            for path in possible_paths:
                if os.path.exists(path):
                    Logger.info(f"ModelManager: 找到模型文件: {path}")
                    return path
            
            Logger.warning("ModelManager: 未找到模型文件")
            return None
            
        except Exception as e:
            Logger.error(f"ModelManager: 查找模型文件失败: {str(e)}")
            return None
    
    def load_model(self):
        """加载YOLO模型"""
        try:
            if not YOLO_AVAILABLE:
                Logger.warning("ModelManager: YOLO库不可用，使用模拟模式")
                self.setup_mock_mode()
                return
            
            if not self.model_path or not os.path.exists(self.model_path):
                Logger.error("ModelManager: 模型文件不存在")
                self.setup_mock_mode()
                return
            
            Logger.info(f"ModelManager: 正在加载模型: {self.model_path}")
            self.model = YOLO(self.model_path)
            self.is_loaded = True
            
            Logger.info("ModelManager: 模型加载成功")
            
        except Exception as e:
            Logger.error(f"ModelManager: 加载模型失败: {str(e)}")
            self.setup_mock_mode()
    
    def setup_mock_mode(self):
        """设置模拟模式"""
        self.model = None
        self.is_loaded = False
        Logger.info("ModelManager: 已启用模拟模式")
    
    def predict(self, image):
        """执行模型推理"""
        try:
            if image is None:
                Logger.error("ModelManager: 输入图像为空")
                return []
            
            if self.is_loaded and self.model is not None:
                return self._predict_real(image)
            else:
                return self._predict_mock(image)
                
        except Exception as e:
            Logger.error(f"ModelManager: 推理失败: {str(e)}")
            return []
    
    def _predict_real(self, image):
        """真实模型推理"""
        try:
            # 执行YOLO推理
            results = self.model(image)
            Logger.info(f"ModelManager: 推理完成，检测到 {len(results)} 个结果")
            return results
            
        except Exception as e:
            Logger.error(f"ModelManager: 真实推理失败: {str(e)}")
            return []
    
    def _predict_mock(self, image):
        """模拟推理（用于测试）"""
        try:
            # 创建模拟的检测结果
            mock_results = []
            
            # 模拟检测框类
            class MockBox:
                def __init__(self, x1, y1, x2, y2, cls, conf):
                    self.xyxy = [[x1, y1, x2, y2]]
                    self.cls = [cls]
                    self.conf = [conf]
            
            # 模拟结果类
            class MockResult:
                def __init__(self):
                    self.boxes = []
                    
                    # 生成一些随机的检测框（模拟8x8棋盘）
                    import random
                    
                    # 假设棋盘区域
                    board_x, board_y = 90, 680  # 默认配置
                    cell_size = 120
                    
                    for i in range(8):
                        for j in range(8):
                            # 随机决定是否在这个位置生成检测框
                            if random.random() > 0.1:  # 90%概率生成
                                x1 = board_x + j * cell_size + 10
                                y1 = board_y + i * cell_size + 10
                                x2 = x1 + cell_size - 20
                                y2 = y1 + cell_size - 20
                                
                                # 随机选择类别（普通食材概率更高）
                                if random.random() > 0.95:  # 5%概率是特殊元素
                                    cls = random.choice([6, 7])  # 凤凰或双龙
                                else:
                                    cls = random.choice([0, 1, 2, 3, 4, 5])  # 普通食材
                                
                                conf = random.uniform(0.7, 0.95)  # 随机置信度
                                
                                box = MockBox(x1, y1, x2, y2, cls, conf)
                                self.boxes.append(box)
            
            mock_result = MockResult()
            mock_results.append(mock_result)
            
            Logger.info(f"ModelManager: 模拟推理完成，生成 {len(mock_result.boxes)} 个检测框")
            return mock_results
            
        except Exception as e:
            Logger.error(f"ModelManager: 模拟推理失败: {str(e)}")
            return []
    
    def get_class_name(self, class_id):
        """根据类别ID获取类别名称"""
        return self.class_mapping.get(class_id, "未知")
    
    def get_model_info(self):
        """获取模型信息"""
        info = {
            'loaded': self.is_loaded,
            'path': self.model_path,
            'mock_mode': not self.is_loaded,
            'yolo_available': YOLO_AVAILABLE,
            'classes': len(self.class_mapping)
        }
        return info
    
    def validate_model(self):
        """验证模型是否正常工作"""
        try:
            if not self.is_loaded:
                Logger.warning("ModelManager: 模型未加载，无法验证")
                return False
            
            # 创建测试图像
            test_image = np.zeros((640, 640, 3), dtype=np.uint8)
            
            # 执行推理测试
            results = self.predict(test_image)
            
            if results is not None:
                Logger.info("ModelManager: 模型验证成功")
                return True
            else:
                Logger.error("ModelManager: 模型验证失败")
                return False
                
        except Exception as e:
            Logger.error(f"ModelManager: 模型验证异常: {str(e)}")
            return False
    
    def reload_model(self):
        """重新加载模型"""
        try:
            Logger.info("ModelManager: 正在重新加载模型...")
            self.model = None
            self.is_loaded = False
            self.init_model()
            
        except Exception as e:
            Logger.error(f"ModelManager: 重新加载模型失败: {str(e)}")
    
    def get_supported_formats(self):
        """获取支持的图像格式"""
        return ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
    
    def preprocess_image(self, image):
        """预处理图像"""
        try:
            if image is None:
                return None
            
            # 确保图像是正确的格式
            if len(image.shape) == 3 and image.shape[2] == 3:
                # BGR格式，YOLO期望RGB
                import cv2
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            return image
            
        except Exception as e:
            Logger.error(f"ModelManager: 图像预处理失败: {str(e)}")
            return image
    
    def postprocess_results(self, results):
        """后处理推理结果"""
        try:
            if not results:
                return []
            
            processed_results = []
            
            for result in results:
                if hasattr(result, 'boxes') and result.boxes is not None:
                    for box in result.boxes:
                        # 提取检测信息
                        detection = {
                            'bbox': box.xyxy[0].tolist() if hasattr(box.xyxy[0], 'tolist') else list(box.xyxy[0]),
                            'class_id': int(box.cls[0]),
                            'class_name': self.get_class_name(int(box.cls[0])),
                            'confidence': float(box.conf[0]) if hasattr(box, 'conf') else 1.0
                        }
                        processed_results.append(detection)
            
            return processed_results
            
        except Exception as e:
            Logger.error(f"ModelManager: 结果后处理失败: {str(e)}")
            return []
