import os
import json
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv

# 載入環境變數（支援本地開發讀取 .env 檔案）
load_dotenv()

app = Flask(__name__)
# 啟用 CORS 允許前端跨網域訪問，為 Vercel 部署至 Render 後端做好準備
CORS(app, resources={r"/api/*": {"origins": "*"}})

# 配置 Google Gemini API 金鑰
API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

# 定義後端系統提示詞（System Instruction），用以約束 AI 的人設、難度、LaTeX 與 SVG 生成格式
SYSTEM_INSTRUCTION = r"""你是一個資深的國中數學全端與教學專家。請協助生成高品質的「國中幾何題目」。
你必須完全使用繁體中文（zh-TW）回答。

【題目難度與人設要求】
- 難度為「會考標準」時：
  - 人設：親切、說明清晰的國中教師。
  - 考題特色：著重基本幾何定義、常用定理（如：畢氏定理、三角形全等性質、平行線性質等）。題目設計直觀，難度適中，符合國中教育會考的單題難度。
- 難度為「學校段考」時：
  - 人設：富挑戰性、嚴謹的國中數學科主席。
  - 考題特色：強調「跨單元綜合應用」（例如：結合相似形與圓形性質，或平行線與特殊四邊形性質）。題幹需要將選取的複數單元進行有機的融合，需要多步推導。
- 難度為「科學班甄選」時：
  - 人設：頂尖高中科學班教授、奧林匹亞幾何教練。
  - 考題特色：難度極高，極具挑戰性。解題過程常需要作輔助線，或運用進階幾何定理（如：孟氏定理、西瓦定理、托勒密定理、圓冪定理、塞姆松線等）。題目設計精妙，著重幾何深度與邏輯推論。

【格式限制】
1. 所有數學敘述中，凡是英文變數、點（如 A, B, C）、線段（如 AB）、角（如 \angle A, \angle ABC）、長度、數值、方程式，皆必須使用標準 LaTeX 格式包裹：
   - 行內公式使用單個 `$` 標籤，例如：點 $A$、線段 $AB$、$\angle ABC = 60^\circ$、面積 $24$。
   - 獨立區塊公式使用雙個 `$$` 標籤。
   - 請勿在非數學文字上使用 $。
2. 圖形 SVG 畫布格式要求：
   - 必須是純 SVG 代碼，並放置於 JSON 中的 `svg_code` 欄位。
   - viewBox 屬性必須精確設置為 `"0 0 400 400"`。
   - 所有幾何點、線段、圓、文字標籤的 x, y 座標必須嚴格限制在 50 至 350 之間（以防超出畫布邊緣）。
   - 請用精緻且專業的風格繪製。線條使用乾淨的色調（如天藍色 #38bdf8 或板岩灰 #94a3b8，寬度約 2.5px）；頂點使用半透明小圓點標示（例如 r="3", fill="#f8fafc"）；文字標籤（點的字母 A, B, C 等）應略微偏離頂點（例如 offset 10-15px），避免被線條覆蓋，且字體大小為 14px-16px，填滿白色 (#f8fafc) 或淺灰色。可以用半透明填充色標註特殊區域或角度（例如 fill="rgba(56, 189, 248, 0.1)"）。
   - SVG 中應包含：頂點、線段、弧、圓、角度標記，以及對應的點名稱標籤（A, B, C...）。
3. 輸出格式限制：
   - 必須是合法的 JSON 物件，不能有任何 Markdown 語法標記（如 ```json...```）或額外的說明文字。
   - JSON 鍵名與格式必須完全符合：
     {
       "question": "題目敘述（包含 $ 包裹的 LaTeX 公式）",
       "options": {
         "A": "選項 A 內容（可用 $ 包裹 LaTeX）",
         "B": "選項 B 內容（可用 $ 包裹 LaTeX）",
         "C": "選項 C 內容（可用 $ 包裹 LaTeX）",
         "D": "選項 D 內容（可用 $ 包裹 LaTeX）"
       },
       "answer": "A 或 B 或 C 或 D",
       "explanation": "詳細的解題步驟說明（包含 $ 包裹的 LaTeX 公式，如果有輔助線作法也請說明）",
       "svg_code": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 400 400\">...</svg>"
     }
"""

def extract_json(response_text):
    """
    強健的 JSON 解析器，當 AI 沒有乖乖回傳純 JSON 而是用 Markdown 包覆時，能自動辨識並擷取
    """
    text = response_text.strip()
    
    # 嘗試直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
        
    # 嘗試以正則表達式擷取 markdown code blocks
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass
            
    # 嘗試尋找第一個 { 與最後一個 }
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1:
        try:
            return json.loads(text[start:end+1])
        except json.JSONDecodeError:
            pass
            
    raise ValueError(f"無法解析合法的 JSON 物件。原始回應為：{text[:200]}...")

@app.route('/api/generate-question', methods=['POST'])
def generate_question():
    if not API_KEY:
        return jsonify({
            "error": "後端伺服器未設定 Gemini API 金鑰 (GEMINI_API_KEY)。請檢視環境變數設定。"
        }), 500
        
    data = request.get_json() or {}
    topic = data.get("topic")
    difficulty = data.get("difficulty")
    
    if not topic or not difficulty:
        return jsonify({"error": "缺少必要欄位 'topic' 或 'difficulty'"}), 400
        
    # 轉換單元格式（若是陣列則以頓號連接，其餘維持字串）
    if isinstance(topic, list):
        topic_str = "、".join(topic)
    else:
        topic_str = str(topic)
        
    user_prompt = f"【幾何單元】：{topic_str}\n【題目難度】：{difficulty}\n\n請依據上述單元與難度，設計一題極具水準的單選幾何題目，並生成對應的 SVG 圖形。記住，所有座標須在 50~350 之間，且數學符號與公式須使用 $ 或 $$ 包裹。"

    try:
        # 配置 GenerativeModel（預設使用速度快、具備優異 JSON 功能的 gemini-2.5-flash）
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SYSTEM_INSTRUCTION
        )
        
        # 調用 API，指定回傳 MIME 類型為 application/json 以加強約束
        response = model.generate_content(
            user_prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        response_text = response.text
        parsed_data = extract_json(response_text)
        return jsonify(parsed_data)
        
    except Exception as e:
        print(f"使用 gemini-2.5-flash 發生錯誤: {str(e)}，嘗試備用方案...")
        try:
            # 備用方案：使用 gemini-1.5-flash 作為 Fallback
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=SYSTEM_INSTRUCTION
            )
            response = model.generate_content(
                user_prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            parsed_data = extract_json(response.text)
            return jsonify(parsed_data)
        except Exception as inner_e:
            return jsonify({
                "error": "無法生成題目，請稍後再試。",
                "details": str(inner_e),
                "original_error": str(e)
            }), 500

@app.errorhandler(Exception)
def handle_global_exception(e):
    # 如果是 Flask 內建的 HTTP 異常（如 404, 405），直接返回原異常
    from werkzeug.exceptions import HTTPException
    if isinstance(e, HTTPException):
        return e

    # 針對其他未預期錯誤，記錄詳細 Traceback 並回傳 JSON，以防 CORS 阻擋 HTML 錯誤頁面
    import traceback
    print("--- 偵測到全域未預期錯誤 ---")
    traceback.print_exc()
    
    return jsonify({
        "error": "伺服器內部發生未預期錯誤，請聯絡管理員。",
        "details": str(e),
        "traceback": traceback.format_exc()
    }), 500

if __name__ == '__main__':
    # 本地端開發預設使用 Port 5000 運行
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
