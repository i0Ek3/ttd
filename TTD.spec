# -*- mode: python ; coding: utf-8 -*-
# TTD PyInstaller Configuration File
# Usage: pyinstaller TTD.spec

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all dependencies for yt-dlp
yt_dlp_datas = collect_data_files('yt_dlp')
yt_dlp_hiddenimports = collect_submodules('yt_dlp')

a = Analysis(
    ['main.py'],  # Main entry file
    pathex=[],
    binaries=[],
    datas=[
        # Add project folders (adjust according to your project structure)
        ('ui', 'ui'),
        ('engines', 'engines'),
        ('utils', 'utils'),
        # Uncomment if you have an assets folder
        # ('assets', 'assets'),
    ] + yt_dlp_datas,
    hiddenimports=[
        # CustomTkinter related
        'customtkinter',
        'customtkinter.windows',
        'customtkinter.windows.widgets',
        
        # PIL/Pillow
        'PIL',
        'PIL._tkinter_finder',
        'PIL.Image',
        'PIL.ImageTk',
        
        # yt-dlp and its dependencies
        'yt_dlp',
        'yt_dlp.extractor',
        'yt_dlp.downloader',
        'yt_dlp.postprocessor',
        
        # Other dependencies
        'pyperclip',
        'requests',
        'certifi',
        'urllib3',
        'charset_normalizer',
        
        # tkinter related
        'tkinter',
        'tkinter.ttk',
        '_tkinter',
        
        # JSON support
        'json',
        'threading',
        'datetime',
        'webbrowser',
        're',
        'os',
        'sys',
    ] + yt_dlp_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TTD',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console for GUI apps
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TTD',
)

# macOS app bundle configuration
app = BUNDLE(
    coll,
    name='TTD.app',
    icon='TTD.icns',  # Ensure this file exists
    bundle_identifier='com.i0ek3.ttd',  # Modify to your identifier
    info_plist={
        'CFBundleName': 'TTD',
        'CFBundleDisplayName': 'TikTok Downloader',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': '????',
        'CFBundleExecutable': 'TTD',
        'CFBundleIdentifier': 'com.i0ek3.ttd',
        'NSHumanReadableCopyright': 'Copyright © 2024 i0Ek3. All rights reserved.',
        'NSHighResolutionCapable': True,
        'NSPrincipalClass': 'NSApplication',
        'LSMinimumSystemVersion': '10.13.0',  # macOS High Sierra or later
        'LSApplicationCategoryType': 'public.app-category.utilities',
        # Permission declaration (if needed)
        'NSAppleEventsUsageDescription': 'TTD needs to access clipboard for auto-paste functionality.',
    },
)