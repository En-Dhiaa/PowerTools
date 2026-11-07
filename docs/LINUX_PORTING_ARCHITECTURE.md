# Powertool Linux Edition — Architecture & Porting Audit

**Project:** Powertool Extended Edition (Linux Port)  
**Lead Developer:** En-Dhiaa ([https://github.com/En-Dhiaa](https://github.com/En-Dhiaa))  
**Base Repository:** Microsoft PowerToys (MIT License)  
**Target Platform:** Linux Desktop (Ubuntu, Debian, Fedora, Linux Mint, Arch Linux)  
**Display Servers:** X11 & Wayland  
**Desktop Environments:** GNOME & KDE Plasma  
**Document Path:** `docs/LINUX_PORTING_ARCHITECTURE.md`

---

## 1. Executive Summary

Upstream Microsoft PowerToys is deeply entangled with Windows-specific APIs, COM shell extensions, DirectX/DirectWrite, WinUI 3, and Win32 low-level hooks (`WH_KEYBOARD_LL`). Attempting a raw compile on Linux fails immediately due to non-portable platform assumptions.

The **Powertool Linux Edition** adopts a clean, modular cross-platform architecture:
1. Retains identical user workflows, UI layouts, keyboard shortcuts, and configurations across Windows and Linux.
2. Implements native Linux technologies (Qt6/PySide6, D-Bus, X11/Wayland input protocols, and Unix Domain Sockets).
3. Delivers fully functional, non-placeholder implementations of all core features:
   - **Offline Translator:** Powered locally by CTranslate2 and SentencePiece (.argosmodel).
   - **Keyboard Layout Converter:** Physical scan-code mapping for Arabic 101/102 and US QWERTY.
   - **Powertool Run:** Linux application and system runner.
   - **Window Layout Manager (FancyZones equivalent):** Multi-monitor grid layout manager for GNOME & KDE.
   - **PowerRename:** Regex and batch renamer.
   - **Image Resizer:** Multi-format image batch resizer.
   - **Color Picker:** Desktop color sampler (X11 & Wayland).
   - **Text Extractor:** Local OCR engine.
   - **Developer / About Page:** Attributed to En-Dhiaa with clickable GitHub links and issue tracker.
4. Generates standard Linux distribution packages: **AppImage**, **Flatpak**, **Debian (.deb)**, and **RPM (.rpm)**.

---

## 2. Comprehensive Compatibility Audit: Windows vs. Linux

### 2.1 Low-Level Input & Global Keyboard Hooks
* **Windows Architecture:** `SetWindowsHookEx(WH_KEYBOARD_LL, ...)` and `RegisterHotKey` allow global intercept of keystrokes across all windows.
* **Linux Challenge:**
  - **X11:** Applications can grab keys globally using `XGrabKey` or query key events with `XRecord`.
  - **Wayland:** Direct global keystroke sniffing is explicitly blocked by security design. Wayland compositors (Mutter in GNOME, KWin in KDE) enforce client isolation.
* **Linux Solution:**
  - Wayland Desktop Portal: Uses `org.freedesktop.portal.GlobalShortcuts` and desktop environment custom shortcut bindings (`gsettings` on GNOME, `kglobalaccel` on KDE).
  - Graceful X11 fallback: Uses Qt key event filters and `xcb`/`Xlib` bindings when running on an X11 session.

### 2.2 Clipboard Interception & Non-Destructive Capture
* **Windows Architecture:** Uses Win32 `OpenClipboard`, `GetClipboardData(CF_UNICODETEXT)`, and synthesizes `Ctrl+C` via `SendInput`.
* **Linux Challenge:**
  - X11 uses `CLIPBOARD` and `PRIMARY` selection targets via ICCCM/EWMH.
  - Wayland requires client focus to read the clipboard unless using the Data Control protocol (`wlr-data-control`) or Wayland clipboard utilities.
* **Linux Solution:**
  - Multi-tier clipboard bridge supporting `wl-clipboard` (`wl-paste` and `wl-copy`) on Wayland and `xclip`/`xsel` on X11.
  - Full backup and atomic restoration of previous clipboard contents so user data is never destroyed during translation or layout correction.

### 2.3 User Interface Framework
* **Windows Architecture:** Built with WinUI 3 (Windows App SDK) and WPF, which only run on Windows 10/11.
* **Linux Solution:**
  - Implemented in **Qt6 (PySide6)**: Delivers 1:1 visual parity with the Windows 11 Fluent design (dark/light themes, rounded corners, subtle drop shadows, and font anti-aliasing).
  - Native Bidirectional Text Support (BiDi): Qt HarfBuzz text shaping engine natively renders Arabic Right-to-Left (RTL) and English Left-to-Right (LTR) text with perfect ligature shaping (`لا`, `لأ`, `لإ`, `لآ`).

### 2.4 Inter-Process Communication (IPC) & Background Runner
* **Windows Architecture:** Windows Named Pipes (`\\.\pipe\powertoys_*`), Windows Event handles, and Mutexes.
* **Linux Solution:**
  - Standard Unix Domain Sockets: `/run/user/$UID/powertool.sock` for local IPC.
  - Session D-Bus service: `org.endhiaa.Powertool` for single-instance enforcement and system tray coordination.

---

## 3. Distribution & Desktop Environment Matrix

The application automatically identifies the host distribution and desktop environment at startup:

| Linux Distribution | Package Format | Tested Desktop Environments | Display Protocols |
|---|---|---|---|
| **Ubuntu 22.04 / 24.04 LTS** | `.deb`, AppImage, Flatpak | GNOME Shell | Wayland & X11 |
| **Debian 12 (Bookworm)** | `.deb`, AppImage, Flatpak | GNOME, KDE Plasma | Wayland & X11 |
| **Fedora 39 / 40 / 41** | `.rpm`, Flatpak, AppImage | GNOME 45/46, KDE Plasma 6 | Wayland |
| **Linux Mint 21 / 22** | `.deb`, AppImage | Cinnamon, XFCE | X11 |
| **Arch Linux / Manjaro** | PKGBUILD, AppImage, Flatpak | GNOME, KDE Plasma | Wayland & X11 |

### Detection Heuristics (`DistroDetector`):
- `/etc/os-release` parsing (`ID`, `VERSION_ID`, `PRETTY_NAME`).
- Desktop environment query: `$XDG_CURRENT_DESKTOP` (`GNOME`, `KDE`, `X-Cinnamon`, `XFCE`).
- Session type query: `$XDG_SESSION_TYPE` (`wayland` vs `x11`).

---

## 4. Module Implementation Architecture

```
                       ┌─────────────────────────────────────────┐
                       │          Powertool Linux Suite          │
                       │    (Python 3 + PySide6 / Qt6 Native)    │
                       └────────────────────┬────────────────────┘
                                            │
                     ┌──────────────────────┼──────────────────────┐
                     │                      │                      │
       ┌─────────────▼────────────┐ ┌───────▼────────┐  ┌──────────▼───────────┐
       │     Core Utilities       │ │   Linux IPC    │  │ Platform Integrations│
       ├──────────────────────────┤ ├────────────────┤  ├──────────────────────┤
       │ 1. Offline Translator    │ │ Unix Sockets   │  │ X11 (Xlib/XRecord)   │
       │ 2. Keyboard Converter    │ │ D-Bus Service  │  │ Wayland Portals      │
       │ 3. Powertool Run         │ │ Single Instance│  │ wl-clipboard / xclip │
       │ 4. Window Layout Manager │ │ System Tray    │  │ FreeDesktop Icons    │
       │ 5. PowerRename (Batch)   │ └────────────────┘  │ AppStream Metadata   │
       │ 6. Image Resizer         │                     └──────────────────────┘
       │ 7. Color Picker          │
       │ 8. Text Extractor (OCR)  │
       │ 9. Always on Top         │
       │ 10. Developer Page       │
       └──────────────────────────┘
```

---

## 5. Directory & Packaging Layout

* `linux/`
  - `powertool-linux.py`: Master Linux GUI suite and dashboard.
  - `powertool.desktop`: XDG FreeDesktop application launcher.
  - `org.endhiaa.Powertool.metainfo.xml`: AppStream metadata for Flatpak & software centers.
  - `debian/`: Debian control, rules, and changelog for `.deb` creation.
  - `powertool.spec`: RPM package specification for Fedora/RHEL/openSUSE.
  - `AppRun`: Entrypoint executable for standalone AppImage.
  - `build-appimage.sh`: Script to build self-contained AppImage.
  - `build-deb.sh`: Script to build Debian package.
  - `setup-dev-env.sh`: Dependency verification and environment setup.
* `src/modules/`
  - `OfflineTranslator/`: CTranslate2 engine and GUI.
  - `KeyboardLayoutConverter/`: Physical scan-code converter and GUI.
  - `LinuxModules/`: Linux-native implementations of Run, Tiling, Rename, ImageResizer, and ColorPicker.
* `docs/`
  - `LINUX_PORTING_ARCHITECTURE.md`: Architecture analysis and technical decisions.
  - `LINUX_EDITION_USER_GUIDE.md`: Installation, shortcuts, and usage guide for Linux.

---

## 6. Security and Backward-Compatibility Commitments

1. **Windows Integrity:** Zero Windows source files or WiX build scripts are modified or removed.
2. **Isolation on Git Branch:** All Linux port development is housed on branch `feature/linux-edition`.
3. **Attribution & Licenses:** Upstream Microsoft PowerToys authorship and MIT license notices are preserved alongside En-Dhiaa's enhancements.
4. **Local Execution:** 100% offline; zero telemetry or external network calls during translation or layout correction.

