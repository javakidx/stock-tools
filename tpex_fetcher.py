"""
櫃買中心股價資料抓取模組
從台灣證券櫃檯買賣中心 API 取得股票收盤價
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import time
import urllib3

# 抑制 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class TPEXFetcher:
    """櫃買中心股價資料抓取器"""

    BASE_URL = "https://www.tpex.org.tw/www/zh-tw/afterTrading/dailyQuotes"

    def __init__(self):
        """初始化 fetcher"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def fetch_daily_quotes(self, date: datetime) -> Optional[List[List]]:
        """
        抓取指定日期的櫃買市場收盤價資料

        Args:
            date: 查詢日期

        Returns:
            股票資料列表，每個元素為 [股票代號, 股票名稱, 收盤價, ...]
            若查詢失敗則返回 None
        """
        # 格式化日期為 YYYY/MM/DD
        date_str = date.strftime('%Y/%m/%d')

        params = {
            'date': date_str,
            'id': '',
            'response': 'json'
        }

        try:
            response = self.session.get(self.BASE_URL, params=params, timeout=10, verify=False)
            response.raise_for_status()

            data = response.json()

            # 檢查回應結構
            if 'tables' not in data:
                print(f"警告：{date_str} 無 tables 資料")
                return None

            if not data['tables'] or 'data' not in data['tables'][0]:
                print(f"警告：{date_str} 無交易資料（可能為非交易日）")
                return None

            # 返回股票資料
            return data['tables'][0]['data']

        except requests.RequestException as e:
            print(f"抓取 {date_str} 資料時發生錯誤: {e}")
            return None
        except (KeyError, ValueError) as e:
            print(f"解析 {date_str} 資料時發生錯誤: {e}")
            return None

    def parse_stock_data(self, raw_data: List[List]) -> List[Dict]:
        """
        解析原始股票資料

        Args:
            raw_data: 原始資料列表

        Returns:
            解析後的股票資料列表
            [{
                'symbol': 股票代號,
                'name': 股票名稱,
                'close_price': 收盤價
            }, ...]
        """
        parsed_data = []

        for row in raw_data:
            try:
                # 確保有足夠的欄位
                if len(row) < 3:
                    continue

                symbol = str(row[0]).strip()
                name = str(row[1]).strip()
                close_price_str = str(row[2]).strip()

                # 跳過空值或無效資料
                if not symbol or not close_price_str or close_price_str == '-':
                    continue

                # 轉換收盤價（移除逗號）
                close_price = float(close_price_str.replace(',', ''))

                parsed_data.append({
                    'symbol': symbol,
                    'name': name,
                    'close_price': close_price
                })

            except (ValueError, IndexError) as e:
                print(f"解析資料錯誤: {row}, {e}")
                continue

        return parsed_data

    def fetch_and_parse(self, date: datetime) -> Optional[List[Dict]]:
        """
        抓取並解析指定日期的股票資料

        Args:
            date: 查詢日期

        Returns:
            解析後的股票資料列表
        """
        raw_data = self.fetch_daily_quotes(date)

        if raw_data is None:
            return None

        return self.parse_stock_data(raw_data)

    def fetch_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        delay: float = 1.0
    ) -> Dict[str, List[Dict]]:
        """
        抓取日期範圍內的股票資料

        Args:
            start_date: 起始日期
            end_date: 結束日期
            delay: 每次請求間的延遲（秒）

        Returns:
            {日期字串: 股票資料列表} 的字典
        """
        results = {}
        current_date = start_date

        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            print(f"抓取 {date_str} 的資料...")

            data = self.fetch_and_parse(current_date)

            if data:
                results[date_str] = data
                print(f"  成功抓取 {len(data)} 檔股票")
            else:
                print(f"  {date_str} 無資料")

            # 延遲以避免過度請求
            time.sleep(delay)

            current_date += timedelta(days=1)

        return results

    def show_sample(self, date: datetime, sample_size: int = 5) -> None:
        """
        顯示指定日期的樣本資料供確認

        Args:
            date: 查詢日期
            sample_size: 顯示筆數
        """
        print(f"\n=== 抓取 {date.strftime('%Y-%m-%d')} 的樣本資料 ===\n")

        raw_data = self.fetch_daily_quotes(date)

        if raw_data is None:
            print("無法取得資料")
            return

        print(f"共取得 {len(raw_data)} 檔股票資料\n")
        print("原始資料結構（前 {} 筆）：".format(min(sample_size, len(raw_data))))
        print("-" * 80)

        for i, row in enumerate(raw_data[:sample_size], 1):
            print(f"{i}. {row}")

        print("\n" + "=" * 80)
        print("\n解析後的資料：")
        print("-" * 80)

        parsed_data = self.parse_stock_data(raw_data)

        for i, stock in enumerate(parsed_data[:sample_size], 1):
            print(f"{i}. 代號: {stock['symbol']:6s} | 名稱: {stock['name']:20s} | 收盤價: {stock['close_price']:8.2f}")

        print("=" * 80)
        print(f"\n成功解析 {len(parsed_data)} 檔股票")


def main():
    """測試用主程式"""
    fetcher = TPEXFetcher()

    # 顯示最近交易日的樣本資料
    test_date = datetime(2024, 12, 23)  # 使用一個確定有交易的日期
    fetcher.show_sample(test_date, sample_size=10)


if __name__ == "__main__":
    main()
