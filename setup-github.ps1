# GitHub Setup Script for MHCS Android Build

Write-Host "========================================" -ForegroundColor Green
Write-Host "GitHub Setup for MHCS Android Build" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Check if git is installed
try {
    $gitVersion = git --version 2>&1
    Write-Host "Git installed: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "Git not found. Please install Git first:" -ForegroundColor Red
    Write-Host "https://git-scm.com/download/win" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Clean up unnecessary files
Write-Host "Cleaning up unnecessary files..." -ForegroundColor Yellow

# Remove cache directories
if (Test-Path "__pycache__") {
    Remove-Item -Recurse -Force "__pycache__"
    Write-Host "Removed __pycache__ directory" -ForegroundColor Green
}

if (Test-Path ".buildozer") {
    Remove-Item -Recurse -Force ".buildozer"
    Write-Host "Removed .buildozer directory" -ForegroundColor Green
}

if (Test-Path "bin") {
    Remove-Item -Recurse -Force "bin"
    Write-Host "Removed bin directory" -ForegroundColor Green
}

# Create .gitignore file
Write-Host "Creating .gitignore file..." -ForegroundColor Yellow
$gitignoreContent = @"
# Python
__pycache__/
*.py[cod]
*$py.class
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
"@

$gitignoreContent | Out-File -FilePath ".gitignore" -Encoding UTF8
Write-Host "Created .gitignore file" -ForegroundColor Green

# Initialize git repository
if (!(Test-Path ".git")) {
    Write-Host "Initializing Git repository..." -ForegroundColor Yellow
    git init
    Write-Host "Git repository initialized" -ForegroundColor Green
} else {
    Write-Host "Git repository already exists" -ForegroundColor Yellow
}

# Add all files
Write-Host "Adding files to Git..." -ForegroundColor Yellow
git add .

# Create initial commit
Write-Host "Creating initial commit..." -ForegroundColor Yellow
git commit -m "Initial commit: MHCS Android app with GitHub Actions build"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Next Steps:" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "1. Create a new repository on GitHub:" -ForegroundColor Yellow
Write-Host "   - Go to https://github.com/new" -ForegroundColor Cyan
Write-Host "   - Repository name: mhcs-android" -ForegroundColor Cyan
Write-Host "   - Make it Public (for free GitHub Actions)" -ForegroundColor Cyan
Write-Host "   - Do NOT initialize with README, .gitignore, or license" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Copy the repository URL (it will look like):" -ForegroundColor Yellow
Write-Host "   https://github.com/YOUR_USERNAME/mhcs-android.git" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Run these commands to push your code:" -ForegroundColor Yellow
Write-Host "   git remote add origin YOUR_REPOSITORY_URL" -ForegroundColor Cyan
Write-Host "   git branch -M main" -ForegroundColor Cyan
Write-Host "   git push -u origin main" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. After pushing, GitHub Actions will automatically:" -ForegroundColor Yellow
Write-Host "   - Start building your APK" -ForegroundColor Cyan
Write-Host "   - You can watch progress in the 'Actions' tab" -ForegroundColor Cyan
Write-Host "   - Download the APK from 'Artifacts' when complete" -ForegroundColor Cyan
Write-Host ""
Write-Host "Example commands (replace YOUR_USERNAME):" -ForegroundColor Green
Write-Host "git remote add origin https://github.com/YOUR_USERNAME/mhcs-android.git" -ForegroundColor White
Write-Host "git branch -M main" -ForegroundColor White
Write-Host "git push -u origin main" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to exit"
