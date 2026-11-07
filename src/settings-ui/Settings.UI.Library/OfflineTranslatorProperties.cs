// Copyright (c) Microsoft Corporation & PowerTool Contributors
// The Microsoft Corporation licenses this file to you under the MIT license.
// See the LICENSE file in the project root for more information.

using System.Text.Json.Serialization;

namespace Microsoft.PowerToys.Settings.UI.Library
{
    public class OfflineTranslatorProperties
    {
        [JsonPropertyName("auto_detect")]
        public bool AutoDetect { get; set; }

        [JsonPropertyName("replace_selected_text")]
        public bool ReplaceSelectedText { get; set; }

        [JsonPropertyName("translation_hotkey")]
        public HotkeySettings TranslationHotkey { get; set; }

        [JsonPropertyName("reverse_hotkey")]
        public HotkeySettings ReverseHotkey { get; set; }

        public OfflineTranslatorProperties()
        {
            AutoDetect = true;
            ReplaceSelectedText = false;
            TranslationHotkey = new HotkeySettings(false, true, false, true, 84); // Ctrl + Alt + T ('T' = 84)
            ReverseHotkey = new HotkeySettings(false, true, true, true, 84);     // Ctrl + Alt + Shift + T
        }
    }
}

