# 展示模式強化計畫（方案 C + A）— 已鎖定

狀態：**A2／B2／C2／D2 已拍板並實作（2026-10-15）**  
範圍：Field Ops 區域劇場／展示模式（`index.html` + `data/regions.json`）  
原則：靜態站、數字可追溯、同圖同口徑、現場不打即時房價 API。

本檔不再是問卷。第 4 節為你的選擇；第 5～6 節由實作方鎖定。若要改範圍，直接改本檔對應條再開工。

---

## 決定摘要

| 項 | 你的決定 |
|---|---|
| 0 目標 | 同意：C 對照牆 → A 情報卡 |
| 1 產品結構 | 同意，並改為大洛杉磯總圖（非只七城廊道） |
| 2 口徑鐵律 | 同意；西徹斯特／Playa Vista 為 **ZCTA 例外**（見 §3.2） |
| 3 地理 | 原七城 + 西區 + 北聖蓋博，共 **15 個展示單元** |
| 4.1 首屏 | **C**；主視覺是加州洛杉磯地區大圖 |
| 4.2 對照條 | 六項都做；**首屏只比選中城＋同廊道**（A2），全區對照為第二層 |
| 4.3 產業 | 只做 **居民就業（ACS DP03）**；另加趨勢列（見 §4.3） |
| 4.4 主圖 | **一律定位圖**（不做 Commons 地標圖） |
| 4.5 四宮格 | **另開「細節」** 才出現 |
| 4.6 語言 | 與全站相同（中文為主、英文專有名詞並列） |
| 4.7 文案 | 每城 **pitch + 對照金句 + 趨勢句**，盡量豐富 |
| 4.8 地圖 | **手繪感 SVG**；多邊形從 TIGER 簡化，禁止憑記憶亂畫 |
| 4.9 配色 | 四群一色（見 §4.9），不給 15 城各一色 |
| 4.10 UI | **更像簡報**（底部分群點、左右切城、藏學習導覽） |
| 4.11 更新 | **寫死每季**：你呼叫一次，重跑過期資料 |
| 5～6 技術 | 你授權「怎麼順手怎麼做」→ 已鎖在本檔 |
| 7 順序 | 同意 §7 |
| 8 授權註記 | 同意 |
| 9 補充 | 無 |

---

## 0. 目標一句話

展示首屏用 **C：大洛杉磯對照牆 + 四廊道總圖**，點進去用 **A：單城情報卡（定位圖／KPI／居民產業／趨勢／pitch）**。讓不熟南加的人先看到「這座城在大 LA 的哪一塊」，再聽學區與適配客群。

- [x] 同意此目標

---

## 1. 產品結構（已鎖定）

```text
展示模式首屏 ＝ 方案 C 對照牆
  ├─ 大洛杉磯總圖（Westchester ←→ Ontario）+ **西區小圖**（B2）
  │     四群填色 + 極淡 LA 市界（D2，不用全市數字）+ 高速公路示意
  ├─ 點城 → 該城高亮，同群其餘半亮，他群變淡
  └─ 下方對照條（A2／C2）
        預設：選中城 + 同廊道（只含 status=ready）
        第二層「全區對照」：ready 七城；draft 只在圖上有輪廓
        指標：人口 | 亞裔% | 西語裔% | 家戶所得 | SFH 中位 | 居民產業前三大

點城／「進入這座城」＝ 方案 A 情報卡
  ├─ 同一套邊界的定位圖（該城放大，大 LA 縮圖指北）
  ├─ KPI：人口、亞裔%、西語裔%、SFH、家戶所得
  ├─ 居民產業條（ACS DP03）
  ├─ 趨勢列（見 §4.3）
  └─ pitchLine + compareLine + trendLine

「細節」按鈕 ＝ 四宮格（基本盤／價格帶／亮點／注意）
  └─ 預設不出現；展示中另開才展開
```

- [x] 同意此資訊架構  
- [x] 首屏改為大洛杉磯圖，不是只畫 60 廊道七塊

---

## 2. 口徑鐵律（已鎖定）

1. **預設地理單位 = Census place**（建制市 + CDP）。同一張對照圖不把 ZIP 和全市混軸。  
2. **例外（你新增西區後必須寫死）：** Westchester、Playa Vista **不是** Census place，用 **ZCTA**（見 §3.2）。Culver City 仍用 place。對照牆這兩格標「ZCTA」，不假裝是市。  
3. 同一張對照圖：同一來源、同一 vintage、同一欄位定義。ZCTA 與 place 可並排 **ACS 同一表**，但標籤必須標單位。  
4. **Asian alone ≠ 台／陸籍**；畫面寫普查分類。  
5. ACS「屋主自估房價」**不**和 Redfin 成交中位畫在同一條軸。  
6. 展示現場只讀烘焙好的 JSON／SVG；Census 只在本機更新腳本時呼叫。  
7. 哈仙達崗若沒有與他城同口徑的 SFH 中位，對照條顯示「未核對」，不拿 ZIP 全類型硬比。  
8. 新八城在 `ready` 之前：地圖可畫輪廓，數字缺就空白，不填假數據。

- [x] 全部同意，加上 §3.2 例外

---

## 3. 展示地理清單（15 單元）

座標取 Census 2025 Gazetteer（place）內點。GEOID 以 Gazetteer 為準。

### 3.1 建制市／CDP（Census place）

| id | 中文 | English | 類型 | GEOID | 內點 | 建議 ZIP | clusterId | 現況 |
|---|---|---|---|---|---|---|---|---|
| `diamond-bar` | 鑽石吧 | Diamond Bar | city | `0619192` | 34.002, −117.818 | 91765 | `east-sgv-60` | ready |
| `walnut` | 沃爾納特 | Walnut | city | **`0683332`** | 34.037, −117.856 | 91789 | `east-sgv-60` | ready |
| `rowland-heights` | 羅蘭崗 | Rowland Heights | CDP | **`0663218`** | 33.970, −117.891 | 91748 | `east-sgv-60` | ready |
| `hacienda-heights` | 哈仙達崗 | Hacienda Heights | CDP | `0631596` | 33.996, −117.973 | 91745 | `east-sgv-60` | ready |
| `chino-hills` | 奇諾崗 | Chino Hills | city | `0613214` | 33.943, −117.726 | 91709 | `west-ie` | ready |
| `ontario` | 安大略 | Ontario | city | `0653896` | 34.037, −117.606 | 91761 / 91764 / 91762 | `west-ie` | ready |
| `pomona` | 波莫納 | Pomona | city | `0658072` | 34.058, −117.761 | 91766 / 91767 / 91768 | `west-ie` | ready |
| `culver-city` | 卡爾弗城 | Culver City | city | `0617568` | 34.006, −118.397 | **90230**（市內還有 90232） | `westside-lax` | draft |
| `san-marino` | 聖馬利諾 | San Marino | city | `0668224` | 34.123, −118.113 | 91108 | `core-sgv-north` | draft |
| `south-pasadena` | 南帕薩迪納 | South Pasadena | city | `0673220` | 34.109, −118.157 | 91030 | `core-sgv-north` | draft |
| `arcadia` | 亞凱迪亞 | Arcadia | city | `0602462` | 34.133, −118.036 | 91006 / 91007 | `core-sgv-north` | draft |
| `temple-city` | 天普市 | Temple City | city | `0678148` | 34.102, −118.058 | 91780 | `core-sgv-north` | draft |
| `rosemead` | 羅斯密 | Rosemead | city | `0662896` | 34.069, −118.083 | 91770 | `core-sgv-north` | draft |

**GEOID 勘誤（必讀）：** 初稿把 Walnut 寫成 `0683346`，那是北加州 **Walnut Creek**。南加沃爾納特正確為 `0683332`。羅蘭崗 Gazetteer 2025 為 `0663218`（舊稿 `0663204` 不用）。

### 3.2 ZCTA 例外（不是市、不是 CDP）

| id | 中文 | English | 單位 | GEOID／ZCTA | 客戶 ZIP | clusterId | 現況 |
|---|---|---|---|---|---|---|---|
| `westchester` | 西徹斯特 | Westchester | **ZCTA** | `90045` | 90045 | `westside-lax` | draft |
| `playa-vista` | 普拉亞維斯塔 | Playa Vista | **ZCTA** | `90094` | 90094 | `westside-lax` | draft |

畫面必註：

- Westchester、Playa Vista 是 **LA 市內社區**，行政上不是獨立市。  
- ACS／地圖用 ZCTA，**不等於**社區口語邊界。90045 含 LAX 周邊，人口／產業會被機場帶影響。  
- Culver City 是獨立市；你寫的 90230 只是該市 ZIP 之一，對照人口用 **全市 place**，不用 90230 冒充全市。  
- 「Playa Vista & Culver City」當 **對照配對**（相鄰、常被同一批西區客人一起問），仍是 **兩張卡、兩塊多邊形**。  
- 「天普市 / Rosemead」同樣：**兩張卡**，對照配對，不合併。

邊界檔：place 用 `cb_*_06_place_500k`；兩塊 ZCTA 用同年 `cb_*_us_zcta520_500k`（或等價）濾 `90045`、`90094`。禁止用 LA 全市多邊形代替這兩格。

### 3.3 分群（地圖由西到東）

| clusterId | 中文 | 單元 | 地圖排序 |
|---|---|---|---|
| `westside-lax` | 西區 · LAX／海霧帶 | Westchester、Playa Vista、Culver City | 10 |
| `core-sgv-north` | 核心聖蓋博 · 110／210 | 南帕、聖馬利諾、亞凱迪亞、天普市、羅斯密 | 20 |
| `east-sgv-60` | 東聖蓋博 · 60 廊道 | 鑽石吧、沃爾納特、羅蘭崗、哈仙達崗 | 30 |
| `west-ie` | 西內陸帝國入口 | 奇諾崗、安大略、波莫納 | 40 |
| `west-southbay-oc` | 西區／南灣／橙縣（預留） | 托倫斯、爾灣等 — **本期不進展示圖** | 90 |

`west-southbay-oc` 保留給以後，避免和本期西區三格搶同一圖層。

---

## 4. 個性化選項（已圈定）

### 4.1 首屏

**C 首屏。** 主圖是大洛杉磯地區總圖（西起灣區示意、東到 Ontario），不是七城局部廊道。一致性來自：**同一 TIGER 來源、同一簡化演算法、同一線寬與配色**，而不是找風格不一的網圖拼貼。

### 4.2 對照牆指標（全部做）

1. 總人口（ACS）  
2. Asian alone %（ACS）  
3. Hispanic or Latino %（ACS）  
4. 家戶所得中位（ACS）  
5. SFH 成交中位（Redfin Living-in；缺則「未核對」）  
6. 居民產業前三大（ACS DP03）

缺值一律留空格，禁止拿不同口徑填滿。

### 4.3 產業 + 趨勢

- **主圖只做居民就業（ACS DP03）**，標籤寫「居民從事的產業」。不做 LEHD 本地崗位。  
- **另加趨勢列**（情報卡 + 對照牆可收成一條「趨勢」）：  

| 趨勢 | 來源 | 用途 |
|---|---|---|
| 人口規模 | 當期 ACS 5-year | 城有多大 |
| 學士及以上 % | ACS DP02 | 學區／客群敘事輔助（不是學區分數） |
| 自住率（owner-occupied） | ACS DP04 | 租買結構 |
| 家戶所得中位 | ACS DP03 | 與價格帶對讀 |
| 相對上一檔 ACS 5-year 的人口／所得變化 | 兩期 ACS | 這才是「趨勢」；不是即時行情 |

禁止：治安分數、GreatSchools 單一分數、假裝 YoY 房價 API。

### 4.4 主圖

一律自產定位圖。不抓 Commons／Wiki 地標照。

### 4.5 四宮格

情報卡預設只看到圖 + KPI + 產業 + 三句話。**「細節」** 才打開四宮格。

### 4.6 語言

與全站相同。

### 4.7 文案欄位

每城三句（`ready` 前可暫用工作稿，你隨時改字）：

| 欄位 | 作用 |
|---|---|
| `pitchLine` | 開場：這是哪、為什麼客人會問 |
| `compareLine` | 對照：若你熟 A，這座城差在哪 |
| `trendLine` | 趨勢：用 ACS 變化＋結構一句話，不寫保證升值 |
| `feelAxes` | 感性四軸（不是分數）：週末怎麼過／學區壓力／街上感覺／華語生活圈。每軸一個 tag + 一句人話 |

### 4.8 地圖美學

手繪感 SVG：**TIGER 多邊形簡化 → 略加紙質／不規則描邊**。高速公路用官方對位的示意線（10／110／405／605／210／60／57／71），標註即可，不畫到像 Google。弱網離線可開。禁止手繪走位導致聖馬利諾跑到 60 廊道。

### 4.9 配色（四群方案）

15 城若各一色會花。大圖用 **四群填色 + 選中加墨線**。

| 群 | CSS 變數 | 色 | 為什麼 |
|---|---|---|---|
| 西區 LAX | `--cluster-westside` | `#3D7A7A` 海霧青 | 靠灣、機場、西區 |
| 核心 SGV | `--cluster-sgv` | `#6B3A3A` 山茶紅 | 聖馬利諾山茶花／老聖蓋博 |
| 東 SGV 60 | `--cluster-east` | `#C4A06A` 山茶金 | 沿用劇場沙色家族 |
| 西 IE | `--cluster-ie` | `#4A6280` 內陸藍 | 物流／內陸，冷色對比山城 |

狀態：

- 選中城：100% 填色 + 2.5px `--theater-ink` 描邊  
- 同群未選：約 70%  
- 他群：約 28%  
- 底紙：既有 `--theater-mist`  
- 海：極淺藍灰，只示意聖塔莫尼卡灣，不當裝飾blobs

### 4.10 更像簡報

- 藏學習導覽與 footer；留「退出展示」  
- 左側城市清單改成 **底部廊道點 + 城名**（簡報底欄）  
- 左右切城；Esc 退出  
- 首屏就是總圖；進城後底欄仍在，方便跳城  
- 不要同時出現學習模組 tab

### 4.11 更新節奏（寫死）

**每一季由你呼叫一次「更新區域展示資料」。** 當季工作：

1. **每次都做：** 核對 Redfin Living-in SFH／全類型，改 `priceBand` + `asOf`；缺口徑的維持「未核對」。  
2. **有新 ACS 5-year vintage 才做：** 重跑 `scripts/fetch_region_snapshot.py`，換 `snapshot.vintage`。ACS 一年一檔，沒有新表就不動人口／產業。  
3. **TIGER 邊界：** 通常一年一檔；無幾何變更則不重出 SVG。  
4. **新加城：** 只追加 JSON + 重出含該 GEOID 的 SVG，不改架構。

腳本與本檔保持這段文字，避免變成「有空再抓」。

---

## 5. 公開 API 與烘焙（實作方鎖定）

現場網站**不**直連下列 API。

### 5.1 ACS 5-year

- 申請 key（不進 git）：https://api.census.gov/data/key_signup.html  
- 鎖定 **當下最新 ACS 5-year Data Profile**（實作時探測 `2024`，沒有則 `2023`）。  
- Place 一次拉 13 個 place；ZCTA 另拉 `90045,90094`。  
- 表：DP05 人口種族、DP03 所得與居民產業、DP02 學歷、DP04 自住率。  
- 趨勢：再拉「上一檔」同一組變數，算人口／所得差。  

變數名以該年 groups 頁為準，腳本內寫死對照表，不在瀏覽器猜。

### 5.2 地圖邊界

- Place：`cb_{year}_06_place_500k`  
- ZCTA：同年全國 ZCTA cartographic boundary，濾兩碼  
- 產出 `data/region-shapes.json`（簡化座標）+ `assets/regions/la-locator.svg`（手繪風格總圖）  
- 單城定位圖用同一 shapes、不同 viewBox，保證套合

### 5.3 LEHD

本期不做、不預留畫面。JSON 不必開空欄。

### 5.4 座標

優先 Gazetteer 內點；ZCTA 用對應 gazetteer／TIGER 質心。不用 Wikipedia 當數字來源。Wiki 摘要不當主文。

### 5.5 圖檔

只產 locator SVG。不抓 Commons。Attribution：U.S. Census Bureau（ACS／TIGER）。若 SVG 底有海岸線來自 OSM 岸線則加 OSM；若只用 TIGER 水體則只寫 Census。

### 5.6 明確不接

- 即時房價 API  
- 各市府 GIS 混接  
- 治安分數、GreatSchools 單一分數  
- 只含 Incorporated Place、不含 CDP 的地圖層  
- 用 LA 全市代替 Westchester／Playa Vista  
- 用 90230 ZCTA 代替 Culver City 全市

---

## 6. JSON 草稿（實作方鎖定）

每城在現有四宮格之外增加：

```json
"geo": {
  "geoid": "0683332",
  "lat": 34.037195,
  "lng": -117.855606,
  "kind": "city"
},
"snapshot": {
  "vintage": "ACS 2020–2024",
  "priorVintage": "ACS 2015–2019",
  "population": null,
  "populationDeltaPct": null,
  "asianAlonePct": null,
  "hispanicPct": null,
  "medianIncome": null,
  "medianIncomeDeltaPct": null,
  "bachelorsPlusPct": null,
  "ownerOccupiedPct": null,
  "residentIndustry": [],
  "priceSfh": null,
  "priceAsOf": null,
  "unit": "place"
},
"media": {
  "locator": "assets/regions/la-locator.svg#walnut"
},
"compareLine": "…",
"trendLine": "…"
```

- `kind`：`city` | `cdp` | `zcta`  
- ZCTA 兩筆 `snapshot.unit` = `"zcta"`，`geo.geoid` = `"90045"` / `"90094"`  
- `priceSfh` 有 Redfin Living-in 才填數字；哈仙達崗目前維持 null  
- 另檔 `data/region-shapes.json`  
- `clusters[].color` 寫入 §4.9 色碼，前端不硬編碼城色

---

## 7. 實作順序（已同意）

| 步 | 做什麼 | 你能先看到什麼 |
|---|---|---|
| 0 | 統一 Redfin SFH 口徑；哈仙達崗缺則對照留空；寫入 15 單元 geo | 對照牆不會比錯價、不會畫錯 Walnut |
| 1 | `scripts/fetch_region_snapshot.py` → ACS snapshot | 有 key 就能灌人口／產業／趨勢 |
| 2 | TIGER → 簡化 → 手繪感大洛杉磯 SVG | C 首屏可點 15 塊 |
| 3 | 簡報化 UI：對照牆 + 情報卡 +「細節」+ 底欄切城 | 可對客翻頁 |
| 4 | 補新八城四宮格與三句話 | 已補：6 城 `ready`；Westchester／Playa Vista `review`（SFH 軸空白） |
| 5 | LEHD | **取消** |

2026-10-15 資料補完：15 城 ACS snapshot 已烘焙；每城有 pitch／compare／trend／explainZh。新八城不擋地圖。

---

## 8. 授權／畫面必備註記

- ACS／TIGER：U.S. Census Bureau + 表號／年份  
- 價格：Redfin + `asOf`  
- 種族： **Asian alone（普查分類）**  
- ZCTA 格：加「郵遞區統計區，非市界」  
- 本期無 OSM／Commons 則不顯示那些授權

- [x] 同意

---

## 9. 補充

無。三句話工作稿先由實作寫入，你之後改。

---

## 10. 開工依據

- [x] 依本檔開始實作第 0～3 步  
- [x] 第 4 步資料補完（ACS + Living-in SFH + 三句話／對客提示）；西區兩格 ZCTA 維持 review

日期：2026-10-15  
確認人：使用者口頭／聊天鎖定
