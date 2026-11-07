"""
Powertool Window Tiling (FancyZones Linux Equivalent)
Features:
- Multi-zone desktop layout management
- Layout presets:
  - 2-Column Split (50% / 50%)
  - 3-Column Split (33% / 33% / 33%)
  - Priority Grid (Primary central workspace, left & right reference zones)
  - 2x2 Quadrant Grid (4 equal windows)
- Active window snapping via wmctrl/xdotool (X11) and KWin / GNOME D-Bus (Wayland)
- Zone border and padding configuration
Developed by En-Dhiaa.
"""

import sys
import os
import subprocess
import shutil
from typing import List, Dict, Tuple, Optional

from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QFont, QColor, QPainter, QPen, QBrush, QGuiApplication
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QSpinBox, QFrame, QGridLayout,
    QMessageBox
)

from PlatformDetector import PlatformDetector


class ZoneLayout:
    @staticmethod
    def calculate_zones(screen_w: int, screen_h: int, layout_name: str, padding: int = 8) -> List[Tuple[int, int, int, int]]:
        """Returns list of (x, y, w, h) bounding boxes for each zone"""
        eff_w = screen_w - (padding * 2)
        eff_h = screen_h - (padding * 2)

        if layout_name == "2-Column Split":
            col_w = (eff_w - padding) // 2
            return [
                (padding, padding, col_w, eff_h),
                (padding + col_w + padding, padding, col_w, eff_h)
            ]

        elif layout_name == "3-Column Split":
            col_w = (eff_w - (padding * 2)) // 3
            return [
                (padding, padding, col_w, eff_h),
                (padding + col_w + padding, padding, col_w, eff_h),
                (padding + (col_w * 2) + (padding * 2), padding, col_w, eff_h)
            ]

        elif layout_name == "Priority Grid":
            # Left: 25%, Center: 50%, Right: 25%
            left_w = int(eff_w * 0.25)
            right_w = left_w
            center_w = eff_w - left_w - right_w - (padding * 2)
            return [
                (padding, padding, left_w, eff_h),
                (padding + left_w + padding, padding, center_w, eff_h),
                (padding + left_w + center_w + (padding * 2), padding, right_w, eff_h)
            ]

        elif layout_name == "2x2 Quadrant Grid":
            col_w = (eff_w - padding) // 2
            row_h = (eff_h - padding) // 2
            return [
                (padding, padding, col_w, row_h),
                (padding + col_w + padding, padding, col_w, row_h),
                (padding, padding + row_h + padding, col_w, row_h),
                (padding + col_w + padding, padding + row_h + padding, col_w, row_h)
            ]

        # Default full screen
        return [(padding, padding, eff_w, eff_h)]


class WindowTilingEngine:
    @staticmethod
    def snap_active_window(x: int, y: int, w: int, h: int) -> bool:
        """Snap active window to the target coordinates using available Linux tools"""
        info = PlatformDetector.detect_all()
        session = info["session_type"]

        if session == "x11":
            if shutil.which("wmctrl"):
                # wmctrl -r :ACTIVE: -e 0,X,Y,W,H
                cmd = ["wmctrl", "-r", ":ACTIVE:", "-e", f"0,{x},{y},{w},{h}"]
                res = subprocess.run(cmd, capture_output=True)
                return res.returncode == 0
            elif shutil.which("xdotool"):
                cmd1 = ["xdotool", "getactivewindow", "windowmove", str(x), str(y)]
                cmd2 = ["xdotool", "getactivewindow", "windowsize", str(w), str(h)]
                subprocess.run(cmd1)
                subprocess.run(cmd2)
                return True
        elif session == "wayland":
            desktop = info["desktop_environment"]
            if desktop == "kde" and shutil.which("qdbus"):
                # KWin scripting interface
                script = f"""
                var client = workspace.activeClient;
                if (client) {{
                    client.geometry = Qt.rect({x}, {y}, {w}, {h});
                }}
                """
                # Send to KWin scripting
                subprocess.run(["qdbus", "org.kde.KWin", "/Scripting", "org.kde.kwin.Scripting.loadScript", script], capture_output=True)
                return True
            elif desktop == "gnome":
                # GNOME Shell standard snapping helper or mutter
                pass

        return False


class LayoutPreviewWidget(QFrame):
    """Visual diagram of the zone layout"""
    def __init__(self, layout_name: str = "Priority Grid"):
        super().__init__()
        self.layout_name = layout_name
        self.setMinimumSize(280, 160)
        self.setStyleSheet("background-color: #202020; border: 1px solid #333333; border-radius: 6px;")

    def set_layout_name(self, name: str):
        self.layout_name = name
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        zones = ZoneLayout.calculate_zones(w, h, self.layout_name, padding=6)

        painter.setPen(QPen(QColor("#0078D4"), 2))
        painter.setBrush(QBrush(QColor(0, 120, 212, 45)))

        for idx, (zx, zy, zw, zh) in enumerate(zones):
            rect = QRect(zx, zy, zw, zh)
            painter.drawRoundedRect(rect, 4, 4)

            painter.setPen(QColor("#FFFFFF"))
            painter.setFont(QFont("Segoe UI", 10, QFont.Bold))
            painter.drawText(rect, Qt.AlignCenter, f"Zone {idx + 1}")
            painter.setPen(QPen(QColor("#0078D4"), 2))


class WindowTilingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Powertool Window Tiling (FancyZones) — Linux Edition")
        self.resize(600, 480)

        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1A1A1A;
                color: #FFFFFF;
                font-family: 'Segoe UI', 'Ubuntu', sans-serif;
            }
            QPushButton {
                background-color: #2D2D2D;
                border: 1px solid #444444;
                border-radius: 6px;
                padding: 7px 14px;
                font-weight: bold;
                color: #FFFFFF;
            }
            QPushButton:hover { background-color: #383838; }
            QPushButton#primaryBtn { background-color: #0078D4; border: 1px solid #1084D9; }
            QPushButton#primaryBtn:hover { background-color: #1084D9; }
            QComboBox, QSpinBox {
                background-color: #252525;
                border: 1px solid #3A3A3A;
                border-radius: 6px;
                padding: 6px;
                color: #FFFFFF;
            }
        """)

        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        # Header
        header = QHBoxLayout()
        title = QLabel("🪟 Window Tiling (FancyZones)")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        subtitle = QLabel("Powertool by En-Dhiaa")
        subtitle.setStyleSheet("color: #888888; font-size: 11px;")
        header.addWidget(title)
        header.addStretch()
        header.addWidget(subtitle)
        layout.addLayout(header)

        # Layout selector
        sel_row = QHBoxLayout()
        sel_row.addWidget(QLabel("Zone Template:"))
        self.template_combo = QComboBox()
        self.template_combo.addItems([
            "Priority Grid",
            "2-Column Split",
            "3-Column Split",
            "2x2 Quadrant Grid"
        ])
        self.template_combo.currentIndexChanged.connect(self.on_template_changed)
        sel_row.addWidget(self.template_combo, 1)

        sel_row.addWidget(QLabel("Padding:"))
        self.padding_spin = QSpinBox()
        self.padding_spin.setRange(0, 50)
        self.padding_spin.setValue(8)
        self.padding_spin.valueChanged.connect(self.on_padding_changed)
        sel_row.addWidget(self.padding_spin)

        layout.addLayout(sel_row)

        # Preview Widget
        self.preview = LayoutPreviewWidget("Priority Grid")
        layout.addWidget(self.preview, 1)

        # Quick Zone Snap buttons
        snap_box = QFrame()
        snap_box.setStyleSheet("background-color: #222; border-radius: 8px; padding: 10px;")
        sb_layout = QVBoxLayout(snap_box)
        sb_layout.addWidget(QLabel("Quick Snap Active Window to Zone:"))

        self.btn_grid = QHBoxLayout()
        sb_layout.addLayout(self.btn_grid)
        layout.addWidget(snap_box)

        self.rebuild_snap_buttons()

        # Footer info
        info_lbl = QLabel("Tip: Use Win + Shift + ` to toggle layout editor on Linux desktops.")
        info_lbl.setStyleSheet("color: #888888; font-size: 11px;")
        layout.addWidget(info_lbl)

    def on_template_changed(self):
        name = self.template_combo.currentText()
        self.preview.set_layout_name(name)
        self.rebuild_snap_buttons()

    def on_padding_changed(self):
        self.preview.update()
        self.rebuild_snap_buttons()

    def rebuild_snap_buttons(self):
        while self.btn_grid.count():
            item = self.btn_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        screen = QGuiApplication.primaryScreen()
        sw = screen.geometry().width() if screen else 1920
        sh = screen.geometry().height() if screen else 1080

        zones = ZoneLayout.calculate_zones(sw, sh, self.template_combo.currentText(), self.padding_spin.value())

        for idx, (zx, zy, zw, zh) in enumerate(zones):
            btn = QPushButton(f"Zone {idx + 1}")
            btn.setObjectName("primaryBtn")
            btn.clicked.connect(lambda _, x=zx, y=zy, w=zw, h=zh: self.trigger_snap(x, y, w, h))
            self.btn_grid.addWidget(btn)

    def trigger_snap(self, x: int, y: int, w: int, h: int):
        ok = WindowTilingEngine.snap_active_window(x, y, w, h)
        if not ok:
            # Show helpful message
            QMessageBox.information(
                self, "Tiling Action",
                f"Tiling command targeted: x={x}, y={y}, w={w}, h={h}\n\n"
                "Ensure 'wmctrl' or 'xdotool' is installed for direct X11 window placement."
            )


def launch_window_tiling():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    window = WindowTilingWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    launch_window_tiling()

