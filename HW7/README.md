# Web 應用三重測試實戰手冊 (Unit + System API + E2E Playwright)

本文件解說如何為 Web 系統建立三層測試防禦網：**單元測試 (Unit Test)**、**系統測試 (System/API Test)** 以及 **端到端無頭瀏覽器測試 (E2E Test)**。

---

## 1. 測試架構金字塔 (Testing Pyramid)

```text
         / \
        /   \      E2E 測試 (Playwright Headless Browser)
       /  ▲  \     模擬真實使用者點擊、表單提交、DOM 與樣式渲染
      /───────\
     /    ▲    \   系統測試 (Web API Integration Test)
    /           \  驗證路由、HTTP 狀態碼、Payload、Header 與異常回傳
   /─────────────\
  /       ▲       \ 單元測試 (Server Unit Test)
 /                 \ 驗證後端純商業邏輯（計算、邊界條件、狀態轉換）
─────────────────────
```

### 三種測試的職責劃分

| 測試類型 | 測試範圍 | 執行速度 | 關注點 |
| :--- | :--- | :--- | :--- |
| **單元測試 (Unit Test)** | 伺服器核心服務 (`Task`, `TaskService`) | 最快 (毫秒級) | 純邏輯正確性、邊界值、例外拋出（空標題等）。後端伺服器（如 Rust / Python）邏輯必須 100% 覆蓋。 |
| **系統測試 (Web API Test)** | API 端點 (`/api/tasks`, `/api/tasks/{id}`) | 快 (直接走 ASGI 記憶體堆疊) | 驗證 HTTP 協定、狀態碼 (201, 400, 404)、JSON 序列化與反序列化。 |
| **E2E 測試 (End-to-End)** | 前後端完整整合 (`Chromium Headless`) | 較慢 (秒級) | 模擬真實瀏覽器操作：輸入文字、觸發事件、異步 AJAX 載入、DOM 節點劃線樣式與元素移除。 |

---

## 2. 環境安裝

請使用 Python 3.8+，並安裝測試與 Web 依賴套件：

```bash
# 安裝 Web 框架與測試工具
pip install fastapi uvicorn pydantic pytest httpx starlette playwright

# 安裝 Playwright 所需之無頭瀏覽器核心 (Chromium)
playwright install chromium
```

---

## 3. 執行測試的三種方式

### 方式 1：一鍵執行三種測試
直接執行 Python 主程式，將自動觸發 pytest 執行所有測試類別：

```bash
python app_and_tests.py
```

### 方式 2：使用 pytest 執行並輸出詳細結果
```bash
# 執行該檔案中的所有測試並顯示詳細輸出
pytest app_and_tests.py -v

# 僅執行伺服器端「單元測試」
pytest app_and_tests.py -k "TestTaskServiceUnit" -v

# 僅執行「Web API 系統測試」
pytest app_and_tests.py -k "TestWebApiSystem" -v

# 僅執行「Playwright E2E 無頭瀏覽器測試」
pytest app_and_tests.py -k "test_e2e_full_user_flow" -v -s
```

### 方式 3：手動啟動 Web 服務並進行人工瀏覽
若想實際檢視前端網頁介面：
```bash
python app_and_tests.py runserver
```
開啟瀏覽器訪問：[http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 4. 測試程式碼核心剖析

### (1) 單元測試：純粹隔離的 Server 邏輯
* 不啟動任何 Web 伺服器、不發起 HTTP 請求。
* 測試類別 `TestTaskServiceUnit` 直接針對 `TaskService` 驗證任務建立、切換狀態 (`toggle`) 及拋出 `ValueError`。

### (2) 系統測試：完整的 API 契約校驗
* 採用 `starlette.testclient.TestClient`，在記憶體中模擬真實 HTTP 請求。
* 測試類別 `TestWebApiSystem` 驗證建立成功回傳 `201 Created`，惡意空白字串回傳 `400 Bad Request`，查詢不存在資源回傳 `404 Not Found`。

### (3) E2E 測試：無頭瀏覽器模擬真實操作
* 測試函式 `test_e2e_full_user_flow` 透過後台執行緒啟動 `uvicorn` 本地服務。
* 使用 `playwright.sync_api` 啟動無頭 Chromium：
  1. `page.goto(live_server)`：載入頁面。
  2. `page.locator("#task-input").fill(...)`：模擬使用者敲擊鍵盤。
  3. `page.locator("#add-btn").click()`：觸發點擊事件並發出 AJAX。
  4. `page.wait_for_selector("#task-title-1.completed")`：驗證 UI 是否正確變更 CSS 類別（劃線刪除效果）。
  5. `page.locator("#task-item-1").wait_for(state="detached")`：驗證 DOM 節點已被徹底移除。