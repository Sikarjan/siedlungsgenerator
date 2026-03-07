# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['/Users/flo/Programmieren/DSA/siedlungsgenerator'],
    binaries=[],
    datas=[('app_icon.icns', '.')],
    hiddenimports=['PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DSA Siedlungsgenerator',
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
    icon='app_icon.icns',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DSA Siedlungsgenerator',
)
app = BUNDLE(
    coll,
    name='DSA Siedlungsgenerator.app',
    icon='app_icon.icns',
    bundle_identifier='de.innobiz.dsa-siedlungsgenerator',
    info_plist={
        'CFBundleName': 'DSA Siedlungsgenerator',
        'CFBundleDisplayName': 'DSA Siedlungsgenerator',
        'CFBundleVersion': '0.1.0',
        'CFBundleShortVersionString': '0.1',
        'NSHighResolutionCapable': 'True',
    }
)
