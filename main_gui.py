#!/usr/bin/env python3
"""
台股相關性分析 GUI 主程式
使用 Tkinter 建立圖形化介面
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from datetime import datetime, timedelta
from database import StockDatabase
from correlation_engine import CorrelationEngine
from data_updater import DataUpdater
from tpex_updater import TPEXUpdater
from stock_list import get_all_taiwan_stocks, get_sample_stocks


class StockCorrelationApp:
    """股票相關性分析應用程式"""

    def __init__(self, root):
        """初始化應用程式"""
        self.root = root
        self.root.title("台股相關性分析系統")
        self.root.geometry("900x700")

        # 初始化資料庫
        self.db = StockDatabase()
        self.engine = CorrelationEngine(self.db)
        self.updater = DataUpdater(self.db)
        self.tpex_updater = TPEXUpdater(self.db)

        # 建立 UI
        self.create_widgets()

        # 更新資料庫統計
        self.update_db_stats()

    def create_widgets(self):
        """建立 UI 元件"""
        # 標題
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        title_frame.pack(fill=tk.X)

        title_label = tk.Label(
            title_frame,
            text="台股相關性分析系統",
            font=("Arial", 20, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=15)

        # 主要內容區
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 資料庫管理區
        db_frame = tk.LabelFrame(main_frame, text="資料庫管理", padx=10, pady=10)
        db_frame.pack(fill=tk.X, pady=(0, 10))

        # 資料庫統計
        self.db_stats_label = tk.Label(
            db_frame,
            text="資料庫統計: 載入中...",
            font=("Arial", 10)
        )
        self.db_stats_label.pack(side=tk.LEFT, padx=5)

        # 更新按鈕
        update_frame = tk.Frame(db_frame)
        update_frame.pack(side=tk.RIGHT)

        self.update_sample_btn = tk.Button(
            update_frame,
            text="更新範例股票資料",
            command=self.update_sample_stocks,
            bg="#3498db",
            fg="white",
            padx=10,
            pady=5
        )
        self.update_sample_btn.pack(side=tk.LEFT, padx=5)

        self.update_all_btn = tk.Button(
            update_frame,
            text="更新所有股票資料",
            command=self.update_all_stocks,
            bg="#3498db",
            fg="white",
            padx=10,
            pady=5
        )
        self.update_all_btn.pack(side=tk.LEFT, padx=5)

        self.update_tpex_btn = tk.Button(
            update_frame,
            text="更新櫃買中心資料",
            command=self.update_tpex_stocks,
            bg="#3498db",
            fg="white",
            padx=10,
            pady=5
        )
        self.update_tpex_btn.pack(side=tk.LEFT, padx=5)

        # 查詢區
        query_frame = tk.LabelFrame(main_frame, text="相關性查詢", padx=10, pady=10)
        query_frame.pack(fill=tk.X, pady=(0, 10))

        # 股票代碼輸入
        input_frame = tk.Frame(query_frame)
        input_frame.pack(fill=tk.X, pady=5)

        tk.Label(
            input_frame,
            text="股票代碼:",
            font=("Arial", 11)
        ).pack(side=tk.LEFT, padx=5)

        self.symbol_entry = tk.Entry(input_frame, font=("Arial", 11), width=15)
        self.symbol_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(
            input_frame,
            text="(例如: 2330)",
            font=("Arial", 9),
            fg="gray"
        ).pack(side=tk.LEFT, padx=5)

        self.analyze_btn = tk.Button(
            input_frame,
            text="開始分析",
            command=self.analyze_correlation,
            bg="#3498db",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=5
        )
        self.analyze_btn.pack(side=tk.LEFT, padx=10)

        # 結果顯示區
        result_frame = tk.LabelFrame(main_frame, text="分析結果", padx=10, pady=10)
        result_frame.pack(fill=tk.BOTH, expand=True)

        # 建立 Treeview 顯示結果
        columns = ("rank", "symbol", "name", "corr_120", "corr_20", "corr_10")
        self.result_tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=15)

        # 定義欄位標題
        self.result_tree.heading("rank", text="排名")
        self.result_tree.heading("symbol", text="股票代碼")
        self.result_tree.heading("name", text="名稱")
        self.result_tree.heading("corr_120", text="120日相關係數")
        self.result_tree.heading("corr_20", text="20日相關係數")
        self.result_tree.heading("corr_10", text="10日相關係數")

        # 定義欄位寬度
        self.result_tree.column("rank", width=50, anchor=tk.CENTER)
        self.result_tree.column("symbol", width=100, anchor=tk.CENTER)
        self.result_tree.column("name", width=150, anchor=tk.CENTER)
        self.result_tree.column("corr_120", width=120, anchor=tk.CENTER)
        self.result_tree.column("corr_20", width=120, anchor=tk.CENTER)
        self.result_tree.column("corr_10", width=120, anchor=tk.CENTER)

        # 添加滾動條
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_tree.yview)
        self.result_tree.configure(yscrollcommand=scrollbar.set)

        self.result_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 狀態列
        self.status_label = tk.Label(
            self.root,
            text="就緒",
            font=("Arial", 9),
            bg="#ecf0f1",
            anchor=tk.W,
            padx=10
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def update_db_stats(self):
        """更新資料庫統計資訊"""
        stock_count = self.db.get_stocks_count()
        price_count = self.db.get_price_records_count()
        self.db_stats_label.config(
            text=f"資料庫統計: {stock_count} 檔股票, {price_count:,} 筆價格記錄"
        )

    def update_sample_stocks(self):
        """更新範例股票資料"""
        def update_thread():
            try:
                self.status_label.config(text="正在更新範例股票資料...")
                self.root.update()

                stocks = get_sample_stocks()
                self.updater.update_all_stocks(stocks, days=120, delay=0.5)

                self.update_db_stats()
                self.status_label.config(text="範例股票資料更新完成")
                messagebox.showinfo("完成", "範例股票資料更新完成！")
            except Exception as e:
                self.status_label.config(text=f"更新失敗: {str(e)}")
                messagebox.showerror("錯誤", f"更新失敗: {str(e)}")
            finally:
                # 重新啟用按鈕
                self.update_sample_btn.config(state=tk.NORMAL)
                self.update_all_btn.config(state=tk.NORMAL)
                self.update_tpex_btn.config(state=tk.NORMAL)
                self.analyze_btn.config(state=tk.NORMAL)

        # 停用所有按鈕
        self.update_sample_btn.config(state=tk.DISABLED)
        self.update_all_btn.config(state=tk.DISABLED)
        self.update_tpex_btn.config(state=tk.DISABLED)
        self.analyze_btn.config(state=tk.DISABLED)

        # 在背景執行緒中執行更新
        thread = threading.Thread(target=update_thread, daemon=True)
        thread.start()

    def update_all_stocks(self):
        """更新所有股票資料"""
        # 確認對話框
        if not messagebox.askyesno(
            "確認",
            "更新所有股票資料需要較長時間（可能超過 30 分鐘），確定要繼續嗎？"
        ):
            return

        def update_thread():
            try:
                self.status_label.config(text="正在取得股票清單...")
                self.root.update()

                stocks = get_all_taiwan_stocks()
                self.status_label.config(text=f"正在更新 {len(stocks)} 檔股票資料...")
                self.root.update()

                self.updater.update_all_stocks(stocks, days=120, delay=0.5)

                self.update_db_stats()
                self.status_label.config(text="所有股票資料更新完成")
                messagebox.showinfo("完成", "所有股票資料更新完成！")

            except Exception as e:
                self.status_label.config(text=f"更新失敗: {str(e)}")
                messagebox.showerror("錯誤", f"更新失敗: {str(e)}")
            finally:
                # 重新啟用按鈕
                self.update_sample_btn.config(state=tk.NORMAL)
                self.update_all_btn.config(state=tk.NORMAL)
                self.update_tpex_btn.config(state=tk.NORMAL)
                self.analyze_btn.config(state=tk.NORMAL)

        # 停用所有按鈕
        self.update_sample_btn.config(state=tk.DISABLED)
        self.update_all_btn.config(state=tk.DISABLED)
        self.update_tpex_btn.config(state=tk.DISABLED)
        self.analyze_btn.config(state=tk.DISABLED)

        # 在背景執行緒中執行更新
        thread = threading.Thread(target=update_thread, daemon=True)
        thread.start()

    def update_tpex_stocks(self):
        """更新櫃買中心資料"""
        # 確認對話框
        if not messagebox.askyesno(
            "確認",
            "更新櫃買中心資料（最近 30 天），確定要繼續嗎？"
        ):
            return

        def update_thread():
            try:
                self.status_label.config(text="正在更新櫃買中心資料...")
                self.root.update()

                # 更新最近 30 天的資料
                count = self.tpex_updater.update_recent_days(days=30, delay=1.0)

                self.update_db_stats()
                self.status_label.config(text=f"櫃買中心資料更新完成，共 {count} 筆")
                messagebox.showinfo("完成", f"櫃買中心資料更新完成！\n共更新 {count} 筆資料")

            except Exception as e:
                self.status_label.config(text=f"更新失敗: {str(e)}")
                messagebox.showerror("錯誤", f"更新失敗: {str(e)}")
            finally:
                # 重新啟用按鈕
                self.update_sample_btn.config(state=tk.NORMAL)
                self.update_all_btn.config(state=tk.NORMAL)
                self.update_tpex_btn.config(state=tk.NORMAL)
                self.analyze_btn.config(state=tk.NORMAL)

        # 停用所有按鈕
        self.update_sample_btn.config(state=tk.DISABLED)
        self.update_all_btn.config(state=tk.DISABLED)
        self.update_tpex_btn.config(state=tk.DISABLED)
        self.analyze_btn.config(state=tk.DISABLED)

        # 在背景執行緒中執行更新
        thread = threading.Thread(target=update_thread, daemon=True)
        thread.start()

    def analyze_correlation(self):
        """分析股票相關性"""
        symbol = self.symbol_entry.get().strip()

        if not symbol:
            messagebox.showwarning("警告", "請輸入股票代碼")
            return

        def analyze_thread():
            try:
                self.status_label.config(text=f"正在分析 {symbol} 的相關性...")
                self.root.update()

                # 清空之前的結果
                for item in self.result_tree.get_children():
                    self.result_tree.delete(item)

                # 執行相關性分析
                results = self.engine.find_correlated_stocks(symbol, top_n=20)

                # 顯示結果
                for i, stock in enumerate(results, 1):
                    self.result_tree.insert("", tk.END, values=(
                        i,
                        stock['symbol'],
                        stock['name'],
                        f"{stock['corr_120']:.4f}",
                        f"{stock['corr_20']:.4f}",
                        f"{stock['corr_10']:.4f}"
                    ))

                self.status_label.config(
                    text=f"分析完成！找到 {len(results)} 檔相關股票"
                )

            except ValueError as e:
                self.status_label.config(text=f"錯誤: {str(e)}")
                messagebox.showerror("錯誤", str(e))

            except Exception as e:
                self.status_label.config(text=f"分析失敗: {str(e)}")
                messagebox.showerror("錯誤", f"分析失敗: {str(e)}")
            finally:
                # 重新啟用按鈕
                self.update_sample_btn.config(state=tk.NORMAL)
                self.update_all_btn.config(state=tk.NORMAL)
                self.update_tpex_btn.config(state=tk.NORMAL)
                self.analyze_btn.config(state=tk.NORMAL)

        # 停用所有按鈕
        self.update_sample_btn.config(state=tk.DISABLED)
        self.update_all_btn.config(state=tk.DISABLED)
        self.update_tpex_btn.config(state=tk.DISABLED)
        self.analyze_btn.config(state=tk.DISABLED)

        # 在背景執行緒中執行分析
        thread = threading.Thread(target=analyze_thread, daemon=True)
        thread.start()

    def on_closing(self):
        """視窗關閉時的處理"""
        self.db.close()
        self.root.destroy()


def main():
    """主程式入口"""
    root = tk.Tk()
    app = StockCorrelationApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
