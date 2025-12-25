"""
相關係數計算引擎
計算股票之間的相關係數並進行排序
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from database import StockDatabase


class CorrelationEngine:
    """相關係數計算引擎"""

    def __init__(self, db: StockDatabase):
        """
        初始化計算引擎

        Args:
            db: 資料庫實例
        """
        self.db = db

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

    def find_correlated_stocks(
        self,
        target_symbol: str,
        top_n: int = 20
    ) -> List[Dict]:
        """
        找出與目標股票最相關的前 N 檔股票

        Args:
            target_symbol: 目標股票代碼
            top_n: 返回前 N 檔股票

        Returns:
            排序後的相關股票列表，每個元素包含:
            {
                'symbol': 股票代碼,
                'name': 股票名稱,
                'corr_120': 120日相關係數,
                'corr_20': 20日相關係數,
                'corr_10': 10日相關係數
            }
        """
        # 確保目標股票代碼有正確的後綴
        if not target_symbol.endswith(('.TW', '.TWO')):
            target_symbol = target_symbol + '.TW'

        # 取得目標股票的價格資料
        target_data = self.db.get_stock_prices(target_symbol, days=120)

        if target_data.empty:
            raise ValueError(f"找不到股票 {target_symbol} 的資料")

        # 取得所有股票代碼
        all_symbols = self.db.get_all_symbols()

        # 儲存結果
        results = []

        print(f"\n正在計算與 {target_symbol} 的相關係數...")
        print(f"共需計算 {len(all_symbols)} 檔股票")
        print("=" * 60)

        # 計算每個股票的相關係數
        for i, symbol in enumerate(all_symbols, 1):
            # 跳過目標股票本身
            if symbol == target_symbol:
                continue

            # 顯示進度
            if i % 50 == 0:
                print(f"進度: {i}/{len(all_symbols)}")

            # 取得股票資料
            stock_data = self.db.get_stock_prices(symbol, days=120)

            if stock_data.empty:
                continue

            # 計算不同週期的相關係數
            corr_120 = self.calculate_correlation(target_data, stock_data, 120)
            corr_20 = self.calculate_correlation(target_data, stock_data, 20)
            corr_10 = self.calculate_correlation(target_data, stock_data, 10)

            # 如果所有相關係數都是 NaN，跳過這個股票
            if pd.isna(corr_120) and pd.isna(corr_20) and pd.isna(corr_10):
                continue

            # 取得股票名稱
            cursor = self.db.conn.cursor()
            cursor.execute(
                "SELECT name FROM stock_list WHERE symbol = ?",
                (symbol,)
            )
            result = cursor.fetchone()
            name = result[0] if result else ""

            results.append({
                'symbol': symbol,
                'name': name,
                'corr_120': corr_120 if not pd.isna(corr_120) else 0.0,
                'corr_20': corr_20 if not pd.isna(corr_20) else 0.0,
                'corr_10': corr_10 if not pd.isna(corr_10) else 0.0
            })

        print(f"計算完成！共找到 {len(results)} 檔有效股票")

        # 多層排序：120日優先，其次20日，最後10日
        sorted_results = sorted(
            results,
            key=lambda x: (x['corr_120'], x['corr_20'], x['corr_10']),
            reverse=True
        )

        # 返回前 N 檔
        return sorted_results[:top_n]

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
