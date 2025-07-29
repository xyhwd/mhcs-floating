# 满汉助手 Android构建环境
FROM ubuntu:20.04

# 设置环境变量
ENV DEBIAN_FRONTEND=noninteractive
ENV ANDROID_HOME=/opt/android-sdk
ENV PATH=${PATH}:${ANDROID_HOME}/cmdline-tools/latest/bin:${ANDROID_HOME}/platform-tools

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    python3 \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    openjdk-11-jdk \
    wget \
    unzip \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    libpng-dev \
    zlib1g-dev \
    autotools-dev \
    autoconf \
    libtool \
    pkg-config \
    libncurses5-dev \
    libncursesw5-dev \
    libtinfo5 \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# 设置Java环境
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# 安装Android SDK
RUN mkdir -p ${ANDROID_HOME}/cmdline-tools && \
    wget -q https://dl.google.com/android/repository/commandlinetools-linux-8512546_latest.zip -O /tmp/cmdline-tools.zip && \
    unzip -q /tmp/cmdline-tools.zip -d ${ANDROID_HOME}/cmdline-tools && \
    mv ${ANDROID_HOME}/cmdline-tools/cmdline-tools ${ANDROID_HOME}/cmdline-tools/latest && \
    rm /tmp/cmdline-tools.zip

# 安装Android SDK组件
RUN yes | ${ANDROID_HOME}/cmdline-tools/latest/bin/sdkmanager --licenses && \
    ${ANDROID_HOME}/cmdline-tools/latest/bin/sdkmanager \
    "platform-tools" \
    "platforms;android-30" \
    "build-tools;30.0.3" \
    "ndk;23.1.7779620"

# 升级pip并安装Python依赖
RUN python3 -m pip install --upgrade pip setuptools wheel

# 安装buildozer和相关依赖
RUN pip3 install \
    buildozer \
    cython \
    kivy \
    kivymd \
    numpy \
    pillow

# 创建工作目录
WORKDIR /app

# 复制项目文件
COPY . /app/

# 设置buildozer配置
RUN buildozer init || true

# 构建脚本
COPY docker-build.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-build.sh

# 默认命令
CMD ["/usr/local/bin/docker-build.sh"]
