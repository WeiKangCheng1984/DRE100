# 加州 DRE 不動產複習網

靜態網站，包含四大模組：

- **名詞手冊**：100 組易混淆名詞（條列檢視、字卡翻閱、領域篩選、收藏／已掌握）
- **精讀講義**：從 `plus.txt` 整理的章節知識點（中英對照、考點、文法拆解）。內含子功能 **長句練習**：76 句考試長難句，先看英文再揭曉解析。
- **題庫練習**：約 225 題選擇題，可上一題／下一題、跳到指定題號，作答後立刻顯示對錯與解析。進度存在瀏覽器 `localStorage`。
- **題庫練習二**：約 210 題艱難考題（`exam bank 2.txt`），同樣可順序刷題、跳題與看解析；進度與第一套題庫分開保存。

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
| `index.html` | 網站入口（名詞手冊 + 精讀講義 + 題庫練習 + 題庫練習二） |
| `data/questions.json` | 結構化題庫（練習一） |
| `data/questions2.json` | 結構化艱難題庫（練習二） |
| `data/notes.json` | 精讀講義與考試長難句 |
| `plus.txt` | 精讀講義原文（含 OCR 雜訊，勿直接貼進網站） |
| `exam bank.txt` | 原始題庫文字，方便對答案 |
| `exam bank 2.txt` | 艱難考題原文（含中文題幹） |
| `dre_100.html` | 原始名詞手冊單檔備份 |
| `scripts/parse_exam_bank.py` | 將 `exam bank.txt` 重新轉成 JSON |
| `scripts/parse_exam_bank2.py` | 將 `exam bank 2.txt` 重新轉成 JSON |
| `scripts/parse_plus_notes.py` | 將 `plus.txt` 清雜訊後轉成 `data/notes.json` |

若之後更新了原始題庫或講義文字，可執行：

```bash
python scripts/parse_exam_bank.py
python scripts/parse_exam_bank2.py
python scripts/parse_plus_notes.py
```
