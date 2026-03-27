"""
Usage:
To create a macOS app bundle using py2app, run the following command in the terminal:
    - pip install py2app
    - python setup_macos.py py2app
    - This will generate a .app bundle in the 'dist' directory.
This script is used to package a Python application into a macOS app bundle using py2app.

This setup works with macOS silicon and intel architectures.
"""

from setuptools import setup


APP = ['src/main.py']
DATA_FILES = [
    "assets/icon.icns"
]

OPTIONS = {
    'iconfile': "assets/icon.icns",
    'argv_emulation': True,
    'plist':{
        'CFBundleName': "From Webp Converter",
        'CFBundleVersion': "V1.0.1",
        'CFBundleShortVersionString': "V1.0.1", 
        'NSHumanReadableCopyright': '© 2023-2026 Made with Love by Simone De Angelis',
        'CFBundleIdentifier': 'com.simonedeamelis.fromwebpconverter',                  # Unique identifier for the app
        'LSApplicationCategoryType': 'public.app-category.utilities',                  # Application category
        'NSHighResolutionCapable': True,                                               # Support for high-resolution displays
    },
    'optimize': 2,                                                                     # Python bytecode optimization level
    # Ensure Qt and PIL modules are collected
    'packages': ['PIL', 'PyQt6'],
    'includes': [
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.sip',
    ],
    # Bundle essential Qt plugins (prevents missing platform/imageformat at runtime)
    'qt_plugins': ['platforms', 'styles', 'imageformats', 'iconengines'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    author="Simone De Angelis",
    copyright="Simone De Angelis",
    description="From Webp Converter is a simple and fast tool to convert WebP images to PNG or JPEG format.",
    license="GPLv3",
    options={'py2app': OPTIONS},
    setup_requires=['py2app', 'PyQt6'],
)
