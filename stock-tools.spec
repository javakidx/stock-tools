# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main_gui.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'pandas',
        'numpy',
        'yfinance',
        'sqlite3',
        'threading',
        'database',
        'correlation_engine',
        'data_updater',
        'tpex_updater',
        'stock_list',
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
    name='台股相關性分析',
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
    name='台股相關性分析',
)

app = BUNDLE(
    coll,
    name='台股相關性分析.app',
    icon=None,
    bundle_identifier='com.stock-tools.correlation',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': 'True',
        'CFBundleDisplayName': '台股相關性分析系統',
        'CFBundleName': '台股相關性分析',
        'CFBundleShortVersionString': '3.0.0',
        'CFBundleVersion': '3.0.0',
        'NSHumanReadableCopyright': '© 2025',
    },
)
