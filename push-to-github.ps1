# Push to GitHub Script

Write-Host "========================================" -ForegroundColor Green
Write-Host "Push Code to GitHub" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Check Git
try {
    $gitVersion = git --version 2>&1
    Write-Host "Git installed: $gitVersion" -ForegroundColor Green
}
catch {
    Write-Host "Git not installed. Please install Git first:" -ForegroundColor Red
    Write-Host "https://git-scm.com/download/win" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Get GitHub username
$USERNAME = Read-Host "Enter your GitHub username"
if ([string]::IsNullOrEmpty($USERNAME)) {
    Write-Host "Username cannot be empty" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "GitHub username: $USERNAME" -ForegroundColor Cyan
Write-Host "Repository URL: https://github.com/$USERNAME/mhcs-floating.git" -ForegroundColor Cyan

# Confirm
$CONFIRM = Read-Host "Is this information correct? (y/n)"
if ($CONFIRM -ne "y" -and $CONFIRM -ne "Y") {
    Write-Host "Operation cancelled" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Starting to push code..." -ForegroundColor Yellow

# Clean up files
Write-Host "Cleaning project files..." -ForegroundColor Yellow

# Remove cache directories
$dirsToRemove = @("__pycache__", ".buildozer", "bin")
foreach ($dir in $dirsToRemove) {
    if (Test-Path $dir) {
        Remove-Item -Recurse -Force $dir
        Write-Host "Removed: $dir" -ForegroundColor Green
    }
}

# Remove unnecessary files
$filesToRemove = @(
    "main.py", "game_core.py", "screen_capture.py", "touch_controller.py", 
    "model_manager.py", "service.py", "mhcs.py", "build.py",
    "build-windows.bat", "build-windows.ps1", "build-simple.ps1",
    "build-floating.bat", "build-floating.ps1", "Dockerfile",
    "docker-build.sh", "docker-compose.yml", "push-to-github.bat"
)

foreach ($file in $filesToRemove) {
    if (Test-Path $file) {
        Remove-Item -Force $file
        Write-Host "Removed: $file" -ForegroundColor Green
    }
}

Write-Host "File cleanup completed" -ForegroundColor Green

# Create .gitignore
Write-Host "Creating .gitignore..." -ForegroundColor Yellow
$gitignoreContent = @"
# Python
__pycache__/
*.py[cod]
*.so
.Python
build/
dist/
*.egg-info/

# Buildozer
.buildozer/
bin/

# Android
*.apk
*.aab

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Logs
*.log
"@

$gitignoreContent | Out-File -FilePath ".gitignore" -Encoding UTF8
Write-Host ".gitignore created" -ForegroundColor Green

# Initialize Git repository
Write-Host "Initializing Git repository..." -ForegroundColor Yellow
if (!(Test-Path ".git")) {
    git init
    Write-Host "Git repository initialized" -ForegroundColor Green
}
else {
    Write-Host "Git repository already exists" -ForegroundColor Yellow
}

# Add files
Write-Host "Adding files to Git..." -ForegroundColor Yellow
git add .

# Create commit
Write-Host "Creating commit..." -ForegroundColor Yellow
git commit -m "MHCS Floating Window Version - Complete Original Algorithm"

# Add remote repository
Write-Host "Adding remote repository..." -ForegroundColor Yellow
try {
    git remote remove origin 2>$null
}
catch {
    # Ignore error if origin doesn't exist
}
git remote add origin "https://github.com/$USERNAME/mhcs-floating.git"

# Set main branch
Write-Host "Setting main branch..." -ForegroundColor Yellow
git branch -M main

# Push code
Write-Host "Pushing code to GitHub..." -ForegroundColor Yellow
try {
    git push -u origin main
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Code pushed successfully!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Visit your repository: https://github.com/$USERNAME/mhcs-floating" -ForegroundColor Cyan
    Write-Host "2. Click 'Actions' tab to view build progress" -ForegroundColor Cyan
    Write-Host "3. Download APK from 'Artifacts' when build completes" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "First build takes about 20-30 minutes" -ForegroundColor Yellow
    Write-Host "Please be patient..." -ForegroundColor Yellow
}
catch {
    Write-Host ""
    Write-Host "Push failed. Possible reasons:" -ForegroundColor Red
    Write-Host "1. Network connection issues" -ForegroundColor Yellow
    Write-Host "2. GitHub authentication issues" -ForegroundColor Yellow
    Write-Host "3. Repository permission issues" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please check your network connection and GitHub login status" -ForegroundColor Yellow
}

Write-Host ""
Read-Host "Press Enter to exit"
