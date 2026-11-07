"""
Powertool Text Extractor — Screen OCR & Text Recognition for Linux
Features:
- Screen snip overlay with rectangular region selection
- Local multilingual Optical Character Recognition (Tesseract: Arabic & English)
- Direct system clipboard integration (X11 & Wayland)
- One-click action buttons: Copy, Offline Translation, and Layout Converter
Developed by En-Dhiaa.
"""

import sys
import os
import subprocess
import shutil
import tempfile
from typing import Optional, Tuple

from PySide6.QtCore import Qt, QRect, QPoint, Signal
from PySide6.QtGui import QFont, QColor, QPainter, QPen, QBrush, QGuiApplication, QPixmap, QImage
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QFrame, QMessageBox, QComboBox
)


class OCREngine:
    @staticmethod
    def is_tesseract_available() -> bool:
        return shutil.which("tesseract") is not None

    @staticmethod
    def extract_text_from_image(pixmap: QPixmap, lang: str = "eng+ara") -> Tuple[str, Optional[str]]:
        """Performs OCR on the provided QPixmap. Returns (extracted_text, error_message)."""
        if not OCREngine.is_tesseract_available():
            return "", (
                "Tesseract OCR is not installed on this system.\n"
                "Install it with:\n"
                "  Debian/Ubuntu: sudo apt install tesseract-ocr tesseract-ocr-ara\n"
                "  Fedora: sudo dnf install tesseract tesseract-langpack-ara\n"
                "  Arch: sudo pacman -S tesseract tesseract-data-ara"
            )

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            pixmap.save(tmp_path, "PNG")
            # Run tesseract tmp_path stdout -l lang
            res = subprocess.run(
                ["tesseract", tmp_path, "stdout", "-l", lang],
                capture_output=True,
                text=True,
                timeout=15
            )
            if res.returncode == 0:
                text = res.stdout.strip()
                return text, None
            else:
                return "", f"OCR Error: {res.stderr}"
        except Exception as e:
            return "", f"Failed to execute OCR: {e}"
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


class SnippingOverlay(QWidget):
    region_selected = Signal(QPixmap)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setCursor(Qt.CrossCursor)

        self.start_pos: Optional[QPoint] = None
        self.end_pos: Optional[QPoint] = None
        self.full_screen_pixmap: Optional[QPixmap] = None

    def start_selection(self):
        screen = QGuiApplication.primaryScreen()
        if screen:
            self.full_screen_pixmap = screen.grabWindow(0)
            self.setGeometry(screen.virtualGeometry())
        self.showFullScreen()

    def paintEvent(self, event):
        painter = QPainter(self)
        # Dim background
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))

        if self.start_pos and self.end_pos:
            rect = QRect(self.start_pos, self.end_pos).normalized()
            # Draw highlight
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.fillRect(rect, Qt.transparent)
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

            # Draw border
            painter.setPen(QPen(QColor("#0078D4"), 2))
            painter.drawRect(rect)

            # Show dimensions tooltip
            dim_text = f"{rect.width()} × {rect.height()}"
            painter.setFont(QFont("Segoe UI", 9, QFont.Bold))
            painter.setPen(QColor("#FFFFFF"))
            painter.drawText(rect.bottomRight() + QPoint(6, 16), dim_text)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = event.pos()
            self.end_pos = event.pos()
            self.update()

    def mouseMoveEvent(self, event):
        if self.start_pos:
            self.end_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.start_pos and self.end_pos:
            rect = QRect(self.start_pos, self.end_pos).normalized()
            self.close()
            if rect.width() > 10 and rect.height() > 10 and self.full_screen_pixmap:
                cropped = self.full_screen_pixmap.copy(rect)
                self.region_selected.emit(cropped)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()


class TextExtractorResultWindow(QMainWindow):
    def __init__(self, initial_text: str = "", error_msg: Optional[str] = None):
        super().__init__()
        self.setWindowTitle("Powertool Text Extractor — OCR Results")
        self.resize(540, 380)

        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1A1A1A;
                color: #FFFFFF;
                font-family: 'Segoe UI', 'Ubuntu', sans-serif;
            }
            QTextEdit {
                background-color: #242424;
                border: 1px solid #333333;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
                color: #FFFFFF;
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
        """)

        self.init_ui(initial_text, error_msg)

    def init_ui(self, initial_text: str, error_msg: Optional[str]):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("📝 Extracted Text (OCR)")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        subtitle = QLabel("Powertool by En-Dhiaa")
        subtitle.setStyleSheet("color: #888888; font-size: 11px;")
        header.addWidget(title)
        header.addStretch()
        header.addWidget(subtitle)
        layout.addLayout(header)

        self.text_edit = QTextEdit()
        if error_msg:
            self.text_edit.setPlainText(error_msg)
            self.text_edit.setStyleSheet("color: #FFB900;")
        else:
            self.text_edit.setPlainText(initial_text)
        layout.addWidget(self.text_edit, 1)

        btn_row = QHBoxLayout()
        copy_btn = QPushButton("📋 Copy to Clipboard")
        copy_btn.setObjectName("primaryBtn")
        copy_btn.clicked.connect(self.copy_to_clipboard)

        translate_btn = QPushButton("🌐 Translate Offline")
        translate_btn.clicked.connect(self.translate_text)

        convert_btn = QPushButton("⌨️ Fix Layout")
        convert_btn.clicked.connect(self.fix_layout)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)

        btn_row.addWidget(copy_btn)
        btn_row.addWidget(translate_btn)
        btn_row.addWidget(convert_btn)
        btn_row.addStretch()
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

    def copy_to_clipboard(self):
        txt = self.text_edit.toPlainText()
        QApplication.clipboard().setText(txt)
        QMessageBox.information(self, "Copied", "Text copied to clipboard!")

    def translate_text(self):
        txt = self.text_edit.toPlainText()
        try:
            from OfflineTranslatorUI import launch_popup
            # Could pass initial text if supported
            launch_popup()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not launch translator: {e}")

    def fix_layout(self):
        txt = self.text_edit.toPlainText()
        try:
            from KeyboardLayoutConverterUI import launch_converter_popup
            launch_converter_popup()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not launch layout converter: {e}")


class TextExtractorController:
    def __init__(self):
        self.overlay: Optional[SnippingOverlay] = None
        self.result_window: Optional[TextExtractorResultWindow] = None

    def trigger_snip(self):
        self.overlay = SnippingOverlay()
        self.overlay.region_selected.connect(self.process_snip)
        self.overlay.start_selection()

    def process_snip(self, pixmap: QPixmap):
        text, err = OCREngine.extract_text_from_image(pixmap)
        if text:
            # Copy to clipboard immediately (like PowerToys)
            QApplication.clipboard().setText(text)

        self.result_window = TextExtractorResultWindow(initial_text=text, error_msg=err)
        self.result_window.show()


def launch_text_extractor():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    controller = TextExtractorController()
    controller.trigger_snip()
    app.exec()


if __name__ == "__main__":
    launch_text_extractor()
