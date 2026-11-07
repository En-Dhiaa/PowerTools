#include "KeyboardLayoutConverterEngine.h"
#include <cwctype>
#include <algorithm>
#include <vector>

namespace PowerTool::KeyboardLayout
{
    KeyboardLayoutConverterEngine::KeyboardLayoutConverterEngine()
    {
        InitializeMappings();
    }

    void KeyboardLayoutConverterEngine::InitializeMappings()
    {
        // 1. English to Arabic 101 mapping
        // Format: English character -> Arabic string (string because ligatures like 'لا' have 2 chars)
        struct EnArPair { wchar_t en; const wchar_t* ar; };

        static const EnArPair enArTable101[] = {
            // Row 1: Number Row
            { L'`', L"ذ" },  { L'~', L"ّ" },
            { L'1', L"1" },  { L'!', L"!" },
            { L'2', L"2" },  { L'@', L"@" },
            { L'3', L"3" },  { L'#', L"#" },
            { L'4', L"4" },  { L'$', L"$" },
            { L'5', L"5" },  { L'%', L"%" },
            { L'6', L"6" },  { L'^', L"^" },
            { L'7', L"7" },  { L'&', L"&" },
            { L'8', L"8" },  { L'*', L"*" },
            { L'9', L"9" },  { L'(', L")" },
            { L'0', L"0" },  { L')', L"(" },
            { L'-', L"-" },  { L'_', L"_" },
            { L'=', L"=" },  { L'+', L"+" },

            // Row 2: QWERTY Row
            { L'q', L"ض" },  { L'Q', L"َ" },
            { L'w', L"ص" },  { L'W', L"ً" },
            { L'e', L"ث" },  { L'E', L"ُ" },
            { L'r', L"ق" },  { L'R', L"ٌ" },
            { L't', L"ف" },  { L'T', L"لإ" },
            { L'y', L"غ" },  { L'Y', L"إ" },
            { L'u', L"ع" },  { L'U', L"`" },
            { L'i', L"ه" },  { L'I', L"÷" },
            { L'o', L"خ" },  { L'O', L"×" },
            { L'p', L"ح" },  { L'P', L"؛" },
            { L'[', L"ج" },  { L'{', L"<" },
            { L']', L"د" },  { L'}', L">" },
            { L'\\', L"\\" }, { L'|', L"|" },

            // Row 3: Home Row (ASDF)
            { L'a', L"ش" },  { L'A', L"ِ" },
            { L's', L"س" },  { L'S', L"ٍ" },
            { L'd', L"ي" },  { L'D', L"]" },
            { L'f', L"ب" },  { L'F', L"[" },
            { L'g', L"ل" },  { L'G', L"لأ" },
            { L'h', L"ا" },  { L'H', L"أ" },
            { L'j', L"ت" },  { L'J', L"ـ" },
            { L'k', L"ن" },  { L'K', L"،" },
            { L'l', L"م" },  { L'L', L"/" },
            { L';', L"ك" },  { L':', L":" },
            { L'\'', L"ط" }, { L'\"', L"\"" },

            // Row 4: Bottom Row (ZXCV)
            { L'z', L"ئ" },  { L'Z', L"~" },
            { L'x', L"ء" },  { L'X', L"ْ" },
            { L'c', L"ؤ" },  { L'C', L"}" },
            { L'v', L"ر" },  { L'V', L"{" },
            { L'b', L"لا" }, { L'B', L"لآ" },
            { L'n', L"ى" },  { L'N', L"آ" },
            { L'm', L"ة" },  { L'M', L"\'" },
            { L',', L"و" },  { L'<', L"," },
            { L'.', L"ز" },  { L'>', L"." },
            { L'/', L"ظ" },  { L'?', L"؟" },

            // Space
            { L' ', L" " }
        };

        for (const auto& item : enArTable101)
        {
            m_enToAr101[item.en] = item.ar;
            std::wstring arStr = item.ar;

            if (arStr.length() == 1)
            {
                m_arToEn101Single[arStr[0]] = item.en;
            }
            else
            {
                m_arToEn101Ligatures[arStr] = item.en;
            }
        }

        // Add single-codepoint Unicode ligatures for Arabic
        m_arToEn101Single[0xFEFB] = L'b'; // Lam-Alef isolated
        m_arToEn101Single[0xFEFC] = L'b'; // Lam-Alef final
        m_arToEn101Single[0xFEF7] = L'G'; // Lam-Alef Hamza Above isolated
        m_arToEn101Single[0xFEF8] = L'G'; // Lam-Alef Hamza Above final
        m_arToEn101Single[0xFEF9] = L'T'; // Lam-Alef Hamza Below isolated
        m_arToEn101Single[0xFEFA] = L'T'; // Lam-Alef Hamza Below final
        m_arToEn101Single[0xFEF5] = L'B'; // Lam-Alef Madda Above isolated
        m_arToEn101Single[0xFEF6] = L'B'; // Lam-Alef Madda Above final

        // Arabic 102 Layout overrides
        m_enToAr102 = m_enToAr101;
        m_arToEn102Single = m_arToEn101Single;
        // 102 layout key beside Z / Left Shift
        m_enToAr102[L'\\'] = L"\\";
        m_enToAr102[L'|'] = L"|";
    }

    ConversionDirection KeyboardLayoutConverterEngine::DetectDirection(std::wstring_view input, double* outConfidence) const
    {
        size_t arabicCount = 0;
        size_t latinCount = 0;

        for (wchar_t ch : input)
        {
            if ((ch >= 0x0600 && ch <= 0x06FF) || (ch >= 0xFB50 && ch <= 0xFDFF) || (ch >= 0xFE70 && ch <= 0xFEFF))
            {
                // Arabic character
                arabicCount++;
            }
            else if ((ch >= L'a' && ch <= L'z') || (ch >= L'A' && ch <= L'Z'))
            {
                // Latin character
                latinCount++;
            }
        }

        size_t total = arabicCount + latinCount;
        double confidence = (total > 0) ? (static_cast<double>(std::max(arabicCount, latinCount)) / total) : 0.0;

        if (outConfidence)
        {
            *outConfidence = confidence;
        }

        if (arabicCount > latinCount)
        {
            return ConversionDirection::ArabicToEnglish;
        }
        else if (latinCount > arabicCount)
        {
            return ConversionDirection::EnglishToArabic;
        }

        // If equal, check active Windows keyboard layout
        if (IsArabicLayoutActive())
        {
            return ConversionDirection::EnglishToArabic;
        }

        return ConversionDirection::ArabicToEnglish;
    }

    ConversionResult KeyboardLayoutConverterEngine::Convert(
        std::wstring_view input,
        ConversionDirection direction,
        LayoutType targetArabicLayout,
        bool preservePunctuation) const
    {
        ConversionResult result;
        if (input.empty())
        {
            result.changed = false;
            return result;
        }

        if (direction == ConversionDirection::AutoDetect)
        {
            direction = DetectDirection(input, &result.confidence);
        }

        result.appliedDirection = direction;

        if (direction == ConversionDirection::EnglishToArabic)
        {
            result.convertedText = EnglishToArabic(input, targetArabicLayout, preservePunctuation);
        }
        else
        {
            result.convertedText = ArabicToEnglish(input, targetArabicLayout, preservePunctuation);
        }

        result.changed = (result.convertedText != input);
        return result;
    }

    std::wstring KeyboardLayoutConverterEngine::EnglishToArabic(std::wstring_view input, LayoutType layout, bool preservePunctuation) const
    {
        const auto& map = (layout == LayoutType::Arabic_102) ? m_enToAr102 : m_enToAr101;
        std::wstring output;
        output.reserve(input.length() + 8);

        for (wchar_t ch : input)
        {
            if (preservePunctuation && iswpunct(ch))
            {
                output.push_back(ch);
                continue;
            }

            auto it = map.find(ch);
            if (it != map.end())
            {
                output.append(it->second);
            }
            else
            {
                output.push_back(ch);
            }
        }

        return output;
    }

    std::wstring KeyboardLayoutConverterEngine::ArabicToEnglish(std::wstring_view input, LayoutType layout, bool preservePunctuation) const
    {
        const auto& singleMap = (layout == LayoutType::Arabic_102) ? m_arToEn102Single : m_arToEn101Single;
        std::wstring output;
        output.reserve(input.length());

        size_t i = 0;
        size_t len = input.length();

        while (i < len)
        {
            // Check 2-character ligatures first (like 'لا', 'لأ', 'لإ', 'لآ')
            if (i + 1 < len)
            {
                std::wstring twoChar = { input[i], input[i + 1] };
                auto ligIt = m_arToEn101Ligatures.find(twoChar);
                if (ligIt != m_arToEn101Ligatures.end())
                {
                    output.push_back(ligIt->second);
                    i += 2;
                    continue;
                }
            }

            wchar_t ch = input[i];
            if (preservePunctuation && iswpunct(ch))
            {
                output.push_back(ch);
                i++;
                continue;
            }

            auto it = singleMap.find(ch);
            if (it != singleMap.end())
            {
                output.push_back(it->second);
            }
            else
            {
                output.push_back(ch);
            }
            i++;
        }

        return output;
    }

    HKL KeyboardLayoutConverterEngine::GetActiveLayout()
    {
        HWND foreground = GetForegroundWindow();
        if (!foreground)
        {
            return GetKeyboardLayout(0);
        }

        DWORD threadId = GetWindowThreadProcessId(foreground, nullptr);
        return GetKeyboardLayout(threadId);
    }

    bool KeyboardLayoutConverterEngine::IsArabicLayoutActive()
    {
        HKL layout = GetActiveLayout();
        WORD langId = LOWORD(layout);
        return PRIMARYLANGID(langId) == LANG_ARABIC;
    }

    bool KeyboardLayoutConverterEngine::IsEnglishLayoutActive()
    {
        HKL layout = GetActiveLayout();
        WORD langId = LOWORD(layout);
        return PRIMARYLANGID(langId) == LANG_ENGLISH;
    }

    std::wstring KeyboardLayoutConverterEngine::GetLayoutName(HKL layout)
    {
        wchar_t name[KL_NAMELENGTH] = { 0 };
        if (GetKeyboardLayoutNameW(name))
        {
            return std::wstring(name);
        }
        return L"Unknown";
    }

    // Backup and restore clipboard data structure
    struct ClipboardBackup
    {
        std::wstring text;
        bool hadText = false;
    };

    static ClipboardBackup SaveCurrentClipboard()
    {
        ClipboardBackup backup;
        if (!OpenClipboard(nullptr))
        {
            return backup;
        }

        HANDLE hData = GetClipboardData(CF_UNICODETEXT);
        if (hData)
        {
            wchar_t* pText = static_cast<wchar_t*>(GlobalLock(hData));
            if (pText)
            {
                backup.text = pText;
                backup.hadText = true;
                GlobalUnlock(hData);
            }
        }
        CloseClipboard();
        return backup;
    }

    static void RestoreCurrentClipboard(const ClipboardBackup& backup)
    {
        if (!backup.hadText)
        {
            return;
        }

        if (!OpenClipboard(nullptr))
        {
            return;
        }

        EmptyClipboard();
        size_t size = (backup.text.length() + 1) * sizeof(wchar_t);
        HGLOBAL hMem = GlobalAlloc(GMEM_MOVEABLE, size);
        if (hMem)
        {
            void* pMem = GlobalLock(hMem);
            if (pMem)
            {
                memcpy(pMem, backup.text.c_str(), size);
                GlobalUnlock(hMem);
                SetClipboardData(CF_UNICODETEXT, hMem);
            }
            else
            {
                GlobalFree(hMem);
            }
        }
        CloseClipboard();
    }

    bool KeyboardLayoutConverterEngine::CaptureSelectedText(std::wstring& outText, DWORD timeoutMs)
    {
        auto backup = SaveCurrentClipboard();

        // Clear clipboard so we can detect newly copied text
        if (OpenClipboard(nullptr))
        {
            EmptyClipboard();
            CloseClipboard();
        }

        // Send Ctrl+C
        INPUT inputs[4] = {};
        // Ctrl down
        inputs[0].type = INPUT_KEYBOARD;
        inputs[0].ki.wVk = VK_CONTROL;
        // C down
        inputs[1].type = INPUT_KEYBOARD;
        inputs[1].ki.wVk = 'C';
        // C up
        inputs[2].type = INPUT_KEYBOARD;
        inputs[2].ki.wVk = 'C';
        inputs[2].ki.dwFlags = KEYEVENTF_KEYUP;
        // Ctrl up
        inputs[3].type = INPUT_KEYBOARD;
        inputs[3].ki.wVk = VK_CONTROL;
        inputs[3].ki.dwFlags = KEYEVENTF_KEYUP;

        SendInput(4, inputs, sizeof(INPUT));

        // Poll for new clipboard content
        DWORD start = GetTickCount();
        bool captured = false;

        while ((GetTickCount() - start) < timeoutMs)
        {
            Sleep(25);
            if (OpenClipboard(nullptr))
            {
                HANDLE hData = GetClipboardData(CF_UNICODETEXT);
                if (hData)
                {
                    wchar_t* pText = static_cast<wchar_t*>(GlobalLock(hData));
                    if (pText && wcslen(pText) > 0)
                    {
                        outText = pText;
                        captured = true;
                        GlobalUnlock(hData);
                        CloseClipboard();
                        break;
                    }
                    if (pText) GlobalUnlock(hData);
                }
                CloseClipboard();
            }
        }

        // Restore original clipboard if no text was captured
        if (!captured)
        {
            RestoreCurrentClipboard(backup);
        }

        return captured;
    }

    bool KeyboardLayoutConverterEngine::ReplaceSelectedText(const std::wstring& newText, DWORD timeoutMs)
    {
        auto backup = SaveCurrentClipboard();

        // Put newText into clipboard
        if (!OpenClipboard(nullptr))
        {
            return false;
        }

        EmptyClipboard();
        size_t size = (newText.length() + 1) * sizeof(wchar_t);
        HGLOBAL hMem = GlobalAlloc(GMEM_MOVEABLE, size);
        if (hMem)
        {
            void* pMem = GlobalLock(hMem);
            if (pMem)
            {
                memcpy(pMem, newText.c_str(), size);
                GlobalUnlock(hMem);
                SetClipboardData(CF_UNICODETEXT, hMem);
            }
            else
            {
                GlobalFree(hMem);
                CloseClipboard();
                return false;
            }
        }
        CloseClipboard();

        // Send Ctrl+V
        INPUT inputs[4] = {};
        // Ctrl down
        inputs[0].type = INPUT_KEYBOARD;
        inputs[0].ki.wVk = VK_CONTROL;
        // V down
        inputs[1].type = INPUT_KEYBOARD;
        inputs[1].ki.wVk = 'V';
        // V up
        inputs[2].type = INPUT_KEYBOARD;
        inputs[2].ki.wVk = 'V';
        inputs[2].ki.dwFlags = KEYEVENTF_KEYUP;
        // Ctrl up
        inputs[3].type = INPUT_KEYBOARD;
        inputs[3].ki.wVk = VK_CONTROL;
        inputs[3].ki.dwFlags = KEYEVENTF_KEYUP;

        SendInput(4, inputs, sizeof(INPUT));

        // Allow target app to paste before restoring original clipboard
        Sleep(50);
        RestoreCurrentClipboard(backup);

        return true;
    }
}

