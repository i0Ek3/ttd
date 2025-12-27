# -*- mode: python ; coding: utf-8 -*-

import sys
import os

# Add current directory to path to import version.py
sys.path.append(os.getcwd())
try:
    from version import __version__
except ImportError:
    __version__ = "1.0.0"

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('ui', 'ui'), ('engines', 'engines'), ('utils', 'utils')],
    hiddenimports=['customtkinter', 'PIL', 'PIL._tkinter_finder', 'yt_dlp', 'pyperclip'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

# Determine if we are running on Windows
is_windows = sys.platform.startswith('win') or os.name == 'nt'

if is_windows:
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.datas,
        [],
        name='TTD',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=['TTD.icns'],
    )
else:
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
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=['TTD.icns'],
    )
    coll = COLLECT(
        exe,
        a.binaries,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='TTD',
    )
    
    if sys.platform == 'darwin':
        app = BUNDLE(
            coll,
            name='TTD.app',
            icon='TTD.icns',
            bundle_identifier='com.i0ek3.ttd',
            info_plist={
                'CFBundleName': 'TTD',
                'CFBundleDisplayName': 'TikTok videos Downloader',
                'CFBundleShortVersionString': __version__,
                'CFBundleVersion': __version__,
                'CFBundlePackageType': 'APPL',
                'NSHighResolutionCapable': True,
            },
        )

