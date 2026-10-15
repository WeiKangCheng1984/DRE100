# DRE-100 Field Ops Hub — Architecture (Adapted)

> 適配本倉現況的規格。專家原稿假設 Next.js + Supabase；本專案採 **靜態增量**，先交付可擴展的南加區域調查與雙軌導覽。

## 1. Positioning

| 面向 | 定義 |
|---|---|
| Core Identity | **DRE Exam Knowledge Base（公開學習）** + **CA–TW Field Ops Hub（個人實戰）** |
| Primary user | 你自己：電話／咖啡桌旁速查區域、流程、客戶初梳 |
| Assisted user | 準客戶：低摩擦需求梳理（P4 再上） |
| Public visitor | 法規／考試知識庫，建立專業可信度 |

**本輪地理戰略：**

1. **Wave 1**：東聖蓋博谷／60 號公路華人帶 + 西內陸帝國入口（七城 `ready`）  
2. **Wave 2（展示擴充）**：西區 LAX 帶（Westchester ZCTA 90045、Playa Vista ZCTA 90094、Culver City）+ 核心聖蓋博 110／210（南帕、聖馬利諾、亞凱迪亞、天普市、羅斯密）  
3. **Wave 3（預留，不進本期總圖）**：托倫斯、爾灣等 → `west-southbay-oc`  

展示模式鎖定規格：`docs/present-mode-ac-plan.md`。  

## 2. Technical Constraints (Do Not Ignore)

| 現況 | 含義 |
|---|---|
| 單檔 `index.html` + `data/*.json` + Python scripts | **不**先引入 `app/`、Next.js、react-hook-form |
| Vercel 靜態部署 | 新模組以 JSON 驅動、前端渲染 |
| 進度在 `localStorage` | 學習模組原樣保留，避免破壞既有狀態鍵 |
| 無後端 | Intake 寫入 Supabase **延後到 P5**；P4 先做摘要卡 |

## 3. Information Architecture

```text
[Hub Landing]
  ├─ 學習庫 (Study)          ← 既有七模組，導覽歸組，不重寫
  │    名詞手冊 / 精讀講義 / 成交實務 / 衝刺280 / 會話 / 題庫×2
  │
  └─ 實戰工作區 (Field Ops)  ← 新增
       ├─ 區域分析 (regions)     P1 殼 + Wave 1 骨架；內容在 P2 填滿
       ├─ 實戰手冊 (guides)      P3
       └─ 需求評估 (intake)      P4（摘要卡）→ P5（可選後端）
```

**路由策略（P1）：** 維持同頁 `switchModule()`；可用 `?module=regions&city=diamond-bar` hash/query 深連結，便於平板收藏。真 URL 路由等有明確需求再評估 Next／多頁靜態。

## 4. Dual Navbar (P1)

- **Brand**：DRE-100｜副標 Study & Field Ops  
- **學習庫**：既有模組下拉或橫向分組  
- **實戰手冊**：Escrow／持有成本／海外貸款（P3 再掛）  
- **區域分析**：進區域總覽  
- **需求評估**：Primary CTA（P1 可先佔位連到即將上線頁；P4 實作表單）  

Mobile-first：導覽可折疊；區域與指引頁以 Accordion、Badge、Checklist 為主，避免長文。

## 5. Region Data Model

單一真相來源：`data/regions.json`。

### 5.1 Top-level

```json
{
  "version": 1,
  "titleZh": "南加區域速查",
  "titleEn": "SoCal Region Field Cards",
  "disclaimerZh": "…",
  "clusters": [ /* corridor 定義 */ ],
  "regions": [ /* 城市卡 */ ]
}
```

### 5.2 Cluster（走廊／分群，利於往西往北擴）

| id | nameZh | wave 預設 |
|---|---|---|
| `westside-lax` | 西區 · LAX／海霧帶 | 2 |
| `core-sgv-north` | 核心聖蓋博 · 110／210 | 2 |
| `east-sgv-60` | 東聖蓋博 · 60 廊道 | 1 |
| `west-ie` | 西內陸帝國入口 | 1 |
| `west-southbay-oc` | 南灣／橙縣（預留） | 3 |

新增城市＝新增 `regions[]` 一筆並掛上既有或新 `clusterId`；**不必改 UI 架構**。

### 5.3 Region card（四宮格 + 營運欄位）

| 區塊 | 欄位 | 說明 |
|---|---|---|
| Meta | `id`, `slug`, `nameZh`, `nameEn`, `clusterId`, `wave`, `status` | `status`: `draft` \| `review` \| `ready` |
| 基本盤 | `zips`, `chineseBelt`, `schoolBand`, `commuteAxes` | 學區用「帶／敘事」，不綁即時 API |
| 價格帶 | `sfhRange`, `condoRange`, `ageProfile`, `hoaMello` | 區間文字 + 更新日期 |
| 亮點 | `jobs`, `amenities`, `safetyNote`, `buyerFit` | 台／客族群適配一句話 |
| 注意 | `propertyCaveats`, `taxCaveats`, `schoolReality`, `pitchLine` | 對客戶怎麼講 |
| 營運 | `compareTags`, `lastReviewed`, `sources[]` | 調查可追溯 |

完整欄位約定見 `docs/region-research-playbook.md`。

## 6. Phase Plan (Locked for P0/P1)

### P0 — 規格與資料骨架（本文件 + JSON）

- [x] 架構適配（本文件）  
- [ ] `docs/region-research-playbook.md`  
- [ ] `data/regions.json`：Wave 1 七城 `status: draft`  
- [ ] 標準 Footer 免責文案定稿  

**Done when：** 之後任何人可依 playbook 填一城，且 UI 無需改 schema。

### P1 — 雙軌殼層 + 區域總覽

- Hub Landing：Study vs Field Ops 雙入口  
- Navbar 雙軌分組 + Footer 免責  
- `regions` 模組：依 cluster 列出 Wave 1；點入四宮格殼  
- `draft` 城顯示「調查中」，不假裝資料齊全  
- 深連結：`?module=regions`  

**明確不做（P1）：** Supabase、Intake 後端、持有成本計算器、學區即時 API、重寫學習模組、Next.js 遷移。

### Later

| 階段 | 內容 |
|---|---|
| P2 | 填滿 Wave 1 七城調查；總覽對比（學區／價格／通勤） |
| P3 | Escrow 30 天、持有成本、外國人貸款；連回成交實務 |
| P4 | Intake 多步驟 → 需求摘要卡 |
| P5 | （可選）Supabase／通知；或再評估框架升級 |
| Wave 2/3 | 往北、往西加城，只追加 JSON |

## 7. Compliance Footer (Canonical)

> 本站內容為加州地產法規研究與市場資訊整理，非公開房產仲介招攬。實體交易合約由南加州持牌經紀團隊（Responsible Brokerage）依法辦理。區域與價格資訊僅供個人實戰備忘，非估價或投資建議。

中英雙語可並列；P1 必須上線。

## 8. Overlap with Existing Modules

| 新模組 | 既有資產 | 原則 |
|---|---|---|
| 區域分析 | 無 | 新建 `data/regions.json` |
| Escrow／表單指引 | `field_practice.json`（24 表單 A+B+C） | P3 **連結／摘要**，不複製長文 |
| 學習庫 | glossary / notes / quiz / cram / speak | **零重寫**；只改導覽歸組 |

## 9. Cursor Implementation Notes

1. 先改資料與導覽殼，再填調查內容。  
2. 價格與學區數字必須帶 `lastReviewed`；過期在 UI 標示。  
3. 新增城市不得 soft-code 在 HTML；只讀 `regions.json`。  
4. 專家原稿中的 `app/ops/...`、`skill.md` Next 路徑 **作廢**；以本文件為準。
