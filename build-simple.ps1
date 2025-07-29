# MHCS Android APK Build Script (PowerShell)

Write-Host "========================================" -ForegroundColor Green
Write-Host "MHCS Android APK Build Script (Windows)" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Check Python installation
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python installed: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python not found. Please install Python 3.8+" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Install Python packages
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
try {
    python -m pip install --upgrade pip
    python -m pip install buildozer
    python -m pip install cython
    python -m pip install kivy
    Write-Host "Dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check required files
Write-Host "Checking project files..." -ForegroundColor Yellow

$requiredFiles = @("main.py", "buildozer.spec")

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "Found file: $file" -ForegroundColor Green
    } else {
        Write-Host "Missing file: $file" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Create necessary directories
if (!(Test-Path "model")) {
    New-Item -ItemType Directory -Path "model"
}
if (!(Test-Path "assets")) {
    New-Item -ItemType Directory -Path "assets"
}

# Check model file
if (!(Test-Path "model\best.pt")) {
    Write-Host "Model file not found, creating empty file..." -ForegroundColor Yellow
    New-Item -ItemType File -Path "model\best.pt" -Force
}

# Clean previous builds
Write-Host "Cleaning build directories..." -ForegroundColor Yellow
if (Test-Path ".buildozer") {
    Remove-Item -Recurse -Force ".buildozer"
}
if (Test-Path "bin") {
    Remove-Item -Recurse -Force "bin"
}

# Build APK
Write-Host "Starting APK build..." -ForegroundColor Yellow
Write-Host "This may take a long time on first build..." -ForegroundColor Yellow

try {
    buildozer android debug
    
    # Check build result
    $apkFiles = Get-ChildItem "bin\*.apk" -ErrorAction SilentlyContinue
    if ($apkFiles) {
        Write-Host "APK build successful!" -ForegroundColor Green
        Write-Host "APK files:" -ForegroundColor Green
        $apkFiles | ForEach-Object { Write-Host $_.FullName -ForegroundColor Cyan }
    } else {
        Write-Host "APK build failed" -ForegroundColor Red
        Write-Host "Consider using alternative build methods:" -ForegroundColor Yellow
        Write-Host "1. WSL (Windows Subsystem for Linux)" -ForegroundColor Yellow
        Write-Host "2. Docker build" -ForegroundColor Yellow
        Write-Host "3. GitHub Actions cloud build" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Build error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Consider using alternative build methods" -ForegroundColor Yellow
}

Write-Host "========================================" -ForegroundColor Green
Write-Host "Build completed!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Read-Host "Press Enter to exit"
