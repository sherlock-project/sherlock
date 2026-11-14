@echo off
chcp 65001 >nul
REM Chay giao dien web cua Sherlock: nhap dup file nay
cd /d "%~dp0"

set PY=
where py >nul 2>nul && set PY=py -3
if not defined PY where python >nul 2>nul && set PY=python
if not defined PY (
  echo Khong tim thay Python. Hay cai Python 3.9+ tu https://www.python.org/downloads/
  echo Khi cai nho tick "Add python.exe to PATH".
  pause
  exit /b 1
)

if not exist .venv\Scripts\python.exe (
  echo Lan dau chay: dang tao moi truong va cai thu vien...
  %PY% -m venv .venv || goto :fail
  .venv\Scripts\python.exe -m pip install -q --upgrade pip
  .venv\Scripts\python.exe -m pip install -q -e . || goto :fail
)

.venv\Scripts\python.exe web\server.py --open %*
pause
exit /b 0

:fail
echo Cai dat that bai. Xem thong bao loi o tren.
pause
exit /b 1
