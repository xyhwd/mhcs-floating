#!/bin/bash

echo "========================================"
echo "满汉助手 Android APK 构建脚本"
echo "========================================"

# 设置错误时退出
set -e

# 检查必要文件
echo "检查项目文件..."
required_files=("main.py" "game_core.py" "screen_capture.py" "touch_controller.py" "model_manager.py" "buildozer.spec")

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ 缺少文件: $file"
        exit 1
    fi
    echo "✅ 找到文件: $file"
done

# 检查模型文件
if [ ! -f "model/best.pt" ]; then
    echo "⚠️  模型文件不存在: model/best.pt"
    echo "   应用将在模拟模式下运行"
    mkdir -p model
    touch model/best.pt  # 创建空文件避免构建错误
else
    echo "✅ 找到模型文件: model/best.pt"
fi

# 创建必要目录
mkdir -p assets

# 清理之前的构建
echo "清理构建目录..."
rm -rf .buildozer bin

# 接受Android SDK许可
echo "接受Android SDK许可..."
yes | $ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager --licenses > /dev/null 2>&1

# 构建APK
echo "开始构建APK..."
echo "这可能需要较长时间，请耐心等待..."

# 设置buildozer环境变量
export BUILDOZER_LOG_LEVEL=2
export ANDROID_API=30
export ANDROID_NDK_VERSION=23b

# 执行构建
buildozer android debug

# 检查构建结果
if [ -d "bin" ] && [ -n "$(ls -A bin/*.apk 2>/dev/null)" ]; then
    echo "✅ APK构建成功！"
    echo "📱 APK文件位置:"
    ls -la bin/*.apk
    
    # 复制APK到输出目录
    mkdir -p /output
    cp bin/*.apk /output/
    echo "APK已复制到 /output/ 目录"
else
    echo "❌ APK构建失败"
    exit 1
fi

echo "========================================"
echo "构建完成！"
echo "========================================"
