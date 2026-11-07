"""
Linux Platform & Desktop Environment Detector for Powertool
Detects:
- Distributions: Ubuntu, Debian, Fedora, Linux Mint, Arch Linux, etc.
- Desktop Environments: GNOME, KDE Plasma, Cinnamon, XFCE, etc.
- Display Protocol: Wayland vs X11
- Installed helper tools: wl-clipboard, xclip, wmctrl, xdotool
Developed by En-Dhiaa.
"""

import os
import sys
import shutil
from typing import Dict, Any


class PlatformDetector:
    @classmethod
    def get_info(cls) -> Dict[str, Any]:
        info = {
            "os": sys.platform,
            "distro_id": "unknown",
            "distro_name": "Linux",
            "distro_version": "",
            "desktop_env": "unknown",
            "session_type": "unknown",
            "is_wayland": False,
            "is_x11": False,
            "has_wl_clipboard": False,
            "has_xclip": False,
            "has_wmctrl": False,
            "has_tesseract": False,
            "can_capture_global_shortcuts": False
        }

        # 1. Parse /etc/os-release (Standard across modern Linux distros)
        os_release_paths = ["/etc/os-release", "/usr/lib/os-release"]
        for p in os_release_paths:
            if os.path.isfile(p):
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        for line in f:
                            if "=" in line:
                                k, v = line.strip().split("=", 1)
                                v = v.strip('"\'')
                                if k == "ID":
                                    info["distro_id"] = v.lower()
                                elif k == "PRETTY_NAME":
                                    info["distro_name"] = v
                                elif k == "VERSION_ID":
                                    info["distro_version"] = v
                    break
                except Exception:
                    pass

        # If on non-Linux or test fallback
        if sys.platform != "linux" and info["distro_id"] == "unknown":
            info["distro_id"] = "ubuntu"
            info["distro_name"] = "Ubuntu Linux (Simulated/Dev)"
            info["distro_version"] = "24.04"

        # 2. Desktop Environment detection
        xdg_current = os.environ.get("XDG_CURRENT_DESKTOP", "").upper()
        desktop_session = os.environ.get("DESKTOP_SESSION", "").upper()

        if "GNOME" in xdg_current or "GNOME" in desktop_session:
            info["desktop_env"] = "GNOME"
        elif "KDE" in xdg_current or "KDE" in desktop_session or "PLASMA" in xdg_current:
            info["desktop_env"] = "KDE Plasma"
        elif "CINNAMON" in xdg_current or "X-CINNAMON" in xdg_current:
            info["desktop_env"] = "Cinnamon"
        elif "XFCE" in xdg_current:
            info["desktop_env"] = "XFCE"
        elif "MATE" in xdg_current:
            info["desktop_env"] = "MATE"
        else:
            info["desktop_env"] = xdg_current if xdg_current else "Standard Desktop"

        # 3. Display Protocol detection (Wayland vs X11)
        session_type = os.environ.get("XDG_SESSION_TYPE", "").lower()
        wayland_display = os.environ.get("WAYLAND_DISPLAY", "")

        if session_type == "wayland" or wayland_display:
            info["session_type"] = "wayland"
            info["is_wayland"] = True
        elif session_type == "x11" or os.environ.get("DISPLAY"):
            info["session_type"] = "x11"
            info["is_x11"] = True
        else:
            # Default to Wayland on modern Linux
            info["session_type"] = "wayland"
            info["is_wayland"] = True

        # 4. Helper binaries check
        info["has_wl_clipboard"] = bool(shutil.which("wl-paste") and shutil.which("wl-copy"))
        info["has_xclip"] = bool(shutil.which("xclip") or shutil.which("xsel"))
        info["has_wmctrl"] = bool(shutil.which("wmctrl"))
        info["has_tesseract"] = bool(shutil.which("tesseract"))

        # Global shortcut availability
        info["can_capture_global_shortcuts"] = info["is_x11"] or (info["is_wayland"] and info["desktop_env"] in ("GNOME", "KDE Plasma"))

        # Compatibility aliases for cross-platform modules
        info["distribution"] = info["distro_id"]
        info["desktop_environment"] = info["desktop_env"]
        info["init_system"] = "systemd" if shutil.which("systemctl") else "init"
        info["is_wsl"] = bool(os.environ.get("WSL_DISTRO_NAME"))

        return info

    @classmethod
    def detect_all(cls) -> Dict[str, Any]:
        return cls.get_info()


if __name__ == "__main__":
    import json
    print(json.dumps(PlatformDetector.get_info(), indent=2))
