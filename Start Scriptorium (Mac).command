#!/bin/bash
# Starts Scriptorium, the Bible database reading room. Double-click this file.
# The first run downloads about 350 MB and builds the database (a few minutes); later runs start right away.
cd "$(dirname "$0")" || exit 1

if command -v python3 >/dev/null 2>&1; then PY=python3
elif command -v python >/dev/null 2>&1; then PY=python
else
  echo
  echo "Python is needed to run Scriptorium, and it isn't installed yet."
  echo "1. Go to https://www.python.org/downloads/ and install Python."
  echo "2. Double-click this file again."
  open "https://www.python.org/downloads/" 2>/dev/null
  read -r -p "Press Enter to close."
  exit 1
fi

echo "Checking what Scriptorium needs..."
"$PY" -m pip install --quiet --disable-pip-version-check -r requirements.txt || {
  echo "Could not install DuckDB. Check your internet connection and try again."; read -r -p "Press Enter to close."; exit 1; }

if [ ! -f bibledb/bible.duckdb ]; then
  echo
  echo "First run: downloading the Bible data (about 350 MB). This can take several minutes."
  "$PY" bibledb/download.py && echo "Building the database (about 2 minutes)..." && "$PY" bibledb/build.py || {
    echo "Something went wrong. Check your internet connection, then double-click this file again."; read -r -p "Press Enter to close."; exit 1; }
fi

echo
echo "Scriptorium is starting and will open in your browser."
echo "Keep this window open while you use it. Close it to stop Scriptorium."
"$PY" bibledb/scriptorium.py
