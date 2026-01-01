"""
相關係數計算引擎
計算股票之間的相關係數並進行排序
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
import yfinance as yf
from database import StockDatabase


class CorrelationEngine:
    """相關係數計算引擎"""

    def __init__(self, db: StockDatabase, updater=None):
        """
        初始化計算引擎

        Args:
            db: 資料庫實例
            updater: DataUpdater 實例（可選，用於自動更新資料）
        """
        self.db = db
        self.updater = updater

    def get_full_symbol(self, symbol: str) -> Optional[str]:
        """
        取得完整的股票代碼（自動加上 .TW 或 .TWO 後綴）

        Args:
            symbol: 股票代碼（可能有或沒有後綴）

        Returns:
            完整的股票代碼，如果找不到則返回 None
        """
        # 如果已經有後綴，先檢查資料庫中是否有資料
        if symbol.endswith(('.TW', '.TWO')):
            data = self.db.get_stock_prices(symbol, days=5)
            if not data.empty:
                return symbol

        # 移除可能存在的後綴
        base_symbol = symbol.replace('.TW', '').replace('.TWO', '')

        # 先檢查資料庫中的 .TW（上市）
        tw_symbol = f"{base_symbol}.TW"
        data = self.db.get_stock_prices(tw_symbol, days=5)
        if not data.empty:
            return tw_symbol

        # 再檢查資料庫中的 .TWO（上櫃）
        two_symbol = f"{base_symbol}.TWO"
        data = self.db.get_stock_prices(two_symbol, days=5)
        if not data.empty:
            return two_symbol

        # 資料庫中都沒有，嘗試從 yfinance 判斷
        try:
            ticker = yf.Ticker(tw_symbol)
            hist = ticker.history(period="5d")
            if not hist.empty:
                return tw_symbol
        except:
            pass

        try:
            ticker = yf.Ticker(two_symbol)
            hist = ticker.history(period="5d")
            if not hist.empty:
                return two_symbol
        except:
            pass

        # 都找不到，返回 None
        return None

    def calculate_correlation(
        self,
        data1: pd.DataFrame,
        data2: pd.DataFrame,
        days: int
    ) -> float:
        """
        計算兩個股票在指定天數內的相關係數

        Args:
            data1: 股票1的價格資料
            data2: 股票2的價格資料
            days: 計算的天數

        Returns:
            相關係數（如果資料不足則返回 NaN）
        """
        # 取得最近 N 天的資料
        df1 = data1.tail(days).copy()
        df2 = data2.tail(days).copy()

        # 確保有足夠的資料
        if len(df1) < days * 0.7 or len(df2) < days * 0.7:
            return np.nan

        # 合併兩個資料集（只保留兩者都有交易的日期）
        merged = pd.merge(
            df1, df2,
            left_index=True,
            right_index=True,
            suffixes=('_1', '_2')
        )

        # 確保合併後有足夠的資料點
        if len(merged) < days * 0.7:
            return np.nan

        # 計算相關係數
        try:
            correlation = merged['close_price_1'].corr(merged['close_price_2'])
            return correlation if not pd.isna(correlation) else np.nan
        except:
            return np.nan

    def calculate_two_stocks_correlation(
        self,
        symbol1: str,
        symbol2: str
    ) -> Dict:
        """
        計算兩檔股票之間的相關係數

        Args:
            symbol1: 第一檔股票代碼
            symbol2: 第二檔股票代碼

        Returns:
            包含相關係數的字典:
            {
                'symbol1': 股票1代碼,
                'symbol2': 股票2代碼,
                'name1': 股票1名稱,
                'name2': 股票2名稱,
                'corr_120': 120日相關係數,
                'corr_60': 60日相關係數,
                'corr_20': 20日相關係數
            }
        """
        # 自動判斷並加上正確的後綴
        full_symbol1 = self.get_full_symbol(symbol1)
        full_symbol2 = self.get_full_symbol(symbol2)

        if not full_symbol1:
            raise ValueError(f"找不到股票 {symbol1} 的資料（已嘗試 .TW 和 .TWO 後綴）")
        if not full_symbol2:
            raise ValueError(f"找不到股票 {symbol2} 的資料（已嘗試 .TW 和 .TWO 後綴）")

        # 取得兩檔股票的價格資料
        data1 = self.db.get_stock_prices(full_symbol1, days=120)
        data2 = self.db.get_stock_prices(full_symbol2, days=120)

        # 如果資料為空且有 updater，嘗試更新資料
        if data1.empty and self.updater:
            print(f"正在從 yfinance 抓取 {full_symbol1} 的資料...")
            if self.updater.update_stock(full_symbol1, days=120):
                data1 = self.db.get_stock_prices(full_symbol1, days=120)

        if data2.empty and self.updater:
            print(f"正在從 yfinance 抓取 {full_symbol2} 的資料...")
            if self.updater.update_stock(full_symbol2, days=120):
                data2 = self.db.get_stock_prices(full_symbol2, days=120)

        # 檢查資料是否成功取得
        if data1.empty:
            raise ValueError(f"找不到股票 {full_symbol1} 的資料")
        if data2.empty:
            raise ValueError(f"找不到股票 {full_symbol2} 的資料")

        # 計算不同週期的相關係數
        corr_120 = self.calculate_correlation(data1, data2, 120)
        corr_60 = self.calculate_correlation(data1, data2, 60)
        corr_20 = self.calculate_correlation(data1, data2, 20)

        # 取得股票名稱
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT name FROM stock_list WHERE symbol = ?", (full_symbol1,))
        result1 = cursor.fetchone()
        name1 = result1[0] if result1 else ""

        cursor.execute("SELECT name FROM stock_list WHERE symbol = ?", (full_symbol2,))
        result2 = cursor.fetchone()
        name2 = result2[0] if result2 else ""

        return {
            'symbol1': full_symbol1,
            'symbol2': full_symbol2,
            'name1': name1,
            'name2': name2,
            'corr_120': corr_120 if not pd.isna(corr_120) else 0.0,
            'corr_60': corr_60 if not pd.isna(corr_60) else 0.0,
            'corr_20': corr_20 if not pd.isna(corr_20) else 0.0
        }

    def format_correlation_strength(self, corr: float) -> str:
        """
        格式化相關係數強度描述

        Args:
            corr: 相關係數

        Returns:
            強度描述字串
        """
        abs_corr = abs(corr)

        if abs_corr >= 0.9:
            strength = "極強"
        elif abs_corr >= 0.7:
            strength = "強"
        elif abs_corr >= 0.5:
            strength = "中等"
        elif abs_corr >= 0.3:
            strength = "弱"
        else:
            strength = "極弱"

        direction = "正相關" if corr >= 0 else "負相關"

        return f"{strength}{direction}"


if __name__ == "__main__":
    # 測試
    with StockDatabase() as db:
        engine = CorrelationEngine(db)

        # 測試相關係數計算
        target = "2330.TW"

        try:
            results = engine.find_correlated_stocks(target, top_n=10)

            print(f"\n與 {target} 相關性最高的前 10 檔股票:")
            print("=" * 80)
            print(f"{'排名':<4} {'代碼':<12} {'名稱':<10} {'120日':<8} {'20日':<8} {'10日':<8}")
            print("-" * 80)

            for i, stock in enumerate(results, 1):
                print(
                    f"{i:<4} {stock['symbol']:<12} {stock['name']:<10} "
                    f"{stock['corr_120']:>7.4f} {stock['corr_20']:>7.4f} {stock['corr_10']:>7.4f}"
                )

        except ValueError as e:
            print(f"錯誤: {e}")
