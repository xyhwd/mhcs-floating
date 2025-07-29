# 满汉助手悬浮窗版本构建脚本

Write-Host "========================================" -ForegroundColor Green
Write-Host "满汉助手悬浮窗版本构建脚本" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# 检查Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "Python未安装" -ForegroundColor Red
    Read-Host "按Enter退出"
    exit 1
}

# 安装依赖
Write-Host "安装依赖..." -ForegroundColor Yellow
try {
    python -m pip install --upgrade pip
    python -m pip install buildozer cython kivy
    Write-Host "依赖安装完成" -ForegroundColor Green
}
catch {
    Write-Host "依赖安装失败" -ForegroundColor Red
    Read-Host "按Enter退出"
    exit 1
}

# 检查文件
Write-Host "检查项目文件..." -ForegroundColor Yellow

$requiredFiles = @("floating_main.py", "mobile_game_engine.py", "buildozer.spec")

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "找到: $file" -ForegroundColor Green
    } else {
        Write-Host "缺少: $file" -ForegroundColor Red
        Read-Host "按Enter退出"
        exit 1
    }
}

# 创建目录
if (!(Test-Path "model")) {
    New-Item -ItemType Directory -Path "model"
}

# 检查模型文件
if (!(Test-Path "model\best.pt")) {
    Write-Host "模型文件不存在，创建空文件..." -ForegroundColor Yellow
    New-Item -ItemType File -Path "model\best.pt" -Force
}

# 清理构建
Write-Host "清理构建目录..." -ForegroundColor Yellow
if (Test-Path ".buildozer") {
    Remove-Item -Recurse -Force ".buildozer"
}
if (Test-Path "bin") {
    Remove-Item -Recurse -Force "bin"
}

# 构建APK
Write-Host "开始构建悬浮窗APK..." -ForegroundColor Yellow
Write-Host "这可能需要较长时间..." -ForegroundColor Yellow

try {
    buildozer android debug

    # 检查结果
    $apkFiles = Get-ChildItem "bin\*.apk" -ErrorAction SilentlyContinue
    if ($apkFiles) {
        Write-Host "悬浮窗APK构建成功！" -ForegroundColor Green
        Write-Host "APK文件:" -ForegroundColor Green
        $apkFiles | ForEach-Object { Write-Host $_.FullName -ForegroundColor Cyan }

        Write-Host ""
        Write-Host "使用说明:" -ForegroundColor Yellow
        Write-Host "1. 安装APK到Android设备" -ForegroundColor White
        Write-Host "2. 启用无障碍服务权限" -ForegroundColor White
        Write-Host "3. 打开游戏后点击'开始'按钮" -ForegroundColor White
        Write-Host "4. 悬浮窗会显示运行状态" -ForegroundColor White

    }
    else {
        Write-Host "APK构建失败" -ForegroundColor Red
        Write-Host "建议使用GitHub Actions云构建" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "构建过程出错: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "建议使用GitHub Actions云构建" -ForegroundColor Yellow
}

Write-Host "========================================" -ForegroundColor Green
Write-Host "构建完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Read-Host "按Enter退出"
