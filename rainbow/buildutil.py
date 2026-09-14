"""Shared helpers for the rainbow/build_*.py scripts."""
import time
from pathlib import Path


def write_text(path, text):
    """Write a generated file with LF line endings, retrying briefly if Windows reports it busy
    (antivirus or OneDrive often hold a file open for a moment right after it was written)."""
    path = Path(path)
    for attempt in range(10):
        try:
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
            return
        except OSError:
            if attempt == 9:
                raise
            time.sleep(1)
