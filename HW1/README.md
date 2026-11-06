# mycurl - 輕量級 HTTP 命令列工具

`mycurl` 是一個以 Python 3 原生標準函式庫實作的命令列工具，旨在模擬常見的 `curl` 核心功能。本專案不依賴任何外部第三方套件（例如 requests、httpx），隨處可用。

---

## 🌟 功能特性

- **多種 HTTP 請求方法**：支援 `GET`、`POST`、`PUT`、`DELETE`、`PATCH`、`HEAD`。
- **自訂 HTTP 標頭**：支援使用多組 `-H / --header` 帶入自訂標頭。
- **資料傳輸 Payload**：使用 `-d / --data` 傳送字串或 JSON 資料。
- **重新導向支援**：透過 `-L / --location` 自動跟隨 HTTP 3xx 重新導向。
- **除錯與檢查**：
  - `-i / --include`：在輸出內容上方包含 HTTP 回應標頭。
  - `-v / --verbose`：顯示類似 curl 的詳細通訊軌跡（`>` 代表發出，`<` 代表接收）。
- **檔案寫入**：使用 `-o / --output` 將伺服器回應寫入本地檔案。
- **超時設定**：使用 `-m / --max-time` 自訂連線與讀取超時秒數。

---

## 🚀 快速開始

### 環境需求
* Python 3.8 或以上版本（無需 `pip install` 任何套件）

### 執行權限（Linux / macOS）
```bash
chmod +x mycurl.py
```

---

## 📖 使用範例

### 1. 基本 GET 請求
```bash
python3 mycurl.py https://httpbin.org/get
# 或者（若已加執行權限）
./mycurl.py https://httpbin.org/get
```

### 2. 顯示回應標頭 (`-i`) 或完整通訊軌跡 (`-v`)
```bash
# 包含回應狀態碼與 Header
python3 mycurl.py -i https://httpbin.org/get

# 顯示詳細連線請求與回應日誌
python3 mycurl.py -v https://httpbin.org/get
```

### 3. POST JSON 資料與自訂標頭 (`-X`, `-H`, `-d`)
```bash
python3 mycurl.py -X POST https://httpbin.org/post \
  -H "Content-Type: application/json" \
  -d '{"username": "demo_user", "action": "login"}'
```

### 4. 跟隨 3xx 重新導向 (`-L`)
```bash
python3 mycurl.py -L https://httpbin.org/redirect/2
```

### 5. 下載並儲存為本地檔案 (`-o`)
```bash
python3 mycurl.py -o result.json https://httpbin.org/json
```

---

## 參數對照表

| 參數 | 全稱 | 說明 |
| :--- | :--- | :--- |
| `-X` | `--request` | 指定 HTTP 請求方法（預設 `GET`） |
| `-H` | `--header` | 自訂 HTTP Header（可重複使用） |
| `-d` | `--data` | 傳送的 Body 資料（自動將預設請求轉為 `POST`） |
| `-L` | `--location` | 跟隨 HTTP 3xx 重新導向 |
| `-i` | `--include` | 輸出包含回應標頭 |
| `-v` | `--verbose` | 顯示連線詳細除錯訊息 |
| `-o` | `--output` | 將回應寫入指定檔案 |
| `-m` | `--max-time` | 請求超時秒數（預設 30 秒） |