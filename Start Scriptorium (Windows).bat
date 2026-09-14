@echo off
rem Starts Scriptorium, the Bible database reading room. Double-click this file.
rem The first run downloads about 350 MB and builds the database (a few minutes); later runs start right away.
title Scriptorium
cd /d "%~dp0"

set PY=
where py >nul 2>nul && set PY=py
if not defined PY where python >nul 2>nul && set PY=python
if not defined PY (
  echo.
  echo Python is needed to run Scriptorium, and it isn't installed yet.
  echo.
  echo 1. Go to https://www.python.org/downloads/ and download Python.
  echo 2. Run the installer and tick "Add python.exe to PATH" on the first screen.
  echo 3. Double-click this file again.
  echo.
  start "" https://www.python.org/downloads/
  pause
  exit /b 1
)

echo Checking what Scriptorium needs...
%PY% -m pip install --quiet --disable-pip-version-check -r requirements.txt
if errorlevel 1 (
  echo Could not install DuckDB. Check your internet connection and try again.
  pause
  exit /b 1
)

if not exist "bibledb\bible.duckdb" (
  echo.
  echo First run: downloading the Bible data ^(about 350 MB^). This can take several minutes.
  %PY% bibledb\download.py || goto failed
  echo.
  echo Building the database ^(about 2 minutes^)...
  %PY% bibledb\build.py || goto failed
)

echo.
echo Scriptorium is starting and will open in your browser.
echo Keep this window open while you use it. Close it to stop Scriptorium.
echo.
%PY% bibledb\scriptorium.py
pause
exit /b 0

:failed
echo.
echo Something went wrong. Check your internet connection, then double-click this file again;
echo it picks up where it left off.
pause
exit /b 1
