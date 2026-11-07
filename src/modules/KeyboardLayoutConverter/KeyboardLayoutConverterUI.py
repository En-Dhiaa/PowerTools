"""
Keyboard Layout Converter Floating UI for Powertool Extended Edition
Interactive preview, layout selector (Arabic 101/102, US QWERTY), copy, replace, undo.
Cross-platform: Windows and Linux.
Developed by En-Dhiaa.
"""

import sys
import os
from typing import Optional

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QComboBox, QFrame, QGraphicsDropShadowEffect, QCheckBox
)

from KeyboardLayoutConverterEngine import KeyboardLayoutConverterEngine


class KeyboardLayoutConverterPopup(QWidget):
    def __init__(self, initial_text: str = ""):
        super().__init__()
        self.original_text = initial_text
        self.history = []

        self.init_ui(initial_text)

    def init_ui(self, initial_text: str):
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(580, 460)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        self.card = QFrame()
        self.card.setObjectName("card")
        self.card.setStyleSheet("""
            QFrame#card {
                background-color: #202020;
                border: 1px solid #383838;
                border-radius: 12px;
            }
            QLabel {
                color: #FFFFFF;
                font-family: 'Segoe UI Variable Text', 'Segoe UI', Tahoma, sans-serif;
            }
            QTextEdit {
                background-color: #2D2D2D;
                border: 1px solid #3A3A3A;
                border-radius: 8px;
                color: #FFFFFF;
                font-family: 'Segoe UI Variable Text', 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                padding: 8px;
            }
            QTextEdit:focus {
                border: 1px solid #0078D4;
            }
            QPushButton {
                background-color: #333333;
                border: 1px solid #444444;
                border-radius: 6px;
                color: #FFFFFF;
                font-family: 'Segoe UI Variable Text', 'Segoe UI', sans-serif;
                font-size: 13px;
                padding: 6px 14px;
            }
            QPushButton:hover {
                background-color: #3E3E3E;
                border: 1px solid #555555;
            }
            QPushButton:pressed {
                background-color: #282828;
            }
            QPushButton#primaryBtn {
                background-color: #0078D4;
                border: 1px solid #1084D9;
                font-weight: bold;
            }
            QPushButton#primaryBtn:hover {
                background-color: #1084D9;
            }
            QComboBox {
                background-color: #2D2D2D;
                border: 1px solid #3D3D3D;
                border-radius: 6px;
                color: #FFFFFF;
                padding: 4px 10px;
                font-size: 13px;
            }
            QCheckBox {
                color: #B0B0B0;
                font-size: 12px;
            }
        """)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(18, 14, 18, 16)
        card_layout.setSpacing(10)

        # Header bar
        header_layout = QHBoxLayout()
        title_label = QLabel("Powertool Keyboard Layout Converter")
        title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))

        badge_label = QLabel("● Physical Scancode Map")
        badge_label.setStyleSheet("color: #4CAF50; font-size: 11px; font-weight: bold;")

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.setStyleSheet("background: transparent; border: none; font-size: 14px; color: #AAA;")
        close_btn.clicked.connect(self.close)

        header_layout.addWidget(title_label)
        header_layout.addWidget(badge_label)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)
        card_layout.addLayout(header_layout)

        # Layout selector bar
        selector_layout = QHBoxLayout()
        self.source_combo = QComboBox()
        self.source_combo.addItems([
            "Auto Detect",
            "English (US QWERTY)",
            "Arabic 101 (لوحة مفاتيح 101)",
            "Arabic 102 (لوحة مفاتيح 102)"
        ])
        self.source_combo.currentIndexChanged.connect(self.trigger_conversion)

        swap_btn = QPushButton("⇄")
        swap_btn.setFixedSize(34, 30)
        swap_btn.setToolTip("Swap conversion direction")
        swap_btn.clicked.connect(self.swap_layouts)

        self.target_combo = QComboBox()
        self.target_combo.addItems([
            "Auto Target",
            "Arabic 101 (لوحة مفاتيح 101)",
            "Arabic 102 (لوحة مفاتيح 102)",
            "English (US QWERTY)"
        ])
        self.target_combo.currentIndexChanged.connect(self.trigger_conversion)

        selector_layout.addWidget(self.source_combo, 1)
        selector_layout.addWidget(swap_btn)
        selector_layout.addWidget(self.target_combo, 1)
        card_layout.addLayout(selector_layout)

        # Source input text
        self.src_text = QTextEdit()
        self.src_text.setPlaceholderText("Enter or select mistyped text to convert (e.g. 'go home now' or 'لخ اخةث ىخص')...")
        self.src_text.setFixedHeight(85)
        self.src_text.textChanged.connect(self.on_text_edited)
        card_layout.addWidget(self.src_text)

        # Converted Preview text
        self.tgt_text = QTextEdit()
        self.tgt_text.setPlaceholderText("Live layout preview will appear here...")
        self.tgt_text.setFixedHeight(85)
        self.tgt_text.setReadOnly(True)
        card_layout.addWidget(self.tgt_text)

        # Options and status bar
        options_layout = QHBoxLayout()
        self.chk_punctuation = QCheckBox("Preserve Punctuation (!@#)")
        self.chk_punctuation.stateChanged.connect(self.trigger_conversion)

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #888888; font-size: 11px;")

        options_layout.addWidget(self.chk_punctuation)
        options_layout.addStretch()
        options_layout.addWidget(self.status_label)
        card_layout.addLayout(options_layout)

        # Action Buttons
        actions_layout = QHBoxLayout()
        self.copy_btn = QPushButton("📋 Copy Converted")
        self.copy_btn.clicked.connect(self.copy_converted)

        self.replace_btn = QPushButton("⏎ Replace Selected")
        self.replace_btn.setObjectName("primaryBtn")
        self.replace_btn.clicked.connect(self.replace_selected)

        self.undo_btn = QPushButton("↩ Undo")
        self.undo_btn.clicked.connect(self.undo_conversion)

        actions_layout.addWidget(self.copy_btn)
        actions_layout.addWidget(self.replace_btn)
        actions_layout.addWidget(self.undo_btn)
        actions_layout.addStretch()

        esc_hint = QLabel("Esc to close")
        esc_hint.setStyleSheet("color: #666; font-size: 11px;")
        actions_layout.addWidget(esc_hint)

        card_layout.addLayout(actions_layout)
        main_layout.addWidget(self.card)

        # Drop shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 8)
        self.card.setGraphicsEffect(shadow)

        # Shortcuts
        QShortcut(QKeySequence("Escape"), self, self.close)
        QShortcut(QKeySequence("Ctrl+Return"), self, self.replace_selected)

        self.center_window()

        if initial_text:
            self.src_text.setText(initial_text)

    def center_window(self):
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            self.move((geo.width() - self.width()) // 2, (geo.height() - self.height()) // 2)

    def on_text_edited(self):
        self.trigger_conversion()

    def swap_layouts(self):
        cur_src = self.src_text.toPlainText()
        cur_tgt = self.tgt_text.toPlainText()
        if cur_tgt:
            self.src_text.setText(cur_tgt)

    def trigger_conversion(self):
        text = self.src_text.toPlainText()
        if not text:
            self.tgt_text.clear()
            self.status_label.setText("Ready")
            return

        # Determine direction
        src_idx = self.source_combo.currentIndex()
        tgt_idx = self.target_combo.currentIndex()

        if src_idx == 1:
            direction = "en_to_ar"
        elif src_idx in (2, 3):
            direction = "ar_to_en"
        else:
            direction = "auto"

        # Determine layout
        layout = "102" if (src_idx == 3 or tgt_idx == 2) else "101"
        preserve = self.chk_punctuation.isChecked()

        converted, applied_dir, conf = KeyboardLayoutConverterEngine.convert(
            text,
            direction=direction,
            layout=layout,
            preserve_punctuation=preserve
        )

        self.tgt_text.setText(converted)

        # Adjust text direction
        if applied_dir == "en_to_ar":
            self.src_text.setLayoutDirection(Qt.LeftToRight)
            self.tgt_text.setLayoutDirection(Qt.RightToLeft)
            dir_text = f"US QWERTY ➔ Arabic {layout}"
        else:
            self.src_text.setLayoutDirection(Qt.RightToLeft)
            self.tgt_text.setLayoutDirection(Qt.LeftToRight)
            dir_text = f"Arabic {layout} ➔ US QWERTY"

        self.status_label.setText(f"✓ Converted ({dir_text}) [{conf * 100:.0f}% confidence]")

    def copy_converted(self):
        text = self.tgt_text.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            orig = self.copy_btn.text()
            self.copy_btn.setText("✓ Copied!")
            QTimer.singleShot(1500, lambda: self.copy_btn.setText(orig))

    def replace_selected(self):
        text = self.tgt_text.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            self.close()

    def undo_conversion(self):
        if self.original_text:
            self.src_text.setText(self.original_text)


def launch_converter_popup(initial_text: str = ""):
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    window = KeyboardLayoutConverterPopup(initial_text)
    window.show()
    app.exec()


if __name__ == "__main__":
    test_text = sys.argv[1] if len(sys.argv) > 1 else "go home now"
    launch_converter_popup(test_text)

