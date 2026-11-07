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
    assert '#define PRODUCT_NAME "Powertool"' in content
    assert "Microsoft Corporation" in content  # Retains Microsoft copyright attribution


def test_tray_icon_branding():
    """Verify Powertool branding in runner tray tooltip"""
    tray_path = os.path.join(REPO_ROOT, "src", "runner", "tray_icon.cpp")
    with open(tray_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert 'pt_version_tooltip_stream << L"Powertool "' in content
    assert 'MessageBoxW(nullptr, about_msg.c_str(), L"About Powertool", MB_OK);' in content


def test_settings_window_title_branding():
    """Verify Settings window title rebranded to Powertool Settings"""
    resw_path = os.path.join(REPO_ROOT, "src", "settings-ui", "Settings.UI", "Strings", "en-us", "Resources.resw")
    with open(resw_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "<value>Powertool Settings</value>" in content
    assert "<value>Administrator: Powertool Settings</value>" in content


def test_developer_profile_attribution():
    """Verify developer identity (En-Dhiaa) and GitHub links in Settings & ViewModels"""
    dev_vm = os.path.join(REPO_ROOT, "src", "settings-ui", "Settings.UI", "ViewModels", "DeveloperViewModel.cs")
    assert os.path.isfile(dev_vm)
    with open(dev_vm, "r", encoding="utf-8") as f:
        vm_text = f.read()
    assert '"En-Dhiaa"' in vm_text
    assert '"https://github.com/En-Dhiaa"' in vm_text
    assert '"https://github.com/En-Dhiaa/PowerToys/issues/new/choose"' in vm_text

    dev_view = os.path.join(REPO_ROOT, "src", "settings-ui", "Settings.UI", "SettingsXAML", "Views", "DeveloperPage.xaml")
    assert os.path.isfile(dev_view)
    with open(dev_view, "r", encoding="utf-8") as f:
        view_text = f.read()
    assert "En-Dhiaa" in view_text
    assert "https://github.com/En-Dhiaa" in view_text
    assert "Powertool" in view_text


def test_linux_packaging_and_desktop_parity():
    """Verify Linux packaging, desktop entry, metainfo, and runner existence"""
    linux_files = [
        os.path.join(REPO_ROOT, "linux", "powertool.desktop"),
        os.path.join(REPO_ROOT, "linux", "org.endhiaa.Powertool.metainfo.xml"),
        os.path.join(REPO_ROOT, "linux", "debian", "control"),
        os.path.join(REPO_ROOT, "linux", "debian", "rules"),
        os.path.join(REPO_ROOT, "linux", "powertool.spec"),
        os.path.join(REPO_ROOT, "linux", "AppRun"),
        os.path.join(REPO_ROOT, "linux", "powertool-linux.py"),
    ]
    for lf in linux_files:
        assert os.path.isfile(lf), f"Linux parity file missing: {lf}"

    # Verify desktop entry name
    with open(os.path.join(REPO_ROOT, "linux", "powertool.desktop"), "r", encoding="utf-8") as f:
        dt = f.read()
    assert "Name=Powertool" in dt
    assert "Exec=python3" in dt


def test_custom_issue_reporting_urls():
    """Verify custom issue reporting URL destinations point to En-Dhiaa repository"""
    bug_cpp = os.path.join(REPO_ROOT, "src", "runner", "bug_report_dialog.cpp")
    with open(bug_cpp, "r", encoding="utf-8") as f:
        cpp_text = f.read()
    assert "https://github.com/En-Dhiaa/PowerToys/issues/new" in cpp_text

    gen_vm = os.path.join(REPO_ROOT, "src", "settings-ui", "Settings.UI", "ViewModels", "GeneralViewModel.cs")
    with open(gen_vm, "r", encoding="utf-8") as f:
        gen_text = f.read()
    assert "https://github.com/En-Dhiaa/PowerToys/issues/new?template=bug_report.yml" in gen_text

    shell_cs = os.path.join(REPO_ROOT, "src", "settings-ui", "Settings.UI", "SettingsXAML", "Views", "ShellPage.xaml.cs")
    with open(shell_cs, "r", encoding="utf-8") as f:
        shell_text = f.read()
    assert "https://github.com/En-Dhiaa/PowerToys/issues/new/choose" in shell_text


def test_issue_templates_complete():
    """Verify all 5 required issue templates and config exist with privacy reminders"""
    templates_dir = os.path.join(REPO_ROOT, ".github", "ISSUE_TEMPLATE")
    expected_files = [
        "config.yml",
        "bug_report.yml",
        "feature_request.yml",
        "translation_problem.yml",
        "keyboard_layout_conversion_problem.yml",
        "offline_translation_model_problem.yml",
    ]
    for fn in expected_files:
        p = os.path.join(templates_dir, fn)
        assert os.path.isfile(p), f"Issue template missing: {fn}"
        with open(p, "r", encoding="utf-8") as f:
            content = f.read()
        if fn in ["bug_report.yml", "translation_problem.yml", "keyboard_layout_conversion_problem.yml", "offline_translation_model_problem.yml"]:
            assert any(kw in content.lower() for kw in ["privacy", "private", "sensitive"])


