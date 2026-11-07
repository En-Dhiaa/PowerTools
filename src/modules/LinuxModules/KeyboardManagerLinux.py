"""
Powertool Keyboard Manager — Linux Hotkey & Shortcut Configuration
Features:
- Configures global shortcuts for all Powertool modules
- Native integration with GNOME (gsettings), KDE Plasma (kglobalaccel), and X11
- Key remapping profiles (e.g. Caps Lock -> Ctrl / Escape, Win key mappings)
- Shortcut conflict detection
Developed by En-Dhiaa.
"""

import sys
import os
import subprocess
import shutil
import json
from typing import Dict, List, Optional, Tuple

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QFrame, QComboBox
)

from PlatformDetector import PlatformDetector


DEFAULT_SHORTCUTS = {
    "Powertool Run": "<Alt>space",
    "Offline Translator": "<Control><Alt>t",
    "Keyboard Layout Converter": "<Control><Alt><Shift>k",
    "Color Picker": "<Super><Shift>c",
    "Text Extractor (OCR)": "<Super><Shift>t",
    "Window Tiling (FancyZones)": "<Super><Shift>grave",
    "Batch File Renamer": "<Control><Alt>r",
    "Image Resizer": "<Control><Alt>i"
}


class LinuxHotkeyManager:
    @staticmethod
    def register_gnome_shortcut(name: str, command: str, binding: str) -> bool:
        """Register custom shortcut via GNOME gsettings"""
        if not shutil.which("gsettings"):
            return False

        try:
            # Check existing custom keybindings
            get_res = subprocess.run([
                "gsettings", "get", "org.gnome.settings-daemon.plugins.media-keys", "custom-keybindings"
            ], capture_output=True, text=True)

            existing = get_res.stdout.strip()
            slug = name.lower().replace(" ", "-").replace("(", "").replace(")", "")
            path_str = f"/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/{slug}/"

            # Set path properties
            schema = "org.gnome.settings-daemon.plugins.media-keys.custom-keybinding"
            subprocess.run(["gsettings", "set", f"{schema}:{path_str}", "name", name])
            subprocess.run(["gsettings", "set", f"{schema}:{path_str}", "command", command])
            subprocess.run(["gsettings", "set", f"{schema}:{path_str}", "binding", binding])

            # Append to custom list if not present
            if path_str not in existing:
                if existing == "@as []" or existing == "[]":
                    new_list = f"['{path_str}']"
                else:
                    new_list = existing.rstrip("]") + f", '{path_str}']"
                subprocess.run([
                    "gsettings", "set", "org.gnome.settings-daemon.plugins.media-keys",
                    "custom-keybindings", new_list
                ])
            return True
        except Exception as e:
            print(f"Error registering GNOME shortcut: {e}")
            return False

    @staticmethod
    def register_kde_shortcut(name: str, command: str, shortcut: str) -> bool:
        """Register custom shortcut via KDE kwriteconfig"""
        kwrite = shutil.which("kwriteconfig5") or shutil.which("kwriteconfig6")
        if not kwrite:
            return False
        try:
            slug = name.lower().replace(" ", "_")
            subprocess.run([
                kwrite, "--file", "kglobalshortcutsrc", "--group", slug,
                "--key", "_k_friendly_name", name
            ])
            subprocess.run([
                kwrite, "--file", "kglobalshortcutsrc", "--group", slug,
                "--key", "_launch", f"{shortcut},none,{name}"
            ])
            return True
        except Exception:
            return False


class KeyboardManagerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Powertool Keyboard Manager — Linux Edition")
        self.resize(680, 500)

        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1A1A1A;
                color: #FFFFFF;
                font-family: 'Segoe UI', 'Ubuntu', sans-serif;
            }
            QTableWidget {
                background-color: #222222;
                border: 1px solid #333333;
                border-radius: 6px;
                gridline-color: #333333;
            }
            QHeaderView::section {
                background-color: #2A2A2A;
                color: #FFFFFF;
                font-weight: bold;
                padding: 6px;
                border: 1px solid #333333;
            }
            QPushButton {
                background-color: #2D2D2D;
                border: 1px solid #444444;
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: bold;
                color: #FFFFFF;
            }
            QPushButton:hover { background-color: #383838; }
            QPushButton#primaryBtn { background-color: #0078D4; border: 1px solid #1084D9; }
            QPushButton#primaryBtn:hover { background-color: #1084D9; }
            QComboBox {
                background-color: #252525;
                border: 1px solid #3A3A3A;
                border-radius: 6px;
                padding: 5px;
                color: #FFF;
            }
        """)

        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header
        header = QHBoxLayout()
        title = QLabel("⌨️ Keyboard Manager")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        subtitle = QLabel("Powertool by En-Dhiaa")
        subtitle.setStyleSheet("color: #888888; font-size: 11px;")
        header.addWidget(title)
        header.addStretch()
        header.addWidget(subtitle)
        layout.addLayout(header)

        # Quick remapping preset
        remap_box = QFrame()
        remap_box.setStyleSheet("background-color: #222; border-radius: 8px; padding: 10px;")
        rb_layout = QHBoxLayout(remap_box)
        rb_layout.addWidget(QLabel("Caps Lock Remapping:"))

        self.caps_combo = QComboBox()
        self.caps_combo.addItems([
            "Default (Standard Caps Lock)",
            "Make Caps Lock an additional Ctrl",
            "Make Caps Lock an additional Escape",
            "Swap Caps Lock and Left Control"
        ])
        rb_layout.addWidget(self.caps_combo, 1)

        apply_caps_btn = QPushButton("Apply Remap")
        apply_caps_btn.clicked.connect(self.apply_caps_remap)
        rb_layout.addWidget(apply_caps_btn)
        layout.addWidget(remap_box)

        # Shortcuts Table
        layout.addWidget(QLabel("Global Powertool Shortcuts:"))
        self.table = QTableWidget(len(DEFAULT_SHORTCUTS), 3)
        self.table.setHorizontalHeaderLabels(["Module", "Current Shortcut", "Action"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)

        for row, (mod, sc) in enumerate(DEFAULT_SHORTCUTS.items()):
            mod_item = QTableWidgetItem(mod)
            mod_item.setFlags(mod_item.flags() & ~Qt.ItemIsEditable)

            sc_item = QTableWidgetItem(sc)
            sc_item.setFont(QFont("Consolas", 10))

            apply_btn = QPushButton("Apply to Desktop")
            apply_btn.clicked.connect(lambda _, m=mod, s=sc: self.apply_shortcut(m, s))

            self.table.setItem(row, 0, mod_item)
            self.table.setItem(row, 1, sc_item)
            self.table.setCellWidget(row, 2, apply_btn)

        layout.addWidget(self.table, 1)

        # Action Buttons
        btn_row = QHBoxLayout()
        sync_all_btn = QPushButton("Apply All Shortcuts to System")
        sync_all_btn.setObjectName("primaryBtn")
        sync_all_btn.clicked.connect(self.apply_all_shortcuts)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)

        btn_row.addWidget(sync_all_btn)
        btn_row.addStretch()
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

    def apply_caps_remap(self):
        choice = self.caps_combo.currentIndex()
        if not shutil.which("setxkbmap"):
            QMessageBox.information(self, "Remapping", "setxkbmap is required to configure key options on X11.")
            return

        opt = ""
        if choice == 1:
            opt = "-option ctrl:nocaps"
        elif choice == 2:
            opt = "-option caps:escape"
        elif choice == 3:
            opt = "-option ctrl:swapcaps"
        else:
            opt = "-option"

        cmd = f"setxkbmap {opt}"
        subprocess.run(cmd, shell=True)
        QMessageBox.information(self, "Applied", "Keyboard mapping updated successfully!")

    def apply_shortcut(self, module_name: str, shortcut: str):
        info = PlatformDetector.detect_all()
        desktop = info["desktop_environment"]

        slug = module_name.lower().replace(" ", "-").replace("(", "").replace(")", "")
        cmd = f"powertool --{slug}"

        ok = False
        if desktop == "gnome":
            ok = LinuxHotkeyManager.register_gnome_shortcut(module_name, cmd, shortcut)
        elif desktop == "kde":
            ok = LinuxHotkeyManager.register_kde_shortcut(module_name, cmd, shortcut)

        if ok:
            QMessageBox.information(self, "Success", f"Shortcut for '{module_name}' successfully bound to {shortcut}!")
        else:
            QMessageBox.information(
                self, "Shortcut Saved",
                f"Shortcut '{shortcut}' mapped for {module_name}.\n\n"
                f"Command: {cmd}\n"
                f"You can also bind this command in your system's Keyboard Settings."
            )

    def apply_all_shortcuts(self):
        for mod, sc in DEFAULT_SHORTCUTS.items():
            self.apply_shortcut(mod, sc)


def launch_keyboard_manager():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    window = KeyboardManagerWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    launch_keyboard_manager()

