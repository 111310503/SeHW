# 從 LLM API 到 AI Agent 建構指南

從單純的 LLM API 進化到能自主解決問題的 AI Agent，底層其實沒有魔法，核心就是**「狀態管理 ＋ 工具呼叫 ＋ `while` 迴圈」**。

本指南將整個過程拆解成 5 個階段，不依賴任何肥大的框架（如 LangChain），直接用純 Python 邏輯理解 Agent 是如何從零建構出來的。

---

## 階段一：無狀態的單次呼叫（LLM API）

LLM API 的本質是一個**無狀態（Stateless）的文字補全函式**：送出一個 HTTP 請求，它根據機率預測並回傳一段文字，呼叫完就忘記上下文。

```python
from openai import OpenAI  # 或 google.genai，概念完全相同

client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "金門今天天氣如何？"}]
)
print(response.choices[0].message.content)
```

* **痛點**：沒有記憶，也無法上網或查詢即時資料，只能依靠訓練時的舊知識回答。

---

## 階段二：加上「短期記憶」（Conversation History）

要讓它變成「聊天機器人」，做法非常單純：**在程式裡維護一個 `messages` 陣列**，每次發送請求時，把過去所有的對話紀錄整包重新傳給 API。

```python
messages = [
    {"role": "system", "content": "你是一個簡潔的技術助教。"}
]

while True:
    user_input = input("你: ")
    messages.append({"role": "user", "content": user_input})
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    reply = response.choices[0].message.content
    
    print(f"AI: {reply}")
    messages.append({"role": "assistant", "content": reply})  # 把 AI 的回答存回去
```

* **關鍵認知**：LLM 本身沒有記憶功能，所謂的「記憶」其實是應用程式不斷把歷史紀錄塞進 Prompt 裡。

---

## 階段三：裝上「手腳」（Function Calling / Tool Use）

要讓 LLM 能執行任務（查天氣、讀寫檔案、查資料庫），必須透過 **Function Calling**。

需要注意的是，**LLM 並不會自己執行程式碼**。完整流程如下：

1. 在本地寫好一個真實的 Python 函式（例如 `get_weather(city)`）。
2. 把這個函式的「說明書」（JSON Schema，描述函式名稱、用途、參數型別）連同 `messages` 一起傳給 LLM。
3. LLM 判斷自己需要這個工具時，**不會回傳普通文字**，而是回傳一個結構化指令：
   ```json
   {"name": "get_weather", "arguments": {"city": "Kinmen"}}
   ```
4. **本地的 Python 程式**解析這個指令、實際執行 `get_weather("Kinmen")` 拿到結果，再把結果當作一條 `role: "tool"` 的訊息塞回 `messages` 傳給 LLM。
5. LLM 看到工具回傳的結果後，整理成人類看得懂的自然語言回覆使用者。

---

## 階段四：裝上「大腦迴圈」（Agent Loop / ReAct）

把階段二的「記憶陣列」和階段三的「工具呼叫」放進一個 **`while` / `for` 迴圈**，讓 LLM 自己決定「還要不要繼續呼叫下一個工具」，這就是一個真正的 **AI Agent**。

這個核心架構通常稱為 **ReAct（Reasoning + Acting）** 迴圈：

```python
import json

def run_agent(user_prompt, max_steps=5):
    messages = [{"role": "user", "content": user_prompt}]
    
    for step in range(max_steps):  # 設定上限，防止無限迴圈燒光 API 額度
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=my_tools_schema  # 告訴 LLM 它有哪些工具可用
        )
        msg = response.choices[0].message
        messages.append(msg)

        # 判斷：LLM 是要「呼叫工具」，還是已經「得出最終答案」？
        if not msg.tool_calls:
            return msg.content  # 沒有要呼叫工具，代表任務完成，跳出迴圈！

        # 執行 LLM 要求的所有工具
        for tool_call in msg.tool_calls:
            func_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            # 在本地端實際執行函式
            result = execute_local_function(func_name, args)
            
            # 把執行結果塞回記憶陣列，準備進入下一輪思考
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })
            
    return "達到最大步數限制，任務中止。"
```

這短短 25 行程式碼，就是市面上絕大多數 AI Agent 框架最核心的引擎。

---

## 階段五：工程化擴展（從玩具到實用）

當上面的迴圈跑通後，真實世界的 Agent 開發就是在解決這個迴圈衍生出的工程問題：

| 擴展模組 | 解決什麼問題 | 常見實作方式 |
| :--- | :--- | :--- |
| **長期記憶（RAG）** | `messages` 太長會超過 Context Window 且成本高 | 用 Embedding 將資料存入向量資料庫，需要時當作「搜尋工具」檢索 |
| **狀態與中斷（Human-in-the-loop）** | 防止 Agent 誤刪檔案或誤發信件 | 在執行高風險工具前暫停迴圈，等待人類確認後再繼續 |
| **結構化輸出與驗證** | LLM 偶爾會傳錯參數格式或產生幻覺 | 用 Pydantic 驗證參數，出錯時把 Error Message 塞回 `messages` 讓它自行修正 |
| **多代理協作（Multi-Agent）** | 單一 Agent 塞太多工具會變笨、容易混淆 | 拆成多個專職 Agent（例如一個寫程式、一個做 Code Review），由主迴圈分派任務 |

---

## 實戰學習法：如何透過 AI 教會自己？

不要只叫 AI「幫我寫一個 Agent」，那樣只會拿到一段難以消化的程式碼。建議把 AI 當成你的 **Pair Programming 導師**，依序進行：

1. **先手寫，再讓 AI Review**：要求 AI 給你一個「只有單一計算機工具、不准用任何框架」的空白骨架，自己把 `while` 迴圈填完，再貼給 AI 問：「這段程式碼在邊界條件（例如工具報錯、JSON 解析失敗）會怎麼掛掉？」
2. **刻意製造 Bug 來學**：給 Agent 一個「會拋出 Exception 的工具」，觀察它怎麼崩潰，然後問 AI：「如何把 Python 的 `traceback` 抓起來回傳給 LLM，讓它自己學會修正參數？」
3. **拆解開源框架**：挑一個標準協定（例如 **MCP, Model Context Protocol**）或輕量框架，把它的原始碼貼給 AI，要求它對照你剛寫的 25 行迴圈，解釋「這個框架幫我們多封裝了哪些事情」。