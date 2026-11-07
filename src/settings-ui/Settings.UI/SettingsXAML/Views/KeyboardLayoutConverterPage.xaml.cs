// Copyright (c) Microsoft Corporation & PowerTool Contributors
// The Microsoft Corporation licenses this file to you under the MIT license.
// See the LICENSE file in the project root for more information.

using Microsoft.PowerToys.Settings.UI.Helpers;
using Microsoft.PowerToys.Settings.UI.Library;
using Microsoft.PowerToys.Settings.UI.ViewModels;

namespace Microsoft.PowerToys.Settings.UI.Views
{
    public sealed partial class KeyboardLayoutConverterPage : NavigablePage
    {
        private KeyboardLayoutConverterViewModel ViewModel { get; set; }

        public KeyboardLayoutConverterPage()
        {
            var settingsUtils = SettingsUtils.Default;
            ViewModel = new KeyboardLayoutConverterViewModel(settingsUtils, SettingsRepository<GeneralSettings>.GetInstance(settingsUtils), ShellPage.SendDefaultIPCMessage);
            DataContext = ViewModel;
            this.InitializeComponent();
        }
    }
}

