#pragma once

#include <string>
#include <string_view>
#include <unordered_map>
#include <vector>
#include <optional>
#include <Windows.h>

namespace PowerTool::KeyboardLayout
{
    enum class LayoutType
    {
        Arabic_101 = 0,
        Arabic_102 = 1,
        US_QWERTY = 2
    };

    enum class ConversionDirection
    {
        AutoDetect = 0,
        EnglishToArabic = 1,
        ArabicToEnglish = 2
    };

    struct ConversionResult
    {
        std::wstring convertedText;
        ConversionDirection appliedDirection = ConversionDirection::AutoDetect;
        double confidence = 1.0;
        bool changed = false;
    };

    class KeyboardLayoutConverterEngine
    {
    public:
        KeyboardLayoutConverterEngine();
        ~KeyboardLayoutConverterEngine() = default;

        // Perform bidirectional conversion
        ConversionResult Convert(
            std::wstring_view input,
            ConversionDirection direction = ConversionDirection::AutoDetect,
            LayoutType targetArabicLayout = LayoutType::Arabic_101,
            bool preservePunctuation = false) const;

        // Smart layout detection based on Unicode character distribution
        ConversionDirection DetectDirection(std::wstring_view input, double* outConfidence = nullptr) const;

        // Explicit converters
        std::wstring EnglishToArabic(std::wstring_view input, LayoutType layout = LayoutType::Arabic_101, bool preservePunctuation = false) const;
        std::wstring ArabicToEnglish(std::wstring_view input, LayoutType layout = LayoutType::Arabic_101, bool preservePunctuation = false) const;

        // Windows active layout awareness
        static HKL GetActiveLayout();
        static bool IsArabicLayoutActive();
        static bool IsEnglishLayoutActive();
        static std::wstring GetLayoutName(HKL layout);

        // Safe Clipboard Capture & Replacement with preservation of user clipboard
        static bool CaptureSelectedText(std::wstring& outText, DWORD timeoutMs = 250);
        static bool ReplaceSelectedText(const std::wstring& newText, DWORD timeoutMs = 250);

    private:
        void InitializeMappings();

        // 101 Layout mappings
        std::unordered_map<wchar_t, std::wstring> m_enToAr101;
        std::unordered_map<wchar_t, wchar_t> m_arToEn101Single;
        std::unordered_map<std::wstring, wchar_t> m_arToEn101Ligatures; // e.g., "لا", "لأ", "لإ", "لآ"

        // 102 Layout mappings overrides
        std::unordered_map<wchar_t, std::wstring> m_enToAr102;
        std::unordered_map<wchar_t, wchar_t> m_arToEn102Single;
    };
}

