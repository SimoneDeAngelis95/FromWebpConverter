"""Locate assets in source, PyInstaller and py2app distributions."""
import os
import sys
from pathlib import Path


def asset_path(name):
    root = getattr(sys, '_MEIPASS', None) or os.environ.get('RESOURCEPATH')
    return str((Path(root) if root else Path(__file__).resolve().parents[1]) / 'assets' / name)
