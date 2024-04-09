%global commit          70e03572b254688b8c3557f898e7ebd765d29ae1
%global checkout_date   20240406
%global short_commit    %(c=%{commit}; echo ${c:0:7})
%global snapshot        .%{checkout_date}git%{short_commit}

Name:       vlmcsd
Version:    0
Release:    2.0%{?snapshot}%{?dist}
Summary:    KMS Emulator in C

License:    AS-IS
URL:        https://github.com/Wind4/%{name}/
Source0:    https://github.com/Wind4/%{name}/archive/%{commit}/%{name}-%{commit}.tar.gz

Source1:    vlmcsd
Source2:    vlmcsd.service
Source3:    vlmcsd.xml

Patch0: 0001-Updated-vlmcsd.kmd.patch

BuildRequires:  gcc
BuildRequires:  git
BuildRequires:  make
BuildRequires:  systemd-rpm-macros
BuildRequires:  firewall-macros

Requires(pre):  shadow-utils


%description
KMS Emulator in C.


%prep
%setup -q -D -T -b0 -n %{name}-%{commit}

git config --global user.email "rpmbuild@example.org"
git config --global user.name "rpmbuild"
git init
git add .
git commit -m "import"
git am %{PATCH0}


%build
%{make_build} STRIP=0 VERBOSE=1 THREADS=1 FEATURES=full

sed -i \
        "s,^\s*;\s*KmsData\s*=.*$,KmsData=%{_datarootdir}/%{name}/vlmcsd.kmd," \
        etc/vlmcsd.ini


%install
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datarootdir}/%{name}
mkdir -p %{buildroot}%{_sysconfdir}/%{name}
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
mkdir -p %{buildroot}/%{_unitdir}
mkdir -p %{buildroot}%{_usr}/lib/firewalld/services

mv bin/* %{buildroot}%{_bindir}/
mv etc/vlmcsd.kmd %{buildroot}%{_datarootdir}/%{name}/
mv etc/* %{buildroot}%{_sysconfdir}/%{name}/
cp %{SOURCE1} %{buildroot}%{_sysconfdir}/sysconfig/
cp %{SOURCE2} %{buildroot}/%{_unitdir}/
cp %{SOURCE3} %{buildroot}%{_usr}/lib/firewalld/services/

for i in man/*.*; do \
    n=$( echo "${i}" | sed -nE "s,^.*\.([0-9]+)$,\1,p" ); \
    mkdir -p "%{buildroot}%{_mandir}/man${n}"; \
    cp "${i}" "%{buildroot}%{_mandir}/man${n}/"; \
done
# Do not install man files for missing binaries.
rm %{buildroot}%{_mandir}/man1/vlmcsdmulti.1
rm %{buildroot}%{_mandir}/man7/vlmcsd-floppy.7


%files
%dir %{_datarootdir}/%{name}
%dir %{_sysconfdir}/%{name}
%{_bindir}/vlmcs
%{_bindir}/vlmcsd
%{_datarootdir}/%{name}/vlmcsd.kmd
%config(noreplace) %{_sysconfdir}/%{name}/vlmcsd.ini
%config(noreplace) %{_sysconfdir}/sysconfig/vlmcsd
%{_unitdir}/%{name}.service
%{_usr}/lib/firewalld/services/%{name}.xml
%doc %{_mandir}/man1/vlmcs.1*
%doc %{_mandir}/man5/vlmcsd.ini.5*
%doc %{_mandir}/man7/vlmcsd.7*
%doc %{_mandir}/man8/vlmcsd.8*


%pre
getent group %{name} >/dev/null || groupadd -r %{name}
getent passwd %{name} >/dev/null || \
        useradd -r -s /sbin/nologin -d %{_datarootdir}/%{name} -M \
        -c '%{name}' -g %{name} %{name}
exit 0


%post
%systemd_post %{name}.service
%firewalld_reload


%preun
%systemd_preun %{name}.service


%postun
%systemd_postun_with_restart %{name}.service


%changelog
* Tue Apr 9 2024 Ivan Mironov <mironov.ivan@gmail.com> - 0-2.0.20240406git70e0357
- Fix firewalld service file detection after package install/update

* Mon Apr 8 2024 Ivan Mironov <mironov.ivan@gmail.com> - 0-1.0.20240406git70e0357
- Fix firewalld service file

* Sat Apr 6 2024 Ivan Mironov <mironov.ivan@gmail.com> - 0-0.0.20240406git70e0357
- Initial packaging
