# 台股相關性分析系統

這是一個完整的台灣股市股票相關性分析系統，可以找出與指定股票最相關的其他股票。

## 功能特色

- 自動從 yfinance 抓取台股股價資料
- SQLite 資料庫儲存，支援增量更新
- 計算 120 日、20 日、10 日的相關係數
- 多層排序（優先 120 日，其次 20 日，最後 10 日）
- 圖形化介面（Tkinter），操作簡便
- 支援範例股票快速測試

## 系統需求

- Python 3.8 或以上版本
- 網路連線（用於抓取股價資料）

## 安裝步驟

1. 確保已啟用虛擬環境：

```bash
source .venv/bin/activate  # macOS/Linux
# 或
.venv\Scripts\activate  # Windows
```

2. 安裝所需套件：

```bash
uv pip install -r requirements.txt
```

或使用一般 pip：

```bash
pip install -r requirements.txt
```

## 使用方法

### 方法一：使用 GUI 圖形介面（推薦）

執行主程式：

```bash
python3 main_gui.py
```

程式介面說明：

1. **資料庫管理區**

   - 顯示目前資料庫中的股票數量和價格記錄數
   - 「更新範例股票資料」：更新 20 檔常見股票（台積電、鴻海等）
   - 「更新所有股票資料」：更新所有台股（需時較長，約 30 分鐘以上）

2. **相關性查詢區**

   - 輸入股票代碼（例如：2330）
   - 點擊「開始分析」
   - 系統會計算並顯示前 20 檔最相關的股票

3. **分析結果區**
   - 以表格顯示排序後的結果
   - 包含股票代碼、名稱、120 日/20 日/10 日相關係數

### 方法二：命令列測試

執行測試腳本：

```bash
python3 test_system.py
```

此腳本會：

1. 自動更新範例股票資料
2. 執行相關性分析測試
3. 顯示完整的分析結果

### 方法三：使用舊版簡易工具

執行原始的兩股相關性計算工具：

```bash
python3 stock_correlation.py
```

此工具僅計算兩個指定股票之間的相關係數。

## 專案結構

```
stock-tools/
├── PRD.md                   # 產品需求文件
├── README.md                # 本文件
├── requirements.txt         # Python 套件依賴
│
├── main_gui.py              # GUI 主程式（Tkinter）
├── test_system.py           # 系統測試腳本
│
├── database.py              # SQLite 資料庫管理模組
├── stock_list.py            # 台股代碼清單模組
├── data_updater.py          # 股價資料更新模組
├── correlation_engine.py    # 相關係數計算引擎
│
├── stock_correlation.py     # 舊版簡易工具
└── stock_data.db            # SQLite 資料庫檔案（自動產生）
```

## 使用範例

### 範例 1：首次使用

```bash
# 啟動 GUI
python3 main_gui.py

# 在 GUI 中：
# 1. 點擊「更新範例股票資料」（等待約 1-2 分鐘）
# 2. 輸入股票代碼：2330
# 3. 點擊「開始分析」
# 4. 查看與台積電最相關的 20 檔股票
```

### 範例 2：更新所有台股資料

```bash
# 啟動 GUI
python3 main_gui.py

# 在 GUI 中：
# 1. 點擊「更新所有股票資料」
# 2. 確認對話框（此操作需時較長）
# 3. 等待更新完成（可能需要 30 分鐘以上）
```

### 範例 3：命令列測試

```bash
# 執行測試腳本
python3 test_system.py

# 輸出範例：
# ================================================================================
# 與 2330.TW 相關性最高的前 10 檔股票
# ================================================================================
# 排名   代碼           名稱         120日       20日        10日
# --------------------------------------------------------------------------------
# 1    2881.TW      富邦金           0.8992    0.5134    0.3037
# 2    2317.TW      鴻海            0.8791    0.5309    0.8212
# ...
```

## 技術說明

### 相關係數計算

使用 Pandas 的 `corr()` 方法計算皮爾森相關係數：

- **1.0**：完全正相關（兩股票完全同步上漲下跌）
- **0.7**：強正相關
- **0.4**：中等正相關
- **0.0**：無相關
- **-0.4**：中等負相關
- **-0.7**：強負相關
- **-1.0**：完全負相關（一漲一跌）

### 排序邏輯

採用多層排序（Multi-level sorting）：

1. 首先按 120 日相關係數由高至低排序
2. 若 120 日相關係數相同，則比較 20 日相關係數
3. 若 20 日相關係數也相同，則比較 10 日相關係數

### 資料更新機制

- 採用增量更新策略
- 檢查資料庫中的最新日期
- 只抓取缺少的日期區間
- 避免重複下載，節省時間

### 資料來源

使用 yfinance 套件從 Yahoo Finance 取得台股資料：

- 上市股票代碼格式：`2330.TW`
- 上櫃股票代碼格式：`6488.TWO`

## 常見問題

### Q: 為什麼某些股票找不到資料？

A: 可能原因：

1. 股票代碼錯誤
2. 該股票尚未加入資料庫（需先更新資料）
3. Yahoo Finance 無此股票資料

### Q: 更新資料需要多久時間？

A:

- 範例股票（20 檔）：約 1-2 分鐘
- 所有台股（約 2000 檔）：約 30-60 分鐘

### Q: 資料庫檔案會很大嗎？

A:

- 範例股票：約 1-2 MB
- 所有台股：約 100-200 MB

### Q: 可以自訂要分析的股票清單嗎？

A: 可以。修改 `stock_list.py` 中的 `get_sample_stocks()` 函數，加入你想要的股票代碼。

### Q: 相關係數計算不準確怎麼辦？

A: 確保：

1. 資料已更新至最新
2. 兩檔股票都有足夠的交易日資料
3. 計算週期內沒有太多缺漏值

## 注意事項

1. **網路連線**：需要穩定的網路連線來抓取股價資料
2. **API 限制**：Yahoo Finance 有速率限制，請勿過於頻繁請求
3. **資料延遲**：股價資料可能有 15 分鐘延遲
4. **免責聲明**：本系統僅供學習與研究使用，不構成投資建議

## 開發者資訊

### 測試資料庫模組

```bash
python3 -c "from database import StockDatabase; db = StockDatabase(); print(f'Stock count: {db.get_stocks_count()}'); db.close()"
```

### 測試資料更新

```bash
python3 -c "from database import StockDatabase; from data_updater import DataUpdater; db = StockDatabase(); updater = DataUpdater(db); updater.update_stock('2330.TW'); db.close()"
```

### 測試相關性計算

```bash
python3 -c "from database import StockDatabase; from correlation_engine import CorrelationEngine; db = StockDatabase(); engine = CorrelationEngine(db); results = engine.find_correlated_stocks('2330.TW', 5); print(results); db.close()"
```

## 版本歷史

- **v2.0** - 2025-12-25

  - 完整重寫，加入 SQLite 資料庫
  - 支援所有台股
  - 增量更新機制
  - Tkinter GUI 介面
  - 多層排序功能

- **v1.0** - 2025-12-25
  - 初始版本
  - 簡易的兩股相關性計算工具

## 授權

本專案僅供學習與研究使用。

---

**最後更新：2025-12-25**
