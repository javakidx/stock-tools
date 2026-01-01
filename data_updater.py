"""
股價資料更新模組
負責從 yfinance 抓取股價資料並更新至資料庫
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List
import time
from database import StockDatabase


class DataUpdater:
    """股價資料更新器"""

    def __init__(self, db: StockDatabase):
        """
        初始化資料更新器

        Args:
            db: 資料庫實例
        """
        self.db = db

    def get_full_symbol(self, symbol: str) -> Optional[str]:
        """
        取得完整的股票代碼（自動加上 .TW 或 .TWO 後綴）

        Args:
            symbol: 股票代碼（可能有或沒有後綴）

        Returns:
            完整的股票代碼，如果找不到則返回 None
        """
        # 如果已經有後綴，直接返回
        if symbol.endswith(('.TW', '.TWO')):
            return symbol

        # 先嘗試 .TW（上市）
        tw_symbol = f"{symbol}.TW"
        try:
            ticker = yf.Ticker(tw_symbol)
            # 嘗試取得一筆資料來驗證股票是否存在
            hist = ticker.history(period="5d")
            if not hist.empty:
                return tw_symbol
        except:
            pass

        # 再嘗試 .TWO（上櫃）
        two_symbol = f"{symbol}.TWO"
        try:
            ticker = yf.Ticker(two_symbol)
            hist = ticker.history(period="5d")
            if not hist.empty:
                return two_symbol
        except:
            pass

        # 都找不到，返回 None
        return None

    def fetch_stock_data(self, symbol: str, start_date: datetime, end_date: datetime) -> Optional[pd.DataFrame]:
        """
        從 yfinance 取得股票資料

        Args:
            symbol: 股票代碼（例如：2330.TW）
            start_date: 起始日期
            end_date: 結束日期

        Returns:
            包含收盤價的 DataFrame，如果失敗則返回 None
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(start=start_date, end=end_date)

            if hist.empty:
                return None

            # 只保留收盤價
            df = hist[['Close']].copy()
            return df

        except Exception as e:
            print(f"  ⚠️  取得 {symbol} 資料時發生錯誤: {e}")
            return None

    def update_stock(self, symbol: str, days: int = 120) -> bool:
        """
        更新單一股票資料（增量更新）

        Args:
            symbol: 股票代碼
            days: 需要保留的天數

        Returns:
            是否更新成功
        """
        try:
            # 取得資料庫中的最新日期
            latest_date = self.db.get_latest_date(symbol)

            # 計算需要抓取的日期範圍
            end_date = datetime.now()

            if latest_date:
                # 如果有歷史資料，從最新日期的下一天開始抓取
                start_date = latest_date + timedelta(days=1)

                # 如果資料已經是最新的，則不需要更新
                if start_date >= end_date:
                    return True
            else:
                # 如果沒有歷史資料，抓取最近 N 天 + 一些額外天數
                start_date = end_date - timedelta(days=days + 60)

            # 從 yfinance 抓取資料
            df = self.fetch_stock_data(symbol, start_date, end_date)

            if df is None or df.empty:
                return False

            # 儲存到資料庫
            self.db.insert_stock_prices(symbol, df)

            # 更新最後更新時間
            self.db.update_last_update(symbol, end_date)

            return True

        except Exception as e:
            print(f"  ⚠️  更新 {symbol} 時發生錯誤: {e}")
            return False

    def update_all_stocks(self, stock_list: List[tuple], days: int = 120, delay: float = 0.5):
        """
        更新所有股票資料

        Args:
            stock_list: 股票清單 [(symbol, name), ...]
            days: 需要保留的天數
            delay: 每次請求之間的延遲（秒）
        """
        total = len(stock_list)
        success_count = 0
        fail_count = 0

        print(f"\n開始更新 {total} 檔股票資料...")
        print("=" * 60)

        for i, (symbol, name) in enumerate(stock_list, 1):
            print(f"[{i}/{total}] 更新 {symbol} ({name})...", end=' ')

            # 將股票加入清單
            self.db.add_stock_to_list(symbol, name)

            # 更新股價資料
            if self.update_stock(symbol, days):
                print("✓")
                success_count += 1
            else:
                print("✗")
                fail_count += 1

            # 延遲以避免請求過快
            if i < total:
                time.sleep(delay)

        print("=" * 60)
        print(f"更新完成！成功: {success_count}, 失敗: {fail_count}")

    def clean_old_data(self, symbol: str, keep_days: int = 120):
        """
        清理過舊的資料

        Args:
            symbol: 股票代碼
            keep_days: 保留的天數
        """
        cutoff_date = datetime.now() - timedelta(days=keep_days + 30)
        cursor = self.db.conn.cursor()
        cursor.execute("""
            DELETE FROM stock_prices
            WHERE symbol = ? AND date < ?
        """, (symbol, cutoff_date.strftime('%Y-%m-%d')))
        self.db.conn.commit()


if __name__ == "__main__":
    # 測試
    from stock_list import get_sample_stocks

    with StockDatabase() as db:
        updater = DataUpdater(db)

        # 取得範例股票清單
        stocks = get_sample_stocks()

        # 更新股票資料
        updater.update_all_stocks(stocks[:5], days=120, delay=1)

        # 顯示資料庫統計
        print(f"\n資料庫統計:")
        print(f"  股票數量: {db.get_stocks_count()}")
        print(f"  價格記錄數: {db.get_price_records_count()}")
