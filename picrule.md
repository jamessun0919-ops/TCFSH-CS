# 📐 AI 幾何圖形 SVG 生成規範 (picrule.md)

本文件定義「國中幾何題目練習系統」中 AI 生成 SVG 幾何圖形時應遵守的數學、美學與排版規範，用以提升幾何圖形的精準度、可讀性與視覺美感。

---

## 1. 畫布基本規格 (Canvas Specifications)

*   **畫布尺寸與 viewBox**：
    *   必須設定 `viewBox="0 0 400 400"`。
    *   不應硬編碼 `width` 與 `height` 屬性，以利前端進行 RWD 響應式縮放。
*   **安全繪圖區域 (Safe Zone)**：
    *   所有幾何頂點、線段、圓弧、文字標籤的 $x$ 與 $y$ 座標必須限制在 `50` 至 `350` 之間。
    *   保留四周各 `50px` 的邊距，以避免文字標籤被畫布邊緣切除。

---

## 2. 幾何數學合理性與真實性 (Mathematical Accuracy)

AI 在設計圖形頂點時，必須透過數學幾何關係精密計算出座標，不得隨意標記不合比例的點。

*   **直角三角形 (Right-angled Triangle)**：
    *   若 $\angle B = 90^\circ$，則 $A(x_A, y_A)$、$B(x_B, y_B)$、$C(x_C, y_C)$ 的座標必須滿足向量垂直關係，即 $(x_A - x_B)(x_C - x_B) + (y_A - y_B)(y_C - y_B) = 0$。
    *   邊長比例必須與題目敘述成正比。例如 $3:4:5$ 的三角形，其直角鄰邊的像素長度比必須精確為 $3:4$。
*   **圓與切線/割線 (Circle & Tangents/Secants)**：
    *   圓心 $(x_0, y_0)$ 與半徑 $r$ 必須精確定義。
    *   若直線與圓相切於點 $P(x_p, y_p)$：
        1. 點 $P$ 必須滿足圓方程式 $(x_p - x_0)^2 + (y_p - y_0)^2 = r^2$。
        2. 切線方向向量必須與半徑向量 $(x_p - x_0, y_p - y_0)$ 垂直。
*   **平行線與截線 (Parallel Lines)**：
    *   兩條平行線的斜率必須完全相同（即平行線兩端點的 $y$ 差值與 $x$ 差值比例一致）。
*   **垂直與交點 (Perpendicular Lines & Intersections) `[DEBUG-USER-ADD]`**：
    *   > 🔧 **[開發者除錯/使用者補充]**：本條目為針對 AI 幾何產圖時「垂直線段懸空、未實質相交」問題所新增的除錯與校準規則。
    *   若題目敘述提到兩條線段互相垂直（例如線段 $AD$ 垂直於線段 $OB$）：
        1. **實質相交**：在圖形中，這兩條線段（或其延長線）**必須實質相交**。
        2. **繪製延長輔助線**：如果線段本身未接觸（例如線段 $OB$ 僅延伸至點 $O$，而 $AD$ 在其外側），**必須使用虛線將其中一條或兩條線段延長**使之相交。
        3. **標示交點代號**：必須在該交點處標註一個新的點代號（例如點 $E$），並在交點繪製實心小圓點。
        4. **直角記號定位**：直角方磚標記（Right Angle Mark）**必須精確定位在該交點上**，絕不能懸空放置在未相交的線段中間。
*   **多重獨立圖形間距與縮放 `[DEBUG-USER-ADD-SEPARATION]`**：
    *   > 🔧 **[開發者除錯/使用者補充]**：為解決 AI 繪製多個獨立圖形（如兩個獨立三角形 $\triangle ABC$ 與 $\triangle DEF$）時，圖形相撞、頂點靠得太近導致點與文字標籤重疊（如點 $C$ 與點 $E$ 文字疊在一起）之問題。
    *   **實質分離**：若圖中包含兩個以上不相連的幾何圖形，必須**縮小個別圖形尺寸**並在它們之間**預留足夠的間距（至少 30px 以上）**。
    *   **左右/上下分割畫布**：例如在 400x400 畫布中繪製兩個並排的三角形，左三角形 $x$ 座標應限制在 `50-180`，右三角形 $x$ 座標限制在 `220-350`，確保中間有大於 `40px` 的空隙。
    *   **標籤反向偏移**：若兩個頂點在幾何上靠近，其文字標籤的偏移方向必須完全相反（例如左側點 $C$ 的標籤往左偏 `text-anchor="end" dx="-8"`，右側點 $E$ 的標籤往右偏 `text-anchor="start" dx="8"`），以防文字重疊。
*   **圖文一致性與幾何元素完整性 `[DEBUG-USER-ADD-ELEMENTS]`**：
    *   > 🔧 **[開發者除錯/使用者補充]**：為解決 AI 生成幾何圖形時，遺漏題目敘述中所提及的關鍵點（如垂心 $H$、中點 $M$）、線段/直線代號（如直線 $L$）或已知角度（如 $60^\circ$）等問題。
    *   **關鍵點完整標記**：題目敘述中凡是出現的頂點或交點代號（如點 $A, B, C, H, M, P, Q$），在 SVG 中**必須**繪製對應的實心小圓點 `<circle cx="..." cy="..." r="3.5" ... />`，並標記對應的 `<text>` 字母標籤，絕不可漏掉任何一個在題目中出現的點。
    *   **直線與線段代號**：若題目提到特定命名直線（如「直線 $L$」），在圖中對應的直線旁必須標記該字母標籤（如 `L`）。
    *   **已知角度數值標示**：若題目提到已知的具體角度（如 $\angle BAC = 60^\circ$），在頂點 $A$ 處必須繪製小圓弧標記，並在旁邊標記數值文字（如 `60°`）。
*   **外接圓與延長線交點 `[DEBUG-USER-ADD-CIRCUMCIRCLE]`**：
    *   > 🔧 **[開發者除錯/使用者補充]**：為解決 AI 繪製三角形之「外接圓」時，圓與三角形頂點未接觸（如 B, C 落在圓外），以及「線段延長線與圓的交點（如點 D）未正確相交並顯示」之問題。
    *   **外接圓接合要求（三角函數精算）**：若題目提及「外接圓」，該圓的圓弧**必須精確通過**三角形的三個頂點 $A, B, C$。
        *   **作圖法**：**必須先定義圓的圓心 $(x_0, y_0)$ 與半徑 $R$，然後以圓心角與三角函數公式計算頂點座標**，以確保頂點 100% 落在圓上。
        *   **標準計算公式**：設圓心為 $(200, 200)$，半徑為 $110$。
            *   頂點 $A$ (角度 $90^\circ$ / 圓心正上方)：$(200 + 110 \cos(90^\circ), 200 - 110 \sin(90^\circ)) = (200, 90)$
            *   頂點 $B$ (角度 $210^\circ$ / 圓心左下方)：$(200 + 110 \cos(210^\circ), 200 - 110 \sin(210^\circ)) \approx (105, 255)$
            *   頂點 $C$ (角度 $330^\circ$ / 圓心右下方)：$(200 + 110 \cos(330^\circ), 200 - 110 \sin(330^\circ)) \approx (295, 255)$
    *   **交點實質相交**：若題目提及「延長線與外接圓交於點 $D$」（如 $AH$ 延長線交外接圓於點 $D$）：
        1. **實質相交**：延長線段（可以使用虛線作為延長輔助線）**必須一路延伸並實質碰觸到外接圓的圓弧**（其座標必須同樣使用上述圓的方程式精確計算）。
        2. **交點與標籤**：在延長線與圓弧的交界處，**必須**繪製實心小圓點，並標註交點代號字母（如 `D`），絕不能讓線段懸空結束在圓內或未碰觸到圓弧。

---

## 3. 視覺標示與幾何符號 (Visual Indicators)

幾何圖形中重要的性質（如直角、等長、平行、角度）應使用圖形符號明確標註。

*   **直角標記 (Right Angle Mark)**：
    *   在直角頂點 $B$ 處，必須使用摺線 `<path>` 繪製寬度約 `10px` 的直角方磚。
    *   例如，若直角在 $B(x_B, y_B)$，鄰邊方向為水平與垂直，則直角標記路徑可寫為：
      ```xml
      <path d="M x_B+10 y_B L x_B+10 y_B-10 L x_B y_B-10" fill="none" stroke="#94a3b8" stroke-width="1.5" />
      ```
*   **角度弧線 (Angle Arcs)**：
    *   使用 `<path>` 繪製小圓弧標記特定角度，並在弧線旁放置角度數值。
    *   圓弧路徑公式可以使用 SVG 的弧線指令 `A`（橢圓弧）。
*   **等長/平行標記**：
    *   等長線段可在線段中點繪製 1~2 條垂直小短線（單撇/雙撇）。
    *   平行線可在線段中點繪製箭頭符號。
*   **輔助線 (Auxiliary Lines)**：
    *   題目中若有輔助線，或詳解圖示，應使用虛線表示：`stroke-dasharray="5,5"`，顏色使用板岩灰 `#64748b`。

---

## 4. 標籤排版與防重疊機制 (Label Alignment)

為了防止點的文字標籤（A, B, C 等）被幾何線段、圓弧或其它標籤遮擋，必須根據頂點相對於圖形幾何中心的方向，調整文字的定位屬性。

*   **偏離方向規則 (Label Directional Offsets)**：
    *   **上方頂點 (如三角形頂點 A)**：
        *   `x` 座標與頂點一致，`y` 座標向上偏移約 `12px` 至 `15px`。
        *   SVG 屬性：`text-anchor="middle" dominant-baseline="auto"`。
    *   **左方頂點**：
        *   `x` 座標向左偏移，`y` 座標微調。
        *   SVG 屬性：`text-anchor="end" dominant-baseline="middle" dx="-8"`。
    *   **右方頂點**：
        *   `x` 座標向右偏移，`y` 座標微調。
        *   SVG 屬性：`text-anchor="start" dominant-baseline="middle" dx="8"`。
    *   **下方頂點**：
        *   `x` 座標與頂點一致，`y` 座標向下偏移。
        *   SVG 屬性：`text-anchor="middle" dominant-baseline="hanging" dy="8"`。
*   **線段長度/角度數值標籤**：
    *   長度數值應標記在線段中點的偏外側，避免疊在線段正上方。
    *   角度數值（如 $60^\circ$）應標記在角平分線方向、距離頂點約 `20px` 至 `25px` 的位置。

---

## 5. 藍圖美學風格規範 (Aesthetics & Blueprint Style)

圖形風格應與前端「工程藍圖風格」完美融合：

*   **畫布背景**：透明（不設定背景色 `<rect>`，直接使用前端網頁的深藍色網格背景）。
*   **實線 (幾何本體)**：
    *   `stroke="#38bdf8"` (天藍色，亮眼搶眼) 或 `stroke="#818cf8"` (靛藍色)。
    *   `stroke-width="2.5"`，且 `stroke-linecap="round"`，`stroke-linejoin="round"`。
*   **虛線 (輔助線/投影線)**：
    *   `stroke="#64748b"` (板岩灰) 且 `stroke-dasharray="5,5"`，`stroke-width="1.5"`。
*   **頂點 (Vertices)**：
    *   在關鍵交點處繪製小實心圓：`<circle cx="..." cy="..." r="3.5" fill="#f8fafc" stroke="#38bdf8" stroke-width="1" />`。
*   **填滿區域 (Shaded Regions)**：
    *   如需標註特定三角形或局部面積，使用半透明填滿：`fill="rgba(56, 189, 248, 0.08)"`，並搭配實線邊框。
*   **文字字型與顏色 `[DEBUG-USER-ADD-CONTRAST]`**：
    *   > 🔧 **[開發者除錯/使用者補充]**：為解決 AI 幾何圖形在深藍底色下生成黑色或暗灰色文字（如 A, B, C, D...）導致無法辨識的問題，強烈約束本條目對比度規範。
    *   **高對比度顏色**：所有文字標籤（如頂點名稱 A, B, C...）與長度/角度數值，**必須使用高對比度的亮色**，如近純白 `#f8fafc`、亮白 `#ffffff` 或亮黃色 `#f59e0b`。
    *   **嚴禁暗色**：**絕對禁止**使用黑色 (`#000000` 或 `black`)、深灰色、暗藍色或任何與深色網格底色對比不明顯的暗系顏色來填滿文字（`fill` 屬性）。
    *   `font-family="'Outfit', 'Inter', sans-serif"`。
    *   `font-size="15px"`。

---

## 6. 精確幾何 SVG 樣版範例 (Few-Shot SVG Templates)

提供以下幾種典型題目的標準 SVG 代碼，AI 在命題時應參照其結構進行變形：

### 範例 A：標準直角三角形 $ABC$（$\angle B = 90^\circ$，邊長 $3:4:5$）
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">
  <!-- 定義填滿區域 (非必要) -->
  <polygon points="100,100 100,320 393.3,320" fill="rgba(56, 189, 248, 0.05)" />
  
  <!-- 繪製三角形三邊 -->
  <line x1="100" y1="100" x2="100" y2="320" stroke="#38bdf8" stroke-width="2.5" stroke-linecap="round" />
  <line x1="100" y1="320" x2="393.3" y2="320" stroke="#38bdf8" stroke-width="2.5" stroke-linecap="round" />
  <line x1="393.3" y1="320" x2="100" y2="100" stroke="#38bdf8" stroke-width="2.5" stroke-linecap="round" />
  
  <!-- 直角標記 (位於頂點 B(100, 320)) -->
  <path d="M 112 320 L 112 308 L 100 308" fill="none" stroke="#94a3b8" stroke-width="1.5" />
  
  <!-- 頂點實心小圓點 -->
  <circle cx="100" cy="100" r="3.5" fill="#f8fafc" stroke="#38bdf8" stroke-width="1" />
  <circle cx="100" cy="320" r="3.5" fill="#f8fafc" stroke="#38bdf8" stroke-width="1" />
  <circle cx="393.3" cy="320" r="3.5" fill="#f8fafc" stroke="#38bdf8" stroke-width="1" />
  
  <!-- 頂點文字標籤 -->
  <text x="100" y="85" text-anchor="middle" dominant-baseline="auto" fill="#f8fafc" font-size="15px" font-family="sans-serif">A</text>
  <text x="85" y="325" text-anchor="end" dominant-baseline="middle" fill="#f8fafc" font-size="15px" font-family="sans-serif">B</text>
  <text x="408" y="325" text-anchor="start" dominant-baseline="middle" fill="#f8fafc" font-size="15px" font-family="sans-serif">C</text>
  
  <!-- 長度數值標籤 -->
  <text x="80" y="210" text-anchor="end" dominant-baseline="middle" fill="#94a3b8" font-size="14px">12</text>
  <text x="246" y="340" text-anchor="middle" dominant-baseline="hanging" fill="#94a3b8" font-size="14px">16</text>
  <text x="256" y="200" text-anchor="start" dominant-baseline="auto" fill="#94a3b8" font-size="14px">x</text>
</svg>
```

### 範例 B：圓與圓內接三角形（圓心 $O$，三角形 $CDE$ 內接）
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">
  <!-- 圓心 O(200, 200)，半徑 r=120 -->
  <circle cx="200" cy="200" r="120" fill="none" stroke="#38bdf8" stroke-width="2.5" />
  
  <!-- 內接三角形 CDE：
       C = (200, 80)  [角度 90 deg, 200 + 120*cos(90), 200 - 120*sin(90)]
       D = (96, 260)  [角度 210 deg, 200 + 120*cos(210), 200 - 120*sin(210)]
       E = (304, 260) [角度 330 deg, 200 + 120*cos(330), 200 - 120*sin(330)]
  -->
  <polygon points="200,80 96,260 304,260" fill="none" stroke="#818cf8" stroke-width="2" />
  
  <!-- 圓心連線 (輔助線) OD, OE -->
  <line x1="200" y1="200" x2="96" y2="260" stroke="#64748b" stroke-width="1.5" stroke-dasharray="4,4" />
  <line x1="200" y1="200" x2="304" y2="260" stroke="#64748b" stroke-width="1.5" stroke-dasharray="4,4" />
  
  <!-- 點 -->
  <circle cx="200" cy="200" r="3.5" fill="#f8fafc" stroke="#38bdf8" stroke-width="1" />
  <circle cx="200" cy="80" r="3.5" fill="#f8fafc" stroke="#38bdf8" stroke-width="1" />
  <circle cx="96" cy="260" r="3.5" fill="#f8fafc" stroke="#38bdf8" stroke-width="1" />
  <circle cx="304" cy="260" r="3.5" fill="#f8fafc" stroke="#38bdf8" stroke-width="1" />
  
  <!-- 標籤 -->
  <text x="200" y="220" text-anchor="middle" dominant-baseline="hanging" fill="#f8fafc" font-size="15px">O</text>
  <text x="200" y="65" text-anchor="middle" dominant-baseline="auto" fill="#f8fafc" font-size="15px">C</text>
  <text x="80" y="265" text-anchor="end" dominant-baseline="middle" fill="#f8fafc" font-size="15px">D</text>
  <text x="320" y="265" text-anchor="start" dominant-baseline="middle" fill="#f8fafc" font-size="15px">E</text>
</svg>
```
