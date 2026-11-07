Name:           powertool
Version:        0.88.0
Release:        1%{?dist}
Summary:        Powertool Extended Edition - Offline Translator and Keyboard Layout Converter

License:        MIT
URL:            https://github.com/En-Dhiaa
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch

Requires:       python3 >= 3.9
Requires:       python3-pyside6
Requires:       wl-clipboard

%description
Powertool Extended Edition is an enhanced productivity suite developed by En-Dhiaa.
It features offline Arabic/English translation via CTranslate2 and physical keyboard layout conversion.

%prep
%autosetup

%build
# Python pure package

%install
mkdir -p %{buildroot}/usr/share/powertool
mkdir -p %{buildroot}/usr/bin
mkdir -p %{buildroot}/usr/share/applications
mkdir -p %{buildroot}/usr/share/metainfo
mkdir -p %{buildroot}/usr/share/icons/hicolor/scalable/apps

install -m 755 linux/powertool-linux.py %{buildroot}/usr/share/powertool/
install -m 644 linux/powertool.desktop %{buildroot}/usr/share/applications/
install -m 644 linux/org.endhiaa.Powertool.metainfo.xml %{buildroot}/usr/share/metainfo/
ln -s /usr/share/powertool/powertool-linux.py %{buildroot}/usr/bin/powertool

%files
/usr/bin/powertool
/usr/share/powertool/*
/usr/share/applications/powertool.desktop
/usr/share/metainfo/org.endhiaa.Powertool.metainfo.xml

%changelog
* Sat Nov 07 2026 En-Dhiaa <en-dhiaa@users.noreply.github.com> - 0.88.0-1
- Initial release of Powertool Extended Edition
