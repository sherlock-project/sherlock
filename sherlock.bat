@echo off
setlocal EnableDelayedExpansion

:: -------------------------------------------------------------
:: Sherlock Launcher for Windows
:: -------------------------------------------------------------

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: Locate Sherlock executable or Python environment
if exist "%SCRIPT_DIR%venv\Scripts\sherlock.exe" (
    set "RUNNER=%SCRIPT_DIR%venv\Scripts\sherlock.exe"
) else if exist "%SCRIPT_DIR%venv\Scripts\python.exe" (
    set "RUNNER=%SCRIPT_DIR%venv\Scripts\python.exe -m sherlock_project"
) else (
    where python >nul 2>nul
    if %errorlevel% equ 0 (
        set "RUNNER=python -m sherlock_project"
    ) else (
        echo [ERROR] Python was not found on your system!
        echo Please install Python 3.9+ or run this from a configured environment.
        pause
        exit /b 1
    )
)

:: If arguments were passed via command line, run directly
if not "%~1"=="" (
    call %RUNNER% %*
    exit /b %errorlevel%
)

:: Interactive mode when double-clicked or run with no arguments
:MENU
cls
echo ============================================================
echo                     SHERLOCK LAUNCHER                      
echo         Hunt down social media accounts by username         
echo ============================================================
echo.

set /p "TARGET_USER=Enter username(s) to search (or 'q' to quit): "

if not defined TARGET_USER (
    echo [!] No username entered.
    goto MENU
)

if /i "%TARGET_USER%"=="q" exit /b 0
if /i "%TARGET_USER%"=="exit" exit /b 0
if /i "%TARGET_USER%"=="quit" exit /b 0

echo.
echo Optional flags:
echo   1. Standard search (default)
echo   2. Save to CSV file (--csv)
echo   3. Save to Excel spreadsheet (--xlsx)
echo   4. Show only found accounts (--print-found)
echo   5. Include NSFW sites (--nsfw)
echo   6. Custom arguments
echo.
set /p "FLAG_CHOICE=Select an option [1-6, default=1]: "

set "EXTRA_FLAGS="
if "%FLAG_CHOICE%"=="2" set "EXTRA_FLAGS=--csv"
if "%FLAG_CHOICE%"=="3" set "EXTRA_FLAGS=--xlsx"
if "%FLAG_CHOICE%"=="4" set "EXTRA_FLAGS=--print-found"
if "%FLAG_CHOICE%"=="5" set "EXTRA_FLAGS=--nsfw"
if "%FLAG_CHOICE%"=="6" (
    set /p "EXTRA_FLAGS=Enter custom flags (e.g. --csv --print-found --timeout 30): "
)

echo.
echo [*] Running Sherlock for: %TARGET_USER% %EXTRA_FLAGS%
echo.
call %RUNNER% %TARGET_USER% %EXTRA_FLAGS%

echo.
echo ============================================================
echo Search finished!
echo Results (if any) are saved in the current folder.
echo ============================================================
echo.
pause
