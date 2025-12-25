"""
台股代碼清單模組
取得台灣股市的股票代碼列表
"""

import requests
from typing import List, Tuple
import time


def get_twse_stock_list() -> List[Tuple[str, str]]:
    """
    從台灣證券交易所取得上市股票清單

    Returns:
        List of (symbol, name) tuples
    """
    stocks = []

    try:
        # TWSE 上市股票列表 API
        url = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'big5'

        if response.status_code == 200:
            lines = response.text.split('\n')
            for line in lines:
                if '股票' in line:  # 只取股票類型
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        code_name = parts[0].strip()
                        if '　' in code_name:
                            code, name = code_name.split('　', 1)
                            # 只取4位數字的股票代碼（排除 ETF 等）
                            if code.isdigit() and len(code) == 4:
                                stocks.append((code + '.TW', name.strip()))

    except Exception as e:
        print(f"取得上市股票清單時發生錯誤: {e}")

    return stocks


def get_tpex_stock_list() -> List[Tuple[str, str]]:
    """
    從櫃買中心取得上櫃股票清單

    Returns:
        List of (symbol, name) tuples
    """
    stocks = []

    try:
        # TPEx 上櫃股票列表 API
        url = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=4"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'big5'

        if response.status_code == 200:
            lines = response.text.split('\n')
            for line in lines:
                if '股票' in line:  # 只取股票類型
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        code_name = parts[0].strip()
                        if '　' in code_name:
                            code, name = code_name.split('　', 1)
                            # 只取4位數字的股票代碼
                            if code.isdigit() and len(code) == 4:
                                stocks.append((code + '.TWO', name.strip()))

    except Exception as e:
        print(f"取得上櫃股票清單時發生錯誤: {e}")

    return stocks


def get_all_taiwan_stocks() -> List[Tuple[str, str]]:
    """
    取得所有台灣股票（上市 + 上櫃）

    Returns:
        List of (symbol, name) tuples
    """
    print("正在取得台股清單...")

    # 取得上市股票
    print("  - 取得上市股票...")
    twse_stocks = get_twse_stock_list()
    time.sleep(1)  # 避免請求過快

    # 取得上櫃股票
    print("  - 取得上櫃股票...")
    tpex_stocks = get_tpex_stock_list()

    all_stocks = twse_stocks + tpex_stocks

    print(f"  - 共取得 {len(all_stocks)} 檔股票")
    print(f"    上市: {len(twse_stocks)} 檔")
    print(f"    上櫃: {len(tpex_stocks)} 檔")

    return all_stocks


def get_sample_stocks() -> List[Tuple[str, str]]:
    """
    取得範例股票清單（用於測試）

    Returns:
        List of (symbol, name) tuples
    """
    return [
        ('2330.TW', '台積電'),
        ('2317.TW', '鴻海'),
        ('2454.TW', '聯發科'),
        ('2881.TW', '富邦金'),
        ('2882.TW', '國泰金'),
        ('2886.TW', '兆豐金'),
        ('2891.TW', '中信金'),
        ('2892.TW', '第一金'),
        ('2412.TW', '中華電'),
        ('1301.TW', '台塑'),
        ('1303.TW', '南亞'),
        ('2308.TW', '台達電'),
        ('2002.TW', '中鋼'),
        ('2303.TW', '聯電'),
        ('3008.TW', '大立光'),
        ('2327.TW', '國巨'),
        ('2395.TW', '研華'),
        ('2408.TW', '南亞科'),
        ('3711.TW', '日月光投控'),
        ('5880.TW', '合庫金'),
    ]


if __name__ == "__main__":
    # 測試
    stocks = get_all_taiwan_stocks()
    if stocks:
        print("\n前 10 檔股票:")
        for symbol, name in stocks[:10]:
            print(f"  {symbol}: {name}")
