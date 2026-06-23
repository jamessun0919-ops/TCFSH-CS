# 📐 國中數學幾何題目練習系統 MVP 交接文檔 (Handover)

本文件整理了「國中數學幾何題目練習系統」MVP 版本的架構設計、當前部署狀態、已解決之技術痛點，以及未來延續開發的指引，以利接續開發工作。

---

## 📂 專案架構與檔案清單

專案採用前後端分離架構，所有核心程式碼已整理於工作目錄：

1.  **[index.html](file:///c:/Users/User/Desktop/TCFSH-CS/index.html)**：前端單頁網頁應用 (SPA)
    *   **技術棧**：HTML5, Vanilla CSS, Vanilla JavaScript, KaTeX CDN。
    *   **核心功能**：幾何工程藍圖畫布、動態單元選擇區（段考為複選 Checkbox，會考與科學班為單選 Select）、作答記錄持久化（LocalStorage）、儀表板即時數據統計、Blob 動態轉換下載 Markdown 練習紀錄。
2.  **[app.py](file:///c:/Users/User/Desktop/TCFSH-CS/app.py)**：後端 Flask 服務
    *   **技術棧**：Python 3.8+, Flask, flask-cors, google-generativeai。
    *   **核心功能**：`/api/generate-question` 題目生成 API、難度人設提示詞工程、SVG 圖形約束與標註、強健 JSON 解析器與全域例外攔截（保證任何錯誤皆回傳包含 CORS 標頭之 JSON 物件）。
3.  **[gunicorn.conf.py](file:///c:/Users/User/Desktop/TCFSH-CS/gunicorn.conf.py)**：Gunicorn Web 伺服器配置檔
    *   設置工作進程超時限制為 `120秒`，解決幾何 AI 產圖逾時問題。
4.  **[requirements.txt](file:///c:/Users/User/Desktop/TCFSH-CS/requirements.txt)**：後端 Python 依賴包。
5.  **[.gitignore](file:///c:/Users/User/Desktop/TCFSH-CS/.gitignore)**：排除 Python 快取（`__pycache__`）及環境變數檔（`.env`）。
6.  **[README.md](file:///c:/Users/User/Desktop/TCFSH-CS/README.md)**：基礎開發啟動與部署指引。

---

## 🌐 當前部署狀態

*   **GitHub 儲存庫**：[jamessun0919-ops/TCFSH-CS](https://github.com/jamessun0919-ops/TCFSH-CS) (分支: `main`)
*   **前端線上 Demo (GitHub Pages)**：[https://jamessun0919-ops.github.io/TCFSH-CS/](https://jamessun0919-ops.github.io/TCFSH-CS/)
*   **後端 API 伺服器 (Render)**：[https://tcfsh-cs.onrender.com](https://tcfsh-cs.onrender.com) (API 路徑: `/api/generate-question`)

> 💡 **重要配置說明**：
> 前端 `index.html` 已硬編碼（Hardcode）預設後端 API。本地開發（`localhost` 或 `127.0.0.1`）會自動連線本地 `http://localhost:5000`，線上部署版則自動導向生產環境的 Render API。

---

## 🛠️ 已解決之關鍵技術痛點 (Key Troubleshooting History)

1.  **Gunicorn Worker 逾時 (Timeout) 導致 CORS 阻擋問題**：
    *   *問題*：Gemini API 產製題目與繪製 SVG 的時間偶爾會超過 Gunicorn 預設的 30 秒上限。Gunicorn 因而強行殺死工作進程並回傳預設 HTML 500 錯誤。由於此 HTML 500 沒有攜帶 CORS 標頭，瀏覽器會以 CORS 安全機制封鎖它，並向 JavaScript 拋出 `Failed to fetch` 錯誤。
    *   *修復*：
        1. 建立 `gunicorn.conf.py`，配置 `timeout = 120`，允許回應時間長達 120 秒。
        2. 在 `app.py` 內註冊 `@app.errorhandler(Exception)` 全域錯誤處理器，確保任何 unhandled 崩潰皆轉為 **帶有 CORS 標頭的 JSON 格式** 回傳，使前端能看見具體的伺服器診斷訊息。
2.  **LaTeX 反斜線轉義 SyntaxWarning**：
    *   *問題*：`app.py` 的提示詞包含大量 LaTeX 定界符與指令（如 `\angle`, `\circ`），在 Python 字串中會被解讀為無效轉義字元。
    *   *修復*：將 `SYSTEM_INSTRUCTION` 的提示詞區塊修改為**原始字串 (Raw String)**：`r"""..."""`，徹底消除語法警告。

---

## 🚀 未來延續開發方向與 Next Steps

1.  **解決 Render 免費版冷啟動 (Cold Start) 延遲**：
    *   Render 免費方案在閒置 15 分鐘後會進入休眠。第一次連線需花費 50~90 秒甦醒。
    *   *建議方案*：可以使用 [UptimeRobot](https://uptimerobot.com/) 或設定定時 GitHub Action 任務，每 10 分鐘向 `https://tcfsh-cs.onrender.com` 發送一個輕量的 GET 請求以維持伺服器常駐活跃。
2.  **資料持久化升級（Database 整合）**：
    *   目前作答歷程儲存於瀏覽器 `localStorage`，若更換裝置或清除快取會遺失資料。
    *   *建議方案*：在後端引入 SQLite 或 PostgreSQL 資料庫，並串接簡單的使用者註冊與登入（Auth），讓練習紀錄可以隨帳號綁定。
3.  **互動式 SVG 畫布開發**：
    *   目前 SVG 圖形僅能靜態展示。
    *   *建議方案*：在前端引入 `d3.js` 或利用 Canvas API，讓學生可以在幾何圖形上畫輔助線、標記長度或拖曳端點做動態幾何（GeoGebra 式）的直觀探索。
4.  **幾何圖形生成精準度調優**：
    *   Gemini API 偶爾在極端條件下生成的幾何圖形（SVG 的線段與圓形比例）可能與題目敘述有輕微數值偏差。
    *   *建議方案*：可以在後端 Prompt 中加入「少樣本提示（Few-Shot Prompts）」，提供 2-3 個完美繪製的幾何 SVG 樣板供 AI 參照；或者是在 System Instruction 中更嚴格地定義數學坐標的計算公式。
