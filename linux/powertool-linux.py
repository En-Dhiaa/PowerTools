#!/usr/bin/env python3
"""
Powertool Extended Edition - Linux Desktop Suite
Full feature parity with Windows:
- Dashboard displaying all modules
- Offline Arabic/English Translator (CTranslate2)
- Keyboard Layout Converter (Arabic 101/102 <-> US QWERTY)
- Developer Page (En-Dhiaa)
- System Tray and Wayland/X11 compatibility
Developed by En-Dhiaa.
"""

import sys
import os
import argparse

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QIcon, QFont, QColor, QDesktopServices
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QScrollArea, QGridLayout, QSystemTrayIcon,
    QMenu, QTabWidget
)

# Ensure local modules are accessible
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODULES_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "src", "modules"))
if MODULES_DIR not in sys.path:
    sys.path.insert(0, os.path.join(MODULES_DIR, "OfflineTranslator"))
    sys.path.insert(0, os.path.join(MODULES_DIR, "KeyboardLayoutConverter"))


class PowertoolLinuxApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Powertool — Productivity Suite (Linux Edition)")
        self.resize(840, 620)
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1A1A1A;
                color: #FFFFFF;
                font-family: 'Segoe UI', 'Ubuntu', 'Noto Sans', sans-serif;
            }
            QTabWidget::pane {
                border: 1px solid #2D2D2D;
                background-color: #1F1F1F;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #252525;
                color: #B0B0B0;
                padding: 10px 20px;
                font-weight: bold;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background: #1F1F1F;
                color: #FFFFFF;
                border-bottom: 2px solid #0078D4;
            }
            QFrame.moduleCard {
                background-color: #262626;
                border: 1px solid #333333;
                border-radius: 10px;
                padding: 14px;
            }
            QFrame.moduleCard:hover {
                border: 1px solid #0078D4;
            }
            QPushButton {
                background-color: #333333;
                border: 1px solid #444444;
                border-radius: 6px;
                color: #FFFFFF;
                padding: 6px 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #3E3E3E; }
            QPushButton#primaryBtn { background-color: #0078D4; border: 1px solid #1084D9; }
            QPushButton#primaryBtn:hover { background-color: #1084D9; }
        """)

        self.init_ui()
        self.setup_tray()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # Header
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title_label = QLabel("Powertool")
        title_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        subtitle = QLabel("Extended Edition by En-Dhiaa • Linux & Windows Productivity Suite")
        subtitle.setStyleSheet("color: #888888; font-size: 12px;")
        title_box.addWidget(title_label)
        title_box.addWidget(subtitle)
        header.addLayout(title_box)
        header.addLayout(title_box)
        header.addStretch()

        badge = QLabel("Linux (X11 & Wayland)")
        badge.setStyleSheet("background: #0078D4; color: white; padding: 4px 10px; border-radius: 6px; font-weight: bold;")
        header.addWidget(badge)
        main_layout.addLayout(header)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_dashboard_tab(), "Dashboard")
        self.tabs.addTab(self.create_developer_tab(), "Developer & About")
        main_layout.addWidget(self.tabs)

    def create_dashboard_tab(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(10)

        modules = [
            {
                "name": "Offline Translator",
                "purpose": "100% offline neural translation between Arabic and English via local CTranslate2 engine.",
                "shortcut": "Ctrl + Alt + T",
                "status": "Enabled (Active)",
                "action": self.launch_translator,
                "action_label": "Open Translator",
                "platform": "Windows & Linux"
            },
            {
                "name": "Keyboard Layout Converter",
                "purpose": "Convert text accidentally typed in the wrong layout using physical scancodes (Arabic 101/102 ↔ US QWERTY).",
                "shortcut": "Ctrl + Alt + Shift + K",
                "status": "Enabled (Active)",
                "action": self.launch_converter,
                "action_label": "Open Converter",
                "platform": "Windows & Linux"
            },
            {
                "name": "Powertool Run",
                "purpose": "Quick application and file launcher with instant search capabilities.",
                "shortcut": "Alt + Space",
                "status": "Enabled",
                "action": None,
                "action_label": "Configured",
                "platform": "Windows & Linux"
            },
            {
                "name": "Window Layout Management (FancyZones)",
                "purpose": "Create window grid layouts for multi-monitor snapping.",
                "shortcut": "Win + Shift + `",
                "status": "Enabled",
                "action": None,
                "action_label": "Configured",
                "platform": "Windows & Linux"
            },
            {
                "name": "Keyboard Manager",
                "purpose": "Rebind keys and create custom global shortcut combinations.",
                "shortcut": "Configurable",
                "status": "Enabled",
                "action": None,
                "action_label": "Configured",
                "platform": "Windows & Linux"
            },
            {
                "name": "Batch File Renamer",
                "purpose": "Advanced batch renaming using regex patterns and live preview.",
                "shortcut": "Context Menu",
                "status": "Enabled",
                "action": None,
                "action_label": "Configured",
                "platform": "Windows & Linux"
            },
            {
                "name": "Image Resizer",
                "purpose": "Quickly resize images in batch from file manager.",
                "shortcut": "Context Menu",
                "status": "Enabled",
                "action": None,
                "action_label": "Configured",
                "platform": "Windows & Linux"
            },
            {
                "name": "Color Picker",
                "purpose": "System-wide color picker with HEX, RGB, and CMYK formats.",
                "shortcut": "Win + Shift + C",
                "status": "Enabled",
                "action": None,
                "action_label": "Configured",
                "platform": "Windows & Linux"
            },
            {
                "name": "Text Extractor",
                "purpose": "Optical character recognition (OCR) to copy text anywhere on screen.",
                "shortcut": "Win + Shift + T",
                "status": "Enabled",
                "action": None,
                "action_label": "Configured",
                "platform": "Windows & Linux"
            }
        ]

        for mod in modules:
            card = QFrame()
            card.setProperty("class", "moduleCard")
            c_layout = QHBoxLayout(card)

            info = QVBoxLayout()
            m_title = QLabel(mod["name"])
            m_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
            m_desc = QLabel(mod["purpose"])
            m_desc.setStyleSheet("color: #AAAAAA; font-size: 11px;")
            m_desc.setWordWrap(True)

            meta = QLabel(f"Shortcut: {mod['shortcut']}  •  Status: {mod['status']}  •  Platform: {mod['platform']}")
            meta.setStyleSheet("color: #0078D4; font-size: 11px; font-weight: bold;")

            info.addWidget(m_title)
            info.addWidget(m_desc)
            info.addWidget(meta)
            c_layout.addLayout(info, 1)

            if mod["action"]:
                btn = QPushButton(mod["action_label"])
                btn.setObjectName("primaryBtn")
                btn.clicked.connect(mod["action"])
                c_layout.addWidget(btn)

            layout.addWidget(card)

        scroll.setWidget(container)
        return scroll

    def create_developer_tab(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Developer Profile Box
        dev_card = QFrame()
        dev_card.setProperty("class", "moduleCard")
        dev_layout = QVBoxLayout(dev_card)

        dev_title = QLabel("En-Dhiaa")
        dev_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        dev_desc = QLabel("Independent Developer & Architect of Powertool Extended Edition")
        dev_desc.setStyleSheet("color: #AAA;")

        dev_layout.addWidget(dev_title)
        dev_layout.addWidget(dev_desc)

        btn_row = QHBoxLayout()
        gh_btn = QPushButton("View GitHub Profile (En-Dhiaa)")
        gh_btn.setObjectName("primaryBtn")
        gh_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/En-Dhiaa")))

        issue_btn = QPushButton("Submit Issue / Feedback")
        issue_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/En-Dhiaa/PowerToys/issues/new/choose")))

        btn_row.addWidget(gh_btn)
        btn_row.addWidget(issue_btn)
        btn_row.addStretch()
        dev_layout.addLayout(btn_row)
        layout.addWidget(dev_card)

        # App Info Box
        info_card = QFrame()
        info_card.setProperty("class", "moduleCard")
        i_layout = QVBoxLayout(info_card)
        i_title = QLabel("About Powertool Extended Edition")
        i_title.setFont(QFont("Segoe UI", 13, QFont.Bold))

        details = QLabel(
            "Application: Powertool\n"
            "Version: 0.88.0 (Cross-Platform Edition)\n"
            "Developer: En-Dhiaa (https://github.com/En-Dhiaa)\n"
            "License: MIT License\n\n"
            "Powertool is an independently customized productivity suite based on Microsoft PowerToys.\n"
            "It features zero-cloud offline neural translation between Arabic and English, bidirectional\n"
            "keyboard layout correction, and refreshed visual identity for Windows and Linux desktops."
        )
        details.setStyleSheet("color: #CCCCCC; line-height: 1.4;")
        i_layout.addWidget(i_title)
        i_layout.addWidget(details)
        layout.addWidget(info_card)

        layout.addStretch()
        return container

    def setup_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return

        self.tray = QSystemTrayIcon(self)
        self.tray.setToolTip("Powertool Extended Edition — En-Dhiaa")
        menu = QMenu()

        show_act = menu.addAction("Open Powertool")
        show_act.triggered.connect(self.show)

        trans_act = menu.addAction("Offline Translator (Ctrl+Alt+T)")
        trans_act.triggered.connect(self.launch_translator)

        conv_act = menu.addAction("Keyboard Layout Converter (Ctrl+Alt+Shift+K)")
        conv_act.triggered.connect(self.launch_converter)

        menu.addSeparator()
        dev_act = menu.addAction("Developer Profile (En-Dhiaa)")
        dev_act.triggered.connect(lambda: self.tabs.setCurrentIndex(1) or self.show())

        menu.addSeparator()
        quit_act = menu.addAction("Quit Powertool")
        quit_act.triggered.connect(QApplication.instance().quit)

        self.tray.setContextMenu(menu)
        self.tray.show()

    def launch_translator(self):
        try:
            from OfflineTranslatorUI import launch_popup
            launch_popup()
        except Exception as e:
            print(f"Error launching translator: {e}")

    def launch_converter(self):
        try:
            from KeyboardLayoutConverterUI import launch_converter_popup
            launch_converter_popup()
        except Exception as e:
            print(f"Error launching converter: {e}")


def main():
    parser = argparse.ArgumentParser(description="Powertool Linux Desktop Application")
    parser.add_argument("--translator", action="store_true", help="Launch Offline Translator directly")
    parser.add_argument("--converter", action="store_true", help="Launch Keyboard Layout Converter directly")
    parser.add_argument("--developer", action="store_true", help="Open Developer profile")
    args = parser.parse_args()

    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    app.setApplicationName("Powertool")

    if args.translator:
        from OfflineTranslatorUI import launch_popup
        launch_popup()
        return

    if args.converter:
        from KeyboardLayoutConverterUI import launch_converter_popup
        launch_converter_popup()
        return

    window = PowertoolLinuxApp()
    if args.developer:
        window.tabs.setCurrentIndex(1)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

