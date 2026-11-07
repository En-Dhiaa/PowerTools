// Copyright (c) Microsoft Corporation & PowerTool Contributors
// The Microsoft Corporation licenses this file to you under the MIT license.
// See the LICENSE file in the project root for more information.

using System;
using System.Runtime.CompilerServices;
using Microsoft.PowerToys.Settings.UI.Helpers;
using Microsoft.PowerToys.Settings.UI.Library;
using Microsoft.PowerToys.Settings.UI.Library.Interfaces;

namespace Microsoft.PowerToys.Settings.UI.ViewModels
{
    public partial class KeyboardLayoutConverterViewModel : Observable
    {
        private GeneralSettings GeneralSettingsConfig { get; set; }

        private readonly KeyboardLayoutConverterSettings _settings;
        private readonly SettingsUtils _settingsUtils;
        private Func<string, int> SendConfigMSG { get; }

        public KeyboardLayoutConverterViewModel(SettingsUtils settingsUtils, ISettingsRepository<GeneralSettings> settingsRepository, Func<string, int> ipcMSGCallBackFunc)
        {
            _settingsUtils = settingsUtils ?? throw new ArgumentNullException(nameof(settingsUtils));
            SendConfigMSG = ipcMSGCallBackFunc;

            if (settingsRepository != null)
            {
                GeneralSettingsConfig = settingsRepository.SettingsConfig;
            }

            try
            {
                if (_settingsUtils.SettingsExists(KeyboardLayoutConverterSettings.ModuleName))
                {
                    _settings = _settingsUtils.GetSettingsOrDefault<KeyboardLayoutConverterSettings>(KeyboardLayoutConverterSettings.ModuleName);
                }
                else
                {
                    _settings = new KeyboardLayoutConverterSettings();
                    _settingsUtils.SaveSettings(_settings.ToJsonString(), KeyboardLayoutConverterSettings.ModuleName);
                }
            }
            catch
            {
                _settings = new KeyboardLayoutConverterSettings();
            }
        }

        public bool IsEnabled
        {
            get => GeneralSettingsConfig?.Enabled.KeyboardLayoutConverter ?? true;
            set
            {
                if (GeneralSettingsConfig != null && GeneralSettingsConfig.Enabled.KeyboardLayoutConverter != value)
                {
                    GeneralSettingsConfig.Enabled.KeyboardLayoutConverter = value;
                    OnPropertyChanged();
                    NotifySettingsChanged();
                }
            }
        }

        public bool AutoDetect
        {
            get => _settings.Properties.AutoDetect;
            set
            {
                if (_settings.Properties.AutoDetect != value)
                {
                    _settings.Properties.AutoDetect = value;
                    OnPropertyChanged();
                    NotifySettingsChanged();
                }
            }
        }

        public bool PreservePunctuation
        {
            get => _settings.Properties.PreservePunctuation;
            set
            {
                if (_settings.Properties.PreservePunctuation != value)
                {
                    _settings.Properties.PreservePunctuation = value;
                    OnPropertyChanged();
                    NotifySettingsChanged();
                }
            }
        }

        public int TargetLayoutIndex
        {
            get => _settings.Properties.TargetLayout == "Arabic102" ? 1 : 0;
            set
            {
                string layout = (value == 1) ? "Arabic102" : "Arabic101";
                if (_settings.Properties.TargetLayout != layout)
                {
                    _settings.Properties.TargetLayout = layout;
                    OnPropertyChanged();
                    NotifySettingsChanged();
                }
            }
        }

        public HotkeySettings ConversionHotkey
        {
            get => _settings.Properties.ConversionHotkey;
            set
            {
                if (value != null && !_settings.Properties.ConversionHotkey.Equals(value))
                {
                    _settings.Properties.ConversionHotkey = value;
                    OnPropertyChanged();
                    NotifySettingsChanged();
                }
            }
        }

        private void NotifySettingsChanged()
        {
            try
            {
                _settingsUtils.SaveSettings(_settings.ToJsonString(), KeyboardLayoutConverterSettings.ModuleName);
                var snd = new SndKeyboardLayoutConverterSettings(_settings);
                SendConfigMSG?.Invoke(snd.ToJsonString());
            }
            catch
            {
            }
        }
    }
}

