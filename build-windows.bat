@echo off
echo ========================================
echo 满汉助手 Android APK 构建脚本 (Windows)
echo ========================================

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python未安装或未添加到PATH
    echo 请安装Python 3.8+并添加到系统PATH
    pause
    exit /b 1
)
echo ✅ Python已安装

REM 检查Java是否安装
java -version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Java未安装或未添加到PATH
    echo 请安装JDK 8+并添加到系统PATH
    pause
    exit /b 1
)
echo ✅ Java已安装

REM 安装必要的Python包
echo 安装Python依赖包...
python -m pip install --upgrade pip
python -m pip install buildozer
python -m pip install cython
python -m pip install kivy
python -m pip install kivymd
python -m pip install numpy
python -m pip install pillow

REM 检查必要文件
echo 检查项目文件...
if not exist "main.py" (
    echo ❌ 缺少文件: main.py
    pause
    exit /b 1
)
echo ✅ 找到文件: main.py

if not exist "buildozer.spec" (
    echo ❌ 缺少文件: buildozer.spec
    pause
    exit /b 1
)
echo ✅ 找到文件: buildozer.spec

REM 检查模型文件
if not exist "model\best.pt" (
    echo ⚠️  模型文件不存在: model\best.pt
    echo    应用将在模拟模式下运行
    if not exist "model" mkdir model
    echo. > model\best.pt
) else (
    echo ✅ 找到模型文件: model\best.pt
)

REM 创建必要目录
if not exist "assets" mkdir assets

REM 清理之前的构建
echo 清理构建目录...
if exist ".buildozer" rmdir /s /q .buildozer
if exist "bin" rmdir /s /q bin

REM 尝试构建APK
echo 开始构建APK...
echo 注意: 在Windows上构建Android APK需要额外配置
echo 如果构建失败，请考虑使用Linux环境或Docker

buildozer android debug

REM 检查构建结果
if exist "bin\*.apk" (
    echo ✅ APK构建成功！
    echo 📱 APK文件位置:
    dir bin\*.apk
) else (
    echo ❌ APK构建失败
    echo 建议使用以下替代方案:
    echo 1. 使用WSL (Windows Subsystem for Linux)
    echo 2. 使用Docker构建
    echo 3. 使用GitHub Actions云构建
)

echo ========================================
echo 构建完成！
echo ========================================
pause
