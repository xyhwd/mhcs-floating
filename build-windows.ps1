# 满汉助手 Android APK 构建脚本 (PowerShell)

Write-Host "========================================" -ForegroundColor Green
Write-Host "满汉助手 Android APK 构建脚本 (Windows)" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# 检查Python是否安装
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python已安装: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python未安装或未添加到PATH" -ForegroundColor Red
    Write-Host "请安装Python 3.8+并添加到系统PATH" -ForegroundColor Yellow
    Read-Host "按Enter键退出"
    exit 1
}

# 检查Java是否安装
try {
    $javaVersion = java -version 2>&1
    Write-Host "✅ Java已安装" -ForegroundColor Green
} catch {
    Write-Host "❌ Java未安装或未添加到PATH" -ForegroundColor Red
    Write-Host "请安装JDK 8+并添加到系统PATH" -ForegroundColor Yellow
    Read-Host "按Enter键退出"
    exit 1
}

# 安装必要的Python包
Write-Host "安装Python依赖包..." -ForegroundColor Yellow
try {
    python -m pip install --upgrade pip
    python -m pip install buildozer
    python -m pip install cython
    python -m pip install kivy
    python -m pip install kivymd
    python -m pip install numpy
    python -m pip install pillow
    Write-Host "✅ Python依赖安装完成" -ForegroundColor Green
} catch {
    Write-Host "❌ Python依赖安装失败" -ForegroundColor Red
    Read-Host "按Enter键退出"
    exit 1
}

# 检查必要文件
Write-Host "检查项目文件..." -ForegroundColor Yellow

$requiredFiles = @("main.py", "game_core.py", "screen_capture.py", "touch_controller.py", "model_manager.py", "buildozer.spec")

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✅ 找到文件: $file" -ForegroundColor Green
    } else {
        Write-Host "❌ 缺少文件: $file" -ForegroundColor Red
        Read-Host "按Enter键退出"
        exit 1
    }
}

# 检查模型文件
if (Test-Path "model\best.pt") {
    Write-Host "✅ 找到模型文件: model\best.pt" -ForegroundColor Green
} else {
    Write-Host "⚠️  模型文件不存在: model\best.pt" -ForegroundColor Yellow
    Write-Host "   应用将在模拟模式下运行" -ForegroundColor Yellow
    if (!(Test-Path "model")) {
        New-Item -ItemType Directory -Path "model"
    }
    New-Item -ItemType File -Path "model\best.pt" -Force
}

# 创建必要目录
if (!(Test-Path "assets")) {
    New-Item -ItemType Directory -Path "assets"
}

# 清理之前的构建
Write-Host "清理构建目录..." -ForegroundColor Yellow
if (Test-Path ".buildozer") {
    Remove-Item -Recurse -Force ".buildozer"
}
if (Test-Path "bin") {
    Remove-Item -Recurse -Force "bin"
}

# 尝试构建APK
Write-Host "开始构建APK..." -ForegroundColor Yellow
Write-Host "注意: 在Windows上构建Android APK需要额外配置" -ForegroundColor Yellow
Write-Host "如果构建失败，请考虑使用Linux环境或Docker" -ForegroundColor Yellow

try {
    buildozer android debug
    
    # 检查构建结果
    if (Test-Path "bin\*.apk") {
        Write-Host "✅ APK构建成功！" -ForegroundColor Green
        Write-Host "📱 APK文件位置:" -ForegroundColor Green
        Get-ChildItem "bin\*.apk" | ForEach-Object { Write-Host $_.FullName -ForegroundColor Cyan }
    } else {
        Write-Host "❌ APK构建失败" -ForegroundColor Red
        Write-Host "建议使用以下替代方案:" -ForegroundColor Yellow
        Write-Host "1. 使用WSL (Windows Subsystem for Linux)" -ForegroundColor Yellow
        Write-Host "2. 使用Docker构建" -ForegroundColor Yellow
        Write-Host "3. 使用GitHub Actions云构建" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ 构建过程中出现错误: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "建议使用替代构建方案" -ForegroundColor Yellow
}

Write-Host "========================================" -ForegroundColor Green
Write-Host "构建完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Read-Host "按Enter键退出"
