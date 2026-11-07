// Copyright (c) Microsoft Corporation & PowerTool Contributors
// The Microsoft Corporation licenses this file to you under the MIT license.
// See the LICENSE file in the project root for more information.

using System.Text.Json.Serialization;
using Microsoft.PowerToys.Settings.UI.Library.Interfaces;

namespace Microsoft.PowerToys.Settings.UI.Library
{
    public class KeyboardLayoutConverterSettings : BasePTModuleSettings, ISettingsConfig
    {
        public const string ModuleName = "KeyboardLayoutConverter";
        public const string ModuleVersion = "1.0.0";

        [JsonPropertyName("properties")]
        public KeyboardLayoutConverterProperties Properties { get; set; }

        public KeyboardLayoutConverterSettings()
        {
            Name = ModuleName;
            Version = ModuleVersion;
            Properties = new KeyboardLayoutConverterProperties();
        }

        public string GetModuleName()
        {
            return Name;
        }

        public bool UpgradeSettingsConfiguration()
        {
            return false;
        }
    }
}

