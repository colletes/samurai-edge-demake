# -*- mode: python ; coding: utf-8 -*-
import sys
import os

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[('assets/portraits', 'assets/portraits')],
    hiddenimports=[
        'src',
        'src.config',
        'src.combat',
        'src.combat.collision',
        'src.effects',
        'src.effects.particles',
        'src.effects.cinematic_director',
        'src.entities',
        'src.entities.samurai',
        'src.entities.red_samurai',
        'src.entities.blue_samurai',
        'src.entities.yellow_ninja',
        'src.entities.american_ninja',
        'src.entities.gray_ninja',
        'src.entities.purple_ninja',
        'src.entities.saitou_samurai',
        'src.entities.rifleman',
        'src.entities.kabuki',
        'src.entities.kyudo_archer',
        'src.entities.pirate',
        'src.entities.musketeer',
        'src.entities.doberman',
        'src.entities.projectile',
        'src.entities.pickups',
        'src.entities.voxel_corpse',
        'src.entities.voxel_models',
        'src.entities.ai_controller',
        'src.i18n',
        'src.input',
        'src.input.controller_manager',
        'src.input.display_scaler',
        'src.input.touch_controls',
        'src.isometric',
        'src.isometric.iso_math',
        'src.isometric.camera',
        'src.isometric.voxel_renderer',
        'src.ui',
        'src.ui.character_select',
        'src.ui.game_help',
        'src.ui.portraits',
        'src.ui.settings_menu',
        'src.world',
        'src.world.map_data',
        'src.world.bamboo',
        'src.world.obstacles',
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
            'CFBundleVersion': '1.2.0',
            'CFBundleShortVersionString': '1.2.0',
            'NSHighResolutionCapable': 'True',
            'LSMinimumSystemVersion': '10.13.0',
        },
    )
