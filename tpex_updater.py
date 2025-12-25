"""
櫃買中心資料更新模組
將櫃買中心股價資料存入資料庫
"""

import pandas as pd
from datetime import datetime, timedelta
from database import StockDatabase
from tpex_fetcher import TPEXFetcher
from typing import List, Dict


class TPEXUpdater:
    """櫃買中心資料更新器"""

    def __init__(self, db: StockDatabase):
        """
        初始化更新器

        Args:
            db: 資料庫實例
        """
        self.db = db
        self.fetcher = TPEXFetcher()

    def update_single_date(self, date: datetime) -> int:
        """
        更新指定日期的所有櫃買股票資料

        Args:
            date: 查詢日期

        Returns:
            成功更新的股票數量
        """
        print(f"\n正在抓取 {date.strftime('%Y-%m-%d')} 的櫃買中心資料...")

        data = self.fetcher.fetch_and_parse(date)

        if data is None or len(data) == 0:
            print("  無資料或非交易日")
            return 0

        success_count = 0

        for stock in data:
            try:
                symbol = stock['symbol']
                close_price = stock['close_price']

                # 將資料轉換為 DataFrame 格式
                df = pd.DataFrame({
                    'Close': [close_price]
                }, index=[date])

                # 存入資料庫，標記來源為 TPEX
                self.db.insert_stock_prices(symbol, df, source='TPEX')

                # 更新股票清單
                self.db.add_stock_to_list(
                    symbol=symbol,
                    name=stock['name'],
                    market='TPEX'
                )

                success_count += 1

            except Exception as e:
                print(f"  錯誤：無法更新 {stock['symbol']}: {e}")
                continue

        print(f"  成功更新 {success_count} 檔股票")
        return success_count

    def update_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        delay: float = 1.0
    ) -> Dict[str, int]:
        """
        更新日期範圍內的櫃買股票資料

        Args:
            start_date: 起始日期
            end_date: 結束日期
            delay: 每次請求間的延遲（秒）

        Returns:
            {日期: 更新數量} 的字典
        """
        results = {}
        current_date = start_date

        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')

            count = self.update_single_date(current_date)
            results[date_str] = count

            # 延遲
            if delay > 0 and current_date < end_date:
                import time
                time.sleep(delay)

            current_date += timedelta(days=1)

        return results

    def update_recent_days(self, days: int = 30, delay: float = 1.0) -> int:
        """
        更新最近 N 天的櫃買股票資料

        Args:
            days: 天數
            delay: 延遲時間

        Returns:
            總更新數量
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        print(f"\n開始更新最近 {days} 天的櫃買中心資料")
        print(f"時間範圍: {start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}")

        results = self.update_date_range(start_date, end_date, delay)

        total = sum(results.values())
        print(f"\n更新完成！總共更新 {total} 筆資料")

        return total


def main():
    """測試用主程式"""
    # 初始化資料庫
    db = StockDatabase()

    # 建立更新器
    updater = TPEXUpdater(db)

    # 測試：更新指定日期的資料
    test_date = datetime(2024, 12, 23)
    print(f"測試：更新 {test_date.strftime('%Y-%m-%d')} 的資料")
    count = updater.update_single_date(test_date)

    print(f"\n完成！成功更新 {count} 檔股票")

    # 查詢資料庫統計
    print(f"\n資料庫統計:")
    print(f"  總股票數: {db.get_stocks_count()}")
    print(f"  總價格記錄數: {db.get_price_records_count()}")

    # 關閉資料庫
    db.close()


if __name__ == "__main__":
    main()
