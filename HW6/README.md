# Docker 微服務系統實作與學習筆記

本專案使用 Docker 與 Docker Compose 建置一套微服務系統，整合 **Nginx 反向代理**、**Node.js 後端 API** 與 **PostgreSQL 資料庫**，並提供一個輕量前端 Web 儀表板，展示容器間網路通訊、資料庫連線以及資料持久化能力。

---

## 一、 系統架構設計

本架構由三個容器服務組成，運作在同一個自訂 Docker Bridge 網路內：

```text
瀏覽器 (Browser)
       │ HTTP (:80)
       ▼
 ┌───────────────┐     /api/* (反向代理)     ┌───────────────┐
 │   app_nginx   │ ────────────────────────▶ │  app_backend  │
 │ (Web Server)  │                           │   (Node.js)   │
 └───────────────┘                           └───────┬───────┘
         │                                           │ SQL (:5432)
     靜態檔案                                         ▼
   (index.html)                              ┌───────────────┐
                                             │    app_db     │
                                             │ (PostgreSQL)  │
                                             └───────────────┘
```

1. **Nginx (Web Server & Reverse Proxy)**
   - 監聽宿主機連接埠 `80`。
   - 提供前端靜態控制台頁面。
   - 將 `/api/*` 路由的流量轉發至內部的 Node.js 容器，使後端不需向外暴露連接埠。
2. **Backend (Node.js REST API)**
   - 使用輕量化 Node.js Alpine 映像檔建置。
   - 透過 Docker 內部 DNS 域名（`db`）連線 PostgreSQL 資料庫。
   - 提供系統狀態查詢 (`GET /api/status`) 與資料讀寫介面 (`GET/POST /api/items`)。
3. **PostgreSQL (Database)**
   - 透過命名磁碟卷（Named Volume）`pgdata` 儲存資料，確保容器重啟後資料不遺失。
   - 配置健康檢查機制（Healthcheck），確保後端在資料庫完全就緒後才啟動。

---

## 二、 Docker 核心學習指令筆記

### 1. 映像檔操作 (Images)
* `docker build -t <image_name> <path>`：根據指定目錄的 Dockerfile 建置本機映像檔。
* `docker images`：檢視主機目前所有的映像檔。
* `docker rmi <image_id>`：刪除本機指定的映像檔。

### 2. 容器生命週期 (Containers)
* `docker run -d -p 80:80 --name my_app <image_name>`：背景執行容器並設定連接埠轉發。
* `docker ps`：列出執行中的容器（加入 `-a` 參數可查看包含已停止的容器）。
* `docker logs -f <container_name>`：即時追蹤容器輸出日誌，排查錯誤必備。
* `docker exec -it <container_name> sh`：進入執行中容器的終端機環境進行除錯。
* `docker stop <container_name>` / `docker start <container_name>`：停止或啟動指定容器。
* `docker rm <container_name>`：刪除已停止的容器。

### 3. 多容器編排 (Docker Compose)
* `docker compose up -d`：背景啟動 compose 檔案定義的所有服務。
* `docker compose up --build -d`：強制重新建置映像檔並在背景啟動服務。
* `docker compose ps`：檢視當前服務叢集的健康狀態與連接埠對應。
* `docker compose down`：停止並移除所有服務容器與虛擬網路。
* `docker compose down -v`：停止服務並徹底清除持久化磁碟卷（Volume）。

---

## 三、 專案目錄結構

```text
.
├── docker-compose.yml       # 多容器編排設定檔
├── README.md                # 專案實作紀錄與操作指南
├── backend/
│   ├── Dockerfile           # 後端 Node.js 容器建置腳本
│   ├── package.json         # Node.js 依賴定義
│   └── server.js            # Express API 與資料庫連線程式碼
├── nginx/
│   ├── nginx.conf           # Nginx 反向代理配置檔
│   └── html/
│       └── index.html       # 簡易 Web 展示介面
└── db/
    └── init.sql             # 資料庫初始 Table 與預設資料
```

---

## 四、 快速啟動指南

### 前置需求
* 已安裝 [Docker Desktop](https://www.docker.com/products/docker-desktop/) 或 Docker Engine 與 Compose 插件。

### 操作步驟

1. **一鍵建置並背景啟動服務**：
   ```bash
   docker compose up --build -d
   ```

2. **確認容器狀態**：
   ```bash
   docker compose ps
   ```
   *確認 `app_db` 狀態為 `healthy`，`app_backend` 與 `app_nginx` 狀態為 `Up`。*

3. **開啟展示介面**：
   * 打開瀏覽器訪問：[http://localhost](http://localhost)
   * 儀表板將自動取得後端執行資訊（Node.js 版本、容器 Hostname）。
   * 可以在介面輸入文字並點擊「寫入資料庫」，測試跨容器寫入與查詢功能。
   * API 健康檢查直接測試：[http://localhost/api/status](http://localhost/api/status)

4. **停止微服務**：
   ```bash
   # 保留資料庫數據停止服務
   docker compose down

   # 停止並清除所有資料庫數據（重置環境）
   docker compose down -v
   ```