FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV ANDROID_HOME="/home/user/.buildozer/android/platform/android-sdk"
ENV PATH="${PATH}:${ANDROID_HOME}/tools:${ANDROID_HOME}/platform-tools"

# Instalar dependências essenciais do sistema e Java
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ccache \
    git \
    libncurses5:i386 \
    libstdc++6:i386 \
    libgtk2.0-0:i386 \
    libpangox-1.0-0:i386 \
    libpangoxft-1.0-0:i386 \
    libidn11:i386 \
    python3 \
    python3-dev \
    python3-pip \
    python3-setuptools \
    openjdk-17-jdk \
    unzip \
    zlib1g-dev \
    zlib1g:i386 \
    zip \
    libffi-dev \
    libssl-dev \
    autoconf \
    libtool \
    pkg-config \
    cmake \
    libltdl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root para o Buildozer
RUN useradd -m -s /bin/bash user
USER user
WORKDIR /home/user/app

# Instalar Buildozer e Cython
RUN pip3 install --no-cache-dir --upgrade pip buildozer cython "kivy>=2.2.0"

# Copiar projeto
COPY --chown=user:user . /home/user/app

CMD ["buildozer", "android", "debug"]
