#include <Windows.h>
#include <interface/powertoy_module_interface.h>
#include <common/SettingsAPI/settings_objects.h>
#include <common/logger/logger.h>
#include <string>
#include <thread>
#include <shellapi.h>

namespace
{
    const wchar_t MODULE_NAME[] = L"Offline Translator";
    const wchar_t MODULE_KEY[] = L"OfflineTranslator";
}

class OfflineTranslatorModule : public PowertoyModuleIface
{
public:
    OfflineTranslatorModule() :
        m_enabled(true),
        m_autoDetect(true),
        m_replaceSelectedText(false),
        m_hotkeyTranslate{ .win = false, .ctrl = true, .shift = false, .alt = true, .key = 'T', .id = 0, .isShown = true },
        m_hotkeyReverse{ .win = false, .ctrl = true, .shift = true, .alt = true, .key = 'T', .id = 1, .isShown = true }
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
        settings.set_description(L"Offline neural translation between Arabic and English without internet access.");

        settings.add_bool_to_toggle(L"auto_detect", L"Automatic source language detection", m_autoDetect);
        settings.add_bool_to_toggle(L"replace_selected_text", L"Replace selected text directly on shortcut", m_replaceSelectedText);
        settings.add_hotkey(L"translation_hotkey", L"Translation shortcut", m_hotkeyTranslate);
        settings.add_hotkey(L"reverse_hotkey", L"Reverse translation shortcut", m_hotkeyReverse);

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
            if (auto val = values.get_bool_value(L"replace_selected_text"))
            {
                m_replaceSelectedText = *val;
            }
            if (auto val = values.get_json(L"translation_hotkey"))
            {
                m_hotkeyTranslate.win = val->GetNamedBoolean(L"win", false);
                m_hotkeyTranslate.ctrl = val->GetNamedBoolean(L"ctrl", true);
                m_hotkeyTranslate.shift = val->GetNamedBoolean(L"shift", false);
                m_hotkeyTranslate.alt = val->GetNamedBoolean(L"alt", true);
                m_hotkeyTranslate.key = static_cast<unsigned char>(val->GetNamedNumber(L"code", 'T'));
            }
            if (auto val = values.get_json(L"reverse_hotkey"))
            {
                m_hotkeyReverse.win = val->GetNamedBoolean(L"win", false);
                m_hotkeyReverse.ctrl = val->GetNamedBoolean(L"ctrl", true);
                m_hotkeyReverse.shift = val->GetNamedBoolean(L"shift", true);
                m_hotkeyReverse.alt = val->GetNamedBoolean(L"alt", true);
                m_hotkeyReverse.key = static_cast<unsigned char>(val->GetNamedNumber(L"code", 'T'));
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
        if (buffer && buffer_size >= 2)
        {
            buffer[0] = m_hotkeyTranslate;
            buffer[1] = m_hotkeyReverse;
        }
        return 2;
    }

    virtual bool on_hotkey(size_t hotkeyId) override
    {
        if (!m_enabled)
        {
            return false;
        }

        bool isReverse = (hotkeyId == 1);

        std::thread([this, isReverse]() {
            LaunchTranslationUI(isReverse);
        }).detach();

        return true;
    }

private:
    void LaunchTranslationUI(bool reverse)
    {
        wchar_t modulePath[MAX_PATH] = { 0 };
        GetModuleFileNameW(reinterpret_cast<HINSTANCE>(&__ImageBase), modulePath, MAX_PATH);

        // Compute directory containing python CLI
        std::wstring dirPath = modulePath;
        size_t lastSlash = dirPath.find_last_of(L"\\/");
        if (lastSlash != std::wstring::npos)
        {
            dirPath = dirPath.substr(0, lastSlash);
        }

        std::wstring cliScript = dirPath + L"\\OfflineTranslator\\OfflineTranslatorCLI.py";
        std::wstring params = L"\"" + cliScript + L"\" --popup";
        if (reverse)
        {
            params += L" --reverse";
        }

        SHELLEXECUTEINFOW sei = { sizeof(sei) };
        sei.fMask = SEE_MASK_NOASYNC | SEE_MASK_FLAG_NO_UI;
        sei.lpFile = L"pythonw.exe";
        sei.lpParameters = params.c_str();
        sei.nShow = SW_SHOWNORMAL;

        if (!ShellExecuteExW(&sei))
        {
            // Fallback to python.exe if pythonw is unavailable
            sei.lpFile = L"python.exe";
            ShellExecuteExW(&sei);
        }
    }

    bool m_enabled;
    bool m_autoDetect;
    bool m_replaceSelectedText;
    Hotkey m_hotkeyTranslate;
    Hotkey m_hotkeyReverse;
};

extern "C" __declspec(dllexport) PowertoyModuleIface* __cdecl powertoy_create()
{
    return new OfflineTranslatorModule();
}
