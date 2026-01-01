#!/usr/bin/env python3
"""
台股相關性分析 GUI 主程式
使用 Tkinter 建立圖形化介面
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from database import StockDatabase
from correlation_engine import CorrelationEngine
from data_updater import DataUpdater
from tpex_updater import TPEXUpdater
from stock_list import get_sample_stocks


class CustomButton(tk.Frame):
    """自訂按鈕類別，支援自訂背景色"""

    def __init__(self, parent, text, command, bg="#2c3e50", fg="white", **kwargs):
        super().__init__(parent, bg=bg, **kwargs)

        self.command = command
        self.bg_normal = bg
        self.bg_hover = "#34495e"
        self.bg_active = "#1a252f"
        self.fg = fg

        # 建立按鈕標籤
        self.label = tk.Label(
            self,
            text=text,
            bg=bg,
            fg=fg,
            font=("Arial", 11, "bold"),
            padx=20,
            pady=8,
            cursor="hand2"
        )
        self.label.pack()

        # 綁定事件
        self.label.bind("<Button-1>", self._on_click)
        self.label.bind("<Enter>", self._on_enter)
        self.label.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def _on_click(self, event):
        """點擊事件"""
        self.label.config(bg=self.bg_active)
        self.config(bg=self.bg_active)
        self.after(100, lambda: self._reset_color())
        if self.command:
            self.command()

    def _on_enter(self, event):
        """滑鼠進入"""
        self.label.config(bg=self.bg_hover)
        self.config(bg=self.bg_hover)

    def _on_leave(self, event):
        """滑鼠離開"""
        self._reset_color()

    def _reset_color(self):
        """重置顏色"""
        self.label.config(bg=self.bg_normal)
        self.config(bg=self.bg_normal)

    def config_state(self, state):
        """設定按鈕狀態"""
        if state == tk.DISABLED:
            self.label.config(bg="#95a5a6", cursor="arrow")
            self.config(bg="#95a5a6")
            self.label.unbind("<Button-1>")
            self.unbind("<Button-1>")
        else:
            self.label.config(bg=self.bg_normal, cursor="hand2")
            self.config(bg=self.bg_normal)
            self.label.bind("<Button-1>", self._on_click)
            self.bind("<Button-1>", self._on_click)


class StockCorrelationApp:
    """股票相關性分析應用程式"""

    def __init__(self, root):
        """初始化應用程式"""
        self.root = root
        self.root.title("台股相關性分析系統")
        self.root.geometry("800x700")

        # 初始化資料庫
        self.db = StockDatabase()
        self.updater = DataUpdater(self.db)
        self.engine = CorrelationEngine(self.db, self.updater)
        self.tpex_updater = TPEXUpdater(self.db)

        # 建立 UI
        self.create_widgets()

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

        # 查詢區
        query_frame = tk.LabelFrame(main_frame, text="相關性查詢", padx=10, pady=10)
        query_frame.pack(fill=tk.X, pady=(0, 10))

        # 股票代碼輸入
        input_frame = tk.Frame(query_frame)
        input_frame.pack(fill=tk.X, pady=5)

        tk.Label(
            input_frame,
            text="股票代碼 1:",
            font=("Arial", 11)
        ).pack(side=tk.LEFT, padx=5)

        self.symbol1_entry = tk.Entry(input_frame, font=("Arial", 11), width=12)
        self.symbol1_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(
            input_frame,
            text="股票代碼 2:",
            font=("Arial", 11)
        ).pack(side=tk.LEFT, padx=15)

        self.symbol2_entry = tk.Entry(input_frame, font=("Arial", 11), width=12)
        self.symbol2_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(
            input_frame,
            text="(例如: 2330, 2317)",
            font=("Arial", 9),
            fg="gray"
        ).pack(side=tk.LEFT, padx=5)

        self.analyze_btn = CustomButton(
            input_frame,
            text="計算相關係數",
            command=self.analyze_correlation,
            bg="#2c3e50",
            fg="white"
        )
        self.analyze_btn.pack(side=tk.LEFT, padx=10)

        # 結果顯示區
        result_frame = tk.LabelFrame(main_frame, text="分析結果", padx=10, pady=10)
        result_frame.pack(fill=tk.BOTH, expand=True)

        # 建立結果顯示標籤
        self.result_text = tk.Text(
            result_frame,
            font=("Courier New", 12),
            height=15,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

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


    def analyze_correlation(self):
        """分析股票相關性"""
        symbol1 = self.symbol1_entry.get().strip()
        symbol2 = self.symbol2_entry.get().strip()

        if not symbol1 or not symbol2:
            messagebox.showwarning("警告", "請輸入兩個股票代碼")
            return

        if symbol1 == symbol2:
            messagebox.showwarning("警告", "兩個股票代碼不能相同")
            return

        def analyze_thread():
            try:
                self.status_label.config(text=f"正在計算 {symbol1} 與 {symbol2} 的相關係數...")
                self.root.update()

                # 執行相關性分析
                result = self.engine.calculate_two_stocks_correlation(symbol1, symbol2)

                # 顯示結果
                self.display_result(result)

                self.status_label.config(text="計算完成！")

            except ValueError as e:
                self.status_label.config(text=f"錯誤: {str(e)}")
                messagebox.showerror("錯誤", str(e))

            except Exception as e:
                self.status_label.config(text=f"計算失敗: {str(e)}")
                messagebox.showerror("錯誤", f"計算失敗: {str(e)}")
            finally:
                self.analyze_btn.config_state(tk.NORMAL)

        self.analyze_btn.config_state(tk.DISABLED)

        thread = threading.Thread(target=analyze_thread, daemon=True)
        thread.start()

    def display_result(self, result):
        """顯示分析結果"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)

        # 標題
        self.result_text.insert(tk.END, "=" * 60 + "\n")
        self.result_text.insert(tk.END, "          台股相關性分析結果\n")
        self.result_text.insert(tk.END, "=" * 60 + "\n\n")

        # 股票資訊
        self.result_text.insert(tk.END, "股票資訊\n")
        self.result_text.insert(tk.END, "-" * 60 + "\n")
        self.result_text.insert(tk.END, f"股票 1: {result['symbol1']}")
        if result['name1']:
            self.result_text.insert(tk.END, f" ({result['name1']})")
        self.result_text.insert(tk.END, "\n")

        self.result_text.insert(tk.END, f"股票 2: {result['symbol2']}")
        if result['name2']:
            self.result_text.insert(tk.END, f" ({result['name2']})")
        self.result_text.insert(tk.END, "\n\n")

        # 相關係數
        self.result_text.insert(tk.END, "相關係數\n")
        self.result_text.insert(tk.END, "-" * 60 + "\n")
        self.result_text.insert(tk.END, f"120 日相關係數: {result['corr_120']:>8.4f}\n")
        self.result_text.insert(tk.END, f" 60 日相關係數: {result['corr_60']:>8.4f}\n")
        self.result_text.insert(tk.END, f" 20 日相關係數: {result['corr_20']:>8.4f}\n\n")

        # 相關性說明
        self.result_text.insert(tk.END, "相關性說明\n")
        self.result_text.insert(tk.END, "-" * 60 + "\n")

        corr_120_strength = self.engine.format_correlation_strength(result['corr_120'])
        corr_60_strength = self.engine.format_correlation_strength(result['corr_60'])
        corr_20_strength = self.engine.format_correlation_strength(result['corr_20'])

        self.result_text.insert(tk.END, f"120 日: {corr_120_strength}\n")
        self.result_text.insert(tk.END, f" 60 日: {corr_60_strength}\n")
        self.result_text.insert(tk.END, f" 20 日: {corr_20_strength}\n\n")

        # 說明
        self.result_text.insert(tk.END, "=" * 60 + "\n")
        self.result_text.insert(tk.END, "註:\n")
        self.result_text.insert(tk.END, "  1.0 = 完全正相關\n")
        self.result_text.insert(tk.END, "  0.0 = 無相關\n")
        self.result_text.insert(tk.END, " -1.0 = 完全負相關\n")
        self.result_text.insert(tk.END, "=" * 60 + "\n")

        self.result_text.config(state=tk.DISABLED)

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
