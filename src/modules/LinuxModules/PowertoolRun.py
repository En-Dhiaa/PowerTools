"""
Powertool Run — Application & Quick Search Launcher for Linux
Features:
- Instant search across installed applications (.desktop entries)
- Integrated calculator for mathematical queries (e.g. '25 * 4 + 10')
- Terminal command execution runner (e.g. '> htop' or '> ls')
- URL and file opener
Developed by En-Dhiaa.
"""

import sys
import os
import glob
import subprocess
import math
from typing import List, Dict, Any, Optional

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QListWidget, QListWidgetItem, QLabel, QFrame, QGraphicsDropShadowEffect
)


class ApplicationIndex:
    _cached_apps: Optional[List[Dict[str, str]]] = None

    @classmethod
    def get_applications(cls) -> List[Dict[str, str]]:
        if cls._cached_apps is not None:
            return cls._cached_apps

        apps = []
        app_dirs = [
            "/usr/share/applications",
            "/usr/local/share/applications",
            os.path.expanduser("~/.local/share/applications")
        ]

        # Standard built-in applications dictionary for fast fallback/development
        fallback_apps = [
            {"name": "Terminal", "exec": "x-terminal-emulator", "comment": "Command Line Interface"},
            {"name": "Files (File Manager)", "exec": "xdg-open .", "comment": "Browse files and folders"},
            {"name": "Web Browser", "exec": "xdg-open https://google.com", "comment": "Access the Internet"},
            {"name": "Text Editor", "exec": "gedit", "comment": "Edit text documents"},
            {"name": "Settings", "exec": "gnome-control-center", "comment": "System configuration"},
            {"name": "Powertool Offline Translator", "exec": "powertool --translator", "comment": "Arabic/English offline translator"},
            {"name": "Powertool Keyboard Layout Converter", "exec": "powertool --converter", "comment": "Arabic 101/102 layout correction"}
        ]

        seen_names = set()
        for d in app_dirs:
            if not os.path.isdir(d):
                continue
            for desktop_file in glob.glob(os.path.join(d, "*.desktop")):
                try:
                    name = ""
                    exec_cmd = ""
                    comment = ""
                    nodisplay = False

                    with open(desktop_file, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith("Name=") and not name:
                                name = line.split("=", 1)[1]
                            elif line.startswith("Exec=") and not exec_cmd:
                                exec_cmd = line.split("=", 1)[1].split("%")[0].strip()
                            elif line.startswith("Comment=") and not comment:
                                comment = line.split("=", 1)[1]
                            elif line.startswith("NoDisplay=true"):
                                nodisplay = True

                    if name and exec_cmd and not nodisplay and name not in seen_names:
                        apps.append({"name": name, "exec": exec_cmd, "comment": comment})
                        seen_names.add(name)
                except Exception:
                    pass

        if not apps:
            apps = fallback_apps

        cls._cached_apps = apps
        return apps

    @classmethod
    def evaluate_math(cls, query: str) -> Optional[str]:
        cleaned = query.lstrip("=").strip()
        if not cleaned:
            return None
        # Security: only allow basic mathematical characters and whitelisted math function names
        import re
        # Check all word tokens in expression
        words = re.findall(r'[a-zA-Z_]\w*', cleaned)
        allowed_words = {"abs", "round", "sqrt", "sin", "cos", "tan", "pi", "e"}
        if any(w not in allowed_words for w in words):
            return None

        # Disallow dangerous characters
        allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+-*/().,%^ _\t")
        if not all(c in allowed_chars for c in cleaned):
            return None

        try:
            # Safe evaluation with limited globals
            safe_dict = {
                "abs": abs, "round": round, "sqrt": math.sqrt,
                "sin": math.sin, "cos": math.cos, "tan": math.tan,
                "pi": math.pi, "e": math.e
            }
            val = eval(cleaned, {"__builtins__": {}}, safe_dict)
            return f"= {val}"
        except Exception:
            return None


class CalculatorEngine:
    """Convenience wrapper for mathematical query evaluation"""
    @staticmethod
    def evaluate(query: str) -> Optional[str]:
        res = ApplicationIndex.evaluate_math(query)
        if res and res.startswith("= "):
            return res[2:].strip()
        return res


class PowertoolRunWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(650, 420)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        self.card = QFrame()
        self.card.setObjectName("card")
        self.card.setStyleSheet("""
            QFrame#card {
                background-color: #1E1E1E;
                border: 1px solid #333333;
                border-radius: 12px;
            }
            QLineEdit {
                background-color: #262626;
                border: 1px solid #3E3E3E;
                border-radius: 8px;
                color: #FFFFFF;
                font-family: 'Segoe UI', 'Ubuntu', sans-serif;
                font-size: 16px;
                padding: 10px 14px;
            }
            QLineEdit:focus {
                border: 1px solid #0078D4;
            }
            QListWidget {
                background-color: transparent;
                border: none;
                color: #FFFFFF;
                font-family: 'Segoe UI', 'Ubuntu', sans-serif;
            }
            QListWidget::item {
                padding: 10px 12px;
                border-radius: 6px;
                margin: 2px 0px;
            }
            QListWidget::item:selected {
                background-color: #2D3748;
                border-left: 3px solid #0078D4;
            }
            QListWidget::item:hover {
                background-color: #262626;
            }
            QLabel {
                color: #777777;
                font-size: 11px;
            }
        """)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(10)

        # Search Bar
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Type an application name, math equation (e.g. 50 * 4), or command (> ls)...")
        self.search_box.textChanged.connect(self.on_query_changed)
        self.search_box.returnPressed.connect(self.execute_selected)
        card_layout.addWidget(self.search_box)

        # Results List
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.execute_selected)
        card_layout.addWidget(self.results_list)

        # Footer Hint
        hint_label = QLabel("Press Enter to launch  •  Esc to close  •  Up/Down to navigate")
        card_layout.addWidget(hint_label)

        main_layout.addWidget(self.card)

        # Drop shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 8)
        self.card.setGraphicsEffect(shadow)

        # Shortcuts
        QShortcut(QKeySequence("Escape"), self, self.close)
        QShortcut(QKeySequence("Down"), self, self.select_next)
        QShortcut(QKeySequence("Up"), self, self.select_prev)

        self.center_window()
        self.populate_initial_results()

    def center_window(self):
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            self.move((geo.width() - self.width()) // 2, geo.height() // 4)

    def populate_initial_results(self):
        self.results_list.clear()
        apps = ApplicationIndex.get_applications()
        for app in apps[:8]:
            item = QListWidgetItem(f"🚀 {app['name']}\n   {app['comment'] or 'Application'}")
            item.setData(Qt.UserRole, app["exec"])
            self.results_list.addItem(item)
        if self.results_list.count() > 0:
            self.results_list.setCurrentRow(0)

    def on_query_changed(self, text: str):
        query = text.strip()
        self.results_list.clear()

        if not query:
            self.populate_initial_results()
            return

        # 1. Check math
        math_res = ApplicationIndex.evaluate_math(query)
        if math_res:
            item = QListWidgetItem(f"🔢 Calculator Result\n   {math_res}")
            item.setData(Qt.UserRole, f"calc:{math_res}")
            self.results_list.addItem(item)

        # 2. Check terminal command
        if query.startswith(">"):
            cmd = query[1:].strip()
            item = QListWidgetItem(f"⚡ Execute Command: {cmd}\n   Run in system shell")
            item.setData(Qt.UserRole, f"cmd:{cmd}")
            self.results_list.addItem(item)

        # 3. Filter applications
        apps = ApplicationIndex.get_applications()
        q_lower = query.lower()
        matches = [a for a in apps if q_lower in a["name"].lower() or q_lower in a.get("comment", "").lower()]

        for app in matches[:8]:
            item = QListWidgetItem(f"🚀 {app['name']}\n   {app['comment'] or app['exec']}")
            item.setData(Qt.UserRole, app["exec"])
            self.results_list.addItem(item)

        if self.results_list.count() > 0:
            self.results_list.setCurrentRow(0)

    def select_next(self):
        r = self.results_list.currentRow()
        if r < self.results_list.count() - 1:
            self.results_list.setCurrentRow(r + 1)

    def select_prev(self):
        r = self.results_list.currentRow()
        if r > 0:
            self.results_list.setCurrentRow(r - 1)

    def execute_selected(self):
        item = self.results_list.currentItem()
        if not item:
            return

        payload = item.data(Qt.UserRole)
        if not payload:
            return

        if payload.startswith("calc:"):
            # Copy result to clipboard
            res_val = payload.split("calc:=")[1].strip()
            QApplication.clipboard().setText(res_val)
        elif payload.startswith("cmd:"):
            cmd = payload.split("cmd:")[1].strip()
            subprocess.Popen(cmd, shell=True)
        else:
            subprocess.Popen(payload, shell=True)

        self.close()


def launch_run():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    window = PowertoolRunWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    launch_run()
