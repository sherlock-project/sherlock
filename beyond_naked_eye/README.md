# Beyond The Naked Eye

Production-oriented terminal intelligence framework for lawful public OSINT correlation and safe local diagnostics.

## What You Get
- Terminal application (`BeyondTheNakedEye.exe`) for investigations and diagnostics.
- Windows installer (`BeyondTheNakedEye_Setup.exe`) with shortcuts/uninstall support.
- Portable package (`BeyondTheNakedEye_Portable.zip`) for no-install usage.

---

## Windows Quick Start (CMD Tutorial)

### 1) Install using the Setup EXE
1. Download `BeyondTheNakedEye_Setup.exe`.
2. Double-click it.
3. Follow installer steps:
   - Choose install folder
   - (Optional) Create Desktop shortcut
   - (Optional) Enable portable mode task
4. Finish setup.
5. Launch from Start Menu: **Beyond The Naked Eye**.

### 2) Run directly in Command Prompt (CMD)
After installation, open **Command Prompt** and run:

```cmd
cd "C:\Program Files\BeyondTheNakedEye"
BeyondTheNakedEye.exe
```

If app folder is in PATH, you can run directly:

```cmd
BeyondTheNakedEye.exe
```

### 3) Portable mode (no install)
1. Extract `BeyondTheNakedEye_Portable.zip`.
2. Open CMD in extracted folder.
3. Run:

```cmd
BeyondTheNakedEye.exe
```

---

## In-App Command Tutorial

Once running, use `help` to list commands.

### Core commands
```text
scan <type> <value>
agentscan <type> <value>
monitor <type> <value>
note <text>
tag <value>
filter <term>
save <name>
load <name>
export <name> <json|txt|csv|html>
graph <name>
analyze url <url>
analyze file <path>
analyze image <path>
analyze executable <path>
analyze source <path>
analyze archive <path>
analyze export <output.json>
clear
help
quit
```

Safety: analysis intake is explicit-user-input only, static/local by default, and does not execute uploaded binaries.

### Diagnostics commands
```text
system status
network status
device info
diagnostics run [--lan]
```

### Example CMD session
```cmd
BeyondTheNakedEye.exe
```
Then inside app:
```text
scan username johndoe
scan email johndoe@example.com
system status
network status
save case_alpha
export case_alpha html
graph case_alpha
quit
```

---

## Build Commands (for developers)

### Build main EXE with PyInstaller
```bash
pyinstaller --onefile --name "BeyondTheNakedEye" -m beyond_naked_eye
```

### Build Setup EXE with Inno Setup
1. Build main EXE first.
2. Open `beyond_naked_eye/install/installer.iss` in Inno Setup Compiler.
3. Compile script.
4. Output: `BeyondTheNakedEye_Setup.exe`.

---

## Architecture
- `/modules` core OSINT scanners and adapters
- `/sources` public OSINT sources
- `/diagnostics` safe local diagnostics
- `/graph` relationship graph engine
- `/exports` report generation
- `/install` installer scripts (Inno Setup/NSIS-ready)
- `/ui` terminal interface components
- `/themes/retro_crt` default monochrome CRT theme engine
- `/legacy_ui` archived neon cyberpunk interface (disabled by default)
- `/core` async task manager and caching layer

---

## Legal / Ethical Use
Public OSINT only. No credential theft, unauthorized access, malware behavior, or phishing.
