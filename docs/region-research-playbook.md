# 南加區域調查手冊（Region Research Playbook）

給 Wave 1 起、可往西／往北複製的固定採集流程。每新增一城，只追加 `data/regions.json` 一筆，並把 `status` 從 `draft` → `review` → `ready`。

## 1. 調查原則

1. **速查優先**：寫給自己在客戶面前 30 秒能講完，不是寫論文。  
2. **可追溯**：每個關鍵數字進 `sources[]`（來源名 + URL 或「實地備忘」+ 日期）。  
3. **不裝精確**：房價／學區用區間與敘事帶；禁止假裝即時 API。  
4. **合規**：不寫「保證升值」「包過戶」；價格標「備忘區間」。  
5. **一句話 pitch**：每城必有 `pitchLine`（對台／港／陸客戶怎麼開場）。

## 2. Wave 地圖

### Wave 1（本輪必填骨架）

| id | 中文 | English | 建議 ZIP | clusterId |
|---|---|---|---|---|
| `diamond-bar` | 鑽石吧 | Diamond Bar | 91765 | `east-sgv-60` |
| `walnut` | 沃爾納特 | Walnut | 91789 | `east-sgv-60` |
| `rowland-heights` | 羅蘭崗 | Rowland Heights | 91748 | `east-sgv-60` |
| `hacienda-heights` | 哈仙達崗 | Hacienda Heights | 91745 | `east-sgv-60` |
| `chino-hills` | 奇諾崗 | Chino Hills | 91709 | `west-ie` |
| `ontario` | 安大略 | Ontario | 91761, 91764, 91762 | `west-ie` |
| `pomona` | 波莫納 | Pomona | 91766, 91767, 91768 | `west-ie` |

### Wave 2（展示擴充 — 已建檔 `draft`）

西區 · LAX／海霧帶 → `westside-lax`  
`westchester`（ZCTA 90045）、`playa-vista`（ZCTA 90094）、`culver-city`

核心聖蓋博 · 110／210 → `core-sgv-north`  
`south-pasadena`, `san-marino`, `arcadia`, `temple-city`, `rosemead`

GEOID、ZCTA 例外與展示配色見 `docs/present-mode-ac-plan.md`。

### Wave 3（往南灣／橙縣 — 僅預留，不進本期總圖）

示例 id：`torrance`, `irvine` → `west-southbay-oc`

## 3. 每城固定四宮格

### A. 基本盤 `basics`

| 欄位 | 要寫什麼 | 範例問法 |
|---|---|---|
| `zips` | 主要郵遞區號 | 客戶說的地址落在哪？ |
| `chineseBelt` | 華人生活圈定位 | 「老牌華人山城／新興台客聚落／物流倉儲城」 |
| `schoolBand` | 學區敘事帶（非單一分數） | 公立學區名 + 「強／中／選私校」 |
| `commuteAxes` | 通勤軸 | 60 / 57 / 10 / 71；到 LAX、DTLA、OC 大致時間 |

### B. 價格帶 `priceBand`

| 欄位 | 要寫什麼 |
|---|---|
| `sfhRange` | 獨立屋備忘區間（例如 `$1.1M–$1.6M`） |
| `condoRange` | Condo／Townhome 區間；若稀缺寫 `limited` |
| `ageProfile` | 屋齡結構（1970s 山城 / 1990s 規劃社區…） |
| `hoaMello` | HOA 常見區間；是否常見 Mello-Roos |
| `asOf` | 區間參考日 `YYYY-MM` |

### C. 核心亮點 `highlights`

| 欄位 | 要寫什麼 |
|---|---|
| `jobs` | 就業圈：倉儲物流、醫療、矽灘通勤、當地商業 |
| `amenities` | 華人超市／餐廳／補習距離敘事 |
| `safetyNote` | 治安相對敘事（相對鄰城，不做犯罪統計牆） |
| `buyerFit` | 最適客戶畫像：學區自住／首購／收租／資金出海停車 |

### D. 實務注意 `caveats`

| 欄位 | 要寫什麼 |
|---|---|
| `propertyCaveats` | 屋況：坡地、老水管、白蟻、山火保險 |
| `taxCaveats` | 稅／特殊費：Mello-Roos、高保險區 |
| `schoolReality` | 入學現實：住址、開放登記、私校備選 |
| `pitchLine` | **對外一句話**（必填才可標 `ready`） |
| `compareLine`（城頂層） | 對照金句：若你熟 A，這座城差在哪 |
| `trendLine`（城頂層） | 趨勢句：ACS 結構／變化，禁止保證升值 |

## 4. 建議資料來源層級

| 優先 | 來源類型 | 用途 |
|---|---|---|
| 1 | 你自己帶看／成交備忘 | buyerFit、pitchLine、caveats |
| 2 | MLS／公佈成交摘要（手動整理） | priceBand 區間 |
| 3 | 學區官方／GreatSchools 等（只作帶狀參考） | schoolBand |
| 4 | 市政府／縣府稅與 Mello-Roos 說明 | taxCaveats |
| 5 | 地圖通勤（Google 離峰／尖峰各記一筆） | commuteAxes |

寫入 `sources[]`：

```json
{ "label": "MLS 備忘區間", "url": "", "date": "2026-10", "note": "SFH 主動掃描" }
```

## 5. 狀態機

```text
draft   → 只有 meta + 空四宮格（P0/P1 允許上線顯示「調查中」）
review  → 四宮格填齊，待你自己過目
ready   → 有 pitchLine + lastReviewed + 至少 1 筆 price/school 來源
```

UI 規則：`draft` 不顯示假數字；`ready` 才進「可對比」預設集合（P2）。

## 6. 單城填寫 checklist（複製用）

- [ ] meta：id / 中英名 / zips / cluster / wave  
- [ ] basics 四欄  
- [ ] priceBand + `asOf`  
- [ ] highlights 四欄  
- [ ] caveats 四欄（含 pitchLine）+ compareLine + trendLine  
- [ ] compareTags（至少 2 個，如 `學區`, `山城`, `60廊道`, `首購`, `物流就業`）  
- [ ] sources ≥ 2  
- [ ] lastReviewed 當天  
- [ ] status → `review` 或 `ready`  

## 7. 對比標籤建議詞表（控制用詞）

`學區` `山城` `規劃社區` `60廊道` `57廊道` `10號公路` `首購友善` `豪宅帶` `Condo多` `物流就業` `醫療就業` `老屋翻新` `Mello-Roos` `高保險` `台客聚落` `多元租盤`

新增標籤可以，但總覽篩選會變吵；盡量复用。

## 8. P1 UI 對 playbook 的期望

- 總覽：依 `clusterId` 分組；顯示 nameZh、schoolBand 摘要、sfhRange 或「調查中」  
- 詳情：四宮格 Accordion；footer 重複全域免責  
- 不在 P1 做地圖多邊形、即時抓價、多語言 CMS
