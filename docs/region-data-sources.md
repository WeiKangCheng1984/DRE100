# Wave 1 區域資料來源盤點（禁止無來源寫入）

盤點日：`2026-10-15`。凡寫入 `data/regions.json` 的數字／行政事實皆需下列來源之一；無法核對者保留空白或標明「未核對」。

## 共同方法

| 類型 | 來源 | 用法 |
|---|---|---|
| 成交中位價 | Redfin Housing Market / Living-in（MLS＋公部門紀錄彙整） | 標明「近 3 個月中位」與截至月 |
| 人口／亞裔比例 | U.S. Census Bureau QuickFacts | 寫「Asian alone %」，**不**自行等同「台／陸籍」 |
| 學區 | 市政府 FAQ／學區官網／CDE | 寫學區全名；邊界以官方為準 |
| 行政地位 | Census / 市府官網 | City vs CDP（未建制） |

**刻意不寫入（避免瞎掰）：** 無來源的治安分數、保證學區排名、未查稅單的 Mello-Roos 金額、虛構通勤分鐘數、未核對的「台客比例」。

## 城別來源摘要

### 鑽石吧 Diamond Bar
- 學區雙軌：City of Diamond Bar FAQ — WVUSD / PUSD，Grand Ave 大致分界  
  https://www.diamondbarca.gov/FAQ.aspx?QID=318
- 價格：Redfin housing-market 全類型中位 $1,095,478（3 months ending Sep 2026）；Living-in SFH $1,234,028 / Condo $534,945 / TH $700,008  
  https://www.redfin.com/city/4957/CA/Diamond-Bar/housing-market  
  https://www.redfin.com/living-in/CA/Diamond-Bar/6/4957
- 亞裔：Census QuickFacts Asian alone 62.7%  
  https://www.census.gov/quickfacts/diamondbarcitycalifornia
- 野火風險敘事：Redfin First Street Fire Factor（93% 房產有某種野火風險）— 同上 housing-market 頁

### 沃爾納特 Walnut
- 學區：Walnut Valley Unified（學區目錄含 Walnut／Diamond Bar 校址）https://www.wvusd.org/
- 價格：Redfin 全類型 $1,284,388（至 Sep 2026）；SFH $1,299,482 / Condo $844,913 / TH $952,000  
  https://www.redfin.com/city/20628/CA/Walnut/housing-market  
  https://www.redfin.com/living-in/CA/Walnut/6/20628
- 亞裔：Census QuickFacts 69.4%

### 羅蘭崗 Rowland Heights
- 地位：Census CDP（未建制社區），ZIP 91748；學區 Rowland Unified（CDE／學區官網）  
  https://www.rowlandschools.org/
- 價格：Redfin 全類型 $937,554（至 Sep 2026）；SFH $938,626 / Condo $457,953 / TH $840,000  
  https://www.redfin.com/city/25415/CA/Rowland-Heights/housing-market  
  https://www.redfin.com/living-in/CA/Rowland-Heights/6/25415
- 亞裔：Census QuickFacts 61.3%
- 華人商圈敘事：Redfin Living-in 原文稱 “center of Chinese cultural and commercial activity”

### 哈仙達崗 Hacienda Heights
- 地位：Census CDP；學區 Hacienda La Puente Unified  
  https://www.hlpschools.org/district/about-hlpusd
- 價格：Redfin ZIP 91745 全類型中位 $970,500（3 months ending Aug 2026）  
  https://www.redfin.com/zipcode/91745/housing-market  
  （未取得與他城同頁口徑的 Condo 分拆 → JSON 標明未分拆）
- 亞裔：Census QuickFacts 42.4%；Hispanic/Latino 43.7%

### 奇諾崗 Chino Hills
- 地位：San Bernardino County 市；1991-12-01 建市（市府 Demographics／History）  
  https://www.chinohills.org/94/Demographics
- 學區：Chino Valley Unified（市府 Schools 頁連至學區）  
  https://www.chinohills.org/434/Schools
- 價格：Redfin 全類型約 $985K（housing-market至 Aug 2026）；Living-in SFH $1,064,576 / Condo $537,945 / TH $595,007  
  https://www.redfin.com/city/3447/CA/Chino-Hills/housing-market  
  https://www.redfin.com/living-in/CA/Chino-Hills/6/3447
- 亞裔：Census QuickFacts 41.0%

### 安大略 Ontario
- 學區：市府 Education 頁列 OMSD、Mountain View、Chaffey Joint Union HSD、CVUSD、Cucamonga 等（**地址必須逐案查**）  
  https://www.ontarioca.gov/residents/residential-services/education
- 價格：Redfin 全類型 $657,687（至 Sep 2026）；SFH $723,268 / Condo $549,943 / TH $563,997  
  https://www.redfin.com/city/13934/CA/Ontario/housing-market  
  https://www.redfin.com/living-in/CA/Ontario/6/13934
- 亞裔：Census QuickFacts 9.8%；Hispanic/Latino 68.6%
- 經濟：Census 2022 transportation & warehousing receipts 極高（物流倉儲就業敘事依據）

### 波莫納 Pomona
- 學區：Pomona Unified（服務 Pomona 與 Diamond Bar 部分）https://proudtobe.pusd.org/
- 價格：Redfin Living-in 全類型 $659,686；SFH $689,725 / Condo $417,957 / TH $599,997  
  https://www.redfin.com/living-in/CA/Pomona/6/15047  
  （housing-market 近 3 月約 $664K／至 Aug 2026，口径接近）
- 亞裔：Census QuickFacts 10.7%；Hispanic/Latino 71.8%
- 地標：Cal Poly Pomona、Fairplex（Redfin Living-in／市府公開資訊）
