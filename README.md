# 📐 國中數學幾何題目練習系統 MVP

[![DEMO](https://img.shields.io/badge/DEMO-%E9%96%8B%E5%95%9F%E7%B7%9A%E4%B8%8A%E7%B7%B4%E7%BF%92-success?style=for-the-badge&logo=githubpages&logoColor=white)](https://jamessun0919-ops.github.io/TCFSH-CS/)

這是一個基於 AI 驅動的**國中數學幾何題目練習系統**的 MVP 版本。本專案包含：
1. **前端 (Vercel 部署)**：純 HTML5, Vanilla CSS (深色工程藍圖風格), JavaScript, KaTeX (數學公式解析)。
2. **後端 (Render 部署)**：Python Flask 搭配 `google-generativeai` 呼叫 Gemini 2.5 API，具備動態人設 Prompt 與強健的 JSON 解析/座標防切防漏機制。

---

## 📂 檔案結構

```text
TCFSH-CS/
├── app.py             # 後端 Flask 主程式
├── index.html         # 前端單一網頁檔案 (HTML, CSS, JS)
├── requirements.txt   # Python 後端套件清單
└── README.md          # 說明文件
```

---

## 🛠️ 本地開發與啟動步驟

### 1. 後端啟動 (Python Flask)

1. **安裝依賴套件**：
   確保您安裝了 Python 3.8+，並在終端機執行：
   ```bash
   pip install -r requirements.txt
   ```

2. **設定環境變數**：
   在同目錄下建立 `.env` 檔案，或直接在環境變數中設定您的 Gemini API Key：
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

3. **啟動伺服器**：
   ```bash
   python app.py
   ```
   啟動後，後端伺服器預設將運行於 `http://localhost:5000`。

### 2. 前端啟動

由於前端是純靜態的 `index.html`，您有兩種方式運行：
- **直接開啟**：在瀏覽器中直接按兩下 `index.html` 檔案打開。
- **使用 Live Server**：利用 VS Code 的 Live Server 插件啟動，此時網址通常為 `http://127.0.0.1:5500`。

> 💡 **串接提示**：
> 前端右上角設有「**後端 API 網址**」設定欄位。當您在本地測試時，請確保該欄位為空（將自動偵測 `http://localhost:5000`）或手動填入 `http://localhost:5000`。當部署至 Render 後，請填入 Render 分配給您的 URL（例如 `https://tcfsh-cs.onrender.com`）。

---

## 🚀 部署指南

### 前端部署 (Vercel)
1. 將專案推送到 GitHub。
2. 登入 [Vercel](https://vercel.com/)，點擊 **Add New > Project**。
3. 選擇並導入您的 GitHub 儲存庫。
4. 因為本專案前端只有 `index.html`，Vercel 會自動辨識為靜態網站，直接點擊 **Deploy** 即可完成部署！

### 後端部署 (Render)
1. 登入 [Render](https://render.com/)，點擊 **New > Web Service**。
2. 連結您的 GitHub 儲存庫。
3. 設定部署參數：
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app` (Render 會自動使用 Gunicorn 執行 Flask)
4. 在 **Environment Variables** (環境變數) 中新增金鑰：
   - `GEMINI_API_KEY` = `（填入您的 Gemini API 金鑰）`
5. 點擊 **Create Web Service** 進行部署。
6. 部署完成後，複製 Render 提供給您的 Web Service URL，將其貼入前端網頁的右上角「後端 API 網址」輸入框中，即可開始練習！
