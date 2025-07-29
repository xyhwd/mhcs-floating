#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
满汉助手 Android版本
基于Kivy框架的消除游戏自动化应用
完整保留原版算法
"""

import os
import sys
import time
import threading
import random
import numpy as np
import cv2
from pathlib import Path
from itertools import product

# Kivy imports
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.utils import platform

# Android specific imports
if platform == 'android':
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path
    from jnius import autoclass, cast
    from android.runnable import run_on_ui_thread

    # Android Java classes
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Intent = autoclass('android.content.Intent')
    Settings = autoclass('android.provider.Settings')
    Uri = autoclass('android.net.Uri')

# 尝试导入YOLO
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    Logger.warning("YOLO not available, using mock mode")

# 导入完整的原版算法模块
from mobile_game_engine import MobileGameEngine

class MainApp(App):
    """主应用类 - 完整保留原版算法"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_engine = None
        self.is_running = False
        self.is_paused = True
        
    def build(self):
        """构建应用界面 - 简洁悬浮窗版本"""
        self.title = "满汉助手"

        # 创建紧凑的悬浮窗布局
        main_layout = BoxLayout(
            orientation='vertical',
            padding=5,
            spacing=5,
            size_hint=(None, None),
            size=(200, 150)  # 固定小尺寸
        )

        # 状态指示器
        self.status_label = Label(
            text='未启动',
            size_hint_y=None,
            height=25,
            font_size=12
        )
        main_layout.add_widget(self.status_label)

        # 步数和分数显示
        info_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=20)
        self.steps_label = Label(text='步数:0', font_size=10)
        self.score_label = Label(text='分数:0', font_size=10)
        info_layout.add_widget(self.steps_label)
        info_layout.add_widget(self.score_label)
        main_layout.add_widget(info_layout)

        # 控制按钮
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=5)

        self.start_pause_btn = Button(
            text='开始',
            size_hint_y=None,
            height=35,
            font_size=12
        )
        self.start_pause_btn.bind(on_press=self.toggle_start_pause)

        self.stop_btn = Button(
            text='停止',
            size_hint_y=None,
            height=35,
            font_size=12
        )
        self.stop_btn.bind(on_press=self.stop_game)

        button_layout.add_widget(self.start_pause_btn)
        button_layout.add_widget(self.stop_btn)
        main_layout.add_widget(button_layout)

        # 设置按钮
        settings_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30, spacing=5)

        settings_btn = Button(text='设置', font_size=10, size_hint_y=None, height=25)
        settings_btn.bind(on_press=self.show_settings)

        exit_btn = Button(text='退出', font_size=10, size_hint_y=None, height=25)
        exit_btn.bind(on_press=self.exit_app)

        settings_layout.add_widget(settings_btn)
        settings_layout.add_widget(exit_btn)
        main_layout.add_widget(settings_layout)

        # 请求必要权限
        if platform == 'android':
            self.request_android_permissions()

        # 初始化组件
        Clock.schedule_once(self.init_components, 1)

        return main_layout
    
    def exit_app(self, instance):
        """退出应用"""
        if self.game_engine:
            self.game_engine.stop_game()
        self.stop()

    def add_log(self, message):
        """添加日志消息 - 简化版本"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        Logger.info(f"MainApp: {log_message}")

        # 在状态标签中显示最新消息
        def update_status(dt):
            if len(message) > 15:
                self.status_label.text = message[:15] + "..."
            else:
                self.status_label.text = message

        Clock.schedule_once(update_status, 0)
    
    def request_android_permissions(self):
        """请求Android权限"""
        if platform == 'android':
            permissions = [
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.SYSTEM_ALERT_WINDOW,
                Permission.CAPTURE_AUDIO_OUTPUT,
            ]
            request_permissions(permissions)
            self.add_log("已请求必要权限")
    
    def init_components(self, dt):
        """初始化核心组件 - 使用完整游戏引擎"""
        try:
            self.add_log("正在初始化游戏引擎...")

            # 初始化完整的游戏引擎
            self.game_engine = MobileGameEngine()
            self.add_log("游戏引擎初始化完成")

            # 获取游戏状态
            status = self.game_engine.get_game_status()

            # 更新UI显示
            if status["board_config"]["screen_size"]:
                width, height = status["board_config"]["screen_size"]
                self.resolution_label.text = f"{width}x{height}"
                self.add_log(f"检测到设备分辨率: {width}x{height}")

            if status["board_config"]["origin"]:
                origin = status["board_config"]["origin"]
                cell_size = status["board_config"]["cell_size"]
                self.add_log(f"棋盘配置: 起点{origin}, 格子大小{cell_size}")

            self.status_label.text = '已就绪'
            self.add_log("游戏引擎初始化完成，应用已就绪")

        except Exception as e:
            self.add_log(f"初始化失败: {str(e)}")
            Logger.error(f"MainApp: 初始化失败: {str(e)}")
    
    def toggle_start_pause(self, instance):
        """切换开始/暂停状态"""
        if not self.game_engine:
            self.add_log("游戏引擎未初始化")
            return

        if not self.is_running:
            # 开始游戏
            self.start_game()
        else:
            # 暂停/继续游戏
            if self.is_paused:
                self.resume_game()
            else:
                self.pause_game()

    def start_game(self):
        """开始游戏"""
        try:
            self.is_running = True
            self.is_paused = False
            self.start_pause_btn.text = '暂停'
            self.status_label.text = '运行中'

            # 启动游戏引擎
            self.game_engine.start_game()

            # 在后台线程中运行游戏
            threading.Thread(target=self.game_loop, daemon=True).start()
            self.add_log("游戏已开始")

        except Exception as e:
            self.add_log(f"启动游戏失败: {str(e)}")

    def pause_game(self):
        """暂停游戏"""
        self.is_paused = True
        self.start_pause_btn.text = '继续'
        self.status_label.text = '已暂停'
        if self.game_engine:
            self.game_engine.pause_game()
        self.add_log("游戏已暂停")

    def resume_game(self):
        """继续游戏"""
        self.is_paused = False
        self.start_pause_btn.text = '暂停'
        self.status_label.text = '运行中'
        if self.game_engine:
            self.game_engine.resume_game()
        self.add_log("游戏已继续")

    def stop_game(self, instance):
        """停止游戏"""
        self.is_running = False
        self.is_paused = True
        self.start_pause_btn.text = '开始'
        self.status_label.text = '已停止'
        if self.game_engine:
            self.game_engine.stop_game()
        self.add_log("游戏已停止")
    
    def game_loop(self):
        """游戏主循环 - 使用完整游戏引擎"""
        while self.is_running:
            if self.is_paused:
                time.sleep(0.5)
                continue

            try:
                # 执行一步游戏逻辑
                result = self.game_engine.execute_one_step()

                if result and result.get("status") == "success":
                    # 更新UI显示
                    Clock.schedule_once(lambda dt, r=result: self.update_game_status(r), 0)
                elif result and result.get("status") == "error":
                    Clock.schedule_once(lambda dt, msg=result.get("message", "未知错误"): self.add_log(f"错误: {msg}"), 0)

                time.sleep(1)  # 控制执行频率

            except Exception as e:
                Clock.schedule_once(lambda dt, err=str(e): self.add_log(f"游戏循环错误: {err}"), 0)
                time.sleep(2)

    def update_game_status(self, result):
        """更新游戏状态显示"""
        if 'steps' in result:
            self.steps_label.text = str(result['steps'])
        if 'score' in result:
            self.score_label.text = str(result['score'])
        if 'message' in result:
            self.add_log(result['message'])
        if 'swap' in result:
            swap = result['swap']
            self.add_log(f"执行交换: {swap[0]} -> {swap[1]}")
    
    def show_settings(self, instance):
        """显示设置对话框 - 简化版本"""
        # 创建简洁的设置弹窗
        content = BoxLayout(orientation='vertical', spacing=5, padding=10)

        # 目标步数设置
        content.add_widget(Label(text='目标步数:', size_hint_y=None, height=25, font_size=12))
        steps_input = TextInput(
            text=str(self.game_engine.TARGET_STEPS if self.game_engine else 30),
            multiline=False,
            size_hint_y=None,
            height=30,
            font_size=12
        )
        content.add_widget(steps_input)

        # 目标分数设置
        content.add_widget(Label(text='目标分数:', size_hint_y=None, height=25, font_size=12))
        score_input = TextInput(
            text=str(self.game_engine.SCORE_TARGET if self.game_engine else 1000),
            multiline=False,
            size_hint_y=None,
            height=30,
            font_size=12
        )
        content.add_widget(score_input)

        # 权限设置按钮
        permission_btn = Button(text='打开无障碍设置', size_hint_y=None, height=35, font_size=12)
        permission_btn.bind(on_press=self.open_accessibility_settings)
        content.add_widget(permission_btn)

        # 按钮布局
        btn_layout = BoxLayout(size_hint_y=None, height=40, spacing=5)

        # 保存按钮
        save_btn = Button(text='保存', font_size=12)
        def save_settings(instance):
            if self.game_engine:
                try:
                    self.game_engine.TARGET_STEPS = int(steps_input.text)
                    self.game_engine.SCORE_TARGET = int(score_input.text)
                    self.add_log("设置已保存")
                except ValueError:
                    self.add_log("设置值无效")
            popup.dismiss()
        save_btn.bind(on_press=save_settings)
        btn_layout.add_widget(save_btn)

        # 取消按钮
        cancel_btn = Button(text='取消', font_size=12)
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        btn_layout.add_widget(cancel_btn)

        content.add_widget(btn_layout)

        # 创建弹窗
        popup = Popup(
            title='设置',
            content=content,
            size_hint=(0.7, 0.5)
        )
        popup.open()

    def open_accessibility_settings(self, instance):
        """打开无障碍服务设置"""
        if platform == 'android':
            try:
                intent = Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)
                PythonActivity.mActivity.startActivity(intent)
                self.add_log("已打开无障碍设置")
            except Exception as e:
                self.add_log(f"打开设置失败")
        else:
            self.add_log("仅在Android可用")

if __name__ == '__main__':
    MainApp().run()
