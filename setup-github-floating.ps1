# GitHub云构建设置脚本 - 悬浮窗版本

Write-Host "========================================" -ForegroundColor Green
Write-Host "满汉助手悬浮窗版本 - GitHub云构建设置" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# 检查Git
try {
    $gitVersion = git --version 2>&1
    Write-Host "Git: $gitVersion" -ForegroundColor Green
}
catch {
    Write-Host "Git未安装，请先安装Git:" -ForegroundColor Red
    Write-Host "https://git-scm.com/download/win" -ForegroundColor Yellow
    Read-Host "按Enter退出"
    exit 1
}

# 清理不需要的文件
Write-Host "清理项目文件..." -ForegroundColor Yellow

# 删除缓存目录
$dirsToRemove = @("__pycache__", ".buildozer", "bin", ".pytest_cache")
foreach ($dir in $dirsToRemove) {
    if (Test-Path $dir) {
        Remove-Item -Recurse -Force $dir
        Write-Host "删除: $dir" -ForegroundColor Green
    }
}

# 删除不需要的文件
$filesToRemove = @("main.py", "game_core.py", "screen_capture.py", "touch_controller.py", "model_manager.py", "service.py", "build-windows.bat", "build-windows.ps1", "build-simple.ps1", "build.py")
foreach ($file in $filesToRemove) {
    if (Test-Path $file) {
        Remove-Item -Force $file
        Write-Host "删除: $file" -ForegroundColor Green
    }
}

# 创建.gitignore
Write-Host "创建.gitignore..." -ForegroundColor Yellow
$gitignoreContent = @"
# Python
__pycache__/
*.py[cod]
*`$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Buildozer
.buildozer/
bin/

# Android
*.apk
*.aab

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Local config
local_config.py

# Temporary files
*.tmp
*.temp
"@

$gitignoreContent | Out-File -FilePath ".gitignore" -Encoding UTF8
Write-Host "创建.gitignore完成" -ForegroundColor Green

# 检查必要文件
Write-Host "检查项目文件..." -ForegroundColor Yellow
$requiredFiles = @("floating_main.py", "mobile_game_engine.py", "buildozer.spec", ".github/workflows/build-apk.yml")

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "找到: $file" -ForegroundColor Green
    }
    else {
        Write-Host "缺少: $file" -ForegroundColor Red
    }
}

# 确保model目录存在
if (!(Test-Path "model")) {
    New-Item -ItemType Directory -Path "model"
    Write-Host "创建model目录" -ForegroundColor Green
}

# 创建空的模型文件（如果不存在）
if (!(Test-Path "model/best.pt")) {
    New-Item -ItemType File -Path "model/best.pt" -Force
    Write-Host "创建空模型文件" -ForegroundColor Green
}

# 初始化Git仓库
if (!(Test-Path ".git")) {
    Write-Host "初始化Git仓库..." -ForegroundColor Yellow
    git init
    Write-Host "Git仓库初始化完成" -ForegroundColor Green
}
else {
    Write-Host "Git仓库已存在" -ForegroundColor Yellow
}

# 添加文件到Git
Write-Host "添加文件到Git..." -ForegroundColor Yellow
git add .

# 创建提交
Write-Host "创建提交..." -ForegroundColor Yellow
git commit -m "满汉助手悬浮窗版本 - 完整保留原版算法"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "GitHub云构建设置完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "下一步操作:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. 创建GitHub仓库:" -ForegroundColor White
Write-Host "   - 访问: https://github.com/new" -ForegroundColor Cyan
Write-Host "   - 仓库名: mhcs-floating" -ForegroundColor Cyan
Write-Host "   - 设为Public (免费使用GitHub Actions)" -ForegroundColor Cyan
Write-Host "   - 不要初始化README、.gitignore或license" -ForegroundColor Cyan
Write-Host ""

Write-Host "2. 推送代码到GitHub:" -ForegroundColor White
Write-Host "   git remote add origin https://github.com/YOUR_USERNAME/mhcs-floating.git" -ForegroundColor Cyan
Write-Host "   git branch -M main" -ForegroundColor Cyan
Write-Host "   git push -u origin main" -ForegroundColor Cyan
Write-Host ""

Write-Host "3. 自动构建:" -ForegroundColor White
Write-Host "   - 推送后GitHub Actions自动开始构建" -ForegroundColor Cyan
Write-Host "   - 在仓库的'Actions'标签查看构建进度" -ForegroundColor Cyan
Write-Host "   - 构建完成后在'Artifacts'下载APK" -ForegroundColor Cyan
Write-Host ""

Write-Host "4. 构建时间:" -ForegroundColor White
Write-Host "   - 首次构建: 约20-30分钟" -ForegroundColor Cyan
Write-Host "   - 后续构建: 约10-15分钟" -ForegroundColor Cyan
Write-Host ""

Write-Host "示例命令 (请替换YOUR_USERNAME):" -ForegroundColor Green
Write-Host "git remote add origin https://github.com/YOUR_USERNAME/mhcs-floating.git" -ForegroundColor White
Write-Host "git branch -M main" -ForegroundColor White
Write-Host "git push -u origin main" -ForegroundColor White
Write-Host ""

Write-Host "构建完成后，您将获得:" -ForegroundColor Yellow
Write-Host "- 悬浮窗APK文件 (约15-20MB)" -ForegroundColor Cyan
Write-Host "- 完整保留原版算法" -ForegroundColor Cyan
Write-Host "- 180x120像素小窗口" -ForegroundColor Cyan
Write-Host "- 一键开始/暂停功能" -ForegroundColor Cyan

Read-Host "按Enter退出"
