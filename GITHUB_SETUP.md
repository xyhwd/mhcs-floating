# GitHub云构建设置指南

## 🚀 快速设置步骤

### 1. 准备文件
确保您的项目目录包含以下文件：
- ✅ `floating_main.py` - 悬浮窗主程序
- ✅ `mobile_game_engine.py` - 完整游戏引擎
- ✅ `buildozer.spec` - 构建配置
- ✅ `.github/workflows/build-apk.yml` - GitHub Actions配置

### 2. 初始化Git仓库
在项目目录中运行：
```bash
git init
git add .
git commit -m "满汉助手悬浮窗版本 - 完整保留原版算法"
```

### 3. 创建GitHub仓库
1. 访问 https://github.com/new
2. 仓库名：`mhcs-floating`
3. 设为 **Public** (免费使用GitHub Actions)
4. **不要**勾选初始化README、.gitignore或license
5. 点击"Create repository"

### 4. 推送代码到GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/mhcs-floating.git
git branch -M main
git push -u origin main
```
**注意**：将 `YOUR_USERNAME` 替换为您的GitHub用户名

### 5. 自动构建
- 推送代码后，GitHub Actions会自动开始构建
- 在仓库页面点击"Actions"标签查看构建进度
- 首次构建约需20-30分钟

### 6. 下载APK
构建完成后：
1. 在"Actions"页面找到最新的构建
2. 点击进入构建详情
3. 在"Artifacts"部分下载APK文件

## 📋 构建特性

### 自动构建触发条件
- 推送到main/master分支
- 创建Pull Request
- 手动触发（在Actions页面点击"Run workflow"）

### 构建产物
- **APK文件**：约15-20MB
- **发布版本**：自动创建GitHub Release
- **构建日志**：详细的构建过程记录

### 构建环境
- **操作系统**：Ubuntu Latest
- **Python版本**：3.9
- **Java版本**：11
- **Android API**：自动配置

## 🎯 悬浮窗特性

### 界面特点
- **尺寸**：180x120像素
- **位置**：悬浮在屏幕上方
- **样式**：简洁现代的按钮设计

### 功能按钮
- **主按钮**：开始/暂停/继续
- **状态显示**：运行状态、步数、分数
- **设置按钮**：打开无障碍服务设置
- **退出按钮**：关闭应用

### 算法保留
- ✅ 100%保留原版YOLO推理逻辑
- ✅ 100%保留原版消除算法
- ✅ 100%保留原版评估函数
- ✅ 100%保留原版特殊元素处理

## 🔧 故障排除

### 构建失败
1. 检查文件是否完整
2. 查看构建日志中的错误信息
3. 确认GitHub Actions权限正常

### 推送失败
1. 检查Git配置
2. 确认仓库URL正确
3. 检查网络连接

### 权限问题
1. 确保仓库为Public
2. 检查GitHub Actions是否启用
3. 确认有推送权限

## 📱 使用说明

### 安装APK
1. 下载构建好的APK文件
2. 在Android设备上启用"未知来源"安装
3. 安装APK

### 设置权限
1. 启动应用
2. 点击"设置"按钮
3. 在系统设置中启用无障碍服务
4. 返回应用

### 开始使用
1. 打开目标游戏
2. 点击悬浮窗中的"开始"按钮
3. 观察悬浮窗状态变化
4. 可随时暂停/继续

## 🎉 完成！

按照以上步骤，您将获得：
- 🎯 专业的悬浮窗Android应用
- ✅ 完整保留原版算法的自动化功能
- 📱 适配各种手机分辨率
- 🚀 通过GitHub云端自动构建

---

**提示**：如果您不熟悉Git操作，可以使用GitHub Desktop等图形化工具来简化操作。
