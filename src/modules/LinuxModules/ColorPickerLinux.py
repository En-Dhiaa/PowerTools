"""
Powertool Color Picker — Screen Color Sampler & Palette Utility for Linux
Features:
- Screen color sampling with magnifier
- Support for HEX, RGB, HSV, HSL, and CMYK formats
- One-click clipboard copy
- Color history palette
- Support for X11 & Wayland (via Freedesktop ColorPicker Portal or fallback sampler)
Developed by En-Dhiaa.
"""

import sys
import os
import subprocess
from typing import List, Dict, Tuple, Optional

from PySide6.QtCore import Qt, QPoint, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QCursor, QGuiApplication, QClipboard, QPainter, QPen
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QListWidget, QListWidgetItem,
    QFrame, QColorDialog, QMessageBox, QGridLayout
)

from PlatformDetector import PlatformDetector


class ColorPickerEngine:
    @staticmethod
    def rgb_to_cmyk(r: int, g: int, b: int) -> Tuple[int, int, int, int]:
        if (r, g, b) == (0, 0, 0):
            return 0, 0, 0, 100
        c = 1 - r / 255.0
        m = 1 - g / 255.0
        y = 1 - b / 255.0
        min_cmy = min(c, m, y)
        c = (c - min_cmy) / (1 - min_cmy)
        m = (m - min_cmy) / (1 - min_cmy)
        y = (y - min_cmy) / (1 - min_cmy)
        k = min_cmy
        return int(c * 100), int(m * 100), int(y * 100), int(k * 100)

    @staticmethod
    def format_color(color: QColor) -> Dict[str, str]:
        r, g, b = color.red(), color.green(), color.blue()
        c, m, y, k = ColorPickerEngine.rgb_to_cmyk(r, g, b)
        h, s, v, _ = color.getHsv()
        h_hsl, s_hsl, l_hsl, _ = color.getHsl()

        return {
            "HEX": color.name().upper(),
            "RGB": f"rgb({r}, {g}, {b})",
            "RGBA": f"rgba({r}, {g}, {b}, {color.alpha()})",
            "HSV": f"hsv({h if h != -1 else 0}°, {int(s / 255 * 100)}%, {int(v / 255 * 100)}%)",
            "HSL": f"hsl({h_hsl if h_hsl != -1 else 0}°, {int(s_hsl / 255 * 100)}%, {int(l_hsl / 255 * 100)}%)",
            "CMYK": f"cmyk({c}%, {m}%, {y}%, {k}%)"
        }

    @staticmethod
    def sample_screen_pixel(point: QPoint) -> Optional[QColor]:
        """Sample pixel color at screen coordinates using QGuiApplication"""
        screen = QGuiApplication.screenAt(point) or QGuiApplication.primaryScreen()
        if screen:
            pixmap = screen.grabWindow(0, point.x(), point.y(), 1, 1)
            img = pixmap.toImage()
            if not img.isNull():
                return img.pixelColor(0, 0)
        return None

    @staticmethod
    def sample_via_portal() -> Optional[QColor]:
        """Attempt to sample via Freedesktop portal on Wayland"""
        try:
            # Query dbus org.freedesktop.portal.ColorPicker
            res = subprocess.run([
                "gdbus", "call", "--session",
                "--dest", "org.freedesktop.portal.Desktop",
                "--object-path", "/org/freedesktop/portal/desktop",
                "--method", "org.freedesktop.portal.ColorPicker.PickColor",
                "{}"
            ], capture_output=True, text=True, timeout=10)
            if res.returncode == 0 and "color" in res.stdout:
                # Output looks like: (<{'color': <(0.123, 0.456, 0.789)>}>,)
                out = res.stdout
                start = out.find("(")
                end = out.rfind(")")
                parts = out[start+1:end].split(",")
                if len(parts) >= 3:
                    r = int(float(parts[0].strip().lstrip("(")) * 255)
                    g = int(float(parts[1].strip()) * 255)
                    b = int(float(parts[2].strip().rstrip(")")) * 255)
                    return QColor(r, g, b)
        except Exception:
            pass
        return None


class ScreenOverlay(QWidget):
    """Fullscreen transparent magnifier overlay to pick pixel under mouse cursor"""
    color_picked = Signal(QColor)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setCursor(Qt.CrossCursor)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.current_color = QColor(0, 120, 212)

    def start_picking(self):
        screen = QGuiApplication.primaryScreen()
        if screen:
            self.setGeometry(screen.virtualGeometry())
        self.showFullScreen()
        self.timer.start(30)

    def paintEvent(self, event):
        pos = QCursor.pos()
        col = ColorPickerEngine.sample_screen_pixel(pos)
        if col:
            self.current_color = col

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw magnifier loupe near mouse
        lx = pos.x() + 20
        ly = pos.y() + 20
        size = 80

        # Adjust position if near screen edge
        if lx + size > self.width():
            lx = pos.x() - size - 20
        if ly + size > self.height():
            ly = pos.y() - size - 20

        # Background circle with sampled color
        painter.setBrush(self.current_color)
        painter.setPen(QPen(QColor(255, 255, 255), 3))
        painter.drawEllipse(lx, ly, size, size)

        # Inner crosshair
        painter.setPen(QPen(QColor(0, 0, 0, 180), 1))
        painter.drawLine(lx + size // 2, ly + 5, lx + size // 2, ly + size - 5)
        painter.drawLine(lx + 5, ly + size // 2, lx + size - 5, ly + size // 2)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.timer.stop()
            self.close()
            self.color_picked.emit(self.current_color)
        elif event.button() == Qt.RightButton:
            self.timer.stop()
            self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.timer.stop()
            self.close()


class ColorPickerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Powertool Color Picker — Linux Edition")
        self.resize(500, 540)
        self.current_color = QColor(0, 120, 212)
        self.history: List[QColor] = [
            QColor("#0078D4"), QColor("#107C41"), QColor("#D83B01"),
            QColor("#E81123"), QColor("#5C2D91"), QColor("#FFB900")
        ]
        self.overlay: Optional[ScreenOverlay] = None

        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1A1A1A;
                color: #FFFFFF;
                font-family: 'Segoe UI', 'Ubuntu', sans-serif;
            }
            QFrame#colorSwatch {
                border-radius: 8px;
                border: 2px solid #444444;
            }
            QPushButton {
                background-color: #2D2D2D;
                border: 1px solid #444444;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
                color: #FFFFFF;
            }
            QPushButton:hover { background-color: #383838; }
            QPushButton#primaryBtn { background-color: #0078D4; border: 1px solid #1084D9; }
            QPushButton#primaryBtn:hover { background-color: #1084D9; }
            QLineEdit {
                background-color: #242424;
                border: 1px solid #3A3A3A;
                border-radius: 6px;
                padding: 6px 10px;
                color: #FFFFFF;
                font-family: 'Consolas', 'Monospace', monospace;
            }
            QListWidget {
                background-color: #242424;
                border: 1px solid #333333;
                border-radius: 6px;
            }
        """)

        self.init_ui()
        self.update_color_display(self.current_color)

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header
        header = QHBoxLayout()
        title = QLabel("🎨 Color Picker")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        subtitle = QLabel("Powertool by En-Dhiaa")
        subtitle.setStyleSheet("color: #888888; font-size: 11px;")
        header.addWidget(title)
        header.addStretch()
        header.addWidget(subtitle)
        layout.addLayout(header)

        # Top Swatch & Picker button
        top_row = QHBoxLayout()
        self.swatch = QFrame()
        self.swatch.setObjectName("colorSwatch")
        self.swatch.setFixedSize(90, 90)
        top_row.addWidget(self.swatch)

        actions_box = QVBoxLayout()
        pick_screen_btn = QPushButton("🔍 Pick from Screen")
        pick_screen_btn.setObjectName("primaryBtn")
        pick_screen_btn.setFixedHeight(38)
        pick_screen_btn.clicked.connect(self.start_screen_pick)

        dialog_btn = QPushButton("Palette / Manual...")
        dialog_btn.setFixedHeight(36)
        dialog_btn.clicked.connect(self.open_color_dialog)

        actions_box.addWidget(pick_screen_btn)
        actions_box.addWidget(dialog_btn)
        top_row.addLayout(actions_box)
        layout.addLayout(top_row)

        # Formats Section
        fmt_frame = QFrame()
        fmt_frame.setStyleSheet("background-color: #222222; border-radius: 8px; padding: 10px;")
        fmt_layout = QGridLayout(fmt_frame)
        fmt_layout.setSpacing(8)

        self.format_fields: Dict[str, QLineEdit] = {}
        formats = ["HEX", "RGB", "RGBA", "HSV", "HSL", "CMYK"]

        for idx, fmt_name in enumerate(formats):
            lbl = QLabel(f"{fmt_name}:")
            lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
            lbl.setStyleSheet("color: #0078D4;")

            line = QLineEdit()
            line.setReadOnly(True)
            self.format_fields[fmt_name] = line

            copy_btn = QPushButton("Copy")
            copy_btn.setFixedWidth(65)
            copy_btn.clicked.connect(lambda _, f=fmt_name: self.copy_field(f))

            fmt_layout.addWidget(lbl, idx, 0)
            fmt_layout.addWidget(line, idx, 1)
            fmt_layout.addWidget(copy_btn, idx, 2)

        layout.addWidget(fmt_frame)

        # History Section
        layout.addWidget(QLabel("Color History:"))
        self.history_row = QHBoxLayout()
        self.history_row.setSpacing(8)
        layout.addLayout(self.history_row)
        self.refresh_history_swatches()

        layout.addStretch()

    def update_color_display(self, color: QColor):
        self.current_color = color
        self.swatch.setStyleSheet(f"background-color: {color.name()}; border: 3px solid #FFFFFF;")

        formatted = ColorPickerEngine.format_color(color)
        for fmt, val in formatted.items():
            if fmt in self.format_fields:
                self.format_fields[fmt].setText(val)

    def copy_field(self, fmt_name: str):
        if fmt_name in self.format_fields:
            txt = self.format_fields[fmt_name].text()
            QApplication.clipboard().setText(txt)

    def start_screen_pick(self):
        info = PlatformDetector.detect_all()
        if info["session_type"] == "wayland":
            # Try Wayland portal first
            portal_color = ColorPickerEngine.sample_via_portal()
            if portal_color:
                self.add_history(portal_color)
                self.update_color_display(portal_color)
                return

        # Fallback / X11 overlay magnifier
        self.overlay = ScreenOverlay()
        self.overlay.color_picked.connect(self.on_overlay_color_picked)
        self.overlay.start_picking()

    def on_overlay_color_picked(self, color: QColor):
        self.add_history(color)
        self.update_color_display(color)

    def open_color_dialog(self):
        chosen = QColorDialog.getColor(self.current_color, self, "Select Color")
        if chosen.isValid():
            self.add_history(chosen)
            self.update_color_display(chosen)

    def add_history(self, color: QColor):
        if color not in self.history:
            self.history.insert(0, color)
            if len(self.history) > 10:
                self.history.pop()
            self.refresh_history_swatches()

    def refresh_history_swatches(self):
        while self.history_row.count():
            item = self.history_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for c in self.history:
            btn = QPushButton()
            btn.setFixedSize(32, 32)
            btn.setStyleSheet(f"background-color: {c.name()}; border-radius: 4px; border: 1px solid #444;")
            btn.setToolTip(c.name())
            btn.clicked.connect(lambda _, col=c: self.update_color_display(col))
            self.history_row.addWidget(btn)

        self.history_row.addStretch()


def launch_color_picker():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    window = ColorPickerWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    launch_color_picker()
