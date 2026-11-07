// Copyright (c) Microsoft Corporation & PowerTool Contributors
// The Microsoft Corporation licenses this file to you under the MIT license.
// See the LICENSE file in the project root for more information.

using System.Text.Json;
using System.Text.Json.Serialization;

namespace Microsoft.PowerToys.Settings.UI.Library
{
    public class SndOfflineTranslatorSettings
    {
        [JsonPropertyName("OfflineTranslator")]
        public OfflineTranslatorSettings OfflineTranslatorSettings { get; set; }

        public SndOfflineTranslatorSettings()
        {
        }

        public SndOfflineTranslatorSettings(OfflineTranslatorSettings settings)
        {
            OfflineTranslatorSettings = settings;
        }

        public string ToJsonString()
        {
            return JsonSerializer.Serialize(this);
        }
    }
}

