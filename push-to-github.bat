@echo off
chcp 65001 >nul
echo ========================================
echo 推送代码到GitHub
echo ========================================

REM 检查Git是否安装
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Git未安装，请先安装Git：
    echo https://git-scm.com/download/win
    pause
    exit /b 1
)

echo Git已安装

REM 获取GitHub用户名
set /p USERNAME="请输入您的GitHub用户名: "
if "%USERNAME%"=="" (
    echo 用户名不能为空
    pause
    exit /b 1
)

echo 您的GitHub用户名: %USERNAME%
echo 仓库URL: https://github.com/%USERNAME%/mhcs-floating.git

REM 确认信息
set /p CONFIRM="确认信息正确吗？(y/n): "
if /i not "%CONFIRM%"=="y" (
    echo 操作已取消
    pause
    exit /b 1
)

echo.
echo 开始推送代码...

REM 清理不需要的文件
echo 清理项目文件...
if exist "__pycache__" rmdir /s /q "__pycache__"
if exist ".buildozer" rmdir /s /q ".buildozer"
if exist "bin" rmdir /s /q "bin"

REM 删除不需要的文件
if exist "main.py" del "main.py"
if exist "game_core.py" del "game_core.py"
if exist "screen_capture.py" del "screen_capture.py"
if exist "touch_controller.py" del "touch_controller.py"
if exist "model_manager.py" del "model_manager.py"
if exist "service.py" del "service.py"
if exist "mhcs.py" del "mhcs.py"
if exist "build*.py" del "build*.py"
if exist "build*.bat" del "build*.bat"
if exist "build*.ps1" del "build*.ps1"
if exist "Dockerfile" del "Dockerfile"
if exist "docker*" del "docker*"

echo 文件清理完成

REM 创建.gitignore
echo 创建.gitignore...
(
echo # Python
echo __pycache__/
echo *.py[cod]
echo *.so
echo .Python
echo build/
echo dist/
echo *.egg-info/
echo.
echo # Buildozer
echo .buildozer/
echo bin/
echo.
echo # Android
echo *.apk
echo *.aab
echo.
echo # IDE
echo .vscode/
echo .idea/
echo.
echo # OS
echo .DS_Store
echo Thumbs.db
echo.
echo # Logs
echo *.log
) > .gitignore

REM 初始化Git仓库
echo 初始化Git仓库...
if not exist ".git" (
    git init
    echo Git仓库初始化完成
) else (
    echo Git仓库已存在
)

REM 添加文件
echo 添加文件到Git...
git add .

REM 创建提交
echo 创建提交...
git commit -m "满汉助手悬浮窗版本 - 完整保留原版算法"

REM 添加远程仓库
echo 添加远程仓库...
git remote remove origin 2>nul
git remote add origin https://github.com/%USERNAME%/mhcs-floating.git

REM 设置主分支
echo 设置主分支...
git branch -M main

REM 推送代码
echo 推送代码到GitHub...
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo 代码推送成功！
    echo ========================================
    echo.
    echo 下一步：
    echo 1. 访问您的仓库: https://github.com/%USERNAME%/mhcs-floating
    echo 2. 点击 "Actions" 标签查看构建进度
    echo 3. 构建完成后在 "Artifacts" 下载APK
    echo.
    echo 首次构建大约需要20-30分钟
    echo 请耐心等待...
) else (
    echo.
    echo 推送失败，可能的原因：
    echo 1. 网络连接问题
    echo 2. GitHub认证问题
    echo 3. 仓库权限问题
    echo.
    echo 请检查网络连接和GitHub登录状态
)

echo.
pause
