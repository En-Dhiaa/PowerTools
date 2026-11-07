# Powertool Extended Edition — Linux User Guide

**Lead Developer:** [En-Dhiaa](https://github.com/En-Dhiaa)  
**Project:** Powertool Extended Edition (Linux & Windows Productivity Suite)  
**Version:** 0.88.0  
**License:** MIT License  
**Issue Tracker:** [https://github.com/En-Dhiaa/PowerToys/issues](https://github.com/En-Dhiaa/PowerToys/issues)

---

## 1. Overview & Architecture

**Powertool** is a cross-platform, enhanced productivity suite independently developed by **En-Dhiaa**, originating from Microsoft PowerToys. 

Unlike simple cross-compilation attempts, the Linux Edition of Powertool is designed with a **clean Linux-native modular architecture**:
- **Modern GUI:** Built with PySide6 (Qt6) following modern dark-mode desktop aesthetics.
- **Display Server Compatibility:** Full support for both **Wayland** (via Freedesktop portals) and traditional **X11** sessions.
- **Desktop Parity:** Seamless integration with **GNOME**, **KDE Plasma**, **XFCE**, and other FreeDesktop-compliant desktop environments.
- **Zero Cloud Footprint:** Translation and OCR execute 100% locally on your machine with zero remote server communication.

---

## 2. Supported Linux Distributions

Powertool Linux Edition is officially tested and packaged for:
- **Ubuntu 22.04 LTS / 24.04 LTS**
- **Debian 12 (Bookworm) / Testing**
- **Fedora 39 / 40 / 41**
- **Arch Linux / Manjaro**
- **Linux Mint 21 / 22**
- **openSUSE Tumbleweed / Leap**

---

## 3. Installation Methods

### Method A: Standalone AppImage (Recommended for all distros)
The AppImage requires no package installation and runs on virtually any modern 64-bit Linux distribution:
```bash
# Download and make executable
chmod +x Powertool-0.88.0-x86_64.AppImage

# Launch Powertool
./Powertool-0.88.0-x86_64.AppImage
```

### Method B: Debian / Ubuntu Package (.deb)
```bash
# Install the .deb package
sudo apt install ./release/powertool_0.88.0_all.deb

# Or using dpkg:
sudo dpkg -i release/powertool_0.88.0_all.deb
sudo apt install -f  # resolves missing dependencies if any
```

### Method C: Fedora / RHEL Package (.rpm)
```bash
# Install the .rpm package
sudo dnf install ./release/powertool-0.88.0-1.noarch.rpm
```

### Method D: Running from Source
```bash
# 1. Run the automatic dependency setup script
bash linux/setup-dev-env.sh

# 2. Launch Powertool
python3 linux/powertool-linux.py
```

---

## 4. Feature Modules & Utilities

### 🌐 1. Offline Translator
* **Default Shortcut:** `Ctrl + Alt + T`
* **CLI:** `powertool --translator`
* **Features:**
  - 100% offline neural machine translation between Arabic and English.
  - Powered by CTranslate2 and SentencePiece quantization (`.argosmodel`).
  - Built-in **Model Management Dialog** to inspect, download, and delete language pairs.
  - Automatic clipboard text capture on launch and single-click copy for translated results.

### ⌨️ 2. Keyboard Layout Converter
* **Default Shortcut:** `Ctrl + Alt + Shift + K`
* **CLI:** `powertool --converter`
* **Features:**
  - Physical scancode bidirectional text conversion (US QWERTY ↔ Arabic 101 / Arabic 102).
  - Fixes text accidentally typed in the wrong keyboard language layout without retyping.
  - Real-time side-by-side preview with Copy, Replace, and Undo history.

### 🚀 3. Powertool Run
* **Default Shortcut:** `Alt + Space`
* **CLI:** `powertool --run`
* **Features:**
  - Instant application and file search indexing FreeDesktop `.desktop` entries.
  - Inline mathematical expression calculator (e.g. `25 * 4 + 10`).
  - Direct shell command execution prefix (e.g. `> top` or `> ls -la`).

### 🪟 4. Window Tiling (FancyZones Linux Equivalent)
* **Default Shortcut:** `Win + Shift + \``
* **CLI:** `powertool --tiling`
* **Features:**
  - Grid layouts: 2-Column Split, 3-Column Split, Priority Center Grid, and 2x2 Quadrant Grid.
  - Interactive visual preview with configurable window padding.
  - Active window snapping via `wmctrl`/`xdotool` on X11 and KWin/GNOME D-Bus on Wayland.

### 🎨 5. Color Picker
* **Default Shortcut:** `Win + Shift + C`
* **CLI:** `powertool --color-picker`
* **Features:**
  - Screen pixel loupe sampler supporting X11 and Wayland portals.
  - Multi-format values: HEX, RGB, RGBA, HSV, HSL, and CMYK.
  - Recent color history palette with instant one-click clipboard copying.

### 📝 6. Text Extractor (Screen OCR)
* **Default Shortcut:** `Win + Shift + T`
* **CLI:** `powertool --text-extractor`
* **Features:**
  - Rubber-band rectangular screen snip overlay.
  - Multilingual offline OCR powered by local Tesseract (Arabic & English).
  - Direct integration: copy to clipboard, send directly to Offline Translator, or fix with Layout Converter.

### 🔄 7. PowerRename (Batch File Renamer)
* **Default Shortcut:** `Ctrl + Alt + R`
* **CLI:** `powertool --rename [files...]`
* **Features:**
  - Regular expression (regex) search and replace.
  - Case conversion (UPPERCASE, lowercase, Title Case, CamelCase).
  - Live side-by-side preview table before applying changes to disk.

### 🖼 8. Image Resizer
* **Default Shortcut:** `Ctrl + Alt + I`
* **CLI:** `powertool --resizer [files...]`
* **Features:**
  - Presets: Small (854x480), Medium (1366x768), Large (1920x1080), 4K UHD, Mobile (1080x1920), Custom.
  - Format conversion: Original, JPEG, PNG, WEBP.
  - Multi-threaded batch worker with progress bar.

### ⚙️ 9. Keyboard Manager
* **CLI:** `powertool --keyboard-manager`
* **Features:**
  - Syncs global shortcuts directly to GNOME (`gsettings`) or KDE (`kglobalaccel`).
  - Caps Lock remapping options (e.g., Caps Lock as Control or Escape).

---

## 5. Wayland vs. X11 Compatibility Notes

| Feature | X11 | Wayland |
| :--- | :--- | :--- |
| **Global Shortcuts** | Direct X11 grabs | Desktop Environment shortcuts / FreeDesktop Portal |
| **Window Snapping** | Direct `wmctrl` / `xdotool` | KWin Scripting (KDE) / GNOME D-Bus |
| **Screen Color Loupe** | Direct Root Window grab | FreeDesktop ColorPicker Portal (`org.freedesktop.portal.ColorPicker`) |
| **Clipboard** | `xclip` / `xsel` | `wl-clipboard` (`wl-copy` / `wl-paste`) |

---

## 6. Developer Identity & Feedback

* **Lead Developer:** **En-Dhiaa** ([https://github.com/En-Dhiaa](https://github.com/En-Dhiaa))
* **Submit Issues & Bug Reports:** [https://github.com/En-Dhiaa/PowerToys/issues/new/choose](https://github.com/En-Dhiaa/PowerToys/issues/new/choose)
* **Original PowerToys Attribution:** This project is an independently developed extended suite based on Microsoft PowerToys, licensed under the MIT License. All original Microsoft copyrights and third-party notices are preserved.

