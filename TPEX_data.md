# 產品描述

寫一個程式，抓取台灣櫃買市場股票的收盤價，儲存到現有的 stock_data.db 的 SQLite 資料庫中。

## 系統需求

### 櫃買中心的收盤價取得

使用下列網址：https://www.tpex.org.tw/www/zh-tw/afterTrading/dailyQuotes?date=2025/12/23&id=&response=json，其中參數data為日期，response為回傳回應的格式。要抓取的收盤價，在回應的payload中的tables.data中，在data下，每一個Array是一個股票的資料，Array中第一個元素是股票代號，第二個元素是股票名稱，而第三個元素是我要收集收盤價。

### 資料儲存

#### 修改現有的 stock_prices 資料表，新增一個欄位 source 來註明資料來源，上列抓取的資料來源設為 TPEX

#### 將上列抓取的資料存入現有的資料表中

### 在嘗試抓取櫃買中心的資料時，列出抓取的樣本，讓我確認抓取的欄位是否正確
