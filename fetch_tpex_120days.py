#!/usr/bin/env python3
"""
抓取櫃買中心最近 120 天的收盤價資料
"""

from datetime import datetime, timedelta
from database import StockDatabase
from tpex_updater import TPEXUpdater
import sys


def main():
    """主程式"""
    print("=" * 80)
    print("櫃買中心股票資料補齊程式")
    print("=" * 80)

    # 初始化資料庫
    print("\n正在初始化資料庫...")
    db = StockDatabase()
    updater = TPEXUpdater(db)

    # 計算日期範圍
    end_date = datetime.now()
    start_date = end_date - timedelta(days=120)

    print(f"\n目標日期範圍: {start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}")
    print(f"預計抓取: 120 天的資料")
    print(f"每次請求間隔: 2 秒（避免被封鎖）")

    # 確認是否繼續
    print("\n" + "=" * 80)
    response = input("確定要開始抓取資料嗎？(y/n): ").strip().lower()

    if response != 'y':
        print("取消操作")
        db.close()
        return

    print("\n開始抓取資料...")
    print("=" * 80)

    # 更新資料，設定 2 秒延遲
    try:
        results = updater.update_date_range(
            start_date=start_date,
            end_date=end_date,
            delay=2.0  # 2 秒間隔
        )

        # 統計結果
        total_records = sum(results.values())
        successful_days = sum(1 for count in results.values() if count > 0)

        print("\n" + "=" * 80)
        print("抓取完成！")
        print("=" * 80)
        print(f"成功抓取天數: {successful_days} / {len(results)} 天")
        print(f"總資料筆數: {total_records:,} 筆")

        # 顯示資料庫統計
        stock_count = db.get_stocks_count()
        price_count = db.get_price_records_count()

        print(f"\n資料庫最新統計:")
        print(f"  總股票數: {stock_count} 檔")
        print(f"  總價格記錄數: {price_count:,} 筆")

        # 查詢櫃買資料的日期範圍
        import sqlite3
        cursor = db.conn.cursor()
        cursor.execute("""
            SELECT
                MIN(date) as earliest,
                MAX(date) as latest,
                COUNT(DISTINCT date) as days,
                COUNT(*) as records
            FROM stock_prices
            WHERE source='TPEX'
        """)
        tpex_stats = cursor.fetchone()

        if tpex_stats and tpex_stats[0]:
            print(f"\n櫃買中心資料統計:")
            print(f"  日期範圍: {tpex_stats[0]} 至 {tpex_stats[1]}")
            print(f"  交易日數: {tpex_stats[2]} 天")
            print(f"  總記錄數: {tpex_stats[3]:,} 筆")

    except KeyboardInterrupt:
        print("\n\n使用者中斷操作")
        print("已抓取的資料已儲存至資料庫")
    except Exception as e:
        print(f"\n錯誤: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 關閉資料庫
        db.close()
        print("\n資料庫已關閉")


if __name__ == "__main__":
    main()
