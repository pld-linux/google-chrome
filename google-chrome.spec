# NOTE
# - to look and update to new version, use update-source.sh script

%define		svnrev	124982
%define		state	stable
%define		rel		1
Summary:	Google Chrome
Name:		google-chrome
Version:	17.0.963.66
Release:	%{svnrev}.%{rel}
License:	Multiple, see http://chrome.google.com/
Group:		Applications/Networking
Source0:	http://dl.google.com/linux/chrome/rpm/stable/i386/%{name}-%{state}-%{version}-%{svnrev}.i386.rpm
# Source0-md5:	28d798109ad9d2e0b5eddedd17996132
Source1:	http://dl.google.com/linux/chrome/rpm/stable/x86_64/%{name}-%{state}-%{version}-%{svnrev}.x86_64.rpm
# Source1-md5:	388db19d984d7cfabac98ec2364b6d42
Source2:	%{name}.sh
Source4:	find-lang.sh
Patch0:		chrome-desktop.patch
URL:		http://chrome.google.com/
BuildRequires:	rpm-utils
BuildRequires:	rpmbuild(macros) >= 1.453
BuildRequires:	sed >= 4.0
Requires:	browser-plugins >= 2.0
Requires:	hicolor-icon-theme
Requires:	xdg-utils >= 1.0.2-4
Provides:	wwwbrowser
ExclusiveArch:	%{ix86} %{x8664}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		find_lang 	sh find-lang.sh %{buildroot}

%define		_enable_debug_packages	0
%define		no_install_post_strip	1

%define		ffmpeg_caps	libffmpegsumo.so
%define		jpeg_caps	libpng12.so.0(PNG12_0)
%define		flash_caps	libflashplayer.so
%define		chrome_caps	libpdf.so libppGoogleNaClPluginChrome.so

# list of script capabilities (regexps) not to be used in Provides
%define		_noautoprov		%{ffmpeg_caps} %{jpeg_caps} %{flash_caps} %{chrome_caps}
# do not require them either
%define		_noautoreq		%{_noautoprov}

%description
The web browser from Google

Google Chrome is a browser that combines a minimal design with
sophisticated technology to make the web faster, safer, and easier.

%description -l hu.UTF-8
Webböngésző a Google-től.

Google Chrome egy böngésző, amely a minimalista külsőt házasítja össze
a kifinomult technológiával, hogy a webböngészés gyorsabb,
biztonságosabb és könnyebb legyen.

%prep
%setup -qcT
%ifarch %{ix86}
SOURCE=%{S:0}
%endif
%ifarch %{x8664}
SOURCE=%{S:1}
%endif

V=$(rpm -qp --nodigest --nosignature --qf '%{V}' $SOURCE)
R=$(rpm -qp --nodigest --nosignature --qf '%{R}' $SOURCE)
if [ version:$V != version:%{version} -o svnrev:$R != svnrev:%{svnrev} ]; then
	exit 1
fi
rpm2cpio $SOURCE | cpio -i -d

mv opt/google/chrome .
mv usr/share/man/man1/* .
mv usr/share/gnome-control-center/default-apps .
mv chrome/default-app-block .
mv chrome/product_logo_*.{png,xpm} .
mv chrome/google-chrome.desktop .
mv chrome/google-chrome .
chmod a+x chrome/lib*.so*

# included in gnome-control-center-2.28.1-3
rm default-app-block default-apps/google-chrome.xml

# xdg-utils snapshot required
rm chrome/xdg-settings
rm chrome/xdg-mime

[ -f *.1.gz ] && gzip -d *.1.gz

%patch0 -p1

%{__sed} -e 's,@localedir@,%{_libdir}/%{name},' %{SOURCE4} > find-lang.sh
%{__sed} -i 's;/opt/google/chrome/product_logo_48.png;%{name}.png;' google-chrome.desktop
%{__sed} -i 's;/opt/google/chrome;%{_bindir};' google-chrome.desktop

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_libdir}/%{name}/plugins,%{_mandir}/man1,%{_desktopdir},%{_libdir}/%{name}/themes}

install -p %{SOURCE2} $RPM_BUILD_ROOT%{_bindir}/%{name}
%{__sed} -i -e 's,@libdir@,%{_libdir}/%{name},' $RPM_BUILD_ROOT%{_bindir}/%{name}
cp -a chrome/* $RPM_BUILD_ROOT%{_libdir}/%{name}
cp -p google-chrome.1 $RPM_BUILD_ROOT%{_mandir}/man1
# for google-chrome --help
echo ".so google-chrome.1" > $RPM_BUILD_ROOT%{_mandir}/man1/chrome.1
cp -p google-chrome.desktop $RPM_BUILD_ROOT%{_desktopdir}

for icon in product_logo_*.png; do
	size=${icon##product_logo_}
	size=${size%.png}

	install -d $RPM_BUILD_ROOT%{_iconsdir}/hicolor/${size}x${size}/apps
	cp -p $icon $RPM_BUILD_ROOT%{_iconsdir}/hicolor/${size}x${size}/apps/%{name}.png
done

%browser_plugins_add_browser %{name} -p %{_libdir}/%{name}/plugins

# binary needs to be at that specific location, or it will abort:
# [1070:1070:3265429789299:FATAL:zygote_host_linux.cc(130)] The SUID sandbox helper binary is missing: /opt/google/chrome/chrome-sandbox Aborting now.
# Aborted
install -d $RPM_BUILD_ROOT/opt/google
ln -s %{_libdir}/%{name} $RPM_BUILD_ROOT/opt/google/chrome

# find locales
%find_lang %{name}.lang

%clean
rm -rf $RPM_BUILD_ROOT

%post
%update_icon_cache hicolor
%update_browser_plugins

%postun
if [ "$1" = 0 ]; then
	%update_icon_cache hicolor
	%update_browser_plugins
fi

%files -f %{name}.lang
%defattr(644,root,root,755)

%{_browserpluginsconfdir}/browsers.d/%{name}.*
%config(noreplace) %verify(not md5 mtime size) %{_browserpluginsconfdir}/blacklist.d/%{name}.*.blacklist

%attr(755,root,root) %{_bindir}/%{name}
%{_mandir}/man1/*.1*
%{_desktopdir}/*.desktop
%{_iconsdir}/hicolor/*/apps/%{name}.png

%dir %{_libdir}/%{name}
%{_libdir}/%{name}/chrome.pak
%{_libdir}/%{name}/resources.pak
%dir %{_libdir}/%{name}/locales
%dir %{_libdir}/%{name}/plugins
%{_libdir}/%{name}/default_apps
%{_libdir}/%{name}/themes
%attr(755,root,root) %{_libdir}/%{name}/chrome
# These unique permissions are intentional and necessary for the sandboxing
%attr(4555,root,root) %{_libdir}/%{name}/chrome-sandbox

# Native Client plugin, to use launch with --enable-nacl
%attr(755,root,root) %{_libdir}/%{name}/libppGoogleNaClPluginChrome.so

%attr(755,root,root) %{_libdir}/%{name}/libpdf.so

%ifarch %{ix86}
# flash player
%{_libdir}/%{name}/plugin.vch
%attr(755,root,root) %{_libdir}/%{name}/libgcflashplayer.so
%endif

# nacl
%attr(755,root,root) %{_libdir}/%{name}/nacl_helper
%attr(755,root,root) %{_libdir}/%{name}/nacl_helper_bootstrap
%attr(755,root,root) %{_libdir}/%{name}/nacl_irt_x86_*.nexe

# ffmpeg libs
%attr(755,root,root) %{_libdir}/%{name}/libffmpegsumo.so

# hack
%dir /opt/google
/opt/google/chrome
