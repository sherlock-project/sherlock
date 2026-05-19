# Installer Pipeline

## Outputs
- `BeyondTheNakedEye.exe` (main app via PyInstaller)
- `BeyondTheNakedEye_Setup.exe` (installer wrapper)
- `BeyondTheNakedEye_Portable.zip`

## Build executable
```bash
pyinstaller --onefile --name "BeyondTheNakedEye" -m beyond_naked_eye
```

## Inno Setup flow (recommended)
1. Build executable.
2. Use `installer.iss` to package setup with shortcuts and uninstaller.
3. Enable first-run wizard in setup tasks.

## NSIS flow (alternative)
- Use an NSIS script to package the same executable and add Start Menu/Desktop entries.

This folder stores packaging manifests only; no invasive behavior is included.
