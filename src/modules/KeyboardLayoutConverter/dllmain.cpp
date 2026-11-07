#include <Windows.h>
#include <interface/powertoy_module_interface.h>
#include <common/SettingsAPI/settings_objects.h>
#include <common/logger/logger.h>
#include "KeyboardLayoutConverterEngine.h"
#include <thread>
#include <atomic>
#include <string>

using namespace PowerTool::KeyboardLayout;

namespace
{
    const wchar_t MODULE_NAME[] = L"Keyboard Layout Converter";
    const wchar_t MODULE_KEY[] = L"KeyboardLayoutConverter";
}

class KeyboardLayoutConverterModule : public PowertoyModuleIface
{
public:
    KeyboardLayoutConverterModule() :
        m_enabled(false),
        m_autoDetect(true),
        m_preservePunctuation(false),
        m_targetArabicLayout(LayoutType::Arabic_101),
        m_hotkey{ .win = false, .ctrl = true, .shift = true, .alt = true, .key = 'K', .id = 0, .isShown = true }
    {
    }

    virtual const wchar_t* get_name() override
    {
        return MODULE_NAME;
    }

    virtual const wchar_t* get_key() override
    {
        return MODULE_KEY;
    }

    virtual bool get_config(wchar_t* buffer, int* buffer_size) override
    {
        HINSTANCE hinstance = reinterpret_cast<HINSTANCE>(&__ImageBase);

        PowerToysSettings::Settings settings(hinstance, get_name());
        settings.set_description(L"Converts incorrectly typed English/Arabic text based on physical keyboard layout.");

        settings.add_bool_to_toggle(L"auto_detect", L"Automatically detect layout direction", m_autoDetect);
        settings.add_bool_to_toggle(L"preserve_punctuation", L"Preserve original punctuation symbols", m_preservePunctuation);
        settings.add_hotkey(L"conversion_hotkey", L"Conversion shortcut", m_hotkey);

        return settings.serialize_to_buffer(buffer, buffer_size);
    }

    virtual void set_config(const wchar_t* config) override
    {
        try
        {
            PowerToysSettings::PowerToyValues values = PowerToysSettings::PowerToyValues::from_json_string(config, get_key());

            if (auto val = values.get_bool_value(L"auto_detect"))
            {
                m_autoDetect = *val;
            }
            if (auto val = values.get_bool_value(L"preserve_punctuation"))
            {
                m_preservePunctuation = *val;
            }
            if (auto val = values.get_string_value(L"target_layout"))
            {
                if (*val == L"Arabic102")
                {
                    m_targetArabicLayout = LayoutType::Arabic_102;
                }
                else
                {
                    m_targetArabicLayout = LayoutType::Arabic_101;
                }
            }
            if (auto val = values.get_json(L"conversion_hotkey"))
            {
                m_hotkey.win = val->GetNamedBoolean(L"win", false);
                m_hotkey.ctrl = val->GetNamedBoolean(L"ctrl", true);
                m_hotkey.shift = val->GetNamedBoolean(L"shift", true);
                m_hotkey.alt = val->GetNamedBoolean(L"alt", true);
                m_hotkey.key = static_cast<unsigned char>(val->GetNamedNumber(L"code", 'K'));
            }
        }
        catch (...)
        {
        }
    }

    virtual void enable() override
    {
        m_enabled = true;
    }

    virtual void disable() override
    {
        m_enabled = false;
    }

    virtual bool is_enabled() override
    {
        return m_enabled;
    }

    virtual void destroy() override
    {
        delete this;
    }

    virtual size_t get_hotkeys(Hotkey* buffer, size_t buffer_size) override
    {
        if (buffer && buffer_size >= 1)
        {
            buffer[0] = m_hotkey;
        }
        return 1;
    }

    virtual bool on_hotkey(size_t hotkeyId) override
    {
        if (!m_enabled || hotkeyId != 0)
        {
            return false;
        }

        // Spawn conversion asynchronously so hotkey hook never hangs
        std::thread([this]() {
            ExecuteConversion();
        }).detach();

        return true;
    }

private:
    void ExecuteConversion()
    {
        std::wstring selectedText;
        if (!KeyboardLayoutConverterEngine::CaptureSelectedText(selectedText, 300))
        {
            return;
        }

        if (selectedText.empty())
        {
            return;
        }

        ConversionDirection dir = m_autoDetect ? ConversionDirection::AutoDetect : ConversionDirection::EnglishToArabic;
        auto result = m_engine.Convert(selectedText, dir, m_targetArabicLayout, m_preservePunctuation);

        if (result.changed)
        {
            KeyboardLayoutConverterEngine::ReplaceSelectedText(result.convertedText, 300);
        }
    }

    bool m_enabled;
    bool m_autoDetect;
    bool m_preservePunctuation;
    LayoutType m_targetArabicLayout;
    Hotkey m_hotkey;
    KeyboardLayoutConverterEngine m_engine;
};

extern "C" __declspec(dllexport) PowertoyModuleIface* __cdecl powertoy_create()
{
    return new KeyboardLayoutConverterModule();
}

