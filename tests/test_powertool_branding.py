"""
Unit Tests for PowerTool Branding and Assets
PowerTool Extended Edition
"""

import os
from PIL import Image

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def test_branding_icon_files_exist():
    """Verify all required icon deliverables exist"""
    paths = [
        os.path.join(REPO_ROOT, "assets", "powertool_branding", "PowerTool.ico"),
        os.path.join(REPO_ROOT, "assets", "powertool_branding", "PowerTool_256.png"),
        os.path.join(REPO_ROOT, "assets", "powertool_branding", "PowerTool_512.png"),
        os.path.join(REPO_ROOT, "assets", "powertool_branding", "PowerTool_1024.png"),
        os.path.join(REPO_ROOT, "src", "runner", "svgs", "icon.ico"),
        os.path.join(REPO_ROOT, "src", "settings-ui", "Settings.UI", "Assets", "Settings", "icon.ico"),
        os.path.join(REPO_ROOT, "src", "settings-ui", "Settings.UI", "Assets", "Settings", "Icons", "OfflineTranslator.png"),
        os.path.join(REPO_ROOT, "src", "settings-ui", "Settings.UI", "Assets", "Settings", "Icons", "KeyboardLayoutConverter.png"),
    ]
    for p in paths:
        assert os.path.isfile(p), f"Asset missing: {p}"


def test_multi_resolution_ico():
    """Verify Master PowerTool.ico contains multi-resolution icons up to 256x256"""
    ico_path = os.path.join(REPO_ROOT, "assets", "powertool_branding", "PowerTool.ico")
    im = Image.open(ico_path)
    assert im.format == "ICO"
    # ICO must support 256x256
    assert (256, 256) in im.ico.sizes() or im.size == (256, 256)


def test_version_h_branding():
    """Verify PRODUCT_NAME and COMPANY_NAME updated in version.h"""
    ver_path = os.path.join(REPO_ROOT, "src", "common", "version", "version.h")
    with open(ver_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert '#define PRODUCT_NAME "PowerTool"' in content
    assert "Microsoft Corporation" in content  # Retains Microsoft copyright attribution


def test_tray_icon_branding():
    """Verify PowerTool branding in runner tray tooltip"""
    tray_path = os.path.join(REPO_ROOT, "src", "runner", "tray_icon.cpp")
    with open(tray_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert 'pt_version_tooltip_stream << L"PowerTool "' in content
    assert 'MessageBoxW(nullptr, about_msg.c_str(), L"About PowerTool", MB_OK);' in content


def test_settings_window_title_branding():
    """Verify Settings window title rebranded to PowerTool Settings"""
    resw_path = os.path.join(REPO_ROOT, "src", "settings-ui", "Settings.UI", "Strings", "en-us", "Resources.resw")
    with open(resw_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "<value>PowerTool Settings</value>" in content
    assert "<value>Administrator: PowerTool Settings</value>" in content
