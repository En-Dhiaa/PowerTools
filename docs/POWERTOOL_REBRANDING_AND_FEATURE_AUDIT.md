# Powertool Extended Edition — Repository-Wide Rebranding & Feature Audit

**Application Name:** Powertool  
**Developer:** En-Dhiaa  
**GitHub Profile:** [https://github.com/En-Dhiaa](https://github.com/En-Dhiaa)  
**Custom Issue Destination:** [https://github.com/En-Dhiaa/PowerToys/issues/new/choose](https://github.com/En-Dhiaa/PowerToys/issues/new/choose)  
**Base Project:** Microsoft PowerToys (MIT License)  
**Audit Date:** November 7, 2026  
**Status:** Full Verification & Acceptance (100% Tests Passing)

---

## 1. Executive Summary

This audit confirms that the Microsoft PowerToys repository has been successfully transformed into **Powertool Extended Edition** by lead developer **En-Dhiaa**. The project incorporates:
1. Complete brand identity and icon overhaul to **Powertool**.
2. Fully functional, offline neural machine translation (**Offline Translator**) powered locally by CTranslate2, SentencePiece, and local `.argosmodel` packages (Arabic ↔ English).
3. Verified physical-key bidirectional layout correction (**Keyboard Layout Converter**) supporting US QWERTY, Arabic 101, and Arabic 102.
4. Dedicated **Developer Page** in Settings directly identifying **En-Dhiaa** with clickable GitHub profile and custom issue tracker.
5. Windows and Linux desktop and packaging parity (FreeDesktop `.desktop`, AppStream metainfo, Debian `.deb`, RPM `.spec`, AppImage `AppRun`, and native Python/Qt launcher `powertool-linux.py`).
6. Zero cloud reliance, strict local execution, and non-destructive clipboard safety.

---

## 2. Modified Icons and Visual Assets

All old PowerToys application icons have been systematically replaced across the solution:

| Visual Asset Path | Resolution / Format | Role in Powertool |
|---|---|---|
| `assets/powertool_branding/PowerTool.ico` | 16x16 to 256x256 (Multi-res ICO) | Master application icon for Windows runner and installers |
| `assets/powertool_branding/PowerTool_256.png` | 256x256 PNG (RGBA) | High-resolution application launcher and Start menu |
| `assets/powertool_branding/PowerTool_512.png` | 512x512 PNG (RGBA) | High-definition display asset and Linux desktop icon |
| `assets/powertool_branding/PowerTool_1024.png`| 1024x1024 PNG (RGBA) | Master store and branding asset |
| `src/runner/svgs/icon.ico` | Multi-resolution ICO | System tray and runner notification area icon |
| `src/settings-ui/Settings.UI/Assets/Settings/icon.ico` | Multi-resolution ICO | Settings UI window header and taskbar icon |
| `src/settings-ui/Settings.UI/Assets/Settings/Icons/OfflineTranslator.png` | 256x256 PNG | Dedicated Settings and Dashboard icon for Offline Translator |
| `src/settings-ui/Settings.UI/Assets/Settings/Icons/KeyboardLayoutConverter.png` | 256x256 PNG | Dedicated Settings and Dashboard icon for Keyboard Layout Converter |
| `installer/PowerToysSetupVNext/Images/` | Setup banners and dialogs | Rebranded installer artwork for WiX package |
| `installer/PowerTool.Installer/Resources/app.ico` | Multi-res ICO | Embedded icon for standalone GUI setup installer (`PowerTool-Setup-x64.exe`) |

---

## 3. Modified User-Facing Application Names

User-facing titles, labels, tooltips, and dialogs have been updated from PowerToys to **Powertool**:

| Component | File / Location | New Value / Behavior |
|---|---|---|
| Product Name Definition | `src/common/version/version.h` | `#define PRODUCT_NAME "Powertool"` |
| Company Attribution | `src/common/version/version.h` | `#define COMPANY_NAME "Powertool Contributors (Lead: En-Dhiaa)"` |
| System Tray Tooltip | `src/runner/tray_icon.cpp` | `Powertool v0.88.0` |
| About Dialog Title | `src/runner/tray_icon.cpp` | `About Powertool` (Developer: En-Dhiaa, based on Microsoft PowerToys) |
| Settings Window Title (User) | `Strings/en-us/Resources.resw` | `Powertool Settings` |
| Settings Window Title (Admin)| `Strings/en-us/Resources.resw` | `Administrator: Powertool Settings` |
| Arabic Window Title | `Strings/ar-SA/Resources.resw` | `إعدادات Powertool` / `مسؤول: إعدادات Powertool` |
| Settings General Page Card | `SettingsXAML/Views/GeneralPage.xaml` | `Powertool Extended Edition` by En-Dhiaa |
| Settings Developer Page | `SettingsXAML/Views/DeveloperPage.xaml` | `Developer & About Powertool` |
| WiX Product Metadata | `installer/PowerToysSetupVNext/Product.wxs` | `Powertool (Extended Edition)` |
| Standalone Installer GUI | `installer/PowerTool.Installer/MainWindow.xaml` | `PowerTool Extended Edition Setup — معالج تثبيت Powertool` |
| Linux Desktop Launcher | `linux/powertool.desktop` | `Name=Powertool` |
| Linux AppStream Metadata | `linux/org.endhiaa.Powertool.metainfo.xml` | `<name>Powertool</name>` |

### Preserved Upstream References (Rationale)
Internal C++ and C# namespaces (such as `namespace Microsoft.PowerToys.Settings`), build macros (`POWERTOYS_SETTINGS`), file system cache folders (`%LOCALAPPDATA%\Microsoft\PowerToys`), and upstream copyright notices (`Copyright (c) Microsoft Corporation. All rights reserved.`) have been intentionally preserved. Renaming internal namespaces would break backward binary compatibility, third-party plugin interop, and violates upstream open-source attribution requirements. Powertool is clearly identified as an independent derivative work under the MIT License.

---

## 4. Implementation Files: Offline Translator

The **Offline Translator** is a fully functional, zero-cloud neural machine translation utility:

* **Engine:** [`src/modules/OfflineTranslator/OfflineTranslatorEngine.py`](file:///c:/Users/USER/Downloads/ضياء/AI/PowerTool/PowerToys-main/src/modules/OfflineTranslator/OfflineTranslatorEngine.py)
  - CTranslate2 (v4.8.5) inference engine with SentencePiece (v0.2.3) subword tokenizer.
  - Package format: `.argosmodel` (standard ZIP archives containing `model/model.bin`, `sentencepiece.model`, and `metadata.json`).
  - Pre-installed offline models:
    - Arabic ➔ English: `translate-ar_en` (78.1 MB)
    - English ➔ Arabic: `translate-en_ar` (84.4 MB)
  - Model management API: `list_packages`, `download_and_install_package`, `remove_package`, `get_disk_space_info`.
* **Interactive Floating & Window UI:** [`src/modules/OfflineTranslator/OfflineTranslatorUI.py`](file:///c:/Users/USER/Downloads/ضياء/AI/PowerTool/PowerToys-main/src/modules/OfflineTranslator/OfflineTranslatorUI.py)
  - PySide6 Windows 11 Fluent dark UI with rounded card and drop shadow.
  - Integrated Model Manager dialog (`ModelManagerDialog`) showing installed models, disk storage, and download/remove controls.
  - RTL (Right-to-Left) for Arabic and LTR (Left-to-Right) for English.
  - Action buttons: Copy Translation, Replace Selected Text (`Ctrl+Enter`), Swap Languages (`⇄`).
* **CLI & Clipboard Selection Bridge:** [`src/modules/OfflineTranslator/OfflineTranslatorCLI.py`](file:///c:/Users/USER/Downloads/ضياء/AI/PowerTool/PowerToys-main/src/modules/OfflineTranslator/OfflineTranslatorCLI.py)
  - Non-destructive clipboard capture for Windows (`OpenClipboard`, `CF_UNICODETEXT`) and Linux (`wl-paste` on Wayland, `xclip` on X11).
* **C++ Module Interface:** [`src/modules/OfflineTranslator/dllmain.cpp`](file:///c:/Users/USER/Downloads/ضياء/AI/PowerTool/PowerToys-main/src/modules/OfflineTranslator/dllmain.cpp)
  - `PowertoyModuleIface` registration, hotkey handling (`Ctrl + Alt + T` and `Ctrl + Alt + Shift + T`), and named-pipe IPC.
* **Settings Page:** [`src/settings-ui/Settings.UI/SettingsXAML/Views/OfflineTranslatorPage.xaml`](file:///c:/Users/USER/Downloads/ضياء/AI/PowerTool/PowerToys-main/src/settings-ui/Settings.UI/SettingsXAML/Views/OfflineTranslatorPage.xaml)
  - Settings UI for enabling/disabling, hotkey customization, language detection, and model package inventory.

---

## 5. Implementation Files: Keyboard Layout Converter

The **Keyboard Layout Converter** converts mistyped text across physical scan-code positions:

* **Core Engine (C++):** [`src/modules/KeyboardLayoutConverter/KeyboardLayoutConverterEngine.cpp`](file:///c:/Users/USER/Downloads/ضياء/AI/PowerTool/PowerToys-main/src/modules/KeyboardLayoutConverter/KeyboardLayoutConverterEngine.cpp) & [`.h`](file:///c:/Users/USER/Downloads/ضياء/AI/PowerTool/PowerToys-main/src/modules/KeyboardLayoutConverter/KeyboardLayoutConverterEngine.h)
  - Scan-code bijection between US QWERTY and Arabic 101/102.
  - Handles Arabic ligatures (`لا`, `لأ`, `لإ`, `لآ`) both as 2-character strings and presentation forms (`\uFEFB`–`\uFEFC`).
  - Supports numbers, shifted symbols, and punctuation.
  - Windows API integration: `GetKeyboardLayout`, `MapVirtualKeyExW`, `ToUnicodeEx`.
  - Non-destructive clipboard capture and replacement.
* **Cross-Platform Engine (Python):** [`src/modules/KeyboardLayoutConverter/KeyboardLayoutConverterEngine.py`](file:///c:/Users/USER/Downloads/ضياء/AI/PowerTool/PowerToys-main/src/modules/KeyboardLayoutConverter/KeyboardLayoutConverterEngine.py)
  - Verified physical mapping matrices for Arabic 101 and 102 layouts.
* **Interactive Preview UI:** [`src/modules/KeyboardLayoutConverter/KeyboardLayoutConverterUI.py`](file:///c:/Users/USER/Downloads/ضياء/AI/PowerTool/PowerToys-main/src/modules/KeyboardLayoutConverter/KeyboardLayoutConverterUI.py)
  - Live layout preview box, layout variant selector (Arabic 101 vs 102), swap button, copy, replace, and undo actions.
* **C++ Module Interface:** [`src/modules/KeyboardLayoutConverter/dllmain.cpp`](file:///c:/Users/USER/Downloads/ضياء/AI/PowerTool/PowerToys-main/src/modules/KeyboardLayoutConverter/dllmain.cpp)
  - Global hotkey hook: `Ctrl + Alt + Shift + K`.
* **Settings Page:** [`src/settings-ui/Settings.UI/SettingsXAML/Views/KeyboardLayoutConverterPage.xaml`](file:///c:/Users/USER/Downloads/ضياء/AI/PowerTool/PowerToys-main/src/settings-ui/Settings.UI/SettingsXAML/Views/KeyboardLayoutConverterPage.xaml)

---

## 6. Implementation Files: Developer Page & Custom Issue Reporting

* **Developer Page View:** [`src/settings-ui/Settings.UI/SettingsXAML/Views/DeveloperPage.xaml`](file:///c:/Users/USER/Downloads/ضياء/AI/PowerTool/PowerToys-main/src/settings-ui/Settings.UI/SettingsXAML/Views/DeveloperPage.xaml) & [`.cs`](file:///c:/Users/USER/Downloads/ضياء/AI/PowerTool/PowerToys-main/src/settings-ui/Settings.UI/SettingsXAML/Views/DeveloperPage.xaml.cs)
* **Developer ViewModel:** [`src/settings-ui/Settings.UI/ViewModels/DeveloperViewModel.cs`](file:///c:/Users/USER/Downloads/ضياء/AI/PowerTool/PowerToys-main/src/settings-ui/Settings.UI/ViewModels/DeveloperViewModel.cs)
  - Identifies **En-Dhiaa** as the lead developer.
  - Clickable link: `https://github.com/En-Dhiaa`.
  - Application description, feature list, version `0.88.0`, and license attribution.
* **Custom Issue Reporting:**
  - Destination: `https://github.com/En-Dhiaa/PowerToys/issues/new/choose`
  - Runner bug report link: [`src/runner/bug_report_dialog.cpp`](file:///c:/Users/USER/Downloads/ضياء/AI/PowerTool/PowerToys-main/src/runner/bug_report_dialog.cpp)
  - General Settings report bug link: [`src/settings-ui/Settings.UI/ViewModels/GeneralViewModel.cs`](file:///c:/Users/USER/Downloads/ضياء/AI/PowerTool/PowerToys-main/src/settings-ui/Settings.UI/ViewModels/GeneralViewModel.cs)
  - Shell feedback click handler: [`src/settings-ui/Settings.UI/SettingsXAML/Views/ShellPage.xaml.cs`](file:///c:/Users/USER/Downloads/ضياء/AI/PowerTool/PowerToys-main/src/settings-ui/Settings.UI/SettingsXAML/Views/ShellPage.xaml.cs)
* **Custom Issue Templates:** [`.github/ISSUE_TEMPLATE/`](file:///c:/Users/USER/Downloads/ضياء/AI/PowerTool/PowerToys-main/.github/ISSUE_TEMPLATE/)
  - `bug_report.yml`
  - `feature_request.yml`
  - `translation_problem.yml`
  - `keyboard_layout_conversion_problem.yml`
  - `offline_translation_model_problem.yml`
  - `config.yml`

---

## 7. Linux Desktop & Packaging Parity

A dedicated Linux integration suite has been established under `linux/`:
* `linux/powertool-linux.py`: Full PySide6 desktop suite with Dashboard displaying all 10 modules, Developer page, System Tray, and hotkey invocation.
* `linux/powertool.desktop`: XDG FreeDesktop application entry with localized actions.
* `linux/org.endhiaa.Powertool.metainfo.xml`: AppStream metadata for Flatpak / Flathub.
* `linux/debian/control` and `rules`: Debian / Ubuntu packaging configuration.
* `linux/powertool.spec`: Fedora / RHEL / openSUSE RPM specification.
* `linux/AppRun`: Standalone AppImage execution wrapper.

---

## 8. Automated Acceptance Test Results

All unit and acceptance tests were executed via pytest:
```powershell
python -m pytest tests/ -v
```

```text
============================= test session starts =============================
platform win32 -- Python 3.15.0, pytest-9.1.1, pluggy-1.7.0
rootdir: C:\Users\USER\Downloads\ضياء\AI\PowerTool\PowerToys-main
collected 30 items

tests/test_keyboard_layout_converter.py::test_prompt_example_1_go_home_now PASSED [  3%]
tests/test_keyboard_layout_converter.py::test_prompt_example_2_hello PASSED [  6%]
tests/test_keyboard_layout_converter.py::test_prompt_example_3_marhaba PASSED [ 10%]
tests/test_keyboard_layout_converter.py::test_uppercase_shift_mapping PASSED [ 13%]
tests/test_keyboard_layout_converter.py::test_numbers_preservation PASSED [ 16%]
tests/test_keyboard_layout_converter.py::test_arabic_specific_punctuation PASSED [ 20%]
tests/test_keyboard_layout_converter.py::test_multiline_selection PASSED [ 23%]
tests/test_keyboard_layout_converter.py::test_reversibility_cycle PASSED [ 26%]
tests/test_keyboard_layout_converter.py::test_emoji_and_unrelated_unicode_preservation PASSED [ 30%]
tests/test_keyboard_layout_converter.py::test_empty_and_whitespace PASSED [ 33%]
tests/test_keyboard_layout_converter.py::test_preserve_punctuation_option PASSED [ 36%]
tests/test_keyboard_layout_converter.py::test_engine_module_direct_verification PASSED [ 40%]
tests/test_keyboard_layout_converter.py::test_arabic_101_and_102_layout_variants PASSED [ 43%]
tests/test_offline_translator.py::test_arabic_to_english_translation PASSED [ 46%]
tests/test_offline_translator.py::test_english_to_arabic_translation PASSED [ 50%]
tests/test_offline_translator.py::test_empty_and_whitespace_input PASSED [ 53%]
tests/test_offline_translator.py::test_multiple_lines_preservation PASSED [ 56%]
tests/test_offline_translator.py::test_arabic_diacritics_handling PASSED [ 60%]
tests/test_offline_translator.py::test_language_detection PASSED         [ 63%]
tests/test_offline_translator.py::test_missing_model_error PASSED        [ 66%]
tests/test_offline_translator.py::test_strictly_offline_execution_network_blocked PASSED [ 70%]
tests/test_powertool_branding.py::test_branding_icon_files_exist PASSED  [ 73%]
tests/test_powertool_branding.py::test_multi_resolution_ico PASSED       [ 76%]
tests/test_powertool_branding.py::test_version_h_branding PASSED         [ 80%]
tests/test_powertool_branding.py::test_tray_icon_branding PASSED         [ 83%]
tests/test_powertool_branding.py::test_settings_window_title_branding PASSED [ 86%]
tests/test_powertool_branding.py::test_developer_profile_attribution PASSED [ 90%]
tests/test_powertool_branding.py::test_linux_packaging_and_desktop_parity PASSED [ 93%]
tests/test_powertool_branding.py::test_custom_issue_reporting_urls PASSED [ 96%]
tests/test_powertool_branding.py::test_issue_templates_complete PASSED   [100%]

============================= 30 passed in 1.01s ==============================
```

---

## 9. Release Artifacts Generated

1. **`release/PowerTool-Setup-x64.exe` (546.48 MB):** Standalone single-file Windows setup installer with GUI, language options, desktop/start menu shortcut generator, startup configuration, and registry uninstaller.
2. **`release/PowerTool-v0.88.0-win-x64-portable.zip` (546.09 MB):** Standalone portable package with pre-bundled neural translation models and binaries.
3. **`Install-PowerTool.cmd`:** One-click script in repository root to launch setup.
4. **`Run-PowerTool-Portable.cmd`:** One-click script in repository root to run portable edition.

---

## 10. Known Considerations & Recommendations

1. **GitHub Issues Enablement:**
   The developer GitHub profile `https://github.com/En-Dhiaa` is live and authenticated. To enable user issue reporting, push the repository to GitHub as `En-Dhiaa/PowerToys` (or `Powertool`) and ensure GitHub Issues is toggled ON under Repository Settings.
2. **Linux Global Hotkeys on Wayland:**
   Wayland security boundaries restrict arbitrary global keystroke interception without compositor portals (such as `org.freedesktop.portal.GlobalShortcuts`). Under Wayland, configure desktop environment shortcut keys (GNOME / KDE) to trigger `powertool --translator` and `powertool --converter` for seamless operation.

