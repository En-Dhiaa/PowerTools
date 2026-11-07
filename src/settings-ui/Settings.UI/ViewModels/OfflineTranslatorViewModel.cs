// Copyright (c) Microsoft Corporation & PowerTool Contributors
// The Microsoft Corporation licenses this file to you under the MIT license.
// See the LICENSE file in the project root for more information.

using System;
using System.Collections.ObjectModel;
using System.Diagnostics;
using System.IO;
using System.Text.Json;
using Microsoft.PowerToys.Settings.UI.Helpers;
using Microsoft.PowerToys.Settings.UI.Library;
using Microsoft.PowerToys.Settings.UI.Library.Interfaces;

namespace Microsoft.PowerToys.Settings.UI.ViewModels
{
    public class TranslationModelItem
    {
        public string Id { get; set; }
        public string FromCode { get; set; }
        public string ToCode { get; set; }
        public string FromName { get; set; }
        public string ToName { get; set; }
        public string Version { get; set; }
        public double SizeMb { get; set; }
        public bool IsInstalled { get; set; }
        public string StatusText => IsInstalled ? "✓ Installed (Offline Ready)" : "Available to Download";
        public string ActionButtonText => IsInstalled ? "Delete Model" : "Download Package";
    }

    public partial class OfflineTranslatorViewModel : Observable
    {
        private GeneralSettings GeneralSettingsConfig { get; set; }

        private readonly OfflineTranslatorSettings _settings;
        private readonly SettingsUtils _settingsUtils;
        private Func<string, int> SendConfigMSG { get; }

        public ObservableCollection<TranslationModelItem> ModelItems { get; set; } = new();

        public OfflineTranslatorViewModel(SettingsUtils settingsUtils, ISettingsRepository<GeneralSettings> settingsRepository, Func<string, int> ipcMSGCallBackFunc)
        {
            _settingsUtils = settingsUtils ?? throw new ArgumentNullException(nameof(settingsUtils));
            SendConfigMSG = ipcMSGCallBackFunc;

            if (settingsRepository != null)
            {
                GeneralSettingsConfig = settingsRepository.SettingsConfig;
            }

            try
            {
                if (_settingsUtils.SettingsExists(OfflineTranslatorSettings.ModuleName))
                {
                    _settings = _settingsUtils.GetSettingsOrDefault<OfflineTranslatorSettings>(OfflineTranslatorSettings.ModuleName);
                }
                else
                {
                    _settings = new OfflineTranslatorSettings();
                    _settingsUtils.SaveSettings(_settings.ToJsonString(), OfflineTranslatorSettings.ModuleName);
                }
            }
            catch
            {
                _settings = new OfflineTranslatorSettings();
            }

            RefreshModelsList();
        }

        public bool IsEnabled
        {
            get => GeneralSettingsConfig?.Enabled.OfflineTranslator ?? true;
            set
            {
                if (GeneralSettingsConfig != null && GeneralSettingsConfig.Enabled.OfflineTranslator != value)
                {
                    GeneralSettingsConfig.Enabled.OfflineTranslator = value;
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

        public bool ReplaceSelectedText
        {
            get => _settings.Properties.ReplaceSelectedText;
            set
            {
                if (_settings.Properties.ReplaceSelectedText != value)
                {
                    _settings.Properties.ReplaceSelectedText = value;
                    OnPropertyChanged();
                    NotifySettingsChanged();
                }
            }
        }

        public HotkeySettings TranslationHotkey
        {
            get => _settings.Properties.TranslationHotkey;
            set
            {
                if (value != null && !_settings.Properties.TranslationHotkey.Equals(value))
                {
                    _settings.Properties.TranslationHotkey = value;
                    OnPropertyChanged();
                    NotifySettingsChanged();
                }
            }
        }

        public HotkeySettings ReverseHotkey
        {
            get => _settings.Properties.ReverseHotkey;
            set
            {
                if (value != null && !_settings.Properties.ReverseHotkey.Equals(value))
                {
                    _settings.Properties.ReverseHotkey = value;
                    OnPropertyChanged();
                    NotifySettingsChanged();
                }
            }
        }

        public void RefreshModelsList()
        {
            ModelItems.Clear();

            string localAppData = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
            string baseDir = Path.Combine(localAppData, "Microsoft", "PowerToys", "OfflineTranslator", "models");

            bool arEnInstalled = Directory.Exists(Path.Combine(baseDir, "translate-ar_en"));
            bool enArInstalled = Directory.Exists(Path.Combine(baseDir, "translate-en_ar"));

            ModelItems.Add(new TranslationModelItem
            {
                Id = "ar_en",
                FromCode = "ar",
                ToCode = "en",
                FromName = "Arabic",
                ToName = "English",
                Version = "1.0",
                SizeMb = 78.1,
                IsInstalled = arEnInstalled
            });

            ModelItems.Add(new TranslationModelItem
            {
                Id = "en_ar",
                FromCode = "en",
                ToCode = "ar",
                FromName = "English",
                ToName = "Arabic",
                Version = "1.0",
                SizeMb = 84.4,
                IsInstalled = enArInstalled
            });
        }

        public void HandleModelAction(TranslationModelItem item)
        {
            if (item == null) return;

            string localAppData = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
            string baseDir = Path.Combine(localAppData, "Microsoft", "PowerToys", "OfflineTranslator", "models");
            string dir = Path.Combine(baseDir, $"translate-{item.FromCode}_{item.ToCode}");

            if (item.IsInstalled)
            {
                if (Directory.Exists(dir))
                {
                    try
                    {
                        Directory.Delete(dir, true);
                    }
                    catch
                    {
                    }
                }
            }

            RefreshModelsList();
        }

        private void NotifySettingsChanged()
        {
            try
            {
                _settingsUtils.SaveSettings(_settings.ToJsonString(), OfflineTranslatorSettings.ModuleName);
                var snd = new SndOfflineTranslatorSettings(_settings);
                SendConfigMSG?.Invoke(snd.ToJsonString());
            }
            catch
            {
            }
        }
    }
}
