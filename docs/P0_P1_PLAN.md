# P0 / P1 執行計畫 — 大規模南加區域調查前置

視覺摘要：[P0／P1 區域擴展規劃 Canvas](https://cursor.com/canvas/store-27487f12-607c-4f24-a47b-3e3fcb6ae6bd/a8779737-e8a4-454c-b347-b72c725f180d)

## 目標一句話

把網站從「純 DRE 讀書站」轉成 **Study + Field Ops**，並讓 **東聖蓋博／60 廊道 + 西 IE 七城** 成為可擴展區域調查的第一塊拼圖；西區與北區只預留 corridor，不擋本期。

## P0 — 規格與資料骨架

| 產出 | 路徑 | 完成定義 |
|---|---|---|
| 適配架構 | `docs/ARCHITECTURE.md` | 靜態增量、雙軌 IA、波次策略寫死 |
| 調查手冊 | `docs/region-research-playbook.md` | 四宮格欄位、來源層級、status 流轉 |
| 區域 JSON | `data/regions.json` | 4 clusters + Wave 1 七城 `draft` |
| 本計畫 | `docs/P0_P1_PLAN.md` | P1 實施清單可直接開幹 |

### Wave 1 城市清單（已入 JSON）

**東聖蓋博 · 60 廊道：** 鑽石吧、沃爾納特、羅蘭崗、哈仙達崗  

**西內陸帝國入口：** 奇諾崗、安大略、波莫納  

### P0 验收

- [x] Schema 支援任意加城（只改 JSON）  
- [x] Wave 2/3 cluster 已預留  
- [x] 免責文案進 `regions.json` top-level  
- [ ] README 加「Field Ops／區域調查」入口說明（P1 實作時一併改）

## P1 — 雙軌殼層 + 區域總覽 UI

### 範圍

1. **Brand / Navbar**  
   - 標題改為 DRE-100｜Study & Field Ops  
   - 導覽分組：學習庫｜區域分析｜實戰手冊（P3 佔位）｜需求評估 CTA（P4 佔位）  
   - 既有七模組全部保留，歸入學習庫  

2. **Hub 感（輕量）**  
   - 首屏或模組切換前：Study / Field Ops 兩個入口（不要做成儀表板）  
   - Field Ops 預設進「區域分析」  

3. **區域模組 `regions`**  
   - `fetch('data/regions.json')`  
   - 依 `clusters`（wave=1 優先）分組列表  
   - 點城市 → 四宮格詳情；`draft` 顯示「調查中」  
   - 支援 `?module=regions&city=diamond-bar`  

4. **Footer**  
   - 使用 canonical 免責（中英可折疊）  

### P1 不做

- 填滿七城調查正文（→ P2）  
- Escrow／持有成本／貸款長頁（→ P3）  
- Intake 表單與 Supabase（→ P4/P5）  
- Next.js 遷移、地圖多邊形、即時房價 API  

### P1 實施順序（給實作 PR）

1. 在 `index.html` 增加 `regionsMain` 區塊與導覽按鈕  
2. 加入 `switchModule('regions')` 與 JSON loader  
3. 渲染 cluster 分組總覽 + 城市詳情（四宮格）  
4. 調整 header 為雙軌分組（學習庫摺疊／橫向）  
5. Footer 免責  
6. 本機 `python -m http.server 8765` 驗證手機寬度  

### P1 验收

- [ ] 平板寬度可切到區域總覽並展開任一 Wave 1 城  
- [ ] draft 城不顯示空白假數字  
- [ ] 學習模組切換與 localStorage 行為未壞  
- [ ] 免責可見  

## 後續銜接

| 階段 | 依賴 P0/P1 | 內容 |
|---|---|---|
| P2 | regions UI | 依 playbook 填七城 → `ready`；加簡易對比 |
| P3 | 雙軌導覽 | guides + 連結成交實務 |
| P4 | CTA 入口 | Intake → 摘要卡 |
| Wave 2/3 | schema | 往北／往西只追加 `regions[]` |

## 決策紀錄

| 決策 | 選擇 | 原因 |
|---|---|---|
| 地理優先 | East SGV / 60 + West IE | 符合你實際客戶動線 |
| 技術 | 靜態 JSON + 既有 SPA | 最快可上；調查規模靠資料擴不是靠框架 |
| 90045／Irvine | Wave 3 預留 | 不刪戰略，只是延後 |
| 專家 Next skill | 不採用原路徑 | 與本倉不符；以 `ARCHITECTURE.md` 為準 |
