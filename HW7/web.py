"""
多層級測試示範專案 (Unit Test + Web API Integration Test + Playwright Headless E2E Test)
功能應用：精簡型待辦清單/任務管理 Web 系統 (Task Manager)
包含：
1. 伺服器端核心業務邏輯 (可獨立執行單元測試的純 Python 領域模型)
2. FastAPI Web 應用與 REST API (提供前後端與 API 端點)
3. 第一層：單元測試 (Server Unit Tests - 驗證領域邏輯與邊界條件)
4. 第二層：系統測試 / 整合測試 (Web API System Tests - 使用 FastAPI TestClient 模擬 HTTP 交互)
5. 第三層:E2E 端到端測試 (Headless Browser E2E - 使用 Playwright 驅動真實無頭瀏覽器測試完整操作流程)
"""

import sys
import threading
import time
from typing import Dict, List, Optional
import uvicorn
import fastapi
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import pytest
from starlette.testclient import TestClient

# =====================================================================
# 1. 核心業務邏輯模組 (Server Domain Model) - 單元測試目標
# =====================================================================

class Task:
    def __init__(self, task_id: int, title: str, completed: bool = False):
        if not title or not title.strip():
            raise ValueError("任務標題不能為空！")
        self.task_id = task_id
        self.title = title.strip()
        self.completed = completed

    def mark_completed(self):
        self.completed = True

    def mark_pending(self):
        self.completed = False

    def to_dict(self) -> Dict:
        return {
            "id": self.task_id,
            "title": self.title,
            "completed": self.completed,
        }


class TaskService:
    """伺服器端核心服務類別 (不依賴任何 Web 框架，確保易測性)"""
    def __init__(self):
        self._tasks: Dict[int, Task] = {}
        self._id_counter = 1

    def create_task(self, title: str) -> Task:
        task = Task(task_id=self._id_counter, title=title)
        self._tasks[self._id_counter] = task
        self._id_counter += 1
        return task

    def get_task(self, task_id: int) -> Optional[Task]:
        return self._tasks.get(task_id)

    def list_tasks(self) -> List[Task]:
        return list(self._tasks.values())

    def toggle_task(self, task_id: int) -> Task:
        task = self._tasks.get(task_id)
        if not task:
            raise KeyError(f"找不到編號為 {task_id} 的任務")
        if task.completed:
            task.mark_pending()
        else:
            task.mark_completed()
        return task

    def delete_task(self, task_id: int) -> bool:
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def reset(self):
        self._tasks.clear()
        self._id_counter = 1


# =====================================================================
# 2. FastAPI Web 應用與前端介面 (Web API + HTML for E2E)
# =====================================================================

service = TaskService()
app = fastapi.FastAPI(title="Task Management System")

class TaskCreateRequest(BaseModel):
    title: str

# 簡易 SPA 前端頁面 (用於 Playwright E2E 測試)
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>待辦清單任務系統</title>
    <style>
        body { font-family: sans-serif; max-width: 600px; margin: 40px auto; padding: 20px; }
        .completed { text-decoration: line-through; color: gray; }
        li { margin: 8px 0; display: flex; align-items: center; justify-content: space-between; }
    </style>
</head>
<body>
    <h1>任務管理系統</h1>
    <div>
        <input type="text" id="task-input" placeholder="請輸入新任務名稱" />
        <button id="add-btn" onclick="addTask()">新增任務</button>
    </div>
    <ul id="task-list"></ul>

    <script>
        async function fetchTasks() {
            const res = await fetch('/api/tasks');
            const tasks = await res.json();
            const list = document.getElementById('task-list');
            list.innerHTML = '';
            tasks.forEach(t => {
                const li = document.createElement('li');
                li.id = `task-item-${t.id}`;
                li.innerHTML = `
                    <span class="${t.completed ? 'completed' : ''}" id="task-title-${t.id}">${t.title}</span>
                    <div>
                        <button id="toggle-btn-${t.id}" onclick="toggleTask(${t.id})">${t.completed ? '標示未完成' : '完成'}</button>
                        <button id="delete-btn-${t.id}" onclick="deleteTask(${t.id})">刪除</button>
                    </div>
                `;
                list.appendChild(li);
            });
        }

        async function addTask() {
            const input = document.getElementById('task-input');
            const title = input.value.trim();
            if (!title) return;
            await fetch('/api/tasks', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title: title })
            });
            input.value = '';
            fetchTasks();
        }

        async function toggleTask(id) {
            await fetch(`/api/tasks/${id}/toggle`, { method: 'POST' });
            fetchTasks();
        }

        async function deleteTask(id) {
            await fetch(`/api/tasks/${id}`, { method: 'DELETE' });
            fetchTasks();
        }

        window.onload = fetchTasks;
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def index():
    return HTML_CONTENT

@app.get("/api/tasks")
def api_get_tasks():
    return [t.to_dict() for t in service.list_tasks()]

@app.post("/api/tasks", status_code=fastapi.status.HTTP_201_CREATED)
def api_create_task(req: TaskCreateRequest):
    try:
        task = service.create_task(req.title)
        return task.to_dict()
    except ValueError as e:
        raise fastapi.HTTPException(status_code=400, detail=str(e))

@app.post("/api/tasks/{task_id}/toggle")
def api_toggle_task(task_id: int):
    try:
        task = service.toggle_task(task_id)
        return task.to_dict()
    except KeyError:
        raise fastapi.HTTPException(status_code=404, detail="任務不存在")

@app.delete("/api/tasks/{task_id}")
def api_delete_task(task_id: int):
    success = service.delete_task(task_id)
    if not success:
        raise fastapi.HTTPException(status_code=404, detail="任務不存在")
    return {"message": "刪除成功"}


# =====================================================================
# 3. 第一層測試：單元測試 (Unit Tests)
# 說明：針對核心邏輯 Task 與 TaskService，驗證空值、新增、切換與異常處理
# =====================================================================

class TestTaskServiceUnit:
    def setup_method(self):
        self.svc = TaskService()

    def test_create_task_success(self):
        task = self.svc.create_task("研讀 Rust 記憶體模型")
        assert task.task_id == 1
        assert task.title == "研讀 Rust 記憶體模型"
        assert task.completed is False

    def test_create_task_empty_title_raises_error(self):
        with pytest.raises(ValueError, match="任務標題不能為空！"):
            self.svc.create_task("   ")

    def test_toggle_task_state(self):
        task = self.svc.create_task("撰寫單元測試")
        assert task.completed is False

        # 切換成完成
        self.svc.toggle_task(task.task_id)
        assert task.completed is True

        # 再次切換回未完成
        self.svc.toggle_task(task.task_id)
        assert task.completed is False

    def test_toggle_nonexistent_task_raises_keyerror(self):
        with pytest.raises(KeyError):
            self.svc.toggle_task(9999)

    def test_delete_task(self):
        task = self.svc.create_task("即將被刪除的任務")
        assert self.svc.delete_task(task.task_id) is True
        assert self.svc.get_task(task.task_id) is None
        assert self.svc.delete_task(task.task_id) is False


# =====================================================================
# 4. 第二層測試：系統測試 / 整合測試 (Web API System Tests)
# 說明：使用 TestClient 發起 HTTP 請求，驗證 API 路由、狀態碼、Payload 與報錯響應
# =====================================================================

class TestWebApiSystem:
    @pytest.fixture(autouse=True)
    def setup_system(self):
        service.reset()
        self.client = TestClient(app)

    def test_api_empty_list(self):
        response = self.client.get("/api/tasks")
        assert response.status_code == 200
        assert response.json() == []

    def test_api_create_task_and_retrieve(self):
        # 1. 建立任務
        create_res = self.client.post("/api/tasks", json={"title": "完成 Web API 系統測試"})
        assert create_res.status_code == 201
        data = create_res.json()
        assert data["id"] == 1
        assert data["title"] == "完成 Web API 系統測試"
        assert data["completed"] is False

        # 2. 驗證清單能正確取得
        list_res = self.client.get("/api/tasks")
        assert list_res.status_code == 200
        tasks = list_res.json()
        assert len(tasks) == 1
        assert tasks[0]["id"] == 1

    def test_api_create_task_invalid_payload(self):
        response = self.client.post("/api/tasks", json={"title": "  "})
        assert response.status_code == 400
        assert "任務標題不能為空" in response.json()["detail"]

    def test_api_toggle_and_delete_flow(self):
        # 建立任務
        res = self.client.post("/api/tasks", json={"title": "待切換狀態之任務"})
        task_id = res.json()["id"]

        # 呼叫切換狀態 API
        toggle_res = self.client.post(f"/api/tasks/{task_id}/toggle")
        assert toggle_res.status_code == 200
        assert toggle_res.json()["completed"] is True

        # 呼叫刪除 API
        del_res = self.client.delete(f"/api/tasks/{task_id}")
        assert del_res.status_code == 200
        assert del_res.json()["message"] == "刪除成功"

        # 再次切換已刪除任務，應回傳 404
        toggle_again = self.client.post(f"/api/tasks/{task_id}/toggle")
        assert toggle_again.status_code == 404


# =====================================================================
# 5. 第三層測試：E2E 端到端測試 (Playwright Headless Browser Test)
# 說明：背景啟動真實 Web 伺服器，由 Playwright 無頭瀏覽器模擬真實使用者在頁面上的完整操作
# =====================================================================

SERVER_PORT = 8765
SERVER_HOST = "127.0.0.1"
BASE_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"

class ServerThread(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.config = uvicorn.Config(app, host=SERVER_HOST, port=SERVER_PORT, log_level="warning")
        self.server = uvicorn.Server(self.config)

    def run(self):
        self.server.run()

    def stop(self):
        self.server.should_exit = True


@pytest.fixture(scope="module")
def live_server():
    """啟動供 E2E 測試連線的背景 Live Server"""
    service.reset()
    server_thread = ServerThread()
    server_thread.start()
    time.sleep(1.2)  # 等候伺服器完成綁定與監聽
    yield BASE_URL
    server_thread.stop()


def test_e2e_full_user_flow(live_server):
    """
    E2E 測試流程：
    1. 打開無頭瀏覽器訪問前端網頁
    2. 在輸入框輸入任務並點擊新增按鈕
    3. 驗證清單出現該項目
    4. 點擊「完成」按鈕，確認文字劃線樣式與狀態變更
    5. 點擊「刪除」按鈕，確認項目自 DOM 中移除
    """
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        # 啟動無頭瀏覽器 (headless=True)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1. 導覽至首頁
        page.goto(live_server)
        assert "待辦清單任務系統" in page.title()

        # 2. 填寫表單並新增任務
        task_input = page.locator("#task-input")
        task_input.fill("Playwright E2E 無頭瀏覽器測試任務")
        page.locator("#add-btn").click()

        # 3. 驗證項目是否被繪製於頁面
        item_text = page.locator("#task-title-1")
        item_text.wait_for(state="visible", timeout=3000)
        assert item_text.inner_text() == "Playwright E2E 無頭瀏覽器測試任務"

        # 4. 點擊完成按鈕並檢查 class 是否附帶 completed
        toggle_btn = page.locator("#toggle-btn-1")
        toggle_btn.click()
        page.wait_for_selector("#task-title-1.completed", timeout=3000)
        assert "completed" in (item_text.get_attribute("class") or "")

        # 5. 點擊刪除按鈕並確認 DOM 節點消失
        delete_btn = page.locator("#delete-btn-1")
        delete_btn.click()
        page.locator("#task-item-1").wait_for(state="detached", timeout=3000)
        assert page.locator("#task-item-1").count() == 0

        browser.close()


# =====================================================================
# 本地直接執行入口 (可手動啟動伺服器供人工體驗，或執行 pytest)
# =====================================================================
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "runserver":
        print(f"啟動任務管理系統: http://127.0.0.1:8000")
        uvicorn.run(app, host="127.0.0.1", port=8000)
    else:
        print("直接執行全部測試套件中...")
        pytest.main(["-v", "-s", __file__])