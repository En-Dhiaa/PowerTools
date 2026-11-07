#!/usr/bin/env bash
# ==============================================================================
# Powertool Extended Edition — Linux Development Environment Setup
# Supported distributions: Ubuntu, Debian, Fedora, Arch Linux, openSUSE
# Developed by En-Dhiaa (https://github.com/En-Dhiaa)
# ==============================================================================

set -e

echo "=== Powertool Linux Environment Setup ==="
echo "Developer: En-Dhiaa"

# Detect package manager
if command -v apt &> /dev/null; then
    echo "[*] Detected Debian/Ubuntu family."
    sudo apt update
    sudo apt install -y \
        python3 python3-pip python3-venv \
        python3-pyside6.qtwidgets python3-pyside6.qtgui python3-pyside6.qtcore \
        wl-clipboard xclip \
        wmctrl xdotool \
        tesseract-ocr tesseract-ocr-ara \
        build-essential git
elif command -v dnf &> /dev/null; then
    echo "[*] Detected Fedora/RHEL family."
    sudo dnf install -y \
        python3 python3-pip \
        python3-pyside6 \
        wl-clipboard xclip \
        wmctrl xdotool \
        tesseract tesseract-langpack-ara \
        gcc-c++ git rpm-build
elif command -v pacman &> /dev/null; then
    echo "[*] Detected Arch Linux family."
    sudo pacman -S --needed --noconfirm \
        python python-pip \
        pyside6 \
        wl-clipboard xclip \
        wmctrl xdotool \
        tesseract tesseract-data-ara \
        base-devel git
elif command -v zypper &> /dev/null; then
    echo "[*] Detected openSUSE family."
    sudo zypper install -y \
        python3 python3-pip \
        python3-pyside6 \
        wl-clipboard xclip \
        wmctrl xdotool \
        tesseract-ocr \
        git
else
    echo "[!] Unknown package manager. Please install Python 3.9+, PySide6, wl-clipboard, and xclip manually."
fi

echo "[*] Installing Python AI and helper libraries..."
python3 -m pip install --upgrade --user ctranslate2 sentencepiece pillow pytest

echo "=== Setup Complete! You can now launch Powertool: ==="
echo "  python3 linux/powertool-linux.py"

