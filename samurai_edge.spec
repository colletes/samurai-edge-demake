# -*- mode: python ; coding: utf-8 -*-
import sys
import os

from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

def get_runtime_assets():
    datas = []
    exclude_patterns = [
        "sound_drafts",
        "promotional",
        "HD2D_Concept_Art.pdf",
        "_gameplay_mockup.jpg",
        "Take ",
        ".DS_Store",
    ]
    for root, dirs, files in os.walk("assets"):
        dirs[:] = [d for d in dirs if not any(p in d for p in ("sound_drafts", "promotional"))]
        for f in files:
            rel_path = os.path.join(root, f)
            if any(p in rel_path for p in exclude_patterns):
                continue
            dest_dir = os.path.dirname(rel_path)
            datas.append((rel_path, dest_dir))
    return datas

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=get_runtime_assets(),
    hiddenimports=collect_submodules('src') + [
        'pygame',
        'pygame._sdl2',
        'pygame._sdl2.audio',
        'pygame._sdl2.video',
        'pygame._sdl2.controller',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'unittest'],
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
    name='SamuraiEdge',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
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
    upx=False,
    upx_exclude=[],
    name='SamuraiEdge',
)

if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='SamuraiEdge.app',
        icon=None,
        bundle_identifier='com.samuraiedge.game',
        info_plist={
            'CFBundleName': 'Samurai Edge Demake',
            'CFBundleDisplayName': 'Samurai Edge Demake',
            'CFBundleVersion': '3.0.0alpha',
            'CFBundleShortVersionString': '3.0.0alpha',
            'NSHighResolutionCapable': 'True',
            'LSApplicationCategoryType': 'public.app-category.action-games',
            'LSMinimumSystemVersion': '10.13.0',
        },
    )
