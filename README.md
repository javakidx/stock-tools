# 台股相關性分析系統

這是一個台灣股市股票相關性分析工具，可以計算兩檔股票之間的相關係數。

## 功能特色

- 計算兩檔股票在 120 日、60 日、20 日的相關係數
- 自動從 yfinance 抓取台股股價資料
- SQLite 資料庫儲存，支援增量更新
- 圖形化介面（Tkinter），操作簡便
- 支援範例股票快速測試
- 顯示相關性強度說明（極強/強/中等/弱/極弱）

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

### GUI 圖形介面（推薦）

執行主程式：

```bash
python3 main_gui.py
```

程式介面說明：

1. **資料庫管理區**
   - 顯示目前資料庫中的股票數量和價格記錄數
   - 「更新範例股票資料」：更新 20 檔常見股票（台積電、鴻海等）
   - 「更新櫃買中心資料」：更新櫃買中心股票資料

2. **相關性查詢區**
   - 輸入兩個股票代碼（例如：2330 和 2317）
   - 點擊「計算相關係數」
   - 系統會計算並顯示這兩檔股票的相關係數

3. **分析結果區**
   - 顯示兩檔股票的詳細資訊
   - 顯示 120 日、60 日、20 日的相關係數
   - 顯示相關性強度說明

### 使用範例

#### 範例 1：首次使用

```bash
# 啟動 GUI
python3 main_gui.py

# 在 GUI 中：
# 1. 點擊「更新範例股票資料」（等待約 1-2 分鐘）
# 2. 輸入股票代碼 1：2330
# 3. 輸入股票代碼 2：2317
# 4. 點擊「計算相關係數」
# 5. 查看台積電與鴻海的相關係數
```

#### 範例 2：命令列測試

```bash
source .venv/bin/activate

python3 -c "
from database import StockDatabase
from correlation_engine import CorrelationEngine

db = StockDatabase()
engine = CorrelationEngine(db)

# 計算台積電和鴻海的相關係數
result = engine.calculate_two_stocks_correlation('2330', '2317')

print(f'股票 1: {result[\"symbol1\"]} ({result[\"name1\"]})')
print(f'股票 2: {result[\"symbol2\"]} ({result[\"name2\"]})')
print(f'120 日相關係數: {result[\"corr_120\"]:.4f}')
print(f' 60 日相關係數: {result[\"corr_60\"]:.4f}')
print(f' 20 日相關係數: {result[\"corr_20\"]:.4f}')

db.close()
"
```

## 專案結構

```
stock-tools/
├── PRD.md                   # 產品需求文件
├── README.md                # 本文件
├── requirements.txt         # Python 套件依賴
│
├── main_gui.py              # GUI 主程式（Tkinter）
│
├── database.py              # SQLite 資料庫管理模組
├── stock_list.py            # 台股代碼清單模組
├── data_updater.py          # 股價資料更新模組
├── correlation_engine.py    # 相關係數計算引擎
├── tpex_updater.py          # 櫃買中心資料更新模組
│
└── stock_data.db            # SQLite 資料庫檔案（自動產生）
```

## 技術說明

### 相關係數計算

使用 Pandas 的 `corr()` 方法計算皮爾森相關係數（Pearson Correlation Coefficient）：

- **1.0**：完全正相關（兩股票完全同步上漲下跌）
- **0.7 ~ 0.9**：強正相關
- **0.4 ~ 0.7**：中等正相關
- **0.0 ~ 0.4**：弱正相關
- **0.0**：無相關
- **-0.4 ~ 0.0**：弱負相關
- **-0.7 ~ -0.4**：中等負相關
- **-0.9 ~ -0.7**：強負相關
- **-1.0**：完全負相關（一漲一跌）

### 計算週期

系統計算三個不同時間週期的相關係數：

- **120 日**：長期趨勢相關性（約 6 個月）
- **60 日**：中期趨勢相關性（約 3 個月）
- **20 日**：短期趨勢相關性（約 1 個月）

### 資料更新機制

- 採用增量更新策略
- 檢查資料庫中的最新日期
- 只抓取缺少的日期區間
- 避免重複下載，節省時間

### 資料來源

使用 yfinance 套件從 Yahoo Finance 取得台股資料：

- 上市股票代碼格式：`2330.TW`
- 上櫃股票代碼格式：`6488.TWO`

程式會自動為股票代碼添加正確的後綴。

## 常見問題

### Q: 為什麼某些股票找不到資料？

A: 可能原因：
1. 股票代碼錯誤
2. 該股票尚未加入資料庫（需先更新資料）
3. Yahoo Finance 無此股票資料

### Q: 更新資料需要多久時間？

A:
- 範例股票（20 檔）：約 1-2 分鐘
- 櫃買中心資料（30 天）：約 5-10 分鐘

### Q: 資料庫檔案會很大嗎？

A:
- 範例股票：約 1-2 MB
- 完整資料庫：約 100-200 MB

### Q: 相關係數為什麼會不同週期差異很大？

A: 這是正常現象。股票在不同時間週期可能展現不同的相關性：
- 長期（120日）可能因產業趨勢而相關
- 短期（20日）可能因個別事件而相關性降低

### Q: 兩個股票代碼可以相同嗎？

A: 不可以。系統會檢查並提示錯誤。一個股票與自己的相關係數永遠是 1.0。

## 注意事項

1. **網路連線**：需要穩定的網路連線來抓取股價資料
2. **API 限制**：Yahoo Finance 有速率限制，請勿過於頻繁請求
3. **資料延遲**：股價資料可能有延遲
4. **資料品質**：若某個週期的資料不足 70%，相關係數會顯示為 0.0
5. **免責聲明**：本系統僅供學習與研究使用，不構成投資建議

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
python3 -c "from database import StockDatabase; from correlation_engine import CorrelationEngine; db = StockDatabase(); engine = CorrelationEngine(db); result = engine.calculate_two_stocks_correlation('2330', '2317'); print(result); db.close()"
```

## API 說明

### CorrelationEngine.calculate_two_stocks_correlation()

計算兩檔股票之間的相關係數。

**參數**：
- `symbol1` (str): 第一檔股票代碼
- `symbol2` (str): 第二檔股票代碼

**返回值**：
```python
{
    'symbol1': str,      # 股票1代碼（含後綴）
    'symbol2': str,      # 股票2代碼（含後綴）
    'name1': str,        # 股票1名稱
    'name2': str,        # 股票2名稱
    'corr_120': float,   # 120日相關係數
    'corr_60': float,    # 60日相關係數
    'corr_20': float     # 20日相關係數
}
```

**錯誤處理**：
- 若股票資料不存在，拋出 `ValueError`

## 版本歷史

- **v3.0** - 2025-12-31
  - 完全重寫為符合 PRD 需求
  - 改為計算兩檔股票的相關係數
  - 計算週期改為 120 日、60 日、20 日
  - 簡化介面，專注於兩檔股票比較

- **v2.0** - 2025-12-25
  - 完整重寫，加入 SQLite 資料庫
  - 支援所有台股
  - 增量更新機制
  - Tkinter GUI 介面

- **v1.0** - 2025-12-25
  - 初始版本
  - 簡易的兩股相關性計算工具

## 授權

本專案僅供學習與研究使用。

---

**最後更新：2025-12-31**
