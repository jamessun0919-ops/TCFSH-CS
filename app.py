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
2. 圖形 SVG 畫布格式與幾何繪圖要求：
   - 必須是純 SVG 代碼，並放置於 JSON 中的 `svg_code` 欄位。
   - viewBox 屬性必須精確設置為 `"0 0 400 400"`，不要在外層寫固定的 width/height 屬性。
   - **安全區域**：所有幾何點、線段、圓、文字標籤的 x, y 座標必須嚴格限制在 50 至 350 之間（以防超出畫布邊緣）。
   - **數學與比例精準度**：點與線段的座標必須依據幾何關係確實計算。例如 3:4:5 的直角三角形，兩直角股的像素長度比必須精確為 3:4。
    - **[DEBUG-USER-ADD] 垂直與交點規則**：若題目敘述或解題過程中提到兩條線段互相垂直（例如線段 $AD$ 垂直於線段 $OB$）：
      1. **實質相交**：在圖形中，這兩條線段（或其延長線）**必須實質相交**。
      2. **繪製延長輔助線**：如果線段本身未接觸（例如線段 $OB$ 僅延伸至外心 $O$，而 $AD$ 在其外側），**必須使用虛線將其中一條或兩條線段延長**使之相交。
      3. **標示交點代號**：必須在該交點處標註一個新的點代號（例如點 $E$），並在交點繪製實心小圓點，且在題目或詳解中提及此交點。
      4. **直角記號定位**：直角方磚標記（Right Angle Mark）**必須精確定位在該相交點上**，絕不能懸空放置在未相交的線段中間。
    - **[DEBUG-USER-ADD-SEPARATION] 多重圖形間距與縮放規則**：若圖形中包含兩個或以上不相連的獨立幾何圖形（例如兩個獨立的直角三角形 $\triangle ABC$ 與 $\triangle DEF$）：
      1. **幾何實質分離**：必須適當縮小各別圖形尺寸，使它們在 400x400 的畫布中有充足間距（至少 30px 以上），禁止頂點重疊或靠得太近。
      2. **劃分繪圖區域**：如繪製兩個並排的三角形，左三角形的 x 座標限制在 `50-180`，右三角形的 x 座標限制在 `220-350`，確保中間有大於 `40px` 的空隙。
      3. **文字標籤反向偏置**：對於靠近的邊界點（如左圖的右下角 $C$ 與右圖的左下角 $E$），其標籤必須往相反方向偏置（如 $C$ 點設 `text-anchor="end" dx="-8"`，而 $E$ 點設 `text-anchor="start" dx="8"`），以防文字重疊。
    - **[DEBUG-USER-ADD-ELEMENTS] 圖文一致性與幾何元素完整標記規則**：為確保生成的圖形與題幹敘述完全對應，嚴格遵守以下完整性要求：
      1. **關鍵點不得遺漏**：題目敘述中提到的每一個代表頂點、交點或特徵點的英文字母（如點 $A, B, C, H, M, P, Q$ 等），在 SVG 中**必須全部繪製**對應的實心小圓點，且**必須**有對應的字母標籤文字，絕不能漏標。
      2. **直線與線段代號標註**：若題目提到特定代號直線（如「直線 $L$」），必須在該線段旁標註對應的文字標籤（如 `L`）。
      3. **已知角度標註**：若題目提到已知的角度（如 $\angle BAC = 60^\circ$），在該角頂點處必須使用 `<path>` 畫出小圓弧標記，並在旁邊標註角度文字（如 `60°`）。
    - **[DEBUG-USER-ADD-CIRCUMCIRCLE] 外接圓與延長線交點接合與精算規則**：若題目包含三角形外接圓或線段延長線與圓相交於點 $D$：
      1. **外接圓與頂點接合（極座標精算步驟，極其重要）**：外接圓**必須精確通過**三角形的三個頂點 $A, B, C$。為了保證頂點 100% 落在圓上，你**必須**先設定一個圓心 $(x_0, y_0)$ 與半徑 $R$（例如：圓心為 $(200, 200)$，半徑為 $110$），然後依據設定的角度 $\theta$ 用三角函數計算出頂點座標。
         - 公式：$x = x_0 + R \cos(\theta)$， $y = y_0 - R \sin(\theta)$（此處減號是因為 SVG 的 $y$ 軸向下，圓心正上方為 $\theta = 90^\circ$）
         - 例如：
           - 頂點 $A$ (角度 $90^\circ$ / 正上方)：$x_A = 200$, $y_A = 200 - 110 \sin(90^\circ) = 90$
           - 頂點 $B$ (角度 $210^\circ$ / 左下方)：$x_B = 200 + 110 \cos(210^\circ) \approx 105$, $y_B = 200 - 110 \sin(210^\circ) = 255$
           - 頂點 $C$ (角度 $330^\circ$ / 右下方)：$x_C = 200 + 110 \cos(330^\circ) \approx 295$, $y_C = 200 - 110 \sin(330^\circ) = 255$
         - 絕對不能隨意估計不相符的座標，或是先畫一個隨意的三角形後再套用一個無關的圓。
      2. **交點實質相交**：若有「延長線與外接圓交於點 $D$」（如 $AI$ 延長線交圓於點 $D$），該交點的座標**也必須**使用上述圓的極座標公式或圓方程式計算，確保其在圓弧上，且延長線段（可使用板岩灰虛線 `stroke-dasharray="5,5"` 延長）**必須實質碰觸到該交點**。必須在交點處繪製小圓點並標註字母 `D`，絕不能懸空結束。
    - **文字標籤定位與高對比度規範 `[DEBUG-USER-ADD-CONTRAST]` (重要)**：
      - 為了在前端深藍色網格背景下能清晰閱讀，**絕對禁止**在任何文字或標籤上使用黑色 (`#000000` 或 `black`)、深灰色、暗藍色等與背景對比度低的暗系顏色。
      - **所有文字標籤（A, B, C 等字母、長度與角度數字）的 `fill` 屬性必須使用高對比度的亮色**，如亮白色 (`#f8fafc` 或 `#ffffff`) 或亮黃色 (`#f59e0b`)。
      - 頂點標籤應偏離頂點 8-15px。應依據頂點相對於圖形幾何中心的方向設定對齊屬性：
        - 上方頂點：使用 `text-anchor="middle" dominant-baseline="auto"` 且 y-offset 向上偏。
        - 下方頂點：使用 `text-anchor="middle" dominant-baseline="hanging"` 且 y-offset 向下偏。
        - 左方頂點：使用 `text-anchor="end" dominant-baseline="middle" dx="-8"`。
        - 右方頂點：使用 `text-anchor="start" dominant-baseline="middle" dx="8"`。
        確保文字不會與線段或其它點重疊，字體大小為 14px-16px。
    - **藍圖風格美感**：
      - 不要設定背景色 `<rect>`，保持畫布透明，直接使用前端網格背景。
      - 幾何實線：使用天藍色 `#38bdf8`，寬度約 2.5px，`stroke-linecap="round"`，`stroke-linejoin="round"`。
      - 輔助線與延長線：使用板岩灰 `#64748b`，且 `stroke-dasharray="5,5"`，寬度約 1.5px。
      - 交點與頂點：交點處用小實心圓 `<circle cx="..." cy="..." r="3.5" fill="#f8fafc" stroke="#38bdf8" stroke-width="1" />`。
      - 區域標註：可用半透明填充色（如 `fill="rgba(56, 189, 248, 0.08)"`）。
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
       "explanation": "詳細的解題步驟說明（包含 $ 包裹的 LaTeX 公式，若因為 [DEBUG-USER-ADD] 規則新增了輔助線延長交點，請在解題步驟中清楚說明，例如：延長 $OB$ 與 $AD$ 相交於 $E$ 點）",
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
        # 配置 GenerativeModel（預設使用額度高達 1500 次/天的穩定版 gemini-flash-latest）
        model = genai.GenerativeModel(
            model_name="gemini-flash-latest",
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
        print(f"使用 gemini-flash-latest 發生錯誤: {str(e)}，嘗試備用方案...")
        try:
            # 備用方案：使用 gemini-3.1-flash-lite 作為 Fallback
            model = genai.GenerativeModel(
                model_name="gemini-3.1-flash-lite",
                system_instruction=SYSTEM_INSTRUCTION
            )
            response = model.generate_content(
                user_prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            parsed_data = extract_json(response.text)
            return jsonify(parsed_data)
        except Exception as inner_e:
            err_msg_primary = str(e)
            err_msg_fallback = str(inner_e)
            
            # 判斷是否為額度限制錯誤 (429 / Quota Exceeded / Rate Limit)
            is_quota_error = any(
                any(keyword in msg.lower() for keyword in ["429", "quota", "limit", "exhausted", "resourceexhausted"])
                for msg in [err_msg_primary, err_msg_fallback]
            )
            
            error_title = "AI模型額度達上限，請更換金鑰或稍後再試。" if is_quota_error else "無法生成題目，請稍後再試。"
            
            return jsonify({
                "error": error_title,
                "details": err_msg_fallback,
                "original_error": err_msg_primary
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
