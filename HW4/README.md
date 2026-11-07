# Git 與 GitHub 核心工作流程操作指南

本說明文件詳細記錄在日常版本控制與開源協作中，如何透過 **Git 指令列 (CLI)** 以及 **GitHub 網頁介面 (Web UI)** 實作「**分支 (Branch)**」、「**合併 (Merge)**」、「**分叉 (Fork)**」與「**拉取請求 (Pull Request)**」四大核心操作。

---

## 目錄
1. [分支 (Branch)](#1-分支-branch)
2. [合併 (Merge)](#2-合併-merge)
3. [分叉 (Fork)](#3-分叉-fork)
4. [拉取請求 (Pull Request, PR)](#4-拉取請求-pull-request-pr)
5. [四大操作綜合協作流程圖](#5-四大操作綜合協作流程圖)

---

## 1. 分支 (Branch)

分支能讓你在不影響主線（如 `main` 或 `master`）的情況下，獨立開發新功能或修復問題。

### 方法 A：使用 Git 指令列 (CLI)
1. **建立新分支**：
   ```bash
   git branch feature/user-auth
   ```
2. **切換至該分支**：
   ```bash
   git checkout feature/user-auth
   ```
   > **快速寫法（建立並立即切換）**：
   > ```bash
   > git checkout -b feature/user-auth
   > # 或使用較新的指令：
   > git switch -c feature/user-auth
   > ```

3. **推送新分支至 GitHub 遠端儲存庫**：
   ```bash
   git push -u origin feature/user-auth
   ```

### 方法 B：在 GitHub 網頁上操作
1. 進入目標專案倉庫首頁。
2. 點擊檔案列表左上方的分支下拉選單（預設通常顯示 **`main`**）。
3. 在搜尋框中輸入新分支名稱（如 `feature/user-auth`）。
4. 點選下拉選單底部的 **`Create branch: feature/user-auth from 'main'`** 即可完成建立。

---

## 2. 合併 (Merge)

當功能分支開發完成並通過測試後，將其更動整合回主線分支。

### 方法 A：使用 Git 指令列 (CLI)
1. **切換回接收更動的目標分支（通常為 `main`）**：
   ```bash
   git checkout main
   # 或
   git switch main
   ```
2. **拉取遠端最新進度，避免衝突**：
   ```bash
   git pull origin main
   ```
3. **將功能分支合併進來**：
   ```bash
   git merge feature/user-auth
   ```
   *(若發生衝突 Conflict，需手動編輯衝突標記檔案，執行 `git add <衝突檔案>`，再輸入 `git commit` 完成合併)*
4. **將合併後的狀態推送到遠端**：
   ```bash
   git push origin main
   ```
5. *(選用) 刪除已完成合併的功能分支*：
   ```bash
   git branch -d feature/user-auth           # 刪除本地分支
   git push origin --delete feature/user-auth # 刪除遠端分支
   ```

### 方法 B：在 GitHub 網頁上操作
在 GitHub 團隊協作中，分支合併多半透過 **Pull Request** 審核後點選 **`Merge pull request`** 按鈕完成（詳見第 4 節）。

---

## 3. 分叉 (Fork)

Fork 是將**他人的公開儲存庫**完整複製一份到「自己的 GitHub 帳號」下，讓你有完整權限自由修改，是參與開源專案與外部貢獻的第一步。

> **注意**：Fork 是 GitHub 提供的雲端服務操作，**無法**單純用本機純 Git 原生指令完成。

### GitHub 網頁操作步驟
1. 打開想要貢獻的第三方專案頁面（例如：`https://github.com/upstream-owner/project-repo`）。
2. 在頁面右上角找到並點擊 **`Fork`** 按鈕。
3. 選擇要 Fork 的目標帳號（你的個人帳號），並確認儲存庫名稱。
4. 點選 **`Create fork`**。
5. 稍等數秒後，你的帳號下就會出現 `https://github.com/your-username/project-repo` 的完整副本。

### 本地終端機設定（取得 Fork 專案後）
為了與原專案同步，建議將專案 Clone 下來後設定原作者的 `upstream` 遠端位址：
```bash
# 1. 複製自己帳號下的 Fork 專案到本地電腦
git clone https://github.com/your-username/project-repo.git
cd project-repo

# 2. 設定原專案為 upstream 遠端位址
git remote add upstream https://github.com/upstream-owner/project-repo.git

# 3. 檢查遠端位址設定 (確認包含 origin 與 upstream)
git remote -v
```

---

## 4. 拉取請求 (Pull Request, PR)

當你在自己 Fork 的專案（或同一個專案的功能分支）完成修改後，發出 PR 請求原專案的維護者審查並「拉取（Pull）」你的程式碼合併進主專案。

### 操作步驟與指令流程

#### 步驟 1：在本地建立分支並提交修改
```bash
# 切出新分支進行修改
git checkout -b fix/login-bug

# 修改檔案後提交暫存與 Commit
git add .
git commit -m "fix: 修復登入逾時的驗證問題"

# 推送到「自己的」GitHub 遠端儲存庫
git push -u origin fix/login-bug
```

#### 步驟 2：在 GitHub 上發起 Pull Request (PR)
1. 回到 GitHub 網頁，進入你的儲存庫頁面。
2. 系統通常會自動彈出黃色提示條，顯示剛剛推送的分支，點擊 **`Compare & pull request`**。  
   *(若無提示，可點擊 **`Pull requests`** 標籤頁 -> 點擊綠色 **`New pull request`** 按鈕)*
3. **比對分支設定 (Base vs Compare)**：
   - **Base repository / Base branch**：目標接收更動的專案與主分支（例如 `upstream-owner/project-repo` 的 `main`）。
   - **Head repository / Compare branch**：你做了更動的專案與分支（例如 `your-username/project-repo` 的 `fix/login-bug`）。
4. 填寫 PR 的 **Title (標題)** 與 **Description (詳細修改說明與 PR 目的)**。
5. 點擊 **`Create pull request`** 綠色按鈕正式送出。

#### 步驟 3：專案維護者審查與合併 (Review & Merge)
1. 專案維護者收到 PR 通知，進行 Code Review 與討論。
2. 審查通過後，維護者點擊 **`Merge pull request`** 並點選 **`Confirm merge`**。
3. 你的程式碼即成功合併進原專案主線。

---

## 5. 四大操作綜合協作流程圖

```text
[ 原專案 (Upstream Repository) ]
               │
           3. Fork (複製到個人帳號)
               ▼
[ 個人遠端專案 (Origin Repository) ]
               │
          git clone (下載到本地)
               ▼
[ 本地工作目錄 (Local Machine) ]
               │
    1. git checkout -b feature-x (建立分支)
       git commit (修改並提交)
       git push origin feature-x (推回個人遠端)
               │
               ▼
[ 個人遠端專案 (Origin: feature-x) ]
               │
        4. 發起 Pull Request
               ▼
[ 原專案 (Upstream: main) ]
               │
        2. Merge Pull Request (審核通過並合併)
```