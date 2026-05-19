# Windows installer artifact

This repository now includes GitHub Actions workflows that build a standalone Windows `.exe` installer-style launcher and publish it to Releases.

## How to get the EXE

1. Go to **Actions** in GitHub.
2. Run **Build Windows Installer** manually (or push a `v*` tag).
3. Open the workflow run and download the artifact named **sherlock-installer-exe**.
4. Extract the ZIP and run `sherlock-installer.exe`.

> Note: GitHub's default "Download ZIP" for source code does **not** include compiled binaries. The `.exe` comes from the workflow artifact.


## Download from Releases

When a GitHub Release is published, the **Release Windows Installer** workflow automatically builds and attaches `sherlock-installer.exe` to that release.
