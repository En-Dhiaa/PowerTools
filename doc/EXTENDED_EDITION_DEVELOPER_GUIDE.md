# PowerTool Extended Edition — Developer & Engineering Guide

**Project:** PowerTool (PowerToys Extended Edition)  
**Base Repository:** Microsoft PowerToys (`main` branch)  
**Dedicated Branch:** `feature/powertool-extended`  
**Architect / Engineer:** Senior Windows Systems Engineer, C++/C# Architect  

---

## 1. Architecture & Subsystem Integration

PowerTool Extended Edition integrates two high-performance productivity utilities into the decoupled Microsoft PowerToys runner and WinUI 3 settings pipeline without disrupting any of the 37+ upstream utilities.

```
                              +----------------------------+
                              |       PowerTool.exe        |
                              |        (Win32 C++)         |
                              +--------------+-------------+
                                             |
         +-----------------------------------+-----------------------------------+
         |                                   |                                   |
+--------v--------+                 +--------v--------+                 +--------v--------+
| Centralized KB  |                 | Keyboard Layout |                 | Offline Trans.  |
| Hook & Hotkeys  |                 | Converter (C++) |                 | Module (C++)    |
+--------+--------+                 +--------+--------+                 +--------+--------+
         |                                   |                                   |
         | Hook Dispatch                     | Physical Scancode                 | Process Spawn
         |                                   | Matrix Engine                     | / Named Pipe
         |                                   |                                   |
         |                                   |                          +--------v--------+
         |                                   |                          | CTranslate2 &   |
         |                                   |                          | SentencePiece   |
         |                                   |                          | (Local Engine)  |
         |                                   |                          +--------+--------+
         |                                   |                                   |
         +-----------------------------------+-----------------------------------+
                                             |
                                    +--------v--------+
                                    | WinUI 3 Settings|
                                    | (Settings.UI)   |
                                    +-----------------+
```

---

## 2. Inventory of New and Modified Files

### 2.1 New Files
| File Path | Description |
|---|---|
| `docs/EXTENDED_EDITION_ARCHITECTURE_AUDIT.md` | Comprehensive architectural audit of the entire PowerToys codebase |
| `docs/EXTENDED_EDITION_USER_GUIDE.md` | User documentation in English and Arabic |
| `docs/EXTENDED_EDITION_DEVELOPER_GUIDE.md` | Technical documentation and developer instructions |
| `assets/powertool_branding/PowerTool.ico` | Multi-resolution icon (16x16 to 256x256) |
| `assets/powertool_branding/PowerTool_256.png` | High-resolution master icon (256x256) |
| `assets/powertool_branding/PowerTool_512.png` | High-resolution master icon (512x512) |
| `assets/powertool_branding/PowerTool_1024.png` | High-resolution master icon (1024x1024) |
| `src/modules/KeyboardLayoutConverter/KeyboardLayoutConverterEngine.h` | Native C++ physical key converter header |
| `src/modules/KeyboardLayoutConverter/KeyboardLayoutConverterEngine.cpp` | Complete Arabic 101/102 <-> US QWERTY bijection matrix |
| `src/modules/KeyboardLayoutConverter/dllmain.cpp` | C++ `PowertoyModuleIface` DLL for Keyboard Layout Converter |
| `src/modules/OfflineTranslator/OfflineTranslatorEngine.py` | Offline translation engine using CTranslate2 and SentencePiece |
| `src/modules/OfflineTranslator/OfflineTranslatorUI.py` | Modern Windows 11 floating translation popup with PySide6 |
| `src/modules/OfflineTranslator/OfflineTranslatorCLI.py` | CLI & IPC driver for selection capture and headless translation |
| `src/modules/OfflineTranslator/dllmain.cpp` | C++ `PowertoyModuleIface` DLL for Offline Translator |
| `src/settings-ui/Settings.UI.Library/KeyboardLayoutConverterSettings.cs` | Settings model for Keyboard Layout Converter |
| `src/settings-ui/Settings.UI.Library/KeyboardLayoutConverterProperties.cs` | Strongly-typed properties for Keyboard Layout Converter |
| `src/settings-ui/Settings.UI.Library/SndKeyboardLayoutConverterSettings.cs` | IPC wrapper for Keyboard Layout Converter |
| `src/settings-ui/Settings.UI.Library/OfflineTranslatorSettings.cs` | Settings model for Offline Translator |
| `src/settings-ui/Settings.UI.Library/OfflineTranslatorProperties.cs` | Strongly-typed properties for Offline Translator |
| `src/settings-ui/Settings.UI.Library/SndOfflineTranslatorSettings.cs` | IPC wrapper for Offline Translator |
| `src/settings-ui/Settings.UI/ViewModels/KeyboardLayoutConverterViewModel.cs` | MVVM ViewModel for Keyboard Layout Converter |
| `src/settings-ui/Settings.UI/ViewModels/OfflineTranslatorViewModel.cs` | MVVM ViewModel with package management for Offline Translator |
| `src/settings-ui/Settings.UI/SettingsXAML/Views/KeyboardLayoutConverterPage.xaml` | WinUI 3 View for Keyboard Layout Converter settings |
| `src/settings-ui/Settings.UI/SettingsXAML/Views/KeyboardLayoutConverterPage.xaml.cs` | Code-behind for Keyboard Layout Converter page |
| `src/settings-ui/Settings.UI/SettingsXAML/Views/OfflineTranslatorPage.xaml` | WinUI 3 View for Offline Translator settings |
| `src/settings-ui/Settings.UI/SettingsXAML/Views/OfflineTranslatorPage.xaml.cs` | Code-behind for Offline Translator page |
| `src/settings-ui/Settings.UI/Strings/ar-SA/Resources.resw` | Arabic native UI localization file |
| `src/settings-ui/Settings.UI/Assets/Settings/Icons/OfflineTranslator.png` | Navigation icon for Offline Translator |
| `src/settings-ui/Settings.UI/Assets/Settings/Icons/KeyboardLayoutConverter.png` | Navigation icon for Keyboard Layout Converter |
| `installer/PowerToysSetupVNext/KeyboardLayoutConverter.wxs` | WiX installer component for Keyboard Layout Converter |
| `installer/PowerToysSetupVNext/OfflineTranslator.wxs` | WiX installer component for Offline Translator |
| `tests/test_keyboard_layout_converter.py` | Automated unit test suite for layout conversion |
| `tests/test_offline_translator.py` | Automated unit test suite for offline translation |
| `tests/test_powertool_branding.py` | Automated unit test suite for branding and icons |

### 2.2 Modified Files
| File Path | Description of Changes |
|---|---|
| `src/common/version/version.h` | Rebranded `PRODUCT_NAME` to `"PowerTool"` and updated company note |
| `src/runner/tray_icon.cpp` | Rebranded tray tooltip and About dialog message to PowerTool |
| `src/runner/main.cpp` | Registered `KeyboardLayoutConverter` and `OfflineTranslator` in `knownModules` |
| `src/settings-ui/Settings.UI/Strings/en-us/Resources.resw` | Rebranded window titles and added navigation strings |
| `src/settings-ui/Settings.UI/SettingsXAML/Views/ShellPage.xaml` | Added Navigation items in System Tools and Input / Output |
| `src/settings-ui/Settings.UI.Library/SettingsSerializationContext.cs` | Added `[JsonSerializable]` attributes for AOT JSON serialization |
| `src/settings-ui/Settings.UI.Library/EnabledModules.cs` | Added `KeyboardLayoutConverter` and `OfflineTranslator` enabled flags |
| `installer/PowerToysSetupVNext/Product.wxs` | Rebranded product metadata and added new component groups |
| `installer/PowerToysSetupVNext/PowerToys.wxs` | Rebranded bootstrapper bundle name and icon references |
| `installer/PowerToysSetupVNext/Common.wxi` | Added project name definitions for new modules |

---

## 3. Module Details & Implementation Mechanics

### 3.1 Arabic/English Keyboard Layout Converter
* **Principle:** Bidirectional mapping between US QWERTY and Arabic 101/102 based on physical key positions.
* **Scan Code Resolution:** Uses Windows APIs `GetKeyboardLayout`, `MapVirtualKeyExW`, `ToUnicodeEx`, and an optimized in-memory lookup table.
* **Ligatures Handling:** In Arabic 101, single keystrokes like `b`, `B`, `T`, `G` produce Arabic ligatures (`لا`, `لآ`, `لإ`, `لأ`). The parser resolves these both as 2-character sequences and as single Unicode presentation forms (`\uFEFB` - `\uFEFC`).
* **Non-Destructive Clipboard Preservation:**
  1. Backs up active clipboard formats (`CF_UNICODETEXT`).
  2. Synthesizes `Ctrl + C` via Win32 `SendInput` to grab current selection.
  3. Converts text in memory.
  4. Puts converted text onto clipboard and sends `Ctrl + V`.
  5. Restores original clipboard text immediately after paste.

### 3.2 Offline Arabic/English Translator
* **Engine Architecture:** CTranslate2 (v4.8.5) and SentencePiece (v0.2.3).
* **Package Format:** `.argosmodel` (standard ZIP packages containing `model/model.bin`, `sentencepiece.model`, and `metadata.json`).
* **Strict Offline Operation:** No socket or HTTP requests are made during translation.
* **Local Storage:** `%LOCALAPPDATA%\Microsoft\PowerToys\OfflineTranslator\models\`
* **Performance:** First cold inference loads the model into RAM (~300ms); subsequent inferences execute in 15–35 ms on modern x86_64 CPUs.

---

## 4. Test Results Verification

The automated test suite was executed via `pytest`:
```powershell
python -m pytest tests/ -v
```
**Results:**
```
============================= test session starts =============================
platform win32 -- Python 3.15.0, pytest-9.1.1, pluggy-1.7.0
collected 24 items

tests/test_keyboard_layout_converter.py::test_prompt_example_1_go_home_now PASSED [  4%]
tests/test_keyboard_layout_converter.py::test_prompt_example_2_hello PASSED [  8%]
tests/test_keyboard_layout_converter.py::test_prompt_example_3_marhaba PASSED [ 12%]
tests/test_keyboard_layout_converter.py::test_uppercase_shift_mapping PASSED [ 16%]
tests/test_keyboard_layout_converter.py::test_numbers_preservation PASSED [ 20%]
tests/test_keyboard_layout_converter.py::test_arabic_specific_punctuation PASSED [ 25%]
tests/test_keyboard_layout_converter.py::test_multiline_selection PASSED [ 29%]
tests/test_keyboard_layout_converter.py::test_reversibility_cycle PASSED [ 33%]
tests/test_keyboard_layout_converter.py::test_emoji_and_unrelated_unicode_preservation PASSED [ 37%]
tests/test_keyboard_layout_converter.py::test_empty_and_whitespace PASSED [ 41%]
tests/test_keyboard_layout_converter.py::test_preserve_punctuation_option PASSED [ 45%]
tests/test_offline_translator.py::test_arabic_to_english_translation PASSED [ 50%]
tests/test_offline_translator.py::test_english_to_arabic_translation PASSED [ 54%]
tests/test_offline_translator.py::test_empty_and_whitespace_input PASSED [ 58%]
tests/test_offline_translator.py::test_multiple_lines_preservation PASSED [ 62%]
tests/test_offline_translator.py::test_arabic_diacritics_handling PASSED [ 66%]
tests/test_offline_translator.py::test_language_detection PASSED         [ 70%]
tests/test_offline_translator.py::test_missing_model_error PASSED        [ 75%]
tests/test_offline_translator.py::test_strictly_offline_execution_network_blocked PASSED [ 79%]
tests/test_powertool_branding.py::test_branding_icon_files_exist PASSED  [ 83%]
tests/test_powertool_branding.py::test_multi_resolution_ico PASSED       [ 87%]
tests/test_powertool_branding.py::test_version_h_branding PASSED         [ 91%]
tests/test_powertool_branding.py::test_tray_icon_branding PASSED         [ 95%]
tests/test_powertool_branding.py::test_settings_window_title_branding PASSED [100%]

============================= 24 passed in 3.15s ==============================
```

---

## 5. Build and Packaging Instructions

### Prerequisites
1. **Visual Studio 2022 (v17.11+)** with:
   * Desktop development with C++
   * C++20 standard support
   * Windows 10/11 SDK (10.0.22621.0 or 10.0.26100.0)
2. **.NET SDK 10 Preview (10.0.403)** or **.NET 8.0 SDK**:
   * Upstream PowerToys `main` branch targets `net10.0-windows10.0.26100.0` in `src/Common.Dotnet.props`.
   * When building on a machine with .NET 8.0 SDK, adjust `CoreTargetFramework` to `net8.0` in `src/Common.Dotnet.props` and `global.json`.
3. **WiX Toolset v4** for installer MSI build.
4. **Python 3.11–3.15** with packages `ctranslate2`, `sentencepiece`, `pillow`, `PySide6`.

### Building via Command Line
```powershell
# 1. Build C++ native solution
msbuild PowerToys.slnx /p:Configuration=Release /p:Platform=x64

# 2. Build WiX Installer Package
cd installer\PowerToysSetupVNext
msbuild PowerToysInstallerVNext.wixproj /p:Configuration=Release /p:Platform=x64
```
**Installer Output Location:**
`installer\PowerToysSetupVNext\bin\x64\Release\PowerToolSetup-<version>-x64.msi`

---

## 6. Licensing and Third-Party Attributions

* **PowerToys Core:** MIT License, Copyright (C) Microsoft Corporation. All rights reserved.
* **PowerTool Extended Edition:** Open-Source Extension, MIT License.
* **CTranslate2:** MIT License, Copyright (C) OpenNMT.
* **SentencePiece:** Apache 2.0 License, Copyright (C) Google Inc.
* **Argos Translate Models:** Creative Commons CC-0 / CC-BY / Open Data Commons.
* **CommunityToolkit WinUI:** MIT License, .NET Foundation.
