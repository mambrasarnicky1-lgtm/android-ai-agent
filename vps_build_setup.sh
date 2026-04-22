#!/bin/bash
# NOIR SOVEREIGN VPS BUILDER SETUP v1.0
# Target: Ubuntu 20.04/22.04

echo "[PROCESS] Starting Sovereign Builder Setup..."

# Update system
sudo apt-get update
sudo apt-get install -y \
    build-essential git python3-dev ffmpeg libsdl2-dev libsdl2-image-dev \
    libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev libswscale-dev \
    libavformat-dev libavcodec-dev zlib1g-dev libgstreamer1.0-dev \
    gstreamer1.0-plugins-base gstreamer1.0-plugins-good libsqlite3-dev \
    sqlite3 bzip2 libbz2-dev libssl-dev openssl libgdbm-dev \
    libgdbm-compat-dev liblzma-dev libreadline-dev libncursesw5-dev \
    libffi-dev uuid-dev libtool automake autoconf libncurses5 \
    libncursesw5 libtinfo5 cmake ant openjdk-17-jdk zip unzip

# Install Buildozer and Cython
pip3 install --user --upgrade buildozer Cython==0.29.33

# Add ~/.local/bin to PATH if not there
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc
    export PATH="$PATH:$HOME/.local/bin"
fi

echo "[SUCCESS] Sovereign Builder Environment Ready."
