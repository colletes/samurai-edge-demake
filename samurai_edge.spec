# -*- mode: python ; coding: utf-8 -*-
import sys
import os

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

# Coleta de assets do jogo
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

# Coleta de dados e binários do FFmpeg empacotado (imageio_ffmpeg)
extra_datas = []
extra_binaries = []
try:
    extra_datas += collect_data_files('imageio_ffmpeg')
except Exception:
    pass

try:
    import imageio_ffmpeg
    f_exe = imageio_ffmpeg.get_ffmpeg_exe()
    if f_exe and os.path.isfile(f_exe):
        extra_binaries.append((f_exe, 'imageio_ffmpeg/binaries'))
except Exception:
    pass

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=extra_binaries,
    datas=get_runtime_assets() + extra_datas,
    hiddenimports=collect_submodules('src') + collect_submodules('pyvidplayer2') + collect_submodules('imageio_ffmpeg') + [
        'pygame',
        'pygame._sdl2',
        'pygame._sdl2.audio',
        'pygame._sdl2.video',
        'pygame._sdl2.controller',
        'cv2',
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
            'CFBundleVersion': '3.0.1alpha',
            'CFBundleShortVersionString': '3.0.1alpha',
            'NSHighResolutionCapable': 'True',
            'LSApplicationCategoryType': 'public.app-category.action-games',
            'LSMinimumSystemVersion': '10.13.0',
        },
    )
