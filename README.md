# Hi-Life Coffee 來送禮 專案說明

## 專案簡介

Hi-Life Coffee 來送禮是一個以 Django 為後端、jQuery 與現代前端技術為基礎的禮物兌換平台。用戶可以線上選購咖啡、飲品、鮮食等商品，並透過 Email 或連結將禮物分享給親友。受贈者可於門市出示條碼進行兌換，實現數位化送禮與即時兌換的便利體驗。

## 主要功能

- 商品瀏覽與選購：支援多種商品類別（咖啡、飲品、鮮食、零食等），可查詢商品資訊、價格與活動期間。
- 線上送禮：用戶可自訂送禮訊息，選擇數量並產生專屬兌換連結。
- Email 通知：自動發送兌換連結至收件者信箱，提升送禮體驗。
- 條碼兌換：受贈者於門市出示條碼即可完成兌換，支援多種條碼格式。
- 防濫用與安全性：表單驗證、CSRF 防護、訊息過濾（防止惡意網址、字數限制）。
- 管理後台：可擴充管理商品、訂單、用戶等功能。

## 技術架構

- **後端**：Python 3.x、Django
- **資料庫**：MySQL
- **前端**：HTML5、CSS3（Tailwind CSS、客製化樣式）、JavaScript（jQuery、SweetAlert2）
- **其他**：AJAX 非同步互動、CSRF 防護、Email 發送

## 專案目錄結構

```
hilifecoffee/
│
├── appcoffee/                # Django 應用程式，包含 models、views、資料庫操作等
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── db_pool.py
│   ├── encryption.py
│   ├── exchange.py
│   ├── linePayHelper.py
│   ├── models.py
│   ├── operationDatabase.py
│   ├── tests.py
│   └── ...
│
├── hilifecoffee/             # Django 專案設定
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── reportContent.txt
│
├── static/                   # 靜態資源（CSS、JS、圖片）
│   ├── css/
│   ├── img/
│   └── js/
│
├── templates/                # 前端模板
│   ├── email_template.html
│   ├── exchange.html
│   ├── index.html
│   └── share.html
│
├── manage.py
└── readme
```

## 安裝與部署

1. **環境需求**
   - Python 3.8 以上
   - MySQL 5.7 以上
   - Node.js（如需前端打包）
   - pip 套件管理工具

2. **安裝步驟**
   ```bash
   git clone <本專案網址>
   cd hilifecoffee
   python -m venv venv
   source venv/bin/activate  # Windows 用 venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **資料庫設定**
   - 建立 MySQL 資料庫與用戶，並於 `hilifecoffee/settings.py` 設定連線資訊。
   - 執行資料庫遷移：
     ```bash
     python manage.py makemigrations
     python manage.py migrate
     ```

4. **啟動伺服器**
   ```bash
   python manage.py runserver
   ```

## 資料庫設計

- 商品表（product）：儲存商品名稱、價格、圖片路徑、庫存、描述、活動期間等。
- 訂單表（order）：紀錄用戶訂購資訊、交易編號、狀態等。
- 兌換紀錄表：追蹤每筆兌換行為，防止重複兌換。
- 其他輔助表：如用戶、Email 發送紀錄等。

## 前後端互動

- 前端透過 jQuery AJAX 向後端發送資料（如送禮、兌換），後端以 JSON 格式回應。
- 表單送出時會進行前端驗證（字數、非法內容、數量等），避免不合法資料進入後端。
- 兌換連結產生後，會以 SweetAlert2 彈窗顯示，並支援一鍵複製功能。
- Email 通知採用 Django 內建郵件系統，模板美觀且支援行動裝置。

## 測試

- 內建單元測試於 `appcoffee/tests.py`，涵蓋商品、訂單、兌換等主要流程。
- 可使用 `python manage.py test` 執行測試，確保功能正確。

## 安全性與最佳實踐

- 所有表單皆有 CSRF 防護。
- 送禮訊息與暱稱皆有長度與內容過濾，防止 XSS、廣告、惡意連結。
- 資料庫操作採用 Django ORM，降低 SQL injection 風險。
- Email 僅用於通知，不做其他用途，保障用戶隱私。

## 貢獻與維護

歡迎任何建議與貢獻！請先 fork 本專案並發送 Pull Request，或於 Issues 提出問題。  
如需協助，請聯絡專案負責人或於專案頁面留言。

---

**本專案致力於提供便利、安全且美觀的數位送禮體驗，讓 Hi-Life 咖啡與好禮輕鬆傳遞每一份心意！**
