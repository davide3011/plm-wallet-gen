# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for PLM Wallet Generator GUI

This configuration creates a single-file Windows executable with:
- Embedded icon for the .exe file and Windows taskbar
- All GUI resources bundled (icons, assets)
- No console window (GUI-only mode)
- Portable standalone executable
"""

a = Analysis(
    ['../../run_gui.py'],  # Entry point at project root
    pathex=['../../src'],  # Add src/ to path so imports work correctly
    binaries=[],
    datas=[
        ('../../src/gui/icons', 'gui/icons'),  # Include all icon files
    ],
    hiddenimports=[
        'gui.app',
        'gui.main_window',
        'gui.wallet_generator_widget',
        'gui.wallet_display_widget',
        'gui.wallet_loader_widget',
        'gui.password_dialog',
        'plm_wallet',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PLM-Wallet-Generator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window - GUI only
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='../../src/gui/icons/icon.ico',  # Icon for executable file and Windows taskbar
)
