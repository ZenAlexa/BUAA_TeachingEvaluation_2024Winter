# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Linux

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
        (str(icons_dir / 'icon.png'), 'icons'),
    ],
    hiddenimports=[
        'webview',
        'webview.platforms.gtk',
        'webview.platforms.qt',
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='buaa-evaluation',
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
)
