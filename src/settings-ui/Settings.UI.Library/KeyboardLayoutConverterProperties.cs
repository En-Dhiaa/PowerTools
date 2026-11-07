// Copyright (c) Microsoft Corporation & PowerTool Contributors
// The Microsoft Corporation licenses this file to you under the MIT license.
// See the LICENSE file in the project root for more information.

using System.Text.Json.Serialization;

namespace Microsoft.PowerToys.Settings.UI.Library
{
    public class KeyboardLayoutConverterProperties
    {
        [JsonPropertyName("auto_detect")]
        public bool AutoDetect { get; set; }

        [JsonPropertyName("target_layout")]
        public string TargetLayout { get; set; }

        [JsonPropertyName("preserve_punctuation")]
        public bool PreservePunctuation { get; set; }

        [JsonPropertyName("conversion_hotkey")]
        public HotkeySettings ConversionHotkey { get; set; }

        public KeyboardLayoutConverterProperties()
        {
            AutoDetect = true;
            TargetLayout = "Arabic101";
            PreservePunctuation = false;
            ConversionHotkey = new HotkeySettings(false, true, true, true, 75); // Ctrl + Alt + Shift + K ('K' = 75)
        }
    }
}
