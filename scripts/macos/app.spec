# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for macOS

import sys
from pathlib import Path

sys.setrecursionlimit(5000)

project_root = Path(SPECPATH).parent.parent
backend_dir = project_root / 'backend'
web_dir = backend_dir / 'web'
icons_dir = project_root / 'assets' / 'icons'

block_cipher = None

a = Analysis(
    [str(backend_dir / 'main.py')],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        (str(web_dir), 'web'),
        (str(backend_dir / 'evaluator.py'), '.'),
    ],
    hiddenimports=[
        'webview',
        'webview.platforms.cocoa',
        'requests',
        'bs4',
        'urllib.parse',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='BUAA-Evaluation',
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
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='BUAA-Evaluation',
)

app = BUNDLE(
    coll,
    name='BUAA-Evaluation.app',
    icon=str(icons_dir / 'icon.icns'),
    bundle_identifier='com.buaa.evaluation',
    info_plist={
        'CFBundleName': 'BUAA Evaluation',
        'CFBundleDisplayName': 'BUAA Evaluation',
        'CFBundleVersion': '1.1.1',
        'CFBundleShortVersionString': '1.1.1',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.13.0',
    },
)
