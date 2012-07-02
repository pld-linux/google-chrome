# NOTE
# - to look and update to new version, use update-source.sh script

%define		flashv	11.3.31.109
%define		svnrev	144678
#define		rel		%{nil}
%define		state	stable
Summary:	Google Chrome
Name:		google-chrome
Version:	20.0.1132.47
Release:	%{svnrev}%{?rel:.%{rel}}
License:	Multiple, see http://chrome.google.com/
Group:		Applications/Networking
Source0:	http://dl.google.com/linux/chrome/rpm/%{state}/i386/%{name}-%{state}-%{version}-%{svnrev}.i386.rpm
# NoSource0-md5:	2019a1388056b8bf5f7349cdfa0af9f2
NoSource:	0
Source1:	http://dl.google.com/linux/chrome/rpm/%{state}/x86_64/%{name}-%{state}-%{version}-%{svnrev}.x86_64.rpm
# NoSource1-md5:	3569ed25382cf39c81f1b138bafd7485
NoSource:	1
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
Suggests:	browser-plugin-adobe-flash
Suggests:	browser-plugin-chrome-pdf
Provides:	wwwbrowser
ExclusiveArch:	%{ix86} %{x8664}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%{expand:%%define	crver %{version}}

%define		find_lang 	sh find-lang.sh %{buildroot}

%define		_enable_debug_packages	0
%define		no_install_post_strip	1

%define		ffmpeg_caps	libffmpegsumo.so
%define		flash_caps	libpepflashplayer.so
%define		chrome_caps	libpdf.so libppGoogleNaClPluginChrome.so

# list of script capabilities (regexps) not to be used in Provides
%define		_noautoprov		%{ffmpeg_caps} %{flash_caps} %{chrome_caps}
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

%package l10n
Summary:	google chrome language packages
Group:		I18n
Requires:	%{name} = %{version}-%{release}

%description l10n
This package contains language packages for 50 languages:

ar, bg, bn, ca, cs, da, de, el, en-GB, es-LA, es, et, fi, fil, fr, gu,
he, hi, hr, hu, id, it, ja, kn, ko, lt, lv, ml, mr, nb, nl, or, pl,
pt-BR, pt-PT, ro, ru, sk, sl, sr, sv, ta, te, th, tr, uk, vi, zh-CN,
zh-TW

%package -n browser-plugin-chrome-pdf
Summary:	Chrome PDF Viewer
Summary(pl.UTF-8):	Wtyczka PDF z Google Chrome
Group:		X11/Applications/Graphics
Requires:	browser-plugins >= 2.0
Conflicts:	google-chrome < 16.0.912.75

%description -n browser-plugin-chrome-pdf
Google Chrome PDF Viewer.

%description -n browser-plugin-chrome-pdf -l pl.UTF-8
Wtyczka PDF z Google Chrome.

# IMPORTANT: keep flash plugin defined as last package
%package -n browser-plugin-adobe-flash
Summary:	Adobe Flash plugin from Google Chrome
Summary(pl.UTF-8):	Wtyczka Adobe Flash z Google Chrome
Version:	%{flashv}
Release:	%{!?rel:1}%{?rel:%{rel}}
License:	Free to use, non-distributable
Group:		X11/Applications/Multimedia
Requires:	browser-plugins >= 2.0
Conflicts:	google-chrome < 16.0.912.75

%description -n browser-plugin-adobe-flash
Adobe Flash plugin from Google Chrome, which is not available in
Chromium.

%description -n browser-plugin-adobe-flash -l pl.UTF-8
Wtyczka Adobe Flash z Google Chrome, która nie jest dostępna w
Chromium.

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
if [ version:$V != version:%{crver} -o svnrev:$R != svnrev:%{svnrev} ]; then
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

# separate to subpackage
install -d browser-plugins
mv chrome/libpdf.so browser-plugins
mv chrome/PepperFlash browser-plugins
chmod a+rx browser-plugins/PepperFlash/*.so

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

%build
v=$(awk -F'"' '/version/{print $4}' browser-plugins/PepperFlash/manifest.json)
if [ "$v" != "%{flashv}" ]; then
	: wrong version
	exit 1
fi

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

install -d $RPM_BUILD_ROOT%{_browserpluginsdir}
cp -a browser-plugins/* $RPM_BUILD_ROOT%{_browserpluginsdir}

%browser_plugins_add_browser %{name} -p %{_libdir}/%{name}/plugins

# binary needs to be at that specific location, or it will abort:
# [1070:1070:3265429789299:FATAL:zygote_host_linux.cc(130)] The SUID sandbox helper binary is missing: /opt/google/chrome/chrome-sandbox Aborting now.
# Aborted
install -d $RPM_BUILD_ROOT/opt/google
ln -s %{_libdir}/%{name} $RPM_BUILD_ROOT/opt/google/chrome

# find locales
%find_lang %{name}.lang
# always package en-US (in main package)
%{__sed} -i -e '/en-US.pak/d' %{name}.lang

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

%post -n browser-plugin-adobe-flash
%update_browser_plugins

%postun -n browser-plugin-adobe-flash
if [ "$1" = 0 ]; then
	%update_browser_plugins
fi

%post -n browser-plugin-chrome-pdf
%update_browser_plugins

%postun -n browser-plugin-chrome-pdf
if [ "$1" = 0 ]; then
	%update_browser_plugins
fi

# FIXME: chrome *needs* it to be in application dir. add symlink until it can load from other places
# for chromium, we could likely patch source
# FIXME: link PepperFlash, browser-plugins ignores subdirs, and currently nothing else than chrome browsers can do pepper
%triggerin -n browser-plugin-adobe-flash -- google-chrome
test -L %{_libdir}/google-chrome/PepperFlash || ln -sf %{_browserpluginsdir}/PepperFlash %{_libdir}/google-chrome/PepperFlash

%triggerun -n browser-plugin-adobe-flash -- google-chrome
if [ "$1" = "0" ] || [ "$2" = "0" ] && [ -L %{_libdir}/google-chrome/PepperFlash ]; then
	rm -f %{_libdir}/google-chrome/PepperFlash
fi

%triggerin -n browser-plugin-chrome-pdf -- google-chrome
test -L %{_libdir}/google-chrome/libpdf.so || ln -sf plugins/libpdf.so %{_libdir}/google-chrome/libpdf.so

%triggerun -n browser-plugin-chrome-pdf -- google-chrome
if [ "$1" = "0" ] || [ "$2" = "0" ] && [ -L %{_libdir}/google-chrome/libpdf.so ]; then
	rm -f %{_libdir}/google-chrome/libpdf.so
fi

%triggerin -n browser-plugin-adobe-flash -- chromium-browser
test -L %{_libdir}/chromium-browser/PepperFlash || ln -sf %{_browserpluginsdir}/PepperFlash %{_libdir}/chromium-browser/PepperFlash

%triggerun -n browser-plugin-adobe-flash -- chromium-browser
if [ "$1" = "0" ] || [ "$2" = "0" ] && [ -L %{_libdir}/chromium-browser/PepperFlash ]; then
	rm -f %{_libdir}/chromium-browser/PepperFlash
fi

%triggerin -n browser-plugin-chrome-pdf -- chromium-browser
test -L %{_libdir}/chromium-browser/libpdf.so || ln -sf plugins/libpdf.so %{_libdir}/chromium-browser/libpdf.so

%triggerun -n browser-plugin-chrome-pdf -- chromium-browser
if [ "$1" = "0" ] || [ "$2" = "0" ] && [ -L %{_libdir}/chromium-browser/libpdf.so ]; then
	rm -f %{_libdir}/chromium-browser/libpdf.so
fi

%triggerin -n browser-plugin-adobe-flash -- chromium-browser-bin
test -L %{_libdir}/chromium-browser-bin/PepperFlash || ln -sf %{_browserpluginsdir}/PepperFlash %{_libdir}/chromium-browser-bin/PepperFlash

%triggerun -n browser-plugin-adobe-flash -- chromium-browser-bin
if [ "$1" = "0" ] || [ "$2" = "0" ] && [ -L %{_libdir}/chromium-browser-bin/PepperFlash ]; then
	rm -f %{_libdir}/chromium-browser-bin/PepperFlash
fi

%triggerin -n browser-plugin-chrome-pdf -- chromium-browser-bin
test -L %{_libdir}/chromium-browser-bin/libpdf.so || ln -sf plugins/libpdf.so %{_libdir}/chromium-browser-bin/libpdf.so

%triggerun -n browser-plugin-chrome-pdf -- chromium-browser-bin
if [ "$1" = "0" ] || [ "$2" = "0" ] && [-L %{_libdir}/chromium-browser-bin/libpdf.so ]; then
	rm -f %{_libdir}/chromium-browser-bin/libpdf.so
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
%{_libdir}/%{name}/theme_resources_standard.pak
%{_libdir}/%{name}/ui_resources_standard.pak
%dir %{_libdir}/%{name}/locales
%{_libdir}/%{name}/locales/en-US.pak
%dir %{_libdir}/%{name}/plugins
%{_libdir}/%{name}/default_apps
%{_libdir}/%{name}/themes
%attr(755,root,root) %{_libdir}/%{name}/chrome
# These unique permissions are intentional and necessary for the sandboxing
%attr(4555,root,root) %{_libdir}/%{name}/chrome-sandbox

# Native Client plugin, to use launch with --enable-nacl
%attr(755,root,root) %{_libdir}/%{name}/libppGoogleNaClPluginChrome.so

# nacl
%attr(755,root,root) %{_libdir}/%{name}/nacl_helper
%attr(755,root,root) %{_libdir}/%{name}/nacl_helper_bootstrap
%attr(755,root,root) %{_libdir}/%{name}/nacl_irt_x86_*.nexe

# ffmpeg libs
%attr(755,root,root) %{_libdir}/%{name}/libffmpegsumo.so

# hack
%dir /opt/google
/opt/google/chrome

%files l10n -f %{name}.lang
%defattr(644,root,root,755)

%files -n browser-plugin-chrome-pdf
%defattr(644,root,root,755)
%attr(755,root,root) %{_browserpluginsdir}/libpdf.so

%files -n browser-plugin-adobe-flash
%defattr(644,root,root,755)
%dir %{_browserpluginsdir}/PepperFlash
%{_browserpluginsdir}/PepperFlash/manifest.json
%attr(755,root,root) %{_browserpluginsdir}/PepperFlash/libpepflashplayer.so
