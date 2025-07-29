@echo off
chcp 65001 >nul
echo ========================================
echo 满汉助手悬浮窗版本 - 最终设置
echo ========================================

echo 正在清理项目文件...

REM 删除不需要的Python文件
if exist "main.py" del "main.py"
if exist "game_core.py" del "game_core.py"
if exist "screen_capture.py" del "screen_capture.py"
if exist "touch_controller.py" del "touch_controller.py"
if exist "model_manager.py" del "model_manager.py"
if exist "service.py" del "service.py"
if exist "mhcs.py" del "mhcs.py"

REM 删除构建脚本
if exist "build.py" del "build.py"
if exist "build-windows.bat" del "build-windows.bat"
if exist "build-windows.ps1" del "build-windows.ps1"
if exist "build-simple.ps1" del "build-simple.ps1"
if exist "build-floating.bat" del "build-floating.bat"
if exist "build-floating.ps1" del "build-floating.ps1"

REM 删除Docker文件
if exist "Dockerfile" del "Dockerfile"
if exist "docker-build.sh" del "docker-build.sh"
if exist "docker-compose.yml" del "docker-compose.yml"

REM 删除缓存目录
if exist "__pycache__" rmdir /s /q "__pycache__"
if exist ".buildozer" rmdir /s /q ".buildozer"
if exist "bin" rmdir /s /q "bin"

echo 文件清理完成

echo 检查必要文件...
if exist "floating_main.py" (
    echo ✓ floating_main.py
) else (
    echo ✗ floating_main.py 缺失
)

if exist "mobile_game_engine.py" (
    echo ✓ mobile_game_engine.py
) else (
    echo ✗ mobile_game_engine.py 缺失
)

if exist "buildozer.spec" (
    echo ✓ buildozer.spec
) else (
    echo ✗ buildozer.spec 缺失
)

if exist ".github\workflows\build-apk.yml" (
    echo ✓ GitHub Actions配置
) else (
    echo ✗ GitHub Actions配置缺失
)

echo.
echo ========================================
echo 项目已准备就绪！
echo ========================================
echo.
echo 下一步操作：
echo 1. 访问 https://github.com/new 创建新仓库
echo 2. 仓库名：mhcs-floating
echo 3. 设为Public
echo 4. 不要初始化任何文件
echo.
echo 然后运行以下命令：
echo git init
echo git add .
echo git commit -m "满汉助手悬浮窗版本"
echo git remote add origin https://github.com/YOUR_USERNAME/mhcs-floating.git
echo git branch -M main
echo git push -u origin main
echo.
echo 推送后GitHub会自动构建APK！
echo.
pause
