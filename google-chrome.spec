# NOTE
# - to look and update to new version, use update-source.sh script
#
# Conditional build:
%bcond_with	ffmpegsumo	# using ffmpegsumo

%define		state	stable
%if "%{state}" == "beta" || "%{state}" == "unstable"
%define		gcsuffix	-%{state}
%endif
Summary:	Google Chrome
Name:		google-chrome
Version:	61.0.3163.79
Release:	1
License:	Multiple, see http://chrome.google.com/
Group:		Applications/Networking
Source0:	http://dl.google.com/linux/chrome/rpm/stable/x86_64/%{name}-%{state}-%{version}-%{release}.x86_64.rpm
# NoSource0-md5:	b0e8d3a585ec2fc134947b474a935059
NoSource:	0
Source1:	%{name}.sh
Source2:	find-lang.sh
URL:		http://chrome.google.com/
BuildRequires:	rpm-utils
BuildRequires:	rpmbuild(macros) >= 1.453
BuildRequires:	sed >= 4.0
Requires:	browser-plugins >= 2.0
Requires:	cpuinfo(sse2)
# crashes if no fontconfig font present
Requires:	fonts-Type1-urw
Requires:	hicolor-icon-theme
# https://www.phoronix.com/scan.php?page=news_item&px=Google-Chrome-TSYNC-Kernel
Requires:	uname(release) >= 3.17
Requires:	xdg-utils >= 1.0.2-4
Provides:	wwwbrowser
ExclusiveArch:	 %{x8664}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%{expand:%%define	crver %{version}}

%define		find_lang 	sh find-lang.sh %{buildroot}

%define		_enable_debug_packages	0
%define		no_install_post_strip	1

%define		ffmpeg_caps	libffmpegsumo.so

# list of script capabilities (regexps) not to be used in Provides
%define		_noautoprov		%{ffmpeg_caps}
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

%prep
%setup -qcT
SOURCE=%{S:0}

V=$(rpm -qp --nodigest --nosignature --qf '%{V}' $SOURCE)
R=$(rpm -qp --nodigest --nosignature --qf '%{R}' $SOURCE)
if [ version:$V != version:%{crver} -o release:$R != release:%{release} ]; then
	exit 1
fi
rpm2cpio $SOURCE | cpio -i -d

mv opt/google/chrome%{?gcsuffix} .
mv usr/share/man/man1/* .
mv usr/share/gnome-control-center/default-apps .
mv chrome%{?gcsuffix}/default-app-block .
mv chrome%{?gcsuffix}/product_logo_*.{png,xpm} .
mv usr/share/applications/google-chrome%{?gcsuffix}.desktop .
mv chrome%{?gcsuffix}/google-chrome* .
chmod a+x chrome%{?gcsuffix}/lib*.so*

# included in gnome-control-center-2.28.1-3
rm default-app-block default-apps/google-chrome%{?gcsuffix}.xml

# xdg-utils snapshot required
rm chrome%{?gcsuffix}/xdg-settings
rm chrome%{?gcsuffix}/xdg-mime

[ -f *.1.gz ] && gzip -d *.1.gz

%{__sed} -e 's,@localedir@,%{_libdir}/%{name},' %{SOURCE2} > find-lang.sh
%{__sed} -i 's;/opt/google/chrome/product_logo_48.png;%{name}.png;' google-chrome%{?gcsuffix}.desktop
%{__sed} -i 's;/opt/google/chrome;%{_bindir};' google-chrome%{?gcsuffix}.desktop
%{__sed} -i 's;xhtml_xml;xhtml+xml;' google-chrome%{?gcsuffix}.desktop
%{__sed} -i 's#google-chrome-\(stable\|beta\|unstable\)#google-chrome#g' google-chrome%{?gcsuffix}.desktop

%build

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_libdir}/%{name}/plugins,%{_mandir}/man1,%{_desktopdir},%{_libdir}/%{name}/themes} \
	$RPM_BUILD_ROOT%{_datadir}/%{name}/extensions

install -p %{SOURCE1} $RPM_BUILD_ROOT%{_bindir}/%{name}
sed -i -e 's#RPM_STATE#%{state}#g' $RPM_BUILD_ROOT%{_bindir}/%{name}

%{__sed} -i -e 's,@libdir@,%{_libdir}/%{name},' $RPM_BUILD_ROOT%{_bindir}/%{name}
cp -a chrome%{?gcsuffix}/* $RPM_BUILD_ROOT%{_libdir}/%{name}
cp -p google-chrome%{?gcsuffix}.1 $RPM_BUILD_ROOT%{_mandir}/man1/google-chrome.1
# for google-chrome --help
echo ".so google-chrome.1" > $RPM_BUILD_ROOT%{_mandir}/man1/chrome.1
cp -p google-chrome%{?gcsuffix}.desktop $RPM_BUILD_ROOT%{_desktopdir}/google-chrome.desktop

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
# see if CHROME_DEVEL_SANDBOX env var helps
# content/browser/browser_main_loop.cc
ln -s %{_libdir}/%{name} $RPM_BUILD_ROOT/opt/google/chrome%{?gcsuffix}

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

%files
%defattr(644,root,root,755)

%{_browserpluginsconfdir}/browsers.d/%{name}.*
%config(noreplace) %verify(not md5 mtime size) %{_browserpluginsconfdir}/blacklist.d/%{name}.*.blacklist

%attr(755,root,root) %{_bindir}/%{name}
%{_mandir}/man1/*.1*
%{_desktopdir}/*.desktop
%{_iconsdir}/hicolor/*/apps/%{name}.png

%dir %{_libdir}/%{name}
%{_libdir}/%{name}/icudtl.dat
%{_libdir}/%{name}/chrome_*_percent.pak
%{_libdir}/%{name}/resources.pak
%{_libdir}/%{name}/natives_blob.bin
%{_libdir}/%{name}/snapshot_blob.bin
%dir %{_libdir}/%{name}/locales
%{_libdir}/%{name}/locales/en-US.pak
#%{_libdir}/%{name}/locales/fake-bidi.pak
%dir %{_libdir}/%{name}/plugins
%dir %{_datadir}/%{name}
# The path to the external extension <id>.json files.
# see https://chromium.googlesource.com/chromium/chromium/+/trunk/chrome/common/chrome_paths.cc
%dir %{_datadir}/%{name}/extensions
%{_libdir}/%{name}/default_apps
%{_libdir}/%{name}/themes
%attr(755,root,root) %{_libdir}/%{name}/chrome
# These unique permissions are intentional and necessary for the sandboxing
%attr(4555,root,root) %{_libdir}/%{name}/chrome-sandbox

# nacl
%attr(755,root,root) %{_libdir}/%{name}/nacl_helper
%attr(755,root,root) %{_libdir}/%{name}/nacl_helper_bootstrap
%attr(755,root,root) %{_libdir}/%{name}/nacl_irt_x86_*.nexe

# DRM
%attr(755,root,root) %{_libdir}/%{name}/libwidevinecdm.so
%attr(755,root,root) %{_libdir}/%{name}/libwidevinecdmadapter.so

# replace with mesa symlinks?
%dir %{_libdir}/%{name}/swiftshader
%attr(755,root,root) %{_libdir}/%{name}/swiftshader/libEGL.so
%attr(755,root,root) %{_libdir}/%{name}/swiftshader/libGLESv2.so

# ffmpeg libs
%if %{with ffmpegsumo}
%attr(755,root,root) %{_libdir}/%{name}/libffmpegsumo.so
%endif

# hack
%dir /opt/google
/opt/google/chrome%{?gcsuffix}

%files l10n -f %{name}.lang
%defattr(644,root,root,755)
