// Copyright (c) Microsoft Corporation & Powertool Contributors
// The Microsoft Corporation licenses this file to you under the MIT license.
// See the LICENSE file in the project root for more information.

using System;
using Microsoft.PowerToys.Settings.UI.Helpers;

namespace Microsoft.PowerToys.Settings.UI.ViewModels
{
    public partial class DeveloperViewModel : Observable
    {
        public string DeveloperName => "En-Dhiaa";
        public string GitHubProfileUrl => "https://github.com/En-Dhiaa";
        public string RepositoryIssuesUrl => "https://github.com/En-Dhiaa/PowerToys/issues/new/choose";
        public string RepositoryUrl => "https://github.com/En-Dhiaa/PowerToys";
        public string AppVersion => Helper.GetProductVersion();

        public string EditionDescription =>
            "Powertool Extended Edition is an enhanced Windows & Linux productivity suite developed independently by En-Dhiaa, based on Microsoft PowerToys. It introduces offline Arabic/English translation, physical-key Arabic/English layout correction, and a refreshed visual identity while preserving all original upstream utilities.";

        public string AttributionNotice =>
            "This is an independently maintained community edition. PowerToys and its original utilities are Copyright (C) Microsoft Corporation under the MIT License. Argos Translate and CTranslate2 models are licensed under MIT and Open Data Commons.";

        public DeveloperViewModel()
        {
        }
    }
}

