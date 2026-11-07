"""
Offline Translator Modern Windows 11 Popup UI
PowerTool Extended Edition
"""

import sys
import os
import time
from typing import Optional

from PySide6.QtCore import Qt, QThread, Signal, Slot, QTimer
from PySide6.QtGui import QIcon, QFont, QColor, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QComboBox, QFrame, QGraphicsDropShadowEffect, QMessageBox
)

from OfflineTranslatorEngine import OfflineTranslator, ModelManager, TranslationResult, ModelNotInstalledError


class TranslationWorker(QThread):
    finished_signal = Signal(object)
    error_signal = Signal(str)

    def __init__(self, translator: OfflineTranslator, text: str, from_code: str, to_code: str):
        super().__init__()
        self.translator = translator
        self.text = text
        self.from_code = from_code
        self.to_code = to_code

    def run(self):
        try:
            res = self.translator.translate(self.text, self.from_code, self.to_code)
            self.finished_signal.emit(res)
        except ModelNotInstalledError as e:
            self.error_signal.emit(str(e))
        except Exception as e:
            self.error_signal.emit(f"Translation error: {str(e)}")


class ModelManagerDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.Window)
        self.setWindowTitle("Powertool Offline Translation Models")
        self.resize(520, 360)
        self.setStyleSheet("""
            QWidget {
                background-color: #202020;
                color: #FFFFFF;
                font-family: 'Segoe UI', sans-serif;
            }
            QFrame.modelCard {
                background-color: #2A2A2A;
                border: 1px solid #3E3E3E;
                border-radius: 8px;
                padding: 12px;
            }
            QPushButton {
                background-color: #333333;
                border: 1px solid #444444;
                border-radius: 6px;
                color: #FFFFFF;
                padding: 6px 12px;
            }
            QPushButton:hover { background-color: #3E3E3E; }
            QPushButton#primaryBtn { background-color: #0078D4; font-weight: bold; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QLabel("Offline Translation Models (CTranslate2 & Argos)")
        header.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(header)

        sub = QLabel("Models run 100% locally on CPU without internet connectivity.")
        sub.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(sub)

        self.cards_layout = QVBoxLayout()
        layout.addLayout(self.cards_layout)

        self.refresh_models()

        # Disk info
        self.disk_label = QLabel()
        self.disk_label.setStyleSheet("color: #777; font-size: 11px;")
        layout.addWidget(self.disk_label)
        self.update_disk_info()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn, alignment=Qt.AlignRight)

    def update_disk_info(self):
        mgr = ModelManager()
        info = mgr.get_disk_space_info()
        self.disk_label.setText(f"Storage path: {info['path']} ({info.get('free_gb', 0)} GB free)")

    def refresh_models(self):
        # Clear existing
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        mgr = ModelManager()
        for pkg in mgr.list_packages():
            card = QFrame()
            card.setProperty("class", "modelCard")
            c_layout = QHBoxLayout(card)
            c_layout.setContentsMargins(10, 8, 10, 8)

            info_layout = QVBoxLayout()
            title = QLabel(f"{pkg['from_name']} ➔ {pkg['to_name']} ({pkg['size_mb']} MB)")
            title.setFont(QFont("Segoe UI", 10, QFont.Bold))
            status_text = "● Installed & Ready" if pkg['is_installed'] else "○ Not Installed"
            status_color = "#4CAF50" if pkg['is_installed'] else "#FFA726"
            status_lbl = QLabel(status_text)
            status_lbl.setStyleSheet(f"color: {status_color}; font-size: 11px;")

            info_layout.addWidget(title)
            info_layout.addWidget(status_lbl)
            c_layout.addLayout(info_layout, 1)

            btn = QPushButton("Remove" if pkg['is_installed'] else "Download")
            if not pkg['is_installed']:
                btn.setObjectName("primaryBtn")
            btn.clicked.connect(lambda ch, p=pkg: self.toggle_package(p))
            c_layout.addWidget(btn)

            self.cards_layout.addWidget(card)

    def toggle_package(self, pkg):
        mgr = ModelManager()
        if pkg['is_installed']:
            mgr.remove_package(pkg['from_code'], pkg['to_code'])
            self.refresh_models()
        else:
            QMessageBox.information(self, "Download Model", f"Downloading {pkg['from_name']} ➔ {pkg['to_name']} model package ({pkg['size_mb']} MB)...")
            try:
                mgr.download_and_install_package(pkg['from_code'], pkg['to_code'])
                self.refresh_models()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to download model: {e}")


class TranslatorPopup(QWidget):
    def __init__(self, initial_text: str = "", default_from: str = "auto", default_to: str = "auto"):
        super().__init__()
        self.translator = OfflineTranslator()
        self.current_from = default_from
        self.current_to = default_to
        self.worker: Optional[TranslationWorker] = None

        self.init_ui(initial_text)

    def init_ui(self, initial_text: str):
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(540, 420)

        # Main background card
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
        """)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(18, 14, 18, 16)
        card_layout.setSpacing(10)

        # Header bar
        header_layout = QHBoxLayout()
        title_label = QLabel("Powertool Offline Translator")
        title_font = QFont("Segoe UI", 12, QFont.Bold)
        title_label.setFont(title_font)

        badge_label = QLabel("● Strictly Offline")
        badge_label.setStyleSheet("color: #4CAF50; font-size: 11px; font-weight: bold;")

        models_btn = QPushButton("📦 Models")
        models_btn.setToolTip("Manage offline translation packages")
        models_btn.clicked.connect(self.open_model_manager)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.setStyleSheet("background: transparent; border: none; font-size: 14px; color: #AAA;")
        close_btn.clicked.connect(self.close)

        header_layout.addWidget(title_label)
        header_layout.addWidget(badge_label)
        header_layout.addWidget(models_btn)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)
        card_layout.addLayout(header_layout)

        # Language selection bar
        lang_layout = QHBoxLayout()
        self.src_combo = QComboBox()
        self.src_combo.addItems(["Auto Detect", "Arabic (العربية)", "English"])
        self.src_combo.currentIndexChanged.connect(self.on_lang_changed)

        swap_btn = QPushButton("⇄")
        swap_btn.setFixedSize(34, 30)
        swap_btn.setToolTip("Swap translation languages")
        swap_btn.clicked.connect(self.swap_languages)

        self.tgt_combo = QComboBox()
        self.tgt_combo.addItems(["Auto Detect", "English", "Arabic (العربية)"])
        self.tgt_combo.currentIndexChanged.connect(self.on_lang_changed)

        lang_layout.addWidget(self.src_combo, 1)
        lang_layout.addWidget(swap_btn)
        lang_layout.addWidget(self.tgt_combo, 1)
        card_layout.addLayout(lang_layout)

        # Source text edit
        self.src_text = QTextEdit()
        self.src_text.setPlaceholderText("Enter or select text to translate offline...")
        self.src_text.setFixedHeight(95)
        self.src_text.textChanged.connect(self.on_text_edited)
        card_layout.addWidget(self.src_text)

        # Target text edit
        self.tgt_text = QTextEdit()
        self.tgt_text.setPlaceholderText("Offline translation will appear here...")
        self.tgt_text.setFixedHeight(95)
        self.tgt_text.setReadOnly(True)
        card_layout.addWidget(self.tgt_text)

        # Status & Duration bar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #888888; font-size: 11px;")
        card_layout.addWidget(self.status_label)

        # Bottom Action Bar
        actions_layout = QHBoxLayout()
        self.copy_btn = QPushButton("📋 Copy Translation")
        self.copy_btn.clicked.connect(self.copy_translation)

        self.replace_btn = QPushButton("⏎ Replace Selected")
        self.replace_btn.setObjectName("primaryBtn")
        self.replace_btn.clicked.connect(self.replace_selected)

        actions_layout.addWidget(self.copy_btn)
        actions_layout.addWidget(self.replace_btn)
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

        # Keyboard shortcuts
        QShortcut(QKeySequence("Escape"), self, self.close)
        QShortcut(QKeySequence("Ctrl+Return"), self, self.replace_selected)

        # Center on screen or near mouse
        self.center_window()

        if initial_text:
            self.src_text.setText(initial_text)
            self.trigger_translation()

    def center_window(self):
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            self.move((geo.width() - self.width()) // 2, (geo.height() - self.height()) // 2)

    def open_model_manager(self):
        self.model_dialog = ModelManagerDialog(self)
        self.model_dialog.show()

    def on_text_edited(self):
        text = self.src_text.toPlainText()
        if not text.strip():
            self.tgt_text.clear()
            self.status_label.setText("Ready")
            return

        # Adjust text direction
        from_code, _ = OfflineTranslator.detect_language(text)
        if from_code == "ar":
            self.src_text.setLayoutDirection(Qt.RightToLeft)
            self.tgt_text.setLayoutDirection(Qt.LeftToRight)
        else:
            self.src_text.setLayoutDirection(Qt.LeftToRight)
            self.tgt_text.setLayoutDirection(Qt.RightToLeft)

    def on_lang_changed(self):
        self.trigger_translation()

    def swap_languages(self):
        src_idx = self.src_combo.currentIndex()
        tgt_idx = self.tgt_combo.currentIndex()

        # Simple swap between ar and en
        if src_idx == 1:
            self.src_combo.setCurrentIndex(2)
        elif src_idx == 2:
            self.src_combo.setCurrentIndex(1)

        if tgt_idx == 1:
            self.tgt_combo.setCurrentIndex(2)
        elif tgt_idx == 2:
            self.tgt_combo.setCurrentIndex(1)

        # Swap text if present
        cur_src = self.src_text.toPlainText()
        cur_tgt = self.tgt_text.toPlainText()
        if cur_tgt:
            self.src_text.setText(cur_tgt)

    def trigger_translation(self):
        text = self.src_text.toPlainText().strip()
        if not text:
            return

        from_code = "auto"
        if self.src_combo.currentIndex() == 1:
            from_code = "ar"
        elif self.src_combo.currentIndex() == 2:
            from_code = "en"

        to_code = "auto"
        if self.tgt_combo.currentIndex() == 1:
            to_code = "en"
        elif self.tgt_combo.currentIndex() == 2:
            to_code = "ar"

        self.status_label.setText("Translating locally with CTranslate2...")
        self.worker = TranslationWorker(self.translator, text, from_code, to_code)
        self.worker.finished_signal.connect(self.on_translation_finished)
        self.worker.error_signal.connect(self.on_translation_error)
        self.worker.start()

    @Slot(object)
    def on_translation_finished(self, result: TranslationResult):
        self.tgt_text.setText(result.translated_text)
        if result.to_code == "ar":
            self.tgt_text.setLayoutDirection(Qt.RightToLeft)
        else:
            self.tgt_text.setLayoutDirection(Qt.LeftToRight)

        self.status_label.setText(f"✓ Translated offline ({result.from_code} → {result.to_code}) in {result.duration_ms:.1f}ms")

    @Slot(str)
    def on_translation_error(self, err_msg: str):
        self.status_label.setText(f"⚠️ {err_msg}")

    def copy_translation(self):
        text = self.tgt_text.toPlainText()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            orig_text = self.copy_btn.text()
            self.copy_btn.setText("✓ Copied!")
            QTimer.singleShot(1500, lambda: self.copy_btn.setText(orig_text))

    def replace_selected(self):
        text = self.tgt_text.toPlainText()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            self.close()


def launch_popup(initial_text: str = ""):
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    window = TranslatorPopup(initial_text)
    window.show()
    app.exec()


if __name__ == "__main__":
    test_text = sys.argv[1] if len(sys.argv) > 1 else "Hello, welcome to PowerTool Extended Edition!"
    launch_popup(test_text)

