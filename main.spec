# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['main.py'],
    pathex=['C:\\Users\\14727\\AppData\\Local\\Programs\\Python\\Python310\\Lib\\site-packages'],
    binaries=[],
    datas=[("C:\\Users\\14727\\AppData\\Local\\Programs\\Python\\Python310\\Lib\\site-packages\\onnxruntime\\onnxruntime_providers_shared.dll",'onnxruntime\\capi'),
    ("C:\\Users\\14727\\AppData\\Local\\Programs\\Python\\Python310\\Lib\\site-packages\\ddddocr\\common.onnx","ddddocr")],
    # 下面的是旧图片识别模型,
    # ("C:\\Users\\14727\\AppData\\Local\\Programs\\Python\\Python310\\Lib\\site-packages\\ddddocr\\common_old.onnx","ddddocr")],
    hiddenimports=[],
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
    name='main',
    icon='icon.ico',
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
