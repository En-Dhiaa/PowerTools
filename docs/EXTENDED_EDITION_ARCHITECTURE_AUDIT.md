# PowerTool (PowerToys Extended Edition) — Architecture & Source Code Audit Report

**Target Repository:** Microsoft PowerToys Extended Edition  
**Branch:** `feature/powertool-extended`  
**Application Name:** PowerTool  
**Auditor / Architect:** Senior Windows Systems Engineer, C++/C# Architect  
**Status:** Audit Completed & Baseline Committed  

---

## 1. Executive Summary

This architecture audit is the mandatory foundation before introducing new modules, updating branding assets, or altering build systems. The PowerToys repository is an enterprise-grade Windows productivity suite composed of native C++ Win32 subsystems, C++/WinRT interop layers, C# / .NET 8 WinUI 3 modern desktop applications, and WiX-based Windows Installer pipelines.

The goal of the **PowerTool Extended Edition** is to transform Microsoft PowerToys into an enhanced Windows productivity suite with:
1. **New Visual Identity & Branding:** Rebranded to **PowerTool** with modern multi-resolution icons, tray icons, and UI assets derived from the original `icon.png` asset.
2. **Offline Arabic/English Translator:** A zero-cloud, strictly offline neural translation utility with global shortcuts (`Ctrl + Alt + T` / `Ctrl + Alt + Shift + T`), bidirectional auto-detection, clipboard preservation, and downloadable local model package management.
3. **Arabic/English Keyboard Layout Converter:** A high-precision physical-key mapping engine solving English/Arabic cross-typing (e.g. typing English under Arabic 101/102 layout or vice versa) using native Windows keyboard layout APIs (`GetKeyboardLayout`, `MapVirtualKeyExW`, `ToUnicodeEx`) with shortcut `Ctrl + Alt + Shift + K`.
4. **Seamless Integration:** Full integration into the PowerToys Runner lifecycle, `CentralizedKeyboardHook`, WinUI 3 Settings, and packaging, while **strictly preserving all existing 37+ PowerToys utilities**.

---

## 2. Existing Architecture Overview

The PowerToys ecosystem employs a decoupled, multi-process architecture engineered for stability, privilege isolation, and UI responsiveness.

```
                           +---------------------------+
                           |       PowerTool.exe       |
                           |   (Runner Win32 / C++)    |
                           +-------------+-------------+
                                         |
         +-------------------------------+-------------------------------+
         |                               |                               |
+--------v--------+             +--------v--------+             +--------v--------+
| Centralized KB  |             |  PowertoyModule |             | Win32 IPC Pipe  |
|  Hook & Hotkeys |             | Dynamic Loader  |             | & Win32 Events  |
+--------+--------+             +--------+--------+             +--------+--------+
         |                               |                               |
         |                               |                               |
         |         +---------------------+---------------------+         |
         |         |                                           |         |
         |  +------v------+                             +------v------+  |
         |  | In-Process  |                             | Out-of-Proc |  |
         |  | Modules     |                             | Services    |  |
         |  | (FancyZones,|                             | (KBM Engine,|  |
         |  |  Awake, etc)|                             |  Adv. Paste)|  |
         |  +-------------+                             +------+------+  |
         |                                                     |         |
         +-------------------------------+---------------------+         |
                                         |                               |
                                +--------v-------------------------------v--------+
                                |              PowerToys.Settings.exe             |
                                |       (WinUI 3 / .NET 8 Desktop App)            |
                                +-------------------------------------------------+
```

### 2.1 Process Separation
* **Runner (`PowerToys.exe` / `PowerTool.exe`)**:
  * Root orchestrator running under user or elevated privilege.
  * Manages application tray icon, background update checks, telemetry, single-instance mutexes (`PowerToys_Runner_Instance_Mutex`), and general settings.
  * Dynamically loads module DLLs implementing `PowertoyModuleIface`.
  * Hosts `CentralizedKeyboardHook` (`WH_KEYBOARD_LL`) and `CentralizedHotkeys` (`RegisterHotKey`) to prevent hotkey collisions.
* **Settings UI (`PowerToys.Settings.exe`)**:
  * Standalone WinUI 3 / XAML / .NET 8 application.
  * Communicates with Runner via Named Pipes (`\\.\pipe\powertoys_runner_*`) and JSON settings files stored in `%LOCALAPPDATA%\Microsoft\PowerToys\`.
  * Loads settings lazily, supports live hotkey rebinding, dark/light theme switching, and localization.
* **Module Execution Models**:
  * *In-Process DLLs:* Lightweight background hooks running in the Runner process (e.g. `FancyZones`, `AlwaysOnTop`, `Awake`, `PowerAccent`).
  * *Out-of-Process Applications:* Standalone WinUI 3 or WPF processes (e.g. `PowerToys.PowerLauncher.exe`, `PowerToys.AdvancedPaste.exe`, `KeyboardManagerEngine.exe`) launched on demand or persistent in background, supervised by the C++ interface DLL.

---

## 3. Module Registration & Lifecycle

### 3.1 The C++ Module Interface (`PowertoyModuleIface`)
Every PowerToys utility DLL exports a single C-linkage factory function:
```cpp
extern "C" __declspec(dllexport) PowertoyModuleIface* __cdecl powertoy_create();
```

Defined in `src/modules/interface/powertoy_module_interface.h`:
* `get_name()`: Returns localized display name.
* `get_key()`: Returns unique non-localized ASCII identifier (e.g. `L"OfflineTranslator"`, `L"KeyboardLayoutConverter"`).
* `get_config(wchar_t* buffer, int* buffer_size)`: Exports module configuration schema and active values as JSON.
* `set_config(const wchar_t* config)`: Receives updated settings from Settings UI.
* `enable()` / `disable()`: Initializes or tears down module resources, threads, and background state.
* `is_enabled()`: Queries running state.
* `destroy()`: Final cleanup before `FreeLibrary`.
* `get_hotkeys(Hotkey* buffer, size_t buffer_size)`: Registers shortcuts with Runner's centralized hook.
* `on_hotkey(size_t hotkeyId)`: Invoked asynchronously or synchronously when a registered shortcut is triggered. Returns `true` to swallow the key press.
* `gpo_policy_enabled_configuration()`: GPO enterprise policy enforcement.

### 3.2 Discovery and Loading in Runner
In `src/runner/main.cpp`:
* The runner defines `knownModules`: a vector containing DLL paths relative to installation directory.
* During initialization, `runner()` loops over `knownModules`:
  1. Calls `load_powertoy(moduleSubdir)` which invokes Win32 `LoadLibraryW()`.
  2. Resolves `powertoy_create` address and calls it.
  3. Registers module hotkeys into `HotkeyConflictDetector` and `CentralizedKeyboardHook`.
  4. Stores the instance into `modules()` map indexed by `get_key()`.
  5. If the module is enabled in `general_settings.json`, calls `enable()`.

---

## 4. Key Source Files & Their Responsibilities

| Subsystem | File Path | Responsibility |
|---|---|---|
| **Runner Core** | `src/runner/main.cpp` | Process initialization, tray icon, module load loop, shutdown sequence |
| **Runner Module Wrapper** | `src/runner/powertoy_module.cpp` | C++ wrapper managing `PowertoyModuleIface` lifecycle and hotkey binding |
| **Centralized Hook** | `src/runner/centralized_kb_hook.cpp` | Centralized `WH_KEYBOARD_LL` hook dispatching hotkeys to registered modules |
| **Centralized Hotkeys** | `src/runner/centralized_hotkeys.cpp` | Win32 `RegisterHotKey` implementation for high-speed hotkeys |
| **Hotkey Conflict Detector** | `src/runner/hotkey_conflict_detector.cpp` | Monitors and prevents overlapping shortcuts across active utilities |
| **Module Interface** | `src/modules/interface/powertoy_module_interface.h` | Base interface contract for all PowerToys utilities |
| **Native Keyboard Layout** | `src/common/interop/keyboard_layout.cpp` | Native Windows keyboard layout queries (`MapVirtualKeyExW`, `ToUnicodeEx`) |
| **Settings Navigation Shell** | `src/settings-ui/Settings.UI/SettingsXAML/Views/ShellPage.xaml` | WinUI 3 Navigation View containing navigation categories and module entries |
| **Settings Library** | `src/settings-ui/Settings.UI.Library/` | Strongly-typed C# settings models, serialization context, and IPC dispatch |
| **Installer Definition** | `installer/PowerToysSetupVNext/Product.wxs` | WiX MSI installer file hierarchy, components, and shortcut definitions |
| **Version & Branding** | `src/common/version/version.h` | Version strings, company metadata, and application product names |

---

## 5. Existing Keyboard & Input Architecture

### 5.1 Keyboard Manager (KBM)
* **Location:** `src/modules/keyboardmanager/`
* **Architecture:** Composed of a thin DLL (`PowerToys.KeyboardManager.dll`), an isolated engine executable (`KeyboardManagerEngine.exe`), and an editor UI (`KeyboardManagerEditorUI`).
* **Hook Mechanism:** Installs a low-level keyboard hook (`WH_KEYBOARD_LL`) in `KeyboardManagerEngine.exe`. When input matches remap rules, it swallows the original `KEYBOARD_INPUT` and emits synthetic input using `SendInput()`.
* **Layout Awareness:** Queries active keyboard layout (`GetKeyboardLayout(0)`) to map virtual keys to localized scan codes.

### 5.2 Quick Accent (`PowerAccent`)
* **Location:** `src/modules/poweraccent/`
* **Architecture:** Hooks the keyboard, measures key press duration, and upon detecting a sustained vowel or character, opens a floating bar presenting accented variants.

### 5.3 Centralized Keyboard Hook
* Modules can register hotkeys without spawning their own global hooks.
* Centralized hook checks modifiers (Win, Ctrl, Alt, Shift) and virtual key codes (`vkCode`).
* Prevents multiple hooks from degrading input latency or timing out under Windows hook watchdog rules.

---

## 6. Existing UI Architecture (WinUI 3 & Modern Windows 11)

* **UI Platform:** Windows App SDK (WinUI 3), XAML controls, WinRT projection via CsWinRT.
* **Layout Structure:**
  * Top-level categories: *System Tools*, *Windowing & Layouts*, *Input / Output*, *File Management*, *Advanced*.
  * Each utility has a dedicated Page (`*Page.xaml`) using standard controls (`SettingsCard`, `SettingsExpander`, `ShortcutControl`).
* **Theming:** Full Mica background, dynamic dark and light mode switching, high-DPI scaling.
* **Localization:** String resources managed in `.resw` / `.resx` across 20+ locales including Arabic (`ar-SA`) and English (`en-US`). RTL layout is natively supported by WinUI 3 `FlowDirection="RightToLeft"`.

---

## 7. Build and Dependency Requirements

* **Compilers & Toolchains:**
  * MSVC v143 (Visual Studio 2022 v17.11+).
  * .NET SDK 8.0 (SDK 8.0.404 installed in user profile).
  * Windows 10 SDK (10.0.22621.0 or higher).
  * C++/WinRT compiler (`cppwinrt`).
* **Package Management:** NuGet, vcpkg (`vcpkg.json`).
* **Packaging:** WiX Toolset v3.14/v4 for MSI bootstrapper creation.
* **Python Environment:** Python 3.15 with Pillow and PySide6 available for standalone processing, asset generation, and local testing.

---

## 8. Potential Conflicts & Integration Analysis

| Potential Conflict | Root Cause | Mitigation Strategy |
|---|---|---|
| **Multiple Keyboard Hooks** | Spawning independent `WH_KEYBOARD_LL` hooks causes input lag, race conditions, or unhooking by Windows OS. | Register all new shortcuts (`Ctrl+Alt+T`, `Ctrl+Alt+Shift+T`, `Ctrl+Alt+Shift+K`) directly through PowerToys `CentralizedKeyboardHook` or `RegisterHotKey`. |
| **Clipboard Data Destruction** | Naive `Ctrl+C` / `Ctrl+V` text capture clears user clipboard history or loses rich data (bitmaps, HTML). | Store and restore clipboard formats using Win32 `OpenClipboard`, `GetClipboardData(CF_UNICODETEXT)`, and restore original clipboard state on completion. |
| **Arabic 101 vs 102 Layout Differences** | Different Arabic keyboards swap certain diacritics and symbols (e.g. `>` and `<` or backslash). | Query physical scan codes (`MAPVK_VSC_TO_VK_EX`) and support explicit layout selection (Arabic 101 vs Arabic 102). |
| **Offline Engine Dependencies** | Large AI/neural models requiring cloud endpoints or gigantic PyTorch runtimes violate strict offline and lightweight desktop rules. | Use lightweight offline neural translation architectures (Argos Translate / OpenNMT / CTranslate2 quantized models) with `.argosmodel` zip packages stored in local application data. |
| **Settings Schema Corruption** | Adding non-backwards compatible JSON fields can break settings serialization. | Follow existing `BasePTModuleSettings` patterns, isolate module JSON configurations in their own subfolders in `%LOCALAPPDATA%\Microsoft\PowerToys\`. |

---

## 9. Recommended Integration Plan

### 9.1 Keyboard Layout Converter
* Module Name: `Keyboard Layout Converter`
* Key: `L"KeyboardLayoutConverter"`
* Code Location: `src/modules/KeyboardLayoutConverter/`
* Shortcut: `Ctrl + Alt + Shift + K` (configurable)
* Settings UI: Integrated under `Input / Output` in `ShellPage.xaml` as `KeyboardLayoutConverterPage.xaml`.
* Native Engine: Bidirectional virtual-key to scan-code matrix for US QWERTY <-> Arabic 101/102.
* Smart Heuristic: Character frequency and Arabic vs Latin alphabet distribution detection to automatically infer conversion direction.

### 9.2 Offline Arabic/English Translator
* Module Name: `Offline Translator`
* Key: `L"OfflineTranslator"`
* Code Location: `src/modules/OfflineTranslator/`
* Shortcuts: `Ctrl + Alt + T` (Translate), `Ctrl + Alt + Shift + T` (Reverse translate)
* Settings UI: Integrated under `System Tools` in `ShellPage.xaml` as `OfflineTranslatorPage.xaml`.
* Engine: Self-contained local offline translation engine using verified `.argosmodel` packages (Arabic-English and English-Arabic), local package manager with progress reporting, hash verification, and disk space calculation.
* Popup UI: Clean, responsive, compact floating translation window supporting RTL/LTR bidirectional rendering.

### 9.3 Branding & Identity Update
* Application Product Name: **PowerTool**
* New Icon Assets: Multi-resolution `.ico` (16, 24, 32, 48, 64, 128, 256 px), high-resolution transparent PNGs, tray icons, and Settings UI assets generated from `icon.png`.
* Preservation: Retain all Microsoft MIT licenses and third-party notices, but rebrand window headers, tray tooltips, and settings titles to PowerTool Extended Edition.

---

## 10. Audit Conclusion

The PowerToys codebase is robust, modular, and cleanly decoupled. The proposed features and branding updates can be integrated natively without degrading system stability or impacting existing utilities.

All 37 original PowerToys utilities will be preserved. Baseline git commit is secured on `feature/powertool-extended`. Proceeding to Phase 2: Brand Identity and Application Icon Asset Generation.

