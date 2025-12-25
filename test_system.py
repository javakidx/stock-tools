#!/usr/bin/env python3
"""
系統測試腳本
測試完整的相關性分析流程
"""

from database import StockDatabase
from data_updater import DataUpdater
from correlation_engine import CorrelationEngine
from stock_list import get_sample_stocks


def test_full_workflow():
    """測試完整工作流程"""
    print("=" * 80)
    print("台股相關性分析系統測試")
    print("=" * 80)

    with StockDatabase() as db:
        updater = DataUpdater(db)
        engine = CorrelationEngine(db)

        # 1. 取得範例股票清單（前10檔測試）
        print("\n[步驟 1] 取得股票清單")
        stocks = get_sample_stocks()[:10]
        print(f"  準備更新 {len(stocks)} 檔股票")

        # 2. 更新股價資料
        print("\n[步驟 2] 更新股價資料")
        updater.update_all_stocks(stocks, days=120, delay=0.3)

        # 3. 顯示資料庫統計
        print("\n[步驟 3] 資料庫統計")
        print(f"  股票數量: {db.get_stocks_count()}")
        print(f"  價格記錄數: {db.get_price_records_count()}")

        # 4. 測試相關性分析
        print("\n[步驟 4] 相關性分析測試")
        target = "2330.TW"
        print(f"  分析目標: {target} (台積電)")

        try:
            results = engine.find_correlated_stocks(target, top_n=10)

            print("\n" + "=" * 80)
            print(f"與 {target} 相關性最高的前 10 檔股票")
            print("=" * 80)
            print(f"{'排名':<4} {'代碼':<12} {'名稱':<10} {'120日':<10} {'20日':<10} {'10日':<10}")
            print("-" * 80)

            for i, stock in enumerate(results, 1):
                print(
                    f"{i:<4} {stock['symbol']:<12} {stock['name']:<10} "
                    f"{stock['corr_120']:>9.4f} {stock['corr_20']:>9.4f} {stock['corr_10']:>9.4f}"
                )

            print("=" * 80)
            print("\n✓ 測試完成！所有功能正常運作")

        except Exception as e:
            print(f"\n✗ 相關性分析失敗: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    test_full_workflow()
