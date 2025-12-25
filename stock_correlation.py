#!/usr/bin/env python3
"""
台股相關係數計算程式
計算兩個台灣股票在不同時間段的股價相關係數
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def get_stock_data(symbol: str, days: int = 150) -> pd.DataFrame:
    """
    取得台股歷史資料

    Args:
        symbol: 股票代碼（例如：2330）
        days: 取得的天數

    Returns:
        包含收盤價的 DataFrame
    """
    # 自動加上 .TW 後綴
    if not symbol.endswith('.TW') and not symbol.endswith('.TWO'):
        symbol = f"{symbol}.TW"

    # 計算起始日期（多抓一些資料以確保有足夠的交易日）
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days + 100)

    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(start=start_date, end=end_date)

        if hist.empty:
            raise ValueError(f"無法取得股票 {symbol} 的資料")

        return hist[['Close']]

    except Exception as e:
        raise Exception(f"取得股票 {symbol} 資料時發生錯誤: {str(e)}")


def calculate_correlation(stock1_data: pd.DataFrame, stock2_data: pd.DataFrame, days: int) -> float:
    """
    計算兩個股票在指定天數內的相關係數

    Args:
        stock1_data: 股票1的價格資料
        stock2_data: 股票2的價格資料
        days: 計算的天數

    Returns:
        相關係數
    """
    # 取得最近 N 天的資料
    data1 = stock1_data.tail(days)
    data2 = stock2_data.tail(days)

    # 合併兩個資料集（只保留兩者都有交易的日期）
    merged = pd.merge(data1, data2, left_index=True, right_index=True, suffixes=('_1', '_2'))

    if len(merged) < days * 0.8:  # 如果實際資料少於預期的 80%，發出警告
        print(f"  ⚠️  警告：只有 {len(merged)} 個交易日的資料（預期 {days} 日）")

    # 計算相關係數
    correlation = merged['Close_1'].corr(merged['Close_2'])

    return correlation


def main():
    """主程式"""
    print("=" * 60)
    print("台股相關係數計算程式")
    print("=" * 60)
    print()

    # 輸入股票代碼
    stock1 = input("請輸入第一個股票代碼（例如：2330）: ").strip()
    stock2 = input("請輸入第二個股票代碼（例如：2317）: ").strip()
    print()

    try:
        # 取得股票資料
        print("正在取得股票資料...")
        stock1_data = get_stock_data(stock1, days=150)
        stock2_data = get_stock_data(stock2, days=150)
        print("✓ 資料取得完成")
        print()

        # 計算相關係數
        periods = [120, 20, 10]
        results = []

        print("計算相關係數中...")
        for period in periods:
            corr = calculate_correlation(stock1_data, stock2_data, period)
            results.append((period, corr))

        print()
        print("=" * 60)
        print("計算結果")
        print("=" * 60)
        print(f"股票代碼: {stock1} vs {stock2}")
        print()

        for period, corr in results:
            # 解釋相關係數
            if abs(corr) >= 0.7:
                strength = "強"
            elif abs(corr) >= 0.4:
                strength = "中等"
            else:
                strength = "弱"

            direction = "正相關" if corr >= 0 else "負相關"

            print(f"{period:3d} 日相關係數: {corr:7.4f}  ({strength}{direction})")

        print()
        print("-" * 60)
        print("相關係數解讀:")
        print("  1.0  : 完全正相關（兩股票完全同步上漲下跌）")
        print("  0.7  : 強正相關")
        print("  0.4  : 中等正相關")
        print("  0.0  : 無相關")
        print(" -0.4  : 中等負相關")
        print(" -0.7  : 強負相關")
        print(" -1.0  : 完全負相關（一漲一跌）")
        print("=" * 60)

    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
