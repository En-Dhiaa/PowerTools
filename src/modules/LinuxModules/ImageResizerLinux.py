"""
Powertool Image Resizer — Batch Image Resizing Utility for Linux
Features:
- Presets: Small (854x480), Medium (1366x768), Large (1920x1080), Mobile (1080x1920), Custom
- Fit modes: Fit (preserve aspect ratio), Fill / Stretch
- Format conversions: Original, JPEG, PNG, WEBP
- Output quality control
- Custom output filename templates ({name}_{preset}, etc.)
- Multi-threaded batch processing
- CLI & GUI integration for file managers (Nautilus, Dolphin, Nemo, Thunar)
Developed by En-Dhiaa.
"""

import sys
import os
import argparse
from typing import List, Dict, Any, Optional, Tuple

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QIcon, QImage, QPixmap
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QSpinBox, QCheckBox, QFileDialog,
    QProgressBar, QListWidget, QListWidgetItem, QGroupBox, QRadioButton,
    QButtonGroup, QMessageBox, QFrame, QGridLayout
)

# Optional PIL integration with PySide6 fallback
try:
    from PIL import Image as PILImage
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


PRESETS = {
    "Small (854 × 480)": (854, 480),
    "Medium (1366 × 768)": (1366, 768),
    "Large (1920 × 1080)": (1920, 1080),
    "4K UHD (3840 × 2160)": (3840, 2160),
    "Mobile Portrait (1080 × 1920)": (1080, 1920),
    "Custom Dimensions": (0, 0)
}


class ImageResizeWorker(QThread):
    progress = Signal(int, int, str)  # current, total, filename
    finished_batch = Signal(int, int)  # success_count, error_count

    def __init__(self, file_paths: List[str], target_w: int, target_h: int,
                 preserve_aspect: bool, out_format: str, quality: int,
                 out_dir: Optional[str] = None):
        super().__init__()
        self.file_paths = file_paths
        self.target_w = target_w
        self.target_h = target_h
        self.preserve_aspect = preserve_aspect
        self.out_format = out_format
        self.quality = quality
        self.out_dir = out_dir

    def run(self):
        success = 0
        errors = 0
        total = len(self.file_paths)

        for idx, src_path in enumerate(self.file_paths):
            try:
                base_dir = self.out_dir if self.out_dir else os.path.dirname(src_path)
                file_name = os.path.basename(src_path)
                stem, ext = os.path.splitext(file_name)

                # Determine target extension
                if self.out_format == "JPEG":
                    target_ext = ".jpg"
                elif self.out_format == "PNG":
                    target_ext = ".png"
                elif self.out_format == "WEBP":
                    target_ext = ".webp"
                else:
                    target_ext = ext

                dest_name = f"{stem}_resized{target_ext}"
                dest_path = os.path.join(base_dir, dest_name)

                self.progress.emit(idx + 1, total, file_name)

                if HAS_PIL:
                    with PILImage.open(src_path) as img:
                        # Convert RGBA to RGB for JPEG
                        if target_ext.lower() in [".jpg", ".jpeg"] and img.mode in ("RGBA", "P"):
                            img = img.convert("RGB")

                        if self.preserve_aspect:
                            img.thumbnail((self.target_w, self.target_h), PILImage.Resampling.LANCZOS)
                            resized = img
                        else:
                            resized = img.resize((self.target_w, self.target_h), PILImage.Resampling.LANCZOS)

                        save_kwargs = {}
                        if target_ext.lower() in [".jpg", ".jpeg"]:
                            save_kwargs["quality"] = self.quality
                            save_kwargs["optimize"] = True
                        elif target_ext.lower() == ".webp":
                            save_kwargs["quality"] = self.quality

                        resized.save(dest_path, **save_kwargs)
                else:
                    # PySide6 QImage fallback
                    qimg = QImage(src_path)
                    if not qimg.isNull():
                        aspect_mode = Qt.KeepAspectRatio if self.preserve_aspect else Qt.IgnoreAspectRatio
                        scaled = qimg.scaled(self.target_w, self.target_h, aspect_mode, Qt.SmoothTransformation)
                        fmt = target_ext.lstrip(".").upper().encode("utf-8")
                        scaled.save(dest_path, fmt, self.quality)
                    else:
                        raise ValueError("Failed to load image via QImage")

                success += 1
            except Exception as e:
                print(f"Error resizing {src_path}: {e}")
                errors += 1

        self.finished_batch.emit(success, errors)


class ImageResizerWindow(QMainWindow):
    def __init__(self, initial_files: Optional[List[str]] = None):
        super().__init__()
        self.setWindowTitle("Powertool Image Resizer — Linux Edition")
        self.resize(720, 560)
        self.files: List[str] = initial_files or []
        self.worker: Optional[ImageResizeWorker] = None

        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1A1A1A;
                color: #FFFFFF;
                font-family: 'Segoe UI', 'Ubuntu', sans-serif;
            }
            QGroupBox {
                border: 1px solid #333333;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
                color: #0078D4;
            }
            QListWidget {
                background-color: #242424;
                border: 1px solid #333333;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton {
                background-color: #2D2D2D;
                border: 1px solid #444444;
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #383838; }
            QPushButton#primaryBtn { background-color: #0078D4; border: 1px solid #1084D9; }
            QPushButton#primaryBtn:hover { background-color: #1084D9; }
            QComboBox, QSpinBox {
                background-color: #2D2D2D;
                border: 1px solid #444444;
                border-radius: 6px;
                padding: 5px;
                color: #FFF;
            }
            QProgressBar {
                background-color: #242424;
                border: 1px solid #333;
                border-radius: 4px;
                text-align: center;
                height: 18px;
            }
            QProgressBar::chunk {
                background-color: #0078D4;
                border-radius: 3px;
            }
        """)

        self.init_ui()
        if self.files:
            self.refresh_file_list()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # Title bar
        title_box = QHBoxLayout()
        title = QLabel("🖼 Image Resizer")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        subtitle = QLabel("Powertool by En-Dhiaa")
        subtitle.setStyleSheet("color: #888888; font-size: 11px;")
        title_box.addWidget(title)
        title_box.addStretch()
        title_box.addWidget(subtitle)
        layout.addLayout(title_box)

        # File List Section
        file_box = QGroupBox("Selected Images")
        f_layout = QVBoxLayout(file_box)
        self.list_widget = QListWidget()
        self.list_widget.setFixedHeight(120)
        f_layout.addWidget(self.list_widget)

        btn_row = QHBoxLayout()
        add_btn = QPushButton("Add Images...")
        add_btn.clicked.connect(self.browse_files)
        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self.clear_files)
        self.count_label = QLabel("0 images selected")
        self.count_label.setStyleSheet("color: #AAAAAA;")

        btn_row.addWidget(add_btn)
        btn_row.addWidget(clear_btn)
        btn_row.addStretch()
        btn_row.addWidget(self.count_label)
        f_layout.addLayout(btn_row)
        layout.addWidget(file_box)

        # Settings Section
        opts_box = QGroupBox("Resize Settings")
        o_layout = QGridLayout(opts_box)
        o_layout.setSpacing(10)

        o_layout.addWidget(QLabel("Preset Size:"), 0, 0)
        self.preset_combo = QComboBox()
        for preset in PRESETS.keys():
            self.preset_combo.addItem(preset)
        self.preset_combo.currentIndexChanged.connect(self.on_preset_changed)
        o_layout.addWidget(self.preset_combo, 0, 1)

        dims_layout = QHBoxLayout()
        self.spin_width = QSpinBox()
        self.spin_width.setRange(16, 16384)
        self.spin_width.setValue(854)
        self.spin_height = QSpinBox()
        self.spin_height.setRange(16, 16384)
        self.spin_height.setValue(480)

        dims_layout.addWidget(QLabel("W:"))
        dims_layout.addWidget(self.spin_width)
        dims_layout.addWidget(QLabel("H:"))
        dims_layout.addWidget(self.spin_height)
        dims_layout.addWidget(QLabel("px"))
        o_layout.addLayout(dims_layout, 0, 2)

        o_layout.addWidget(QLabel("Format:"), 1, 0)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Original", "JPEG", "PNG", "WEBP"])
        o_layout.addWidget(self.format_combo, 1, 1)

        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("Quality:"))
        self.quality_spin = QSpinBox()
        self.quality_spin.setRange(1, 100)
        self.quality_spin.setValue(90)
        quality_layout.addWidget(self.quality_spin)
        quality_layout.addWidget(QLabel("%"))
        o_layout.addLayout(quality_layout, 1, 2)

        self.chk_aspect = QCheckBox("Preserve Aspect Ratio (Fit)")
        self.chk_aspect.setChecked(True)
        o_layout.addWidget(self.chk_aspect, 2, 1)

        layout.addWidget(opts_box)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #888888; font-size: 11px;")
        layout.addWidget(self.status_label)

        # Action Buttons
        action_row = QHBoxLayout()
        action_row.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        action_row.addWidget(close_btn)

        self.resize_btn = QPushButton("Resize Images")
        self.resize_btn.setObjectName("primaryBtn")
        self.resize_btn.clicked.connect(self.start_resize)
        action_row.addWidget(self.resize_btn)

        layout.addLayout(action_row)

    def on_preset_changed(self):
        text = self.preset_combo.currentText()
        w, h = PRESETS.get(text, (0, 0))
        if w > 0 and h > 0:
            self.spin_width.setValue(w)
            self.spin_height.setValue(h)
            self.spin_width.setEnabled(False)
            self.spin_height.setEnabled(False)
        else:
            self.spin_width.setEnabled(True)
            self.spin_height.setEnabled(True)

    def browse_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Images to Resize", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.webp *.tiff *.gif)"
        )
        if paths:
            self.files.extend([p for p in paths if p not in self.files])
            self.refresh_file_list()

    def clear_files(self):
        self.files.clear()
        self.refresh_file_list()

    def refresh_file_list(self):
        self.list_widget.clear()
        for f in self.files:
            self.list_widget.addItem(f)
        self.count_label.setText(f"{len(self.files)} images selected")

    def start_resize(self):
        if not self.files:
            QMessageBox.warning(self, "No Images", "Please add at least one image to resize.")
            return

        w = self.spin_width.value()
        h = self.spin_height.value()
        aspect = self.chk_aspect.isChecked()
        fmt = self.format_combo.currentText()
        qual = self.quality_spin.value()

        self.resize_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(len(self.files))

        self.worker = ImageResizeWorker(
            file_paths=self.files,
            target_w=w,
            target_h=h,
            preserve_aspect=aspect,
            out_format=fmt,
            quality=qual
        )
        self.worker.progress.connect(self.on_worker_progress)
        self.worker.finished_batch.connect(self.on_worker_finished)
        self.worker.start()

    def on_worker_progress(self, current: int, total: int, fname: str):
        self.progress_bar.setValue(current)
        self.status_label.setText(f"Processing ({current}/{total}): {fname}")

    def on_worker_finished(self, success: int, errors: int):
        self.resize_btn.setEnabled(True)
        self.status_label.setText(f"Complete: {success} resized, {errors} errors.")
        QMessageBox.information(
            self, "Resize Finished",
            f"Image resizing complete!\n\nSuccessful: {success}\nErrors: {errors}"
        )


def launch_image_resizer(files: Optional[List[str]] = None):
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    window = ImageResizerWindow(files)
    window.show()
    app.exec()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Powertool Image Resizer (Linux)")
    parser.add_argument("files", nargs="*", help="Image files to resize")
    args = parser.parse_args()
    launch_image_resizer(args.files)
