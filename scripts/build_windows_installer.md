# Build BeyondTheNakedEye Windows Installer

## Prerequisites
- Windows 10/11 build host
- Python 3.11+
- `pip install pyinstaller`
- Inno Setup 6 (`iscc` in PATH)

## Build
```powershell
# from repository root
pyinstaller --noconfirm --clean --onedir --name "BeyondTheNakedEye" -m beyond_naked_eye
iscc beyond_naked_eye\install\installer.iss
```

## Outputs
- `dist\BeyondTheNakedEye\BeyondTheNakedEye.exe`
- `beyond_naked_eye\install\Output\BeyondTheNakedEye_Setup.exe` (path depends on Inno defaults)
- Installed uninstaller: `C:\Program Files\Beyond The Naked Eye\unins000.exe` (user-facing BeyondTheNakedEye_Uninstaller.exe equivalent)
