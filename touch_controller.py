#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
触摸控制器模块
实现Android平台的触摸操作功能
"""

import time
import subprocess
from kivy.utils import platform
from kivy.logger import Logger

if platform == 'android':
    from jnius import autoclass, cast
    from android.runnable import run_on_ui_thread
    
    # Android Java classes
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    MotionEvent = autoclass('android.view.MotionEvent')
    SystemClock = autoclass('android.os.SystemClock')
    Instrumentation = autoclass('android.app.Instrumentation')

class TouchController:
    """触摸控制器类"""
    
    def __init__(self):
        self.last_touch_time = 0
        self.min_touch_interval = 0.1  # 最小触摸间隔（秒）
        
        if platform == 'android':
            self.init_android_touch()
        else:
            self.init_desktop_touch()
        
        Logger.info("TouchController: 触摸控制器初始化完成")
    
    def init_android_touch(self):
        """初始化Android触摸功能"""
        try:
            self.activity = PythonActivity.mActivity
            Logger.info("TouchController: Android触摸功能初始化完成")
        except Exception as e:
            Logger.error(f"TouchController: Android触摸初始化失败: {str(e)}")
    
    def init_desktop_touch(self):
        """初始化桌面触摸功能（用于测试）"""
        Logger.info("TouchController: 桌面模拟触摸功能初始化完成")
    
    def swipe(self, x1, y1, x2, y2, duration=250):
        """执行滑动操作"""
        try:
            # 检查触摸间隔
            current_time = time.time()
            if current_time - self.last_touch_time < self.min_touch_interval:
                time.sleep(self.min_touch_interval - (current_time - self.last_touch_time))
            
            if platform == 'android':
                success = self._swipe_android(x1, y1, x2, y2, duration)
            else:
                success = self._swipe_desktop(x1, y1, x2, y2, duration)
            
            self.last_touch_time = time.time()
            
            if success:
                Logger.info(f"TouchController: 滑动成功 ({x1},{y1}) -> ({x2},{y2})")
            else:
                Logger.error(f"TouchController: 滑动失败 ({x1},{y1}) -> ({x2},{y2})")
            
            return success
            
        except Exception as e:
            Logger.error(f"TouchController: 滑动操作异常: {str(e)}")
            return False
    
    def _swipe_android(self, x1, y1, x2, y2, duration):
        """Android平台滑动实现"""
        try:
            # 方法1: 使用shell命令（需要root权限或无障碍服务）
            return self._swipe_shell(x1, y1, x2, y2, duration)
            
        except Exception as e:
            Logger.error(f"TouchController: Android滑动失败: {str(e)}")
            return False
    
    def _swipe_shell(self, x1, y1, x2, y2, duration):
        """使用shell命令执行滑动"""
        try:
            # 使用input命令
            cmd = ['input', 'swipe', str(int(x1)), str(int(y1)), str(int(x2)), str(int(y2)), str(duration)]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=5,
                text=True
            )
            
            if result.returncode == 0:
                Logger.info(f"TouchController: Shell滑动命令执行成功")
                return True
            else:
                Logger.error(f"TouchController: Shell滑动命令失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            Logger.error("TouchController: Shell滑动命令超时")
            return False
        except Exception as e:
            Logger.error(f"TouchController: Shell滑动命令异常: {str(e)}")
            return False
    
    def _swipe_accessibility(self, x1, y1, x2, y2, duration):
        """使用无障碍服务执行滑动（需要用户授权）"""
        try:
            # 这里需要实现无障碍服务的滑动功能
            # 由于复杂性，暂时使用shell命令替代
            return self._swipe_shell(x1, y1, x2, y2, duration)
            
        except Exception as e:
            Logger.error(f"TouchController: 无障碍服务滑动失败: {str(e)}")
            return False
    
    def _swipe_desktop(self, x1, y1, x2, y2, duration):
        """桌面平台滑动实现（用于测试）"""
        try:
            Logger.info(f"TouchController: 模拟滑动 ({x1},{y1}) -> ({x2},{y2}), 持续时间: {duration}ms")
            time.sleep(duration / 1000.0)  # 模拟滑动时间
            return True
            
        except Exception as e:
            Logger.error(f"TouchController: 桌面滑动失败: {str(e)}")
            return False
    
    def tap(self, x, y):
        """执行点击操作"""
        try:
            # 检查触摸间隔
            current_time = time.time()
            if current_time - self.last_touch_time < self.min_touch_interval:
                time.sleep(self.min_touch_interval - (current_time - self.last_touch_time))
            
            if platform == 'android':
                success = self._tap_android(x, y)
            else:
                success = self._tap_desktop(x, y)
            
            self.last_touch_time = time.time()
            
            if success:
                Logger.info(f"TouchController: 点击成功 ({x},{y})")
            else:
                Logger.error(f"TouchController: 点击失败 ({x},{y})")
            
            return success
            
        except Exception as e:
            Logger.error(f"TouchController: 点击操作异常: {str(e)}")
            return False
    
    def _tap_android(self, x, y):
        """Android平台点击实现"""
        try:
            # 使用shell命令
            cmd = ['input', 'tap', str(int(x)), str(int(y))]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=3,
                text=True
            )
            
            if result.returncode == 0:
                Logger.info(f"TouchController: Android点击成功")
                return True
            else:
                Logger.error(f"TouchController: Android点击失败: {result.stderr}")
                return False
                
        except Exception as e:
            Logger.error(f"TouchController: Android点击异常: {str(e)}")
            return False
    
    def _tap_desktop(self, x, y):
        """桌面平台点击实现（用于测试）"""
        try:
            Logger.info(f"TouchController: 模拟点击 ({x},{y})")
            return True
            
        except Exception as e:
            Logger.error(f"TouchController: 桌面点击失败: {str(e)}")
            return False
    
    def long_press(self, x, y, duration=1000):
        """执行长按操作"""
        try:
            if platform == 'android':
                success = self._long_press_android(x, y, duration)
            else:
                success = self._long_press_desktop(x, y, duration)
            
            if success:
                Logger.info(f"TouchController: 长按成功 ({x},{y}), 持续时间: {duration}ms")
            else:
                Logger.error(f"TouchController: 长按失败 ({x},{y})")
            
            return success
            
        except Exception as e:
            Logger.error(f"TouchController: 长按操作异常: {str(e)}")
            return False
    
    def _long_press_android(self, x, y, duration):
        """Android平台长按实现"""
        try:
            # 使用swipe命令实现长按（起点和终点相同）
            cmd = ['input', 'swipe', str(int(x)), str(int(y)), str(int(x)), str(int(y)), str(duration)]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=5,
                text=True
            )
            
            return result.returncode == 0
            
        except Exception as e:
            Logger.error(f"TouchController: Android长按异常: {str(e)}")
            return False
    
    def _long_press_desktop(self, x, y, duration):
        """桌面平台长按实现（用于测试）"""
        try:
            Logger.info(f"TouchController: 模拟长按 ({x},{y}), 持续时间: {duration}ms")
            time.sleep(duration / 1000.0)
            return True
            
        except Exception as e:
            Logger.error(f"TouchController: 桌面长按失败: {str(e)}")
            return False
    
    def multi_touch(self, touches):
        """执行多点触摸操作"""
        try:
            # touches: [(x1, y1), (x2, y2), ...]
            if platform == 'android':
                success = self._multi_touch_android(touches)
            else:
                success = self._multi_touch_desktop(touches)
            
            if success:
                Logger.info(f"TouchController: 多点触摸成功, 点数: {len(touches)}")
            else:
                Logger.error(f"TouchController: 多点触摸失败")
            
            return success
            
        except Exception as e:
            Logger.error(f"TouchController: 多点触摸异常: {str(e)}")
            return False
    
    def _multi_touch_android(self, touches):
        """Android平台多点触摸实现"""
        try:
            # 简化实现：依次执行单点触摸
            for x, y in touches:
                if not self.tap(x, y):
                    return False
                time.sleep(0.05)  # 短暂延迟
            return True
            
        except Exception as e:
            Logger.error(f"TouchController: Android多点触摸异常: {str(e)}")
            return False
    
    def _multi_touch_desktop(self, touches):
        """桌面平台多点触摸实现（用于测试）"""
        try:
            Logger.info(f"TouchController: 模拟多点触摸, 点数: {len(touches)}")
            for i, (x, y) in enumerate(touches):
                Logger.info(f"TouchController: 触摸点{i+1}: ({x},{y})")
            return True
            
        except Exception as e:
            Logger.error(f"TouchController: 桌面多点触摸失败: {str(e)}")
            return False
    
    def is_touch_available(self):
        """检查触摸功能是否可用"""
        try:
            if platform == 'android':
                # 检查是否有input命令权限
                result = subprocess.run(
                    ['input'],
                    capture_output=True,
                    timeout=3,
                    text=True
                )
                return result.returncode == 0 or 'usage:' in result.stderr.lower()
            else:
                return True  # 桌面平台总是可用
                
        except Exception as e:
            Logger.error(f"TouchController: 检查触摸可用性失败: {str(e)}")
            return False
    
    def get_touch_capabilities(self):
        """获取触摸功能能力"""
        capabilities = {
            'tap': True,
            'swipe': True,
            'long_press': True,
            'multi_touch': True,
            'available': self.is_touch_available()
        }
        
        Logger.info(f"TouchController: 触摸能力: {capabilities}")
        return capabilities
