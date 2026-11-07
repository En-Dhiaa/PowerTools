// Copyright (c) Microsoft Corporation & PowerTool Contributors
// The Microsoft Corporation licenses this file to you under the MIT license.
// See the LICENSE file in the project root for more information.

using Microsoft.PowerToys.Settings.UI.Helpers;
using Microsoft.PowerToys.Settings.UI.Library;
using Microsoft.PowerToys.Settings.UI.ViewModels;
using Microsoft.UI.Xaml;

namespace Microsoft.PowerToys.Settings.UI.Views
{
    public sealed partial class OfflineTranslatorPage : NavigablePage
    {
        private OfflineTranslatorViewModel ViewModel { get; set; }

        public OfflineTranslatorPage()
        {
            var settingsUtils = SettingsUtils.Default;
            ViewModel = new OfflineTranslatorViewModel(settingsUtils, SettingsRepository<GeneralSettings>.GetInstance(settingsUtils), ShellPage.SendDefaultIPCMessage);
            DataContext = ViewModel;
            this.InitializeComponent();
        }

        private void OnModelActionClick(object sender, RoutedEventArgs e)
        {
            if (sender is FrameworkElement element && element.DataContext is TranslationModelItem item)
            {
                ViewModel.HandleModelAction(item);
            }
        }
    }
}
