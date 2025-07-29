#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
满汉助手 Android版本构建脚本
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_requirements():
    """检查构建环境"""
    print("检查构建环境...")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ Python版本需要3.8+")
        return False
    print("✅ Python版本检查通过")
    
    # 检查buildozer
    try:
        result = subprocess.run(['buildozer', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Buildozer已安装")
        else:
            print("❌ Buildozer未正确安装")
            return False
    except FileNotFoundError:
        print("❌ Buildozer未安装，请运行: pip install buildozer")
        return False
    
    # 检查Java
    try:
        result = subprocess.run(['java', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Java已安装")
        else:
            print("❌ Java未安装")
            return False
    except FileNotFoundError:
        print("❌ Java未安装，请安装JDK 8+")
        return False
    
    return True

def prepare_files():
    """准备构建文件"""
    print("准备构建文件...")
    
    # 检查必要文件
    required_files = [
        'main.py',
        'game_core.py', 
        'screen_capture.py',
        'touch_controller.py',
        'model_manager.py',
        'buildozer.spec'
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ 缺少文件: {file}")
            return False
        print(f"✅ 找到文件: {file}")
    
    # 创建必要目录
    os.makedirs('model', exist_ok=True)
    os.makedirs('assets', exist_ok=True)
    
    # 检查模型文件
    model_file = 'model/best.pt'
    if not os.path.exists(model_file):
        print(f"⚠️  模型文件不存在: {model_file}")
        print("   应用将在模拟模式下运行")
    else:
        print(f"✅ 找到模型文件: {model_file}")
    
    return True

def clean_build():
    """清理构建目录"""
    print("清理构建目录...")
    
    dirs_to_clean = ['.buildozer', 'bin']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✅ 清理目录: {dir_name}")
    
    print("构建目录清理完成")

def build_debug():
    """构建调试版APK"""
    print("开始构建调试版APK...")
    
    try:
        # 运行buildozer构建命令
        result = subprocess.run(
            ['buildozer', 'android', 'debug'],
            cwd=os.getcwd(),
            text=True
        )
        
        if result.returncode == 0:
            print("✅ 调试版APK构建成功！")
            
            # 查找生成的APK文件
            bin_dir = Path('bin')
            if bin_dir.exists():
                apk_files = list(bin_dir.glob('*.apk'))
                if apk_files:
                    print(f"📱 APK文件位置: {apk_files[0]}")
                    return True
            
            print("⚠️  APK文件未找到")
            return False
        else:
            print("❌ 构建失败")
            return False
            
    except Exception as e:
        print(f"❌ 构建过程中出现异常: {str(e)}")
        return False

def build_release():
    """构建发布版APK"""
    print("开始构建发布版APK...")
    
    try:
        # 运行buildozer构建命令
        result = subprocess.run(
            ['buildozer', 'android', 'release'],
            cwd=os.getcwd(),
            text=True
        )
        
        if result.returncode == 0:
            print("✅ 发布版APK构建成功！")
            
            # 查找生成的APK文件
            bin_dir = Path('bin')
            if bin_dir.exists():
                apk_files = list(bin_dir.glob('*-release*.apk'))
                if apk_files:
                    print(f"📱 APK文件位置: {apk_files[0]}")
                    return True
            
            print("⚠️  APK文件未找到")
            return False
        else:
            print("❌ 构建失败")
            return False
            
    except Exception as e:
        print(f"❌ 构建过程中出现异常: {str(e)}")
        return False

def install_dependencies():
    """安装Python依赖"""
    print("安装Python依赖...")
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
            text=True
        )
        
        if result.returncode == 0:
            print("✅ 依赖安装成功")
            return True
        else:
            print("❌ 依赖安装失败")
            return False
            
    except Exception as e:
        print(f"❌ 安装依赖时出现异常: {str(e)}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("满汉助手 Android版本构建脚本")
    print("=" * 50)
    
    # 解析命令行参数
    if len(sys.argv) < 2:
        print("用法:")
        print("  python build.py debug    - 构建调试版APK")
        print("  python build.py release  - 构建发布版APK")
        print("  python build.py clean    - 清理构建目录")
        print("  python build.py deps     - 安装依赖")
        print("  python build.py check    - 检查环境")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'check':
        if check_requirements():
            print("✅ 环境检查通过")
        else:
            print("❌ 环境检查失败")
        return
    
    elif command == 'deps':
        install_dependencies()
        return
    
    elif command == 'clean':
        clean_build()
        return
    
    elif command in ['debug', 'release']:
        # 完整的构建流程
        if not check_requirements():
            print("❌ 环境检查失败，请先解决环境问题")
            return
        
        if not prepare_files():
            print("❌ 文件准备失败")
            return
        
        if command == 'debug':
            success = build_debug()
        else:
            success = build_release()
        
        if success:
            print("\n🎉 构建完成！")
            print("\n下一步:")
            print("1. 将APK文件传输到Android设备")
            print("2. 在设备上启用'未知来源'安装")
            print("3. 安装APK并授予必要权限")
        else:
            print("\n❌ 构建失败，请检查错误信息")
    
    else:
        print(f"❌ 未知命令: {command}")

if __name__ == '__main__':
    main()
