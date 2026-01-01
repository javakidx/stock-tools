"""
Setup script for py2app
"""
from setuptools import setup

APP = ['main_gui.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'iconfile': None,
    'plist': {
        'CFBundleName': '台股相關性分析',
        'CFBundleDisplayName': '台股相關性分析系統',
        'CFBundleIdentifier': 'com.stock-tools.correlation',
        'CFBundleVersion': '3.0.0',
        'CFBundleShortVersionString': '3.0.0',
        'NSHighResolutionCapable': True,
    },
    'packages': ['tkinter', 'pandas', 'numpy', 'yfinance', 'sqlite3'],
    'includes': [
        'database',
        'correlation_engine',
        'data_updater',
        'tpex_updater',
        'stock_list',
    ],
}

setup(
    app=APP,
    name='台股相關性分析',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
