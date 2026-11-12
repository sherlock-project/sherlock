@echo off
where python >nul 2>nul
if errorlevel 1 (
    echo python is not on PATH >&2
    exit /b 1
)
python %*
