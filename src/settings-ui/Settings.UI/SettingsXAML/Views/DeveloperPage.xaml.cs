// Copyright (c) Microsoft Corporation & PowerTool Contributors
// The Microsoft Corporation licenses this file to you under the MIT license.
// See the LICENSE file in the project root for more information.

using System;
using Microsoft.PowerToys.Settings.UI.Helpers;
using Microsoft.PowerToys.Settings.UI.ViewModels;
using Windows.System;

namespace Microsoft.PowerToys.Settings.UI.Views
{
    public sealed partial class DeveloperPage : NavigablePage
    {
        public DeveloperViewModel ViewModel { get; set; }

        public DeveloperPage()
        {
            ViewModel = new DeveloperViewModel();
            DataContext = ViewModel;
            this.InitializeComponent();
        }

        private async void OpenGitHubProfile_Click(object sender, Microsoft.UI.Xaml.RoutedEventArgs e)
        {
            await Launcher.LaunchUriAsync(new Uri(ViewModel.GitHubProfileUrl));
        }

        private async void OpenIssuesPage_Click(object sender, Microsoft.UI.Xaml.RoutedEventArgs e)
        {
            await Launcher.LaunchUriAsync(new Uri(ViewModel.RepositoryIssuesUrl));
        }
    }
}

