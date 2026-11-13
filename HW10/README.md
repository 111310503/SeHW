# 套件發布指南

本文件說明如何將您的程式碼打包並發布至公開套件庫：Python (PyPI)、Node.js (npm) 以及 Rust (crates.io) 的完整步驟。

## 1. Python：發布至 PyPI

現代 Python 專案建議使用 `pyproject.toml` 來設定專案資訊與打包依賴。

### 發布步驟：
1. **註冊 PyPI 帳號**：前往 [pypi.org](https://pypi.org/) 註冊並在帳號設定中產生 API Token。
2. **安裝打包與上傳工具**：
   ```bash
   pip install --upgrade build twine
   ```
3. **建立發行檔案 (`.whl` 與 `.tar.gz`)**：
   在包含 `pyproject.toml` 的目錄下執行：
   ```bash
   python -m build
   ```
4. **上傳至 PyPI**：
   ```bash
   twine upload dist/*
   ```
   *(系統會提示輸入帳號密碼，帳號請填 `__token__`，密碼請貼上您的 API Token)*

---

## 2. Node.js：發布至 npm (包含 Cloudflare App)

將 Cloudflare Workers 專案發布至 npm 時，重點在於抽離核心邏輯（例如中介軟體或路由），並排除個人的環境設定檔。

### 準備工作：
- 確保 `package.json` 中的 `name` (套件名稱) 是唯一的。如果是特定範圍套件，可以加上 `@username/`。
- **務必**建立 `.npmignore` 檔案，排除 `wrangler.toml`、`.dev.vars` 及 `.wrangler/` 等敏感資訊。

### 發布步驟：
1. **登入 npm 帳號**：
   ```bash
   npm login
   ```
2. **檢查將被打包的檔案 (預演)**：
   這一步可用來確認有沒有不小心包入機密資訊。
   ```bash
   npm pack --dry-run
   ```
3. **正式發布**：
   ```bash
   npm publish --access public
   ```

---

## 3. Rust：發布至 crates.io

Rust 的官方套件管理器 Cargo 已內建完整的打包與發布功能。

### 準備工作：
- 確保 `Cargo.toml` 中已填寫 `description` 與 `license` 欄位（crates.io 的強制規定）。

### 發布步驟：
1. **取得並設定 API Token**：
   前往 [crates.io](https://crates.io/) 登入後，在 Account Settings 取得 Token，接著在終端機執行：
   ```bash
   cargo login <您的_API_TOKEN>
   ```
2. **發布前檢查 (預演)**：
   確保專案能成功編譯，且沒有未提交的 Git 變更。
   ```bash
   cargo publish --dry-run
   ```
3. **正式發布**：
   *(注意：發布至 crates.io 後無法刪除該版本，只能使用 `cargo yank` 將其標記為撤回)*
   ```bash
   cargo publish
   ```