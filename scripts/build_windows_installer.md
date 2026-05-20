# Windows installer artifact

This repository builds a real Windows installer (`BeyondTheNakedEye_Setup.exe`) using Inno Setup.

## What you get

- `BeyondTheNakedEye_Setup.exe` (actual installer that installs app + shortcuts + uninstaller)
- `BeyondTheNakedEye_Setup.exe.sha256` (checksum)

## How to get the installer

1. Go to **Actions** in GitHub.
2. Run **Build Windows Installer** manually (or push a `v*` tag).
3. Open the workflow run and download artifact **beyond-the-naked-eye-installer**.
4. Extract ZIP and run `BeyondTheNakedEye_Setup.exe`.

## Download from Releases

When a GitHub Release is published, the **Release Windows Installer** workflow attaches both installer files to the release.

## SmartScreen / Defender blocking

If Windows blocks the installer, it is usually because it is unsigned.

Long-term fix:
- Add repository secrets `WINDOWS_CODESIGN_CERT_BASE64` and `WINDOWS_CODESIGN_CERT_PASSWORD`.
- Workflows will sign the installer automatically when secrets are present.
