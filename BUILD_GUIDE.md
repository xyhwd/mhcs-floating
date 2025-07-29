# 满汉助手 Android APK 构建指南

本指南提供了多种构建Android APK的方法，您可以根据自己的环境选择最适合的方式。

## 🚀 快速开始

### 方法1: 使用GitHub Actions (推荐)

这是最简单的方法，无需本地配置复杂环境。

1. **上传代码到GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/mhcs-android.git
   git push -u origin main
   ```

2. **触发自动构建**
   - 推送代码后，GitHub Actions会自动开始构建
   - 在GitHub仓库的"Actions"标签页查看构建进度
   - 构建完成后，在"Artifacts"中下载APK文件

3. **手动触发构建**
   - 在GitHub仓库页面，点击"Actions"
   - 选择"Build Android APK"工作流
   - 点击"Run workflow"

### 方法2: 使用Docker (适合有Docker环境)

1. **安装Docker**
   - Windows: 下载Docker Desktop
   - 确保Docker正在运行

2. **构建APK**
   ```bash
   # 使用docker-compose (推荐)
   docker-compose up android-builder
   
   # 或者直接使用Docker
   docker build -t mhcs-builder .
   docker run -v "%cd%":/app -v "%cd%/output":/output mhcs-builder
   ```

3. **获取APK**
   - 构建完成后，APK文件将在`output`目录中

### 方法3: Windows本地构建 (需要配置环境)

⚠️ **注意**: Windows上构建Android APK需要复杂的环境配置，建议使用上述方法。

1. **安装必要软件**
   - Python 3.8+ (添加到PATH)
   - Java JDK 8+ (添加到PATH)
   - Android SDK (可选，buildozer会自动下载)

2. **运行构建脚本**
   ```cmd
   build-windows.bat
   ```

### 方法4: 使用WSL (Windows用户推荐)

1. **安装WSL**
   ```cmd
   wsl --install
   ```

2. **在WSL中构建**
   ```bash
   # 进入WSL
   wsl
   
   # 安装依赖
   sudo apt update
   sudo apt install python3 python3-pip openjdk-11-jdk
   
   # 安装buildozer
   pip3 install buildozer cython
   
   # 构建APK
   buildozer android debug
   ```

## 📋 构建要求

### 系统要求
- **内存**: 至少4GB RAM (推荐8GB+)
- **存储**: 至少5GB可用空间
- **网络**: 稳定的网络连接 (下载SDK和依赖)

### 软件要求
- Python 3.8+
- Java JDK 8+
- Android SDK (buildozer会自动处理)
- Git (用于GitHub方法)

## 🔧 配置说明

### buildozer.spec 配置
主要配置项已在`buildozer.spec`中设置：

```ini
[app]
title = 满汉助手
package.name = mhcs
package.domain = com.mhcs.app
requirements = python3,kivy,numpy,opencv-python,pillow,ultralytics,torch,torchvision,pyjnius,plyer

[android]
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,SYSTEM_ALERT_WINDOW
android.archs = arm64-v8a, armeabi-v7a
android.api = 30
android.minapi = 21
```

### 权限说明
APK将请求以下权限：
- `INTERNET`: 网络访问
- `WRITE_EXTERNAL_STORAGE`: 写入存储
- `READ_EXTERNAL_STORAGE`: 读取存储
- `SYSTEM_ALERT_WINDOW`: 系统级窗口 (无障碍服务)

## 🐛 常见问题

### Q: 构建时间很长？
A: 首次构建需要下载Android SDK和Python依赖，可能需要30-60分钟。后续构建会快很多。

### Q: 构建失败，提示缺少SDK？
A: buildozer会自动下载SDK。如果失败，检查网络连接或尝试使用VPN。

### Q: Windows上构建失败？
A: Windows环境复杂，建议使用WSL、Docker或GitHub Actions。

### Q: APK安装后闪退？
A: 检查：
- 设备Android版本 (需要5.0+)
- 权限是否正确授予
- 模型文件是否正确包含

### Q: 无法识别游戏元素？
A: 确保：
- 模型文件`model/best.pt`存在且有效
- 已授予屏幕录制权限
- 游戏界面清晰可见

## 📱 安装和使用

### 安装APK
1. 在Android设备上启用"未知来源"安装
2. 传输APK文件到设备
3. 点击安装

### 首次使用
1. 启动应用
2. 点击"权限设置"
3. 在系统设置中启用无障碍服务
4. 返回应用开始使用

## 🔄 更新和维护

### 更新模型
1. 替换`model/best.pt`文件
2. 重新构建APK

### 修改界面
1. 编辑相应的Python文件
2. 重新构建APK

### 添加功能
1. 在对应模块中添加代码
2. 更新`buildozer.spec`中的依赖
3. 重新构建APK

## 📞 技术支持

如果遇到构建问题：

1. **检查日志**: 查看构建过程中的错误信息
2. **清理缓存**: 删除`.buildozer`目录后重试
3. **更新依赖**: 确保使用最新版本的buildozer和依赖
4. **环境问题**: 考虑使用Docker或GitHub Actions

---

**提示**: 推荐使用GitHub Actions进行构建，这样可以避免本地环境配置的复杂性。
