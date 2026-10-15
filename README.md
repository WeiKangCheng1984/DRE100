# 加州 DRE 不動產複習網（Study & Field Ops）

靜態網站，雙軌定位：**DRE 學習庫** + **個人跨國地產實戰工作站（Field Ops Hub）**。

## 學習庫（既有）

- **名詞手冊**：100 組易混淆名詞（條列檢視、字卡翻閱、領域篩選、收藏／已掌握）
- **精讀講義**：從 `plus.txt` 整理的章節知識點（中英對照、考點、文法拆解）。內含子功能 **長句練習**：76 句考試長難句，先看英文再揭曉解析。
- **成交實務**：從 `new function.md` / `data/field_practice.json` 整理的雙語實務手冊——課文精讀、**A+B 表單導覽**（關鍵欄位／常見錯／虛構成交填寫範例）、可勾選檢查清單、**C 層情境表單手冊**（先想再揭曉）。
- **衝刺280**：考前 280 關鍵聯想（英文題幹關鍵詞 → 答案；條列／英文字卡；章節篩選）。資料：`data/cram280.json`、`考前衝刺_280關鍵知識點.md`。
- **題庫練習**：約 225 題選擇題，可上一題／下一題、跳到指定題號，作答後立刻顯示對錯與解析。進度存在瀏覽器 `localStorage`。
- **題庫練習二**：約 210 題艱難考題（`exam bank 2.txt`），同樣可順序刷題、跳題與看解析；進度與第一套題庫分開保存。
- **題庫練習三**：LV17 評量約 100 題，並接續 `exam bank 3-2.txt` 的 Level 延伸題（合計約 300 題）；中英對照與解析，進度獨立保存。

## Field Ops（升級中）

大規模南加區域調查採「靜態 JSON 可擴展」路線，**Wave 1 優先東聖蓋博／60 廊道 + 西內陸帝國**：

鑽石吧、沃爾納特、羅蘭崗、哈仙達崗、奇諾崗、安大略、波莫納（往西／往北為 Wave 2–3 預留）。

| 文件 | 用途 |
|---|---|
| `docs/ARCHITECTURE.md` | 雙軌架構與階段邊界（P0 規格） |
| `docs/region-research-playbook.md` | 每城四宮格調查手冊 |
| `docs/P0_P1_PLAN.md` | P0／P1 執行與验收清單 |
| `data/regions.json` | 區域總覽資料（Wave 1 七城骨架） |

## 本機預覽

請不要直接雙擊 `index.html`（瀏覽器會擋 `fetch` 載入題庫）。在專案根目錄執行：

```bash
python -m http.server 8765
```

然後開啟 <http://localhost:8765/>。

## 部署到 GitHub + Vercel

1. 在這個資料夾建立獨立 Git repo（不要用使用者家目錄當 repo）。
2. 把專案推到 GitHub。
3. 到 [Vercel](https://vercel.com) 匯入該 repo：
   - Framework Preset：`Other`
   - Build Command：留空
   - Output Directory：留空（根目錄靜態網站）
4. 部署完成後用 Vercel 網址檢查：名詞手冊篩選與字卡、精讀講義章節與長句練習、題庫跳題與解析、深淺色模式。

## 檔案說明

| 檔案 | 用途 |
|---|---|
| `index.html` | 網站入口（名詞手冊 + 精讀講義 + 成交實務 + 衝刺280 + 會話 + 題庫練習） |
| `data/questions.json` | 結構化題庫（練習一） |
| `data/questions2.json` | 結構化艱難題庫（練習二） |
| `data/questions3.json` | 結構化 LV17＋Level 延伸題庫（練習三，約 319 題） |
| `data/questions3_part2.json` | exam bank 3-2 解析結果（合併用中間檔） |
| `data/notes.json` | 精讀講義與考試長難句 |
| `data/field_practice.json` | 成交實務雙語課文、表單、清單、情境 |
| `data/cram280.json` | 考前衝刺 280 關鍵聯想（中英雙語） |
| `data/regions.json` | 南加區域速查（Field Ops；Wave 1 七城骨架） |
| `docs/ARCHITECTURE.md` | Field Ops Hub 適配架構規格 |
| `docs/region-research-playbook.md` | 區域四宮格調查手冊 |
| `docs/P0_P1_PLAN.md` | P0／P1 執行計畫 |
| `new function.md` | 成交實務手冊 Markdown（由 build 腳本產生） |
| `考前衝刺_280關鍵知識點.md` | 衝刺清單 Markdown 版 |
| `plus.txt` | 精讀講義原文（含 OCR 雜訊，勿直接貼進網站） |
| `exam bank.txt` | 原始題庫文字，方便對答案 |
| `exam bank 2.txt` | 艱難考題原文（含中文題幹） |
| `exam bank 3.txt` | LV17 評量原文（英文題 + 雙語深度解析） |
| `exam bank 3-2.txt` | Level 延伸題庫原文（接在題庫三後面） |
| `exam bank 3.formatted.txt` | 練習三中英對照整理版（與 JSON 同步） |
| `dre_100.html` | 原始名詞手冊單檔備份 |
| `scripts/parse_exam_bank.py` | 將 `exam bank.txt` 重新轉成 JSON |
| `scripts/parse_exam_bank2.py` | 將 `exam bank 2.txt` 重新轉成 JSON |
| `scripts/parse_exam_bank3.py` | 將 `exam bank 3.txt` 合併雙語後轉成 JSON |
| `scripts/parse_exam_bank3_2.py` | 將 `exam bank 3-2.txt` 轉成 `questions3_part2.json` |
| `scripts/merge_questions3_part2.py` | 把延伸題接到 `questions3.json` 後面 |
| `scripts/enrich_questions3.py` | 強化題庫三前 100 題陷阱解析 |
| `scripts/parse_plus_notes.py` | 將 `plus.txt` 清雜訊後轉成 `data/notes.json` |
| `scripts/build_field_practice.py` | 產生雙語成交實務 `data/field_practice.json` 與 `new function.md` |
| `scripts/field_form_guides.py` | 24 張表單 A+B 導覽／虛構成交範例，以及額外情境 C 手冊 |

若之後更新了原始題庫或講義文字，可執行：

```bash
python scripts/parse_exam_bank.py
python scripts/parse_exam_bank2.py
python scripts/parse_exam_bank3.py
python scripts/enrich_questions3.py
python scripts/parse_exam_bank3_2.py
python scripts/merge_questions3_part2.py
python scripts/parse_plus_notes.py
python scripts/build_field_practice.py
```
