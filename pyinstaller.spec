from PyInstaller.building.api import EXE, PYZ
from PyInstaller.building.build_main import Analysis

analysis = Analysis(
    ["ryukit/__main__.py"],
    pathex=[],
    binaries=[],
    datas=[("ryukit", "ryukit")],
    hiddenimports=["psutil"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
exe = EXE(
    PYZ(analysis.pure),
    analysis.scripts,
    analysis.binaries,
    analysis.datas,
    [],
    name="ryukit",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="assets/exe.ico",
)
