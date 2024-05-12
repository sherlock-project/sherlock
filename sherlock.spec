# Package maintained by Paul Pfeister <rh-bugzilla@pfeister.dev> (GitHub @ppfeister)
%global source_ref master
%global friendly_name sherlock
%global pkg_version 0.14.4
%global pkg_build 1

Name:           python-%{friendly_name}
Version:        %{pkg_version}
Release:        %{pkg_build}%{?dist}
Summary:        Hunt down social media accounts by username across social networks

License:        MIT
URL:            http://sherlock-project.github.io/
Source0:        https://github.com/sherlock-project/sherlock/archive/%{source_ref}.tar.gz
BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  python3dist(certifi) >= 2019.6.16
BuildRequires:  python3dist(colorama) >= 0.4.1
BuildRequires:  python3dist(exrex) >= 0.11
BuildRequires:  python3dist(openpyxl) >= 3.0.10
BuildRequires:  python3dist(pandas) >= 1
BuildRequires:  python3dist(pysocks) >= 1.7
BuildRequires:  python3dist(requests) >= 2.22
BuildRequires:  python3dist(requests-futures) >= 1
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(stem) >= 1.8
BuildRequires:  python3dist(torrequest) >= 0.1

%description
Hunt down social media accounts by username across social networks

%package -n     python3-%{friendly_name}
Summary:        %{summary}
%{?python_provide:%python_provide python3-%{pypi_name}}

Requires:       python3dist(certifi) >= 2019.6.16
Requires:       python3dist(colorama) >= 0.4.1
Requires:       python3dist(exrex) >= 0.11
Requires:       python3dist(openpyxl) >= 3.0.10
Requires:       python3dist(pandas) >= 1
Requires:       python3dist(pysocks) >= 1.7
Requires:       python3dist(requests) >= 2.22
Requires:       python3dist(requests-futures) >= 1
Requires:       python3dist(setuptools)
Requires:       python3dist(stem) >= 1.8
Requires:       python3dist(torrequest) >= 0.1
%description -n python3-%{friendly_name}
Hunt down social media accounts by username across social networks


%prep
%autosetup -n sherlock-%{source_ref}

%build
%py3_build

%install
%py3_install

%check
cd sherlock
%{python3} -m unittest tests.all --verbose
cd ..

%files -n python3-%{friendly_name}
%license LICENSE
%doc README.md
%{_bindir}/sherlock
%{python3_sitelib}/__init__.py
%{python3_sitelib}/__main__.py
%{python3_sitelib}/__pycache__/*
%{python3_sitelib}/notify.py
%{python3_sitelib}/result.py
%{python3_sitelib}/sherlock.py
%{python3_sitelib}/sites.py
%{python3_sitelib}/resources
%{python3_sitelib}/tests
%{python3_sitelib}/Sherlock.egg-info

%changelog
* Sun May 12 2024 Paul Pfeister - 0.14.4
- Initial package.
