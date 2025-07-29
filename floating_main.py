#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
满汉助手 Android悬浮窗版本
只有一个小的悬浮控制窗口
完整保留原版算法
"""

import os
import sys
import time
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.utils import platform
from kivy.config import Config

# 设置窗口为悬浮窗
Config.set('graphics', 'resizable', False)
Config.set('graphics', 'width', '180')
Config.set('graphics', 'height', '120')

# Android specific imports
if platform == 'android':
    from android.permissions import request_permissions, Permission
    from jnius import autoclass
    
    # Android Java classes
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Intent = autoclass('android.content.Intent')
    Settings = autoclass('android.provider.Settings')

# 导入完整的原版算法模块
from mobile_game_engine import MobileGameEngine

class FloatingControlApp(App):
    """悬浮控制窗口应用"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_engine = None
        self.is_running = False
        
    def build(self):
        """构建悬浮窗界面"""
        self.title = "满汉助手"
        
        # 创建紧凑的悬浮窗布局
        main_layout = BoxLayout(
            orientation='vertical', 
            padding=3, 
            spacing=3
        )
        
        # 状态显示
        self.status_label = Label(
            text='未启动',
            size_hint_y=None,
            height=20,
            font_size=10,
            color=(1, 1, 1, 1)
        )
        main_layout.add_widget(self.status_label)
        
        # 步数和分数显示
        info_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=18)
        self.steps_label = Label(text='步:0', font_size=9, color=(0.8, 0.8, 0.8, 1))
        self.score_label = Label(text='分:0', font_size=9, color=(0.8, 0.8, 0.8, 1))
        info_layout.add_widget(self.steps_label)
        info_layout.add_widget(self.score_label)
        main_layout.add_widget(info_layout)
        
        # 主控制按钮
        self.main_btn = Button(
            text='开始',
            size_hint_y=None,
            height=35,
            font_size=12,
            background_color=(0.2, 0.7, 0.2, 1)
        )
        self.main_btn.bind(on_press=self.toggle_main_action)
        main_layout.add_widget(self.main_btn)
        
        # 底部按钮行
        bottom_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=25, spacing=2)
        
        # 设置按钮
        settings_btn = Button(
            text='设置', 
            font_size=9,
            background_color=(0.5, 0.5, 0.5, 1)
        )
        settings_btn.bind(on_press=self.open_settings)
        
        # 退出按钮
        exit_btn = Button(
            text='退出', 
            font_size=9,
            background_color=(0.7, 0.2, 0.2, 1)
        )
        exit_btn.bind(on_press=self.exit_app)
        
        bottom_layout.add_widget(settings_btn)
        bottom_layout.add_widget(exit_btn)
        main_layout.add_widget(bottom_layout)
        
        # 请求权限并初始化
        if platform == 'android':
            self.request_android_permissions()
        
        Clock.schedule_once(self.init_game_engine, 1)
        
        return main_layout
    
    def request_android_permissions(self):
        """请求Android权限"""
        try:
            permissions = [
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.SYSTEM_ALERT_WINDOW,
            ]
            request_permissions(permissions)
            Logger.info("FloatingApp: 权限请求完成")
        except Exception as e:
            Logger.error(f"FloatingApp: 权限请求失败: {str(e)}")
    
    def init_game_engine(self, dt):
        """初始化游戏引擎"""
        try:
            self.update_status("初始化中...")
            self.game_engine = MobileGameEngine()
            self.update_status("已就绪")
            Logger.info("FloatingApp: 游戏引擎初始化完成")
        except Exception as e:
            self.update_status("初始化失败")
            Logger.error(f"FloatingApp: 初始化失败: {str(e)}")
    
    def toggle_main_action(self, instance):
        """主按钮动作 - 开始/暂停/继续"""
        if not self.game_engine:
            self.update_status("引擎未就绪")
            return
        
        if not self.is_running:
            # 开始游戏
            self.start_game()
        else:
            # 暂停/继续游戏
            if self.game_engine.paused:
                self.resume_game()
            else:
                self.pause_game()
    
    def start_game(self):
        """开始游戏"""
        try:
            self.is_running = True
            self.game_engine.start_game()
            self.main_btn.text = '暂停'
            self.main_btn.background_color = (0.7, 0.7, 0.2, 1)
            self.update_status("运行中")
            
            # 启动游戏循环
            threading.Thread(target=self.game_loop, daemon=True).start()
            Logger.info("FloatingApp: 游戏已开始")
            
        except Exception as e:
            self.update_status("启动失败")
            Logger.error(f"FloatingApp: 启动失败: {str(e)}")
    
    def pause_game(self):
        """暂停游戏"""
        if self.game_engine:
            self.game_engine.pause_game()
        self.main_btn.text = '继续'
        self.main_btn.background_color = (0.2, 0.7, 0.2, 1)
        self.update_status("已暂停")
        Logger.info("FloatingApp: 游戏已暂停")
    
    def resume_game(self):
        """继续游戏"""
        if self.game_engine:
            self.game_engine.resume_game()
        self.main_btn.text = '暂停'
        self.main_btn.background_color = (0.7, 0.7, 0.2, 1)
        self.update_status("运行中")
        Logger.info("FloatingApp: 游戏已继续")
    
    def stop_game(self):
        """停止游戏"""
        self.is_running = False
        if self.game_engine:
            self.game_engine.stop_game()
        self.main_btn.text = '开始'
        self.main_btn.background_color = (0.2, 0.7, 0.2, 1)
        self.update_status("已停止")
        Logger.info("FloatingApp: 游戏已停止")
    
    def game_loop(self):
        """游戏主循环"""
        while self.is_running:
            if self.game_engine and not self.game_engine.paused:
                try:
                    result = self.game_engine.execute_one_step()
                    
                    if result and result.get("status") == "success":
                        Clock.schedule_once(lambda dt, r=result: self.update_game_status(r), 0)
                    elif result and result.get("status") == "error":
                        Clock.schedule_once(lambda dt: self.update_status("错误"), 0)
                    
                except Exception as e:
                    Clock.schedule_once(lambda dt: self.update_status("异常"), 0)
                    Logger.error(f"FloatingApp: 游戏循环错误: {str(e)}")
            
            time.sleep(1)
    
    def update_game_status(self, result):
        """更新游戏状态"""
        if 'steps' in result:
            self.steps_label.text = f"步:{result['steps']}"
        if 'score' in result:
            self.score_label.text = f"分:{result['score']}"
    
    def update_status(self, message):
        """更新状态显示"""
        def update_ui(dt):
            # 限制状态文本长度
            if len(message) > 12:
                self.status_label.text = message[:12] + ".."
            else:
                self.status_label.text = message
        
        Clock.schedule_once(update_ui, 0)
    
    def open_settings(self, instance):
        """打开设置"""
        if platform == 'android':
            try:
                intent = Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)
                PythonActivity.mActivity.startActivity(intent)
                self.update_status("已打开设置")
            except Exception as e:
                self.update_status("设置失败")
                Logger.error(f"FloatingApp: 打开设置失败: {str(e)}")
        else:
            self.update_status("仅Android可用")
    
    def exit_app(self, instance):
        """退出应用"""
        self.stop_game()
        self.stop()
        Logger.info("FloatingApp: 应用已退出")

if __name__ == '__main__':
    FloatingControlApp().run()
