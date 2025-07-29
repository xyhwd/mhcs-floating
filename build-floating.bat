@echo off
chcp 65001 >nul
echo ========================================
echo 满汉助手悬浮窗版本构建脚本
echo ========================================

REM 检查Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python未安装
    pause
    exit /b 1
)
echo Python已安装

REM 安装依赖
echo 安装依赖...
python -m pip install --upgrade pip
python -m pip install buildozer cython kivy

REM 检查文件
echo 检查项目文件...
if not exist "floating_main.py" (
    echo 缺少文件: floating_main.py
    pause
    exit /b 1
)
echo 找到: floating_main.py

if not exist "mobile_game_engine.py" (
    echo 缺少文件: mobile_game_engine.py
    pause
    exit /b 1
)
echo 找到: mobile_game_engine.py

if not exist "buildozer.spec" (
    echo 缺少文件: buildozer.spec
    pause
    exit /b 1
)
echo 找到: buildozer.spec

REM 创建目录
if not exist "model" mkdir model

REM 检查模型文件
if not exist "model\best.pt" (
    echo 模型文件不存在，创建空文件...
    echo. > model\best.pt
)

REM 清理构建
echo 清理构建目录...
if exist ".buildozer" rmdir /s /q .buildozer
if exist "bin" rmdir /s /q bin

REM 构建APK
echo 开始构建悬浮窗APK...
echo 这可能需要较长时间...

buildozer android debug

REM 检查结果
if exist "bin\*.apk" (
    echo 悬浮窗APK构建成功！
    echo APK文件:
    dir bin\*.apk
    echo.
    echo 使用说明:
    echo 1. 安装APK到Android设备
    echo 2. 启用无障碍服务权限
    echo 3. 打开游戏后点击开始按钮
    echo 4. 悬浮窗会显示运行状态
) else (
    echo APK构建失败
    echo 建议使用GitHub Actions云构建
)

echo ========================================
echo 构建完成！
echo ========================================
pause
