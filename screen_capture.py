#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
屏幕截图模块
实现Android平台的屏幕截图功能
"""

import os
import time
import numpy as np
from kivy.utils import platform
from kivy.logger import Logger

if platform == 'android':
    from jnius import autoclass, cast
    from android.runnable import run_on_ui_thread
    
    # Android Java classes
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    MediaProjectionManager = autoclass('android.media.projection.MediaProjectionManager')
    ImageReader = autoclass('android.media.ImageReader')
    PixelFormat = autoclass('android.graphics.PixelFormat')
    VirtualDisplay = autoclass('android.hardware.display.VirtualDisplay')
    DisplayMetrics = autoclass('android.util.DisplayMetrics')
    WindowManager = autoclass('android.view.WindowManager')
    Context = autoclass('android.content.Context')
    
else:
    # 桌面平台的模拟实现
    import cv2

class ScreenCapture:
    """屏幕截图类"""
    
    def __init__(self):
        self.screen_width = None
        self.screen_height = None
        self.board_origin = None
        self.cell_size = None
        
        # 预设的分辨率配置
        self.resolution_configs = {
            (1080, 1920): (90, 680, 120),    # 1080p 竖屏
            (1080, 2340): (90, 850, 120),    # 19.5:9 竖屏
            (1080, 2400): (90, 900, 120),    # 20:9 竖屏
            (720, 1280): (60, 450, 80),      # 720p 竖屏
            (1440, 2560): (120, 900, 160),   # 2K 竖屏
            (1440, 2960): (120, 1100, 160),  # 2K+ 竖屏
        }
        
        self.init_screen_config()
        Logger.info("ScreenCapture: 屏幕截图模块初始化完成")
    
    def init_screen_config(self):
        """初始化屏幕配置"""
        try:
            # 获取屏幕分辨率
            width, height = self.get_screen_resolution()
            if width and height:
                self.screen_width = width
                self.screen_height = height
                self.calculate_board_config(width, height)
                Logger.info(f"ScreenCapture: 屏幕分辨率 {width}x{height}")
            else:
                # 使用默认配置
                self.screen_width = 1080
                self.screen_height = 1920
                self.board_origin = (90, 680)
                self.cell_size = 120
                Logger.warning("ScreenCapture: 使用默认屏幕配置")
                
        except Exception as e:
            Logger.error(f"ScreenCapture: 初始化屏幕配置失败: {str(e)}")
            # 使用默认配置
            self.screen_width = 1080
            self.screen_height = 1920
            self.board_origin = (90, 680)
            self.cell_size = 120
    
    def get_screen_resolution(self):
        """获取屏幕分辨率"""
        try:
            if platform == 'android':
                return self._get_android_resolution()
            else:
                return self._get_desktop_resolution()
        except Exception as e:
            Logger.error(f"ScreenCapture: 获取屏幕分辨率失败: {str(e)}")
            return None, None
    
    def _get_android_resolution(self):
        """获取Android设备分辨率"""
        try:
            activity = PythonActivity.mActivity
            window_manager = activity.getSystemService(Context.WINDOW_SERVICE)
            display = window_manager.getDefaultDisplay()
            
            metrics = DisplayMetrics()
            display.getRealMetrics(metrics)
            
            width = metrics.widthPixels
            height = metrics.heightPixels
            
            return width, height
            
        except Exception as e:
            Logger.error(f"ScreenCapture: 获取Android分辨率失败: {str(e)}")
            return None, None
    
    def _get_desktop_resolution(self):
        """获取桌面分辨率（用于测试）"""
        try:
            # 模拟手机分辨率
            return 1080, 1920
        except Exception as e:
            Logger.error(f"ScreenCapture: 获取桌面分辨率失败: {str(e)}")
            return None, None
    
    def calculate_board_config(self, width, height):
        """根据分辨率计算棋盘配置"""
        try:
            # 检查是否有预设配置
            if (width, height) in self.resolution_configs:
                x, y, size = self.resolution_configs[(width, height)]
                self.board_origin = (x, y)
                self.cell_size = size
                Logger.info(f"ScreenCapture: 使用预设配置 - 起点({x},{y}), 格子大小{size}")
                return
            
            # 自适应计算
            base_width, base_height = 1080, 1920
            base_x, base_y, base_size = 90, 680, 120
            
            # 计算缩放比例
            scale_x = width / base_width
            scale_y = height / base_height
            scale = min(scale_x, scale_y)
            
            # 计算新配置
            new_x = int(base_x * scale_x)
            new_y = int(base_y * scale_y)
            new_size = int(base_size * scale)
            
            # 确保棋盘不超出屏幕
            board_width = 8 * new_size  # 8x8棋盘
            board_height = 8 * new_size
            
            if new_x + board_width > width:
                new_x = width - board_width - 10
            if new_y + board_height > height:
                new_y = height - board_height - 10
            
            new_x = max(10, new_x)
            new_y = max(10, new_y)
            
            self.board_origin = (new_x, new_y)
            self.cell_size = new_size
            
            Logger.info(f"ScreenCapture: 自适应配置 - 起点({new_x},{new_y}), 格子大小{new_size}")
            
        except Exception as e:
            Logger.error(f"ScreenCapture: 计算棋盘配置失败: {str(e)}")
            # 使用默认配置
            self.board_origin = (90, 680)
            self.cell_size = 120
    
    def capture(self):
        """截取屏幕"""
        try:
            if platform == 'android':
                return self._capture_android()
            else:
                return self._capture_desktop()
        except Exception as e:
            Logger.error(f"ScreenCapture: 截图失败: {str(e)}")
            return None
    
    def _capture_android(self):
        """Android平台截图"""
        try:
            # 这里需要使用MediaProjection API
            # 由于权限限制，可能需要用户授权
            
            # 简化实现：使用shell命令截图
            import subprocess
            
            # 使用screencap命令
            result = subprocess.run(
                ['screencap', '-p'],
                capture_output=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # 将字节数据转换为numpy数组
                img_array = np.frombuffer(result.stdout, dtype=np.uint8)
                
                # 使用OpenCV解码
                import cv2
                img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                
                if img is not None:
                    Logger.info("ScreenCapture: Android截图成功")
                    return img
                else:
                    Logger.error("ScreenCapture: 图像解码失败")
                    return None
            else:
                Logger.error(f"ScreenCapture: screencap命令失败: {result.stderr}")
                return None
                
        except Exception as e:
            Logger.error(f"ScreenCapture: Android截图异常: {str(e)}")
            return None
    
    def _capture_desktop(self):
        """桌面平台截图（用于测试）"""
        try:
            # 创建一个模拟的截图
            img = np.zeros((self.screen_height, self.screen_width, 3), dtype=np.uint8)
            img.fill(128)  # 灰色背景
            
            Logger.info("ScreenCapture: 桌面模拟截图")
            return img
            
        except Exception as e:
            Logger.error(f"ScreenCapture: 桌面截图失败: {str(e)}")
            return None
    
    def get_board_config(self):
        """获取棋盘配置"""
        return self.board_origin, self.cell_size
    
    def get_board_area(self, screenshot):
        """获取棋盘区域"""
        try:
            if screenshot is None or self.board_origin is None or self.cell_size is None:
                return None
            
            x, y = self.board_origin
            size = self.cell_size * 8  # 8x8棋盘
            
            # 确保不超出图像边界
            h, w = screenshot.shape[:2]
            x2 = min(x + size, w)
            y2 = min(y + size, h)
            
            board_area = screenshot[y:y2, x:x2]
            return board_area
            
        except Exception as e:
            Logger.error(f"ScreenCapture: 获取棋盘区域失败: {str(e)}")
            return None
    
    def save_debug_image(self, image, filename="debug_screenshot.jpg"):
        """保存调试图像"""
        try:
            if image is None:
                return False
            
            # 获取应用数据目录
            if platform == 'android':
                from android.storage import app_storage_path
                debug_dir = os.path.join(app_storage_path(), "debug")
            else:
                debug_dir = "debug"
            
            # 创建目录
            os.makedirs(debug_dir, exist_ok=True)
            
            # 保存图像
            import cv2
            filepath = os.path.join(debug_dir, filename)
            success = cv2.imwrite(filepath, image)
            
            if success:
                Logger.info(f"ScreenCapture: 调试图像已保存: {filepath}")
            else:
                Logger.error(f"ScreenCapture: 保存调试图像失败: {filepath}")
            
            return success
            
        except Exception as e:
            Logger.error(f"ScreenCapture: 保存调试图像异常: {str(e)}")
            return False
    
    def draw_board_grid(self, image):
        """在图像上绘制棋盘网格（用于调试）"""
        try:
            if image is None or self.board_origin is None or self.cell_size is None:
                return image
            
            import cv2
            debug_img = image.copy()
            x, y = self.board_origin
            cell_size = self.cell_size
            
            # 绘制网格线
            for i in range(9):  # 9条线形成8个格子
                # 垂直线
                x_line = x + i * cell_size
                cv2.line(debug_img, (x_line, y), (x_line, y + 8 * cell_size), (0, 255, 0), 2)
                
                # 水平线
                y_line = y + i * cell_size
                cv2.line(debug_img, (x, y_line), (x + 8 * cell_size, y_line), (0, 255, 0), 2)
            
            return debug_img
            
        except Exception as e:
            Logger.error(f"ScreenCapture: 绘制棋盘网格失败: {str(e)}")
            return image
