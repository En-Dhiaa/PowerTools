"""
Unit and integration tests for Powertool Linux Edition modules.
Verifies:
- PlatformDetector logic
- PowertoolRun search and calculation engine
- PowerRenameLinux regex, search/replace, and case transforms
- ColorPickerEngine color conversions
- WindowTiling ZoneLayout bounding boxes
- Linux packaging scripts and desktop parity
Developed by En-Dhiaa.
"""

import os
import sys
import pytest

# Ensure LinuxModules and common modules are in sys.path
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(TEST_DIR, ".."))
LINUX_MODULES = os.path.join(ROOT_DIR, "src", "modules", "LinuxModules")
if LINUX_MODULES not in sys.path:
    sys.path.insert(0, LINUX_MODULES)

from PlatformDetector import PlatformDetector
from PowertoolRun import CalculatorEngine, ApplicationIndex
from PowerRenameLinux import PowerRenameEngine
from ColorPickerLinux import ColorPickerEngine
from WindowTilingLinux import ZoneLayout
from ImageResizerLinux import PRESETS


def test_platform_detector_structure():
    """Verify PlatformDetector returns well-formed metadata dictionary."""
    info = PlatformDetector.detect_all()
    assert isinstance(info, dict)
    assert "distribution" in info
    assert "desktop_environment" in info
    assert "session_type" in info
    assert "init_system" in info
    assert "is_wsl" in info


def test_powertool_run_calculator():
    """Verify Powertool Run inline calculator evaluates expressions accurately."""
    assert CalculatorEngine.evaluate("2 + 2") == "4"
    assert CalculatorEngine.evaluate("25 * 4 + 10") == "110"
    assert CalculatorEngine.evaluate("100 / 4") == "25.0"
    assert CalculatorEngine.evaluate("sqrt(144)") == "12.0"
    assert CalculatorEngine.evaluate("sin(0)") == "0.0"
    # Malformed queries should return None, not crash
    assert CalculatorEngine.evaluate("hello world") is None
    assert CalculatorEngine.evaluate("import os") is None


def test_powertool_run_app_index():
    """Verify ApplicationIndex provides fallback built-in applications."""
    apps = ApplicationIndex.get_applications()
    assert isinstance(apps, list)
    assert len(apps) > 0
    names = [a["name"] for a in apps]
    assert any("Terminal" in n or "Offline Translator" in n or "Files" in n for n in names)


def test_power_rename_engine_basic():
    """Verify PowerRename plain text replacement."""
    files = ["/tmp/report_2025.txt", "/tmp/summary_2025.pdf"]
    results = PowerRenameEngine.preview_rename(
        files, search="2025", replace="2026",
        use_regex=False, match_case=True
    )
    assert len(results) == 2
    assert results[0]["new_name"] == "report_2026.txt"
    assert results[0]["changed"] is True
    assert results[1]["new_name"] == "summary_2026.pdf"
    assert results[1]["changed"] is True


def test_power_rename_engine_regex():
    """Verify PowerRename regex pattern replacement."""
    files = ["/tmp/img_001.jpg", "/tmp/img_002.jpg"]
    results = PowerRenameEngine.preview_rename(
        files, search=r"img_(\d+)", replace=r"photo_\1",
        use_regex=True, match_case=False
    )
    assert results[0]["new_name"] == "photo_001.jpg"
    assert results[1]["new_name"] == "photo_002.jpg"
    assert results[0]["changed"] is True


def test_power_rename_engine_case_transform():
    """Verify PowerRename case conversion (UPPERCASE, lowercase, Title Case)."""
    files = ["/tmp/my_test_document.txt"]
    upper_res = PowerRenameEngine.preview_rename(
        files, search="", replace="", case_transform="UPPERCASE", include_extension=True
    )
    assert upper_res[0]["new_name"] == "MY_TEST_DOCUMENT.TXT"

    lower_res = PowerRenameEngine.preview_rename(
        ["/tmp/MY_TEST_DOCUMENT.TXT"], search="", replace="", case_transform="lowercase", include_extension=True
    )
    assert lower_res[0]["new_name"] == "my_test_document.txt"


def test_color_picker_cmyk_conversion():
    """Verify RGB to CMYK color conversion."""
    # Pure red: (255, 0, 0) -> C:0%, M:100%, Y:100%, K:0%
    c, m, y, k = ColorPickerEngine.rgb_to_cmyk(255, 0, 0)
    assert (c, m, y, k) == (0, 100, 100, 0)

    # Pure black: (0, 0, 0) -> K:100%
    c, m, y, k = ColorPickerEngine.rgb_to_cmyk(0, 0, 0)
    assert (c, m, y, k) == (0, 0, 0, 100)

    # Pure white: (255, 255, 255) -> 0% all
    c, m, y, k = ColorPickerEngine.rgb_to_cmyk(255, 255, 255)
    assert (c, m, y, k) == (0, 0, 0, 0)


def test_window_tiling_zone_calculations():
    """Verify FancyZones bounding box calculations for each preset layout."""
    screen_w, screen_h = 1920, 1080
    padding = 10

    # 2-Column Split
    zones_2col = ZoneLayout.calculate_zones(screen_w, screen_h, "2-Column Split", padding=padding)
    assert len(zones_2col) == 2
    z1_x, z1_y, z1_w, z1_h = zones_2col[0]
    z2_x, z2_y, z2_w, z2_h = zones_2col[1]
    assert z1_x == padding
    assert z2_x > z1_x
    assert z1_w + z2_w + (padding * 3) <= screen_w

    # 3-Column Split
    zones_3col = ZoneLayout.calculate_zones(screen_w, screen_h, "3-Column Split", padding=padding)
    assert len(zones_3col) == 3

    # Priority Grid
    zones_prio = ZoneLayout.calculate_zones(screen_w, screen_h, "Priority Grid", padding=padding)
    assert len(zones_prio) == 3
    # Center column is wider than side columns
    left_w = zones_prio[0][2]
    center_w = zones_prio[1][2]
    assert center_w > left_w

    # 2x2 Quadrant Grid
    zones_4quad = ZoneLayout.calculate_zones(screen_w, screen_h, "2x2 Quadrant Grid", padding=padding)
    assert len(zones_4quad) == 4


def test_image_resizer_presets():
    """Verify Image Resizer preset dimensions."""
    assert "Small (854 × 480)" in PRESETS
    assert PRESETS["Small (854 × 480)"] == (854, 480)
    assert "Large (1920 × 1080)" in PRESETS
    assert PRESETS["Large (1920 × 1080)"] == (1920, 1080)


def test_linux_packaging_scripts_exist():
    """Verify all packaging scripts and manifests exist on disk."""
    linux_dir = os.path.join(ROOT_DIR, "linux")
    assert os.path.isfile(os.path.join(linux_dir, "powertool-linux.py"))
    assert os.path.isfile(os.path.join(linux_dir, "powertool.desktop"))
    assert os.path.isfile(os.path.join(linux_dir, "powertool.spec"))
    assert os.path.isfile(os.path.join(linux_dir, "org.endhiaa.Powertool.metainfo.xml"))
    assert os.path.isfile(os.path.join(linux_dir, "setup-dev-env.sh"))
    assert os.path.isfile(os.path.join(linux_dir, "build-deb.sh"))
    assert os.path.isfile(os.path.join(linux_dir, "build-appimage.sh"))
    assert os.path.isfile(os.path.join(linux_dir, "build-rpm.sh"))
    assert os.path.isfile(os.path.join(linux_dir, "debian", "control"))
    assert os.path.isfile(os.path.join(linux_dir, "debian", "rules"))


def test_linux_branding_and_attribution():
    """Verify Linux files feature correct Powertool branding and En-Dhiaa attribution."""
    linux_py = os.path.join(ROOT_DIR, "linux", "powertool-linux.py")
    with open(linux_py, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Powertool" in content
    assert "En-Dhiaa" in content
    assert "https://github.com/En-Dhiaa" in content

    desktop_file = os.path.join(ROOT_DIR, "linux", "powertool.desktop")
    with open(desktop_file, "r", encoding="utf-8") as f:
        d_content = f.read()
    assert "Name=Powertool" in d_content
    assert "En-Dhiaa" in d_content

    metainfo_file = os.path.join(ROOT_DIR, "linux", "org.endhiaa.Powertool.metainfo.xml")
    with open(metainfo_file, "r", encoding="utf-8") as f:
        m_content = f.read()
    assert "<developer_name>En-Dhiaa</developer_name>" in m_content
    assert "https://github.com/En-Dhiaa/PowerToys/issues" in m_content
