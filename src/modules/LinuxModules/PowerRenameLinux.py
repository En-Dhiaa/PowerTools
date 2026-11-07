"""
PowerRename Linux — Advanced Batch File Renaming Tool
Features:
- Regex and standard search/replace
- Case conversion (Title Case, UPPERCASE, lowercase)
- Real-time live preview table
- Safe renaming execution
Developed by En-Dhiaa.
"""

import sys
import os
import re
from typing import List, Dict, Tuple

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QCheckBox, QComboBox,
    QFileDialog, QHeaderView, QMessageBox
)


class PowerRenameEngine:
    @classmethod
    def preview_rename(
        cls,
        files: List[str],
        search_pattern: str = "",
        replace_text: str = "",
        use_regex: bool = False,
        match_case: bool = False,
        case_transform: str = "None",
        include_extension: bool = False,
        **kwargs
    ) -> List[Dict[str, str]]:
        # Support keyword aliases 'search' and 'replace'
        if "search" in kwargs:
            search_pattern = kwargs["search"]
        if "replace" in kwargs:
            replace_text = kwargs["replace"]

        results = []
        flags = 0 if match_case else re.IGNORECASE

        for full_path in files:
            dirname, filename = os.path.split(full_path)
            stem, ext = os.path.splitext(filename)

            target = filename if include_extension else stem
            new_target = target

            # 1. Search and replace
            if search_pattern:
                try:
                    if use_regex:
                        new_target = re.sub(search_pattern, replace_text, target, flags=flags)
                    else:
                        if match_case:
                            new_target = target.replace(search_pattern, replace_text)
                        else:
                            compiled = re.compile(re.escape(search_pattern), re.IGNORECASE)
                            new_target = compiled.sub(replace_text, target)
                except Exception:
                    new_target = target

            # 2. Case transformation
            c_trans = case_transform.lower()
            if c_trans == "uppercase":
                new_target = new_target.upper()
                if include_extension:
                    ext = ext.upper()
            elif c_trans == "lowercase":
                new_target = new_target.lower()
                if include_extension:
                    ext = ext.lower()
            elif c_trans == "title case":
                new_target = new_target.title()

            new_filename = new_target if include_extension else f"{new_target}{ext}"
            new_full_path = os.path.join(dirname, new_filename)

            results.append({
                "original_path": full_path,
                "original_name": filename,
                "new_name": new_filename,
                "new_path": new_full_path,
                "changed": filename != new_filename
            })

        return results


class PowerRenameWindow(QWidget):
    def __init__(self, initial_files: Optional[List[str]] = None):
        super().__init__()
        self.files = initial_files or []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("PowerRename — Batch File Renamer (Powertool)")
        self.resize(750, 520)
        self.setStyleSheet("""
            QWidget {
                background-color: #1F1F1F;
                color: #FFFFFF;
                font-family: 'Segoe UI', 'Ubuntu', sans-serif;
            }
            QLineEdit, QComboBox {
                background-color: #2D2D2D;
                border: 1px solid #3E3E3E;
                border-radius: 6px;
                color: #FFFFFF;
                padding: 6px 10px;
                font-size: 13px;
            }
            QLineEdit:focus { border: 1px solid #0078D4; }
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
            QTableWidget {
                background-color: #262626;
                border: 1px solid #333333;
                border-radius: 6px;
                gridline-color: #383838;
            }
            QHeaderView::section {
                background-color: #2D2D2D;
                color: #FFFFFF;
                padding: 6px;
                border: 1px solid #383838;
                font-weight: bold;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header
        h_layout = QHBoxLayout()
        title = QLabel("PowerRename")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        h_layout.addWidget(title)
        h_layout.addStretch()

        add_btn = QPushButton("📁 Add Files...")
        add_btn.clicked.connect(self.select_files)
        h_layout.addWidget(add_btn)
        layout.addLayout(h_layout)

        # Controls Row 1: Search & Replace
        c1 = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search for...")
        self.search_input.textChanged.connect(self.update_preview)

        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("Replace with...")
        self.replace_input.textChanged.connect(self.update_preview)

        c1.addWidget(QLabel("Search:"))
        c1.addWidget(self.search_input, 1)
        c1.addWidget(QLabel("Replace:"))
        c1.addWidget(self.replace_input, 1)
        layout.addLayout(c1)

        # Controls Row 2: Options
        c2 = QHBoxLayout()
        self.chk_regex = QCheckBox("Use Regular Expressions")
        self.chk_regex.stateChanged.connect(self.update_preview)

        self.chk_case = QCheckBox("Match Case")
        self.chk_case.stateChanged.connect(self.update_preview)

        self.case_combo = QComboBox()
        self.case_combo.addItems(["None", "Title Case", "Uppercase", "Lowercase"])
        self.case_combo.currentIndexChanged.connect(self.update_preview)

        c2.addWidget(self.chk_regex)
        c2.addWidget(self.chk_case)
        c2.addWidget(QLabel("Format:"))
        c2.addWidget(self.case_combo)
        c2.addStretch()
        layout.addLayout(c2)

        # Table Preview
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Original Name", "Renamed Preview", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        layout.addWidget(self.table)

        # Bottom Actions
        b_layout = QHBoxLayout()
        self.status_lbl = QLabel(f"Files loaded: {len(self.files)}")
        self.status_lbl.setStyleSheet("color: #888;")
        b_layout.addWidget(self.status_lbl)
        b_layout.addStretch()

        self.apply_btn = QPushButton("Apply Rename")
        self.apply_btn.setObjectName("primaryBtn")
        self.apply_btn.clicked.connect(self.apply_rename)
        b_layout.addWidget(self.apply_btn)
        layout.addLayout(b_layout)

        self.update_preview()

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files to Rename")
        if files:
            self.files.extend(files)
            self.files = list(set(self.files))
            self.update_preview()

    def update_preview(self):
        self.table.setRowCount(0)
        self.status_lbl.setText(f"Files loaded: {len(self.files)}")

        if not self.files:
            return

        items = PowerRenameEngine.preview_rename(
            self.files,
            self.search_input.text(),
            self.replace_input.text(),
            use_regex=self.chk_regex.isChecked(),
            match_case=self.chk_case.isChecked(),
            case_transform=self.case_combo.currentText()
        )

        self.table.setRowCount(len(items))
        for row, it in enumerate(items):
            orig_item = QTableWidgetItem(it["original_name"])
            new_item = QTableWidgetItem(it["new_name"])
            status_item = QTableWidgetItem("Modified" if it["changed"] else "Unchanged")

            if it["changed"]:
                new_item.setForeground(QColor("#0078D4"))
                status_item.setForeground(QColor("#4CAF50"))
            else:
                status_item.setForeground(QColor("#777777"))

            self.table.setItem(row, 0, orig_item)
            self.table.setItem(row, 1, new_item)
            self.table.setItem(row, 2, status_item)

    def apply_rename(self):
        if not self.files:
            return

        items = PowerRenameEngine.preview_rename(
            self.files,
            self.search_input.text(),
            self.replace_input.text(),
            use_regex=self.chk_regex.isChecked(),
            match_case=self.chk_case.isChecked(),
            case_transform=self.case_combo.currentText()
        )

        renamed_count = 0
        new_file_list = []
        for it in items:
            if it["changed"] and os.path.exists(it["original_path"]):
                try:
                    os.rename(it["original_path"], it["new_path"])
                    new_file_list.append(it["new_path"])
                    renamed_count += 1
                except Exception as e:
                    new_file_list.append(it["original_path"])
            else:
                new_file_list.append(it["original_path"])

        self.files = new_file_list
        self.update_preview()
        QMessageBox.information(self, "Rename Complete", f"Successfully renamed {renamed_count} files.")


def launch_rename(files: Optional[List[str]] = None):
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    window = PowerRenameWindow(files)
    window.show()
    app.exec()


if __name__ == "__main__":
    launch_rename()
