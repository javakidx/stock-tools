#!/bin/bash
# 台股相關性分析系統啟動腳本

# 取得腳本所在目錄
cd "$(dirname "$0")"

# 啟動虛擬環境並執行程式
source .venv/bin/activate
python3 main_gui.py

# 保持視窗開啟以顯示錯誤訊息（如果有的話）
if [ $? -ne 0 ]; then
    echo ""
    echo "程式執行時發生錯誤，請按任意鍵關閉視窗..."
    read -n 1
fi
