# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_data_files

python_flag = [] if os.getenv("OJV_DEBUG") == 1 else [("O", None, "OPTION")]

datas = [
    ("engine_manifest_assets", "engine_manifest_assets"),
    ("resources", "resources"),
    ("ui_template", "ui_template"),
    ("default_setting.yml", "."),
    ("default.csv", "."),
    ("licenses.json", "."),
    ("presets.yaml", "."),
    ("engine_manifest.json", "."),
]
datas += collect_data_files(
    "pyopenjtalk", includes=["**/open_jtalk_dic_utf_8-1.11/*.*"]
)


block_cipher = None


a = Analysis(
    ["run.py"],
    pathex=[],
    binaries=[],
    datas=datas,
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
    python_flag,
    exclude_binaries=True,
    name="run",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
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
    name="run",
)
