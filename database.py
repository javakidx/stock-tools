"""
資料庫管理模組
處理台股股價資料的 SQLite 儲存與查詢
"""

import sqlite3
import pandas as pd
from datetime import datetime
from typing import List, Optional, Tuple
import os


class StockDatabase:
    """股票資料庫管理類別"""

    def __init__(self, db_path: str = "stock_data.db"):
        """
        初始化資料庫連線

        Args:
            db_path: 資料庫檔案路徑
        """
        self.db_path = db_path
        self.conn = None
        self._init_database()

    def _init_database(self):
        """初始化資料庫結構"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = self.conn.cursor()

        # 建立股票價格表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                date DATE NOT NULL,
                close_price REAL NOT NULL,
                source TEXT DEFAULT 'TWSE',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, date)
            )
        """)

        # 建立索引以加速查詢
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_symbol_date
            ON stock_prices(symbol, date)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_date
            ON stock_prices(date)
        """)

        # 建立股票清單表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_list (
                symbol TEXT PRIMARY KEY,
                name TEXT,
                market TEXT,
                last_update DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 遷移：為現有資料庫新增 source 欄位
        try:
            cursor.execute("SELECT source FROM stock_prices LIMIT 1")
        except sqlite3.OperationalError:
            # source 欄位不存在，需要新增
            cursor.execute("""
                ALTER TABLE stock_prices ADD COLUMN source TEXT DEFAULT 'TWSE'
            """)
            print("已為 stock_prices 資料表新增 source 欄位")

        self.conn.commit()

    def insert_stock_prices(self, symbol: str, df: pd.DataFrame, source: str = 'TWSE'):
        """
        插入股票價格資料

        Args:
            symbol: 股票代碼
            df: 包含日期索引和 Close 欄位的 DataFrame
            source: 資料來源 (預設 'TWSE'，櫃買中心為 'TPEX')
        """
        cursor = self.conn.cursor()

        for date, row in df.iterrows():
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO stock_prices (symbol, date, close_price, source)
                    VALUES (?, ?, ?, ?)
                """, (symbol, date.strftime('%Y-%m-%d'), float(row['Close']), source))
            except Exception as e:
                print(f"插入資料錯誤 {symbol} {date}: {e}")

        self.conn.commit()

    def get_stock_prices(self, symbol: str, days: int = 120) -> pd.DataFrame:
        """
        取得股票最近 N 天的收盤價

        Args:
            symbol: 股票代碼
            days: 天數

        Returns:
            DataFrame with date index and close_price column
        """
        query = """
            SELECT date, close_price
            FROM stock_prices
            WHERE symbol = ?
            ORDER BY date DESC
            LIMIT ?
        """

        df = pd.read_sql_query(query, self.conn, params=(symbol, days))

        if df.empty:
            return pd.DataFrame()

        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        df = df.sort_index()  # 按日期升序排列

        return df

    def get_latest_date(self, symbol: str) -> Optional[datetime]:
        """
        取得股票在資料庫中的最新日期

        Args:
            symbol: 股票代碼

        Returns:
            最新日期或 None
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT MAX(date) FROM stock_prices WHERE symbol = ?
        """, (symbol,))

        result = cursor.fetchone()[0]
        if result:
            return datetime.strptime(result, '%Y-%m-%d')
        return None

    def add_stock_to_list(self, symbol: str, name: str = "", market: str = "TW"):
        """
        新增股票到清單

        Args:
            symbol: 股票代碼
            name: 股票名稱
            market: 市場代碼
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO stock_list (symbol, name, market)
            VALUES (?, ?, ?)
        """, (symbol, name, market))
        self.conn.commit()

    def get_all_symbols(self) -> List[str]:
        """
        取得所有股票代碼

        Returns:
            股票代碼列表
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT symbol FROM stock_list ORDER BY symbol")
        return [row[0] for row in cursor.fetchall()]

    def update_last_update(self, symbol: str, date: datetime):
        """
        更新股票的最後更新日期

        Args:
            symbol: 股票代碼
            date: 更新日期
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE stock_list SET last_update = ? WHERE symbol = ?
        """, (date.strftime('%Y-%m-%d'), symbol))
        self.conn.commit()

    def get_stocks_count(self) -> int:
        """取得資料庫中的股票數量"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM stock_list")
        return cursor.fetchone()[0]

    def get_price_records_count(self) -> int:
        """取得價格記錄總數"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM stock_prices")
        return cursor.fetchone()[0]

    def close(self):
        """關閉資料庫連線"""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
