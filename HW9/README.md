# Cloudflare Pages 專案架設與 GitHub 整合指南

本指南整合了專案目錄結構規劃、本機 Git 操作、GitHub 推送以及 Cloudflare Pages 的自動部署流程。

---

## 專案目錄結構

在開始之前，請確認專案資料夾結構如下配置：

```text
my-cf-app/
├── functions/
│   └── api/
│       └── notes.js      # 後端 Serverless API 邏輯
└── public/
    ├── index.html        # 前端網頁介面
    └── style.css         # 介面樣式表
```

---

## 一鍵建立檔案結構（終端機指令）

開啟終端機（Terminal）或命令提示字元，執行下列指令以快速建立專案結構與空檔案：

```bash
mkdir -p my-cf-app/public my-cf-app/functions/api
cd my-cf-app
touch public/index.html public/style.css functions/api/notes.js
```

---

## 本機 Git 初始化與 GitHub 推送

1. 先在 [GitHub](https://github.com/new) 上建立一個全新的儲存庫（Repository），例如命名為 `my-cf-app`（請勿勾選初始化 README）。
2. 在本地專案根目錄下，依序執行下列指令將檔案加入版本控制並推送到遠端：

```bash
# 初始化 Git 儲存庫
git init

# 將所有檔案加入暫存區並提交
git add .
git commit -m "feat: initial commit for cloudflare pages app"

# 將主要分支命名為 main
git branch -M main

# 關聯遠端儲存庫（請將 <YOUR_GITHUB_USERNAME> 與 <REPO_NAME> 換成你的資訊）
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/<REPO_NAME>.git

# 推送至 GitHub
git push -u origin main
```

---

## Cloudflare Pages 部署設定

1. 登入 [Cloudflare Dashboard](https://dash.cloudflare.com/)。
2. 在左側導覽列選取 **Workers & Pages**。
3. 點擊 **Create application** 按鈕，切換至 **Pages** 標籤。
4. 選擇 **Connect to Git** 並授權存取你的 GitHub 帳號。
5. 選擇剛才建立的儲存庫名稱。
6. 設定專案部署參數：
   - **Framework preset**：選擇 `None`
   - **Build command**：留空（純靜態與 Functions 架構不需建置指令）
   - **Build output directory**：填入 `public`
7. 點擊 **Save and Deploy**。完成後 Cloudflare 會自動指派一個 `pages.dev` 網址供即時預覽。
8. 之後只要本地使用 `git push` 更新 `main` 分支，Cloudflare 就會自動觸發重新部署。

---

## 資料持久化設定（選用 - KV 資料庫）

若應用程式需使用 Cloudflare KV 永久保存資料：

1. 前往 Cloudflare 後台的 **Workers & Pages** > **KV**。
2. 點選 **Create namespace**，建立名稱為 `NOTES_KV` 的命名空間。
3. 進入剛剛建立的 Pages 專案設定頁面：**Settings** > **Functions** > **KV namespace bindings**。
4. 點選 **Add binding**：
   - **Variable name**：`NOTES_KV`
   - **KV namespace**：選取剛建立的命名空間
5. 儲存設定後重新執行一次部署（Retry Deployment）即可生效。