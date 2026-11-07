# PowerTool Extended Edition — User Guide
# دليل المستخدم — النسخة الموسعة PowerTool

Welcome to **PowerTool Extended Edition**, an enhanced Windows productivity suite built upon Microsoft PowerToys. PowerTool introduces a fresh modern Windows 11 visual identity, a new application icon, a high-precision **Arabic/English Keyboard Layout Converter**, and a zero-cloud **Offline Arabic/English Translator**.

All original 37+ PowerToys utilities (FancyZones, PowerToys Run, Text Extractor, Quick Accent, Awake, ColorPicker, Peek, etc.) are fully preserved.

---

## 1. New Features Overview

| Feature | Shortcut | Description |
|---|---|---|
| **Offline Translator** | `Ctrl + Alt + T` | Translates selected text between Arabic and English offline using CTranslate2 and SentencePiece |
| **Reverse Offline Translator** | `Ctrl + Alt + Shift + T` | Translates selected text in the reverse direction directly |
| **Keyboard Layout Converter** | `Ctrl + Alt + Shift + K` | Corrects text accidentally typed in the wrong layout (e.g., Arabic typed under English or vice versa) |

---

## 2. Feature 1: Offline Arabic/English Translator

### What it does
Translates selected text between Arabic and English without sending any text to external servers, cloud endpoints, or web APIs.

### How to use
1. Select any text in any application (Browser, Word, Notepad, Slack, etc.).
   * Example (Arabic): `مرحبا، كيف حالك اليوم؟`
   * Example (English): `I need to finish this project today.`
2. Press `Ctrl + Alt + T`.
3. A compact floating translation window appears instantly:
   * **Source Language:** Auto-detected (Arabic or English).
   * **Target Language:** Auto-switched to the counterpart language.
   * **Original Text & Translated Text:** Displayed in clean, native RTL or LTR orientation.
   * **Duration:** In-memory local inference speed indicator (typically 20–350 ms).
4. Click **Copy Translation** to copy to clipboard, or click **Replace Selected** to paste directly back into your active window.
5. Press `Esc` anytime to dismiss.

### Global Shortcuts
* `Ctrl + Alt + T`: Translate selected text (or open empty translator popup if no text selected).
* `Ctrl + Alt + Shift + T`: Translate in the reverse direction.

### Language Model Management
PowerTool manages language packages locally under:
`%LOCALAPPDATA%\Microsoft\PowerToys\OfflineTranslator\models\`

In **PowerTool Settings > System Tools > Offline Translator**:
* View installed packages and available downloads.
* Download packages on demand (Arabic -> English: 78.1 MB; English -> Arabic: 84.4 MB).
* View disk space and package versioning.
* Once downloaded, the models operate **100% offline** with zero internet connection required.

---

## 3. Feature 2: Arabic/English Keyboard Layout Converter

### What it does
Solves the frustrating problem of typing while the wrong keyboard layout is active in Windows.

**Important:** This is NOT machine translation. It accurately remaps physical keyboard key positions based on Windows keyboard layout definitions.

### Real-world Examples
* **Intended English:** `go home now`
  * Typed while Arabic layout was active: `لخ اخةث ىخص`
  * Press `Ctrl + Alt + Shift + K` ➔ Converted to: `go home now`
* **Intended Arabic:** `hello`
  * Converted to: `اثممخ`
* **Intended English:** `مرحبا`
  * Converted to: `lvpfh`

### How to use
1. Select the garbled/cross-typed text with your mouse or keyboard.
2. Press `Ctrl + Alt + Shift + K`.
3. PowerTool automatically:
   * Safely captures the text while preserving your clipboard history.
   * Detects the source layout based on character distribution.
   * Converts characters using physical key scan codes.
   * Replaces the selected text in-place.
   * Restores your original clipboard data.

### Configuration
In **PowerTool Settings > Input / Output > Keyboard Layout Converter**:
* **Automatic Layout Detection:** Enable/disable automatic language direction heuristics.
* **Arabic Layout Standard:** Select between **Arabic (101)** (Standard) and **Arabic (102)** (Enhanced).
* **Preserve Punctuation:** Toggle whether punctuation marks are preserved or converted.
* **Shortcut Customization:** Customize the global activation shortcut.

---

## 4. Rebranding and Visual Identity

PowerTool Extended Edition features an original, modern Windows 11 icon and visual identity:
* Multi-resolution `.ico` icon (16x16 to 256x256).
* Adaptive dark and light mode System Tray icons.
* Seamlessly rebranded Settings application and Tray menu.
* Original Microsoft copyrights, open-source MIT licenses, and third-party notices are strictly preserved in the About dialog and repository notices.

---

## 5. دليل المستخدم باللغة العربية (Arabic Summary)

### أداة المترجم بدون إنترنت (Offline Translator)
* **اختصار التشغيل:** `Ctrl + Alt + T`
* **عكس اتجاه الترجمة:** `Ctrl + Alt + Shift + T`
* **المميزات:**
  1. ترجمة عصبية محلية بالكامل باستخدام محرك CTranslate2 ونماذج Argos المتقدمة.
  2. أمان وخصوصية تامة: لا يتم إرسال أي نصوص إلى خوادم خارجية أو سحابية.
  3. كشف تلقائي للغة (من العربية للإنجليزية أو العكس).
  4. واجهة منبثقة عصرية تدعم اتجاه الكتابة من اليمين لليسار (RTL) ومن اليسار لليمين (LTR).

### أداة مصحح تخطيط لوحة المفاتيح (Keyboard Layout Converter)
* **اختصار التشغيل:** `Ctrl + Alt + Shift + K`
* **المميزات:**
  1. تصحيح النصوص المكتوبة باللغة الخطأ عند نسيان تبديل لغة لوحة المفاتيح (مثال: كتابة `لخ اخةث ىخص` تتحول بضغطة زر إلى `go home now`).
  2. يعتمد على المواقع الفيزيائية للمفاتيح وتخطيطات ويندوز (Arabic 101 و Arabic 102).
  3. حماية الحافظة: لا يتم مسح بيانات الحافظة السابقة للمستخدم أثناء العملية.
