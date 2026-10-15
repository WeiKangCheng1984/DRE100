#!/usr/bin/env python3
"""Rewrite region copy in broker voice and add qualitative feel axes."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGIONS = ROOT / "data" / "regions.json"

FEEL = {
    "diamond-bar": {
        "weekend": {"tag": "山城安靜", "line": "平常晚上很靜，週末要熱鬧多半開車下山。"},
        "school": {"tag": "雙學區對址", "line": "Grand Ave 兩邊可能是 Walnut Valley 或 Pomona Unified，地址沒對完別報校。"},
        "street": {"tag": "坡地巷弄", "line": "坡地屋多，帶看排水、停車跟保險。"},
        "chineseLife": {"tag": "商圈要開車", "line": "華語家庭不少，買菜補習很多人往羅蘭崗一帶跑。"},
    },
    "walnut": {
        "weekend": {"tag": "山城安靜", "line": "自住節奏，不是逛街城。"},
        "school": {"tag": "多數單一學區", "line": "多數討論指向 Walnut Valley，交界還是要對址。"},
        "street": {"tag": "坡地巷弄", "line": "丘陵地段常見，屋況跟排水要現場看。"},
        "chineseLife": {"tag": "商圈要開車", "line": "生活圈在東聖蓋博，超市密度不如羅蘭崗。"},
    },
    "rowland-heights": {
        "weekend": {"tag": "商圈滿位", "line": "週末 Colima、超市、餐廳是滿的，這就是客人要的機能。"},
        "school": {"tag": "多數單一學區", "line": "主軸 Rowland Unified，還是用地址確認。"},
        "street": {"tag": "主幹道混住商", "line": "幹道熱鬧，巷內才比較像住家。"},
        "chineseLife": {"tag": "超市補習密集", "line": "華語圈常把這裡當東邊買菜、吃飯的一站。"},
    },
    "hacienda-heights": {
        "weekend": {"tag": "住商都有", "line": "比山市方便一點，比羅蘭崗安靜一點，看你停在哪一條。"},
        "school": {"tag": "多數單一學區", "line": "走 Hacienda La Puente Unified。"},
        "street": {"tag": "主幹道混住商", "line": "別跟羅蘭崗混成同一個崗，學區跟客群都不一樣。"},
        "chineseLife": {"tag": "華語圈在、不是單一客群", "line": "亞裔跟西語裔都高，別預設進來的都是華語客人。"},
    },
    "chino-hills": {
        "weekend": {"tag": "規劃社區內轉", "line": "公園、商場在規劃裡轉，比較不像聖蓋博逛街。"},
        "school": {"tag": "多數單一學區", "line": "Chino Valley Unified，已經跨出 LA 縣。"},
        "street": {"tag": "規劃社區", "line": "1991 建市，HOA、特別稅要逐案查。"},
        "chineseLife": {"tag": "要開車回東 SGV", "line": "華語機能有，密度還是不如羅蘭崗。"},
    },
    "ontario": {
        "weekend": {"tag": "機場物流節奏", "line": "不是週末逛街城，比較是機場、倉儲、上班的節奏。"},
        "school": {"tag": "學區拼圖", "line": "可能跨好幾個學區，地址沒對完我不會報校名。"},
        "street": {"tag": "舊城分區差大", "line": "各區差很多，一定要分區帶看。"},
        "chineseLife": {"tag": "華語圈討論少", "line": "別拿東聖蓋博的生活圈期待套過來。"},
    },
    "pomona": {
        "weekend": {"tag": "舊城分區差大", "line": "Downtown、Fairplex 附近跟各郵遞區號感覺不一樣。"},
        "school": {"tag": "多數單一學區", "line": "Pomona Unified；鑽石吧有些地址也是這套，可以當對照。"},
        "street": {"tag": "舊城分區差大", "line": "91766、67、68 要分開看，不要整城一句話帶過。"},
        "chineseLife": {"tag": "華語圈討論少", "line": "別跟鑽石吧、Walnut 的山市標籤混在一起。"},
    },
    "westchester": {
        "weekend": {"tag": "機場帶節奏", "line": "靠近 LAX，有派駐、有自住，週末不是聖蓋博那種商圈。"},
        "school": {"tag": "LAUSD 對址", "line": "還在洛杉磯市，用官方工具查，別套 Culver City。"},
        "street": {"tag": "戰後郊區混新案", "line": "90045 比口語「西徹斯特」大，含機場周邊。"},
        "chineseLife": {"tag": "西區要另找", "line": "華語超市補習不是這裡的主軸，客人多半為了機場跟西區。"},
    },
    "playa-vista": {
        "weekend": {"tag": "規劃社區內轉", "line": "比較新、比較規劃，週末在社區裡轉的人多。"},
        "school": {"tag": "LAUSD 對址", "line": "不是 Culver City 學區。"},
        "street": {"tag": "規劃社區", "line": "HOA 幾乎必讀，Condo 比重高。"},
        "chineseLife": {"tag": "西區要另找", "line": "常跟 Culver 一起被問，但這是洛杉磯市的規劃村。"},
    },
    "culver-city": {
        "weekend": {"tag": "城中可走", "line": "Downtown、Washington 一帶可以吃飯逛街。"},
        "school": {"tag": "多數單一學區", "line": "Culver City Unified，這是跟隔壁最大的差別。"},
        "street": {"tag": "舊城混媒體園區", "line": "舊城、Fox Hills、片廠附近屋況差很大。"},
        "chineseLife": {"tag": "西區要另找", "line": "從聖蓋博過來，這是西區總價跟就業，不是 210 名校故事。"},
    },
    "san-marino": {
        "weekend": {"tag": "豪宅街區", "line": "亨廷頓、Lacy Park，節奏慢、盤面小。"},
        "school": {"tag": "多數單一學區", "line": "只報 San Marino Unified，不報排名。"},
        "street": {"tag": "豪宅街區", "line": "成交筆數少，中位容易被單筆拉動。"},
        "chineseLife": {"tag": "衝學區不是衝逛街", "line": "華語家庭在，客人衝的是學區跟總價，不是 Valley Blvd。"},
    },
    "south-pasadena": {
        "weekend": {"tag": "老街可走", "line": "Mission、Fair Oaks 可以走路吃飯，靠 110。"},
        "school": {"tag": "多數單一學區", "line": "South Pasadena Unified，不是帕薩迪納那套。"},
        "street": {"tag": "老屋尺度", "line": "歷史街區改建，別隨便承諾能加蓋。"},
        "chineseLife": {"tag": "商圈要開車", "line": "生活尺度像小城，華語密集商圈多半還是往東。"},
    },
    "arcadia": {
        "weekend": {"tag": "住商都有", "line": "賽馬場、植物園、Baldwin 一帶，盤面比聖馬大。"},
        "school": {"tag": "多數單一學區", "line": "主軸 Arcadia Unified，交界仍要對址。"},
        "street": {"tag": "平地混山麓", "line": "91006、91007 跟山邊平地差很多。"},
        "chineseLife": {"tag": "超市補習密集", "line": "北聖蓋博華語客人很熟這座城。"},
    },
    "temple-city": {
        "weekend": {"tag": "住商都有", "line": "山茶花節、Las Tunas 一帶，比亞凱、聖馬好接近。"},
        "school": {"tag": "多數單一學區", "line": "Temple City Unified；交界別誤以為亞凱迪亞。"},
        "street": {"tag": "戰後郊區屋", "line": "屋況差大，門牌所在市要看清。"},
        "chineseLife": {"tag": "華語自住圈", "line": "常跟羅斯密一起被問，學區跟市政不是同一套。"},
    },
    "rosemead": {
        "weekend": {"tag": "商圈滿位", "line": "Valley、Garvey 週末吃飯買菜很滿。"},
        "school": {"tag": "學區拼圖", "line": "小學可能是 Garvey 或 Rosemead，高中常走 El Monte Union，一定要對址。"},
        "street": {"tag": "主幹道混住商", "line": "幹道是商業，巷內才是住家。"},
        "chineseLife": {"tag": "超市補習密集", "line": "機能強，但別用聖馬那套客群來套。"},
    },
}

VOICE = {
    "diamond-bar": {
        "chineseBelt": "60、57 交會的山城。華語家庭不少，可是普查寫的亞裔不是台籍比例。日常買菜、補習，很多人還是往羅蘭崗那一帶跑。",
        "schoolBand": "同一座城可能是 Walnut Valley 或 Pomona Unified。市府說 Grand Ave 大致分界，北側偏 Pomona、南側偏 Walnut Valley——我帶看一定先對地址。",
        "jobs": "住這裡的人，工作多半在教育醫療、專業服務跟零售，多數還是開車去區域上班，不是鑽石吧自己有大園區。",
        "amenities": "公園、高爾夫、Golden Springs 那條是日常。週末要熱鬧，很多人會下山。",
        "safetyNote": "治安分數我沒核過就不講。保險那邊常看到野火風險敘事，報價要逐案問。",
        "buyerFit": "在意學區、也接受山市節奏的自住家庭。學區沒對完，我不會先談價。",
        "propertyCaveats": "坡地屋多，排水、擋土、保險（含野火）現場跟保單一起看。",
        "taxCaveats": "地稅看縣稅單，特別稅別假設全市一樣。",
        "schoolReality": "可能是 WVUSD 或 PUSD，成交條件寫明用地址查官方。",
        "pitchLine": "鑽石吧是 60、57 交會的山城。客人常問學區，可是同一座城可能是 Walnut Valley 或 Pomona Unified，地址沒對完我不會報校名。",
        "compareLine": "若你熟 Walnut：總價帶接近，大約一百二十萬級的獨立屋。差在鑽石吧學區可能是兩套，Walnut 多數討論指向 Walnut Valley。",
        "trendLine": "人口五萬出頭，家戶所得中位大概十萬八，自住比例高。這是普查五年估計，拿來看結構，不是今年漲跌。",
        "explainZh": "我會先講山城，再講雙學區。亞裔比例高可以提，別說成台客比例。",
        "sfhRange": "獨立屋中位大約 123 萬（Redfin，近幾個月）。",
        "condoRange": "Condo 大約 53 萬、聯排大約 70 萬。全類型會低一點，因為混進較小單位，大約 110 萬（至 2026-09）。",
        "ageProfile": "屋齡差很大，以 listing 跟縣府建造年為準。",
        "hoaMello": "有沒有 HOA、特別稅，看 title 跟稅單，我這張卡不寫沒核過的金額。",
    },
    "walnut": {
        "chineseBelt": "東聖蓋博山市裡，很多人拿它當標尺。華語家庭比例高，可是普查亞裔不是台籍。超市密度不如羅蘭崗，生活偏自住。",
        "schoolBand": "多數討論指向 Walnut Valley Unified。學區總部在 Walnut，交界仍可能跨 Rowland Unified，要對址。",
        "jobs": "居民工作前三是教育醫療、專業服務、零售，多數通勤出去。",
        "amenities": "Valley Blvd、Amar Rd 一帶有吃飯的地方，還有 Suzanne Park、步道。不是逛街城。",
        "safetyNote": "治安分數沒核過就不講。保險跟現場帶看為準。",
        "buyerFit": "想鎖定 Walnut Valley、也接受山市總價的自住家庭。",
        "propertyCaveats": "丘陵地段常見，排水跟屋況要現場看。",
        "taxCaveats": "以 LA 縣稅單為準，特別稅逐案。",
        "schoolReality": "多數指向 WVUSD，不是全市保證。用地址查官方。",
        "pitchLine": "Walnut 是東聖蓋博山市裡常被拿來當標尺的一座。獨立屋大約 130 萬。我先問是不是 Walnut Valley，再拿鑽石吧、羅蘭崗比預算。",
        "compareLine": "同廊道裡所得跟亞裔比例都偏高。要比機能往羅蘭崗，要比學區單純度先確認 WVUSD，鑽石吧則多一道雙學區功課。",
        "trendLine": "人口大約兩萬八，家戶所得中位大約十三萬。自住、教育醫療通勤族偏多。普查五年估計，不是今年行情。",
        "explainZh": "先問學區是不是 Walnut Valley，再比鑽石吧預算。別把亞裔比例講成台籍。",
        "sfhRange": "獨立屋中位大約 130 萬（Redfin）。",
        "condoRange": "Condo 大約 84 萬、聯排大約 95 萬。全類型大約 128 萬（至 2026-09）。",
        "ageProfile": "山市、丘陵，屋齡以建造年為準。",
        "hoaMello": "逐案看 CC&Rs 跟稅單。",
    },
    "rowland-heights": {
        "chineseBelt": "這不是市，是縣裡的未建制社區。華語圈很熟這裡的超市、餐廳，週末 Colima 一帶常常滿的。市政服務走縣府，不是自己有市府。",
        "schoolBand": "主軸 Rowland Unified，還是用地址確認。",
        "jobs": "住這裡的人，工作前三是教育醫療、餐旅、零售。商圈熱鬧，不代表人人在當地上班。",
        "amenities": "華語超市、餐廳密。幹道熱鬧，巷內才比較像住家。",
        "safetyNote": "治安分數沒核過就不講。保險頁常看到野火風險敘事，逐案問。",
        "buyerFit": "要華語生活圈機能、總價低於 Walnut 一帶的自住或首購比較。",
        "propertyCaveats": "幹道跟巷內差很多，帶看分清。",
        "taxCaveats": "未建制社區，稅跟特別區以稅單為準。",
        "schoolReality": "主軸 Rowland Unified，交界仍要對址。",
        "pitchLine": "羅蘭崗不是市，是縣裡的社區。華語圈很熟這裡的超市餐廳，獨立屋大約 94 萬。學區看 Rowland Unified，地址還是要對。",
        "compareLine": "比 Walnut、鑽石吧便宜一截，機能卻更滿。差在它不是市，市政跟服務跟建制市不一樣。",
        "trendLine": "人口四萬六左右，家戶所得中位大約八萬六。餐旅比重比旁邊山市高一點，跟商圈性格合。普查五年估計。",
        "explainZh": "開場先講：這不是市。商圈可以誇，市政別講得跟 Culver、Walnut 一樣。",
        "sfhRange": "獨立屋中位大約 94 萬（Redfin）。",
        "condoRange": "Condo 大約 46 萬、聯排大約 84 萬。全類型大約 94 萬（至 2026-09）。",
        "ageProfile": "住商混雜，屋齡以建造年為準。",
        "hoaMello": "Condo 較常見 HOA；獨立屋逐案。",
    },
    "hacienda-heights": {
        "chineseBelt": "一樣是未建制社區，可是別跟羅蘭崗混成同一個崗。亞裔跟西語裔都高，進來的客人不是單一客群。",
        "schoolBand": "Hacienda La Puente Unified。",
        "jobs": "居民工作前三是教育醫療、專業服務、零售，多數通勤。",
        "amenities": "比山市方便一點，比羅蘭崗安靜一點，看你停在哪一條。",
        "safetyNote": "治安分數沒核過就不講。",
        "buyerFit": "學區走 HLPUSD、想跟羅蘭崗比機能可是不要同一套標籤的自住比較。",
        "propertyCaveats": "幹道跟住宅巷差很多。",
        "taxCaveats": "未建制，稅單為準。",
        "schoolReality": "HLPUSD，不要講成 Rowland Unified。",
        "pitchLine": "哈仙達崗也是未建制社區，學區是 Hacienda La Puente。全類型大約 97 萬，獨立屋我還沒跟他城對上同一口徑，所以對照條先空著，不是沒有市場。",
        "compareLine": "別跟羅蘭崗混。客群更混、學區不同。獨立屋中位我沒對上同一頁，比價先用文字講全類型，不要硬並排。",
        "trendLine": "人口五萬四左右，亞裔、西語裔都四成出頭。家戶所得中位大約十一萬。普查五年估計。",
        "explainZh": "獨立屋格子空著是因為口徑還沒對齊，我會改口講全類型。客群別預設都是華語。",
        "sfhRange": "獨立屋單獨中位我還沒跟他城對上同一口徑，對照條先空著。",
        "condoRange": "ZIP 91745 全類型大約 97 萬（至 2026-08）。這是全類型，不是獨立屋軸。",
        "ageProfile": "住商都有，屋齡以建造年為準。",
        "hoaMello": "逐案看稅單、CC&Rs。",
    },
    "chino-hills": {
        "chineseBelt": "已經是聖伯納丁諾縣的市，1991 年建市。規劃社區味道濃，華語家庭有，生活圈密度還是不如羅蘭崗。",
        "schoolBand": "Chino Valley Unified。",
        "jobs": "居民前三是教育醫療、專業服務、製造，多數還是區域通勤。",
        "amenities": "公園、商場在規劃裡轉。通勤軸換成 71、60、91。",
        "safetyNote": "治安分數沒核過就不講。",
        "buyerFit": "接受跨出 LA 縣、要規劃社區跟 CVUSD 的自住家庭。",
        "propertyCaveats": "規劃村常見 HOA，逐案讀。",
        "taxCaveats": "聖伯納丁諾縣稅單；特別稅別略過。",
        "schoolReality": "CVUSD，不要講成 Walnut Valley。",
        "pitchLine": "奇諾崗是聖伯納丁諾縣的市，不是東聖蓋博延伸。學區 Chino Valley Unified，獨立屋大約 106 萬。規劃整齊，HOA 跟特別稅要逐案。",
        "compareLine": "價位接近東聖蓋博中段，可是縣、學區、通勤軸都換了。拿鑽石吧來比總價可以，拿學區來套不行。",
        "trendLine": "人口將近八萬，家戶所得中位大約十三萬。規劃社區、自住偏多。普查五年估計。",
        "explainZh": "先講跨縣。規劃社區可以誇，別講成沒有 HOA、沒有特別稅。",
        "sfhRange": "獨立屋中位大約 106 萬（Redfin）。",
        "condoRange": "Condo 大約 54 萬、聯排大約 60 萬。全類型大約 98 到 99 萬級。",
        "ageProfile": "1990 年代後規劃為主，各村不同。",
        "hoaMello": "規劃村常見 HOA；特別稅看稅單。",
    },
    "ontario": {
        "chineseBelt": "機場、物流城，不是東聖蓋博延伸社區。華語圈討論少，別拿山市那套生活圈期待套過來。",
        "schoolBand": "市府列出 Ontario-Montclair、Mountain View、Chaffey 高中，還可能碰到 Chino Valley、Cucamonga。地址沒對完，我不會報校名。",
        "jobs": "本地確實有機場、倉儲的故事。住在這裡的人，工作前三是教育醫療、零售、運輸倉儲——居民就業跟本地崗位不是同一件事。",
        "amenities": "機能看區。別用東聖蓋博週末商圈來想像。",
        "safetyNote": "治安分數沒核過就不講。分區差異大，帶看為準。",
        "buyerFit": "預算明顯低於東聖蓋博山市、能接受多學區跟物流城特質的買家。",
        "propertyCaveats": "各區差很多，一定要分區帶看。",
        "taxCaveats": "聖伯納丁諾縣稅單為準。",
        "schoolReality": "拼圖學區，成交條件寫明對址。",
        "pitchLine": "安大略是機場、物流城，獨立屋大約 72 萬。學區可能跨好幾套，地址沒對完我不會報校名。別把它當成東聖蓋博比較便宜的延伸。",
        "compareLine": "鑽石吧獨立屋大約 123 萬，安大大約 72 萬。總價可以比，客群、學區、生活圈不是同一件事。",
        "trendLine": "人口十八萬級，西語裔約七成，亞裔約一成。家戶所得中位大約九萬。普查五年估計。",
        "explainZh": "先講物流城，再講學區拼圖。華語客人若用山市標準來問，我會直接拆開。",
        "sfhRange": "獨立屋中位大約 72 萬（Redfin）。",
        "condoRange": "Condo 大約 55 萬、聯排大約 56 萬。全類型大約 66 萬（至 2026-09）。",
        "ageProfile": "舊城跟各區差很大。",
        "hoaMello": "逐案查稅單、CC&Rs。",
    },
    "pomona": {
        "chineseBelt": "LA 縣的市，可是別套鑽石吧、Walnut 的山市標籤。舊城跟各郵遞區號差很大。",
        "schoolBand": "Pomona Unified。官網寫服務 Pomona 跟鑽石吧部分社區，所以可以拿來當鑽石吧學區對照。",
        "jobs": "附近有 Cal Poly Pomona、Fairplex。居民工作前三是教育醫療、零售、專業服務。",
        "amenities": "Downtown、Fairplex 一帶。華語生活圈密度低於東聖蓋博。",
        "safetyNote": "治安分數沒核過就不講。鄰里差很大。",
        "buyerFit": "總價帶偏低的自住或首購比較，要接受社區差異跟 PUSD。",
        "propertyCaveats": "91766、67、68 特質不同，分開帶看。",
        "taxCaveats": "LA 縣稅單為準。",
        "schoolReality": "PUSD；鑽石吧部分地址也可能是 PUSD。",
        "pitchLine": "波莫納是 LA 縣市，獨立屋大約 66 到 69 萬。學區 Pomona Unified。別跟鑽石吧、Walnut 的山市混為一談。",
        "compareLine": "價位接近安大略，可是縣不一樣、學區是 PUSD。鑽石吧有些地址也是 PUSD，客人糾結學區時可以拿來對照。",
        "trendLine": "人口十五萬級，西語裔約七成，亞裔約一成。家戶所得中位大約八萬。普查五年估計。",
        "explainZh": "先拆山市標籤，再講 PUSD 跟分區。總價可以跟安大略放一起比。",
        "sfhRange": "獨立屋中位大約 69 萬（Redfin）。",
        "condoRange": "Condo 大約 42 萬、聯排大約 60 萬。全類型大約 66 萬。",
        "ageProfile": "舊城跟各鄰里差很大。",
        "hoaMello": "逐案查稅單、CC&Rs。",
    },
    "westchester": {
        "chineseBelt": "洛杉磯市裡面的社區，不是獨立市。地圖跟普查用 90045 郵區，範圍比口語「西徹斯特」大，含機場周邊。",
        "schoolBand": "LAUSD，用官方住址工具查。網頁上常見的校名只當線索，不當保證。",
        "jobs": "靠近機場跟 LMU。住這裡的人，工作前三是專業服務、教育醫療、資訊，不是「人人在機場上班」。",
        "amenities": "機場、西區、LMU。常跟 Playa Vista、Culver 一起被問。",
        "safetyNote": "治安分數沒核過就不講。鄰機場，噪音、航道現場確認。",
        "buyerFit": "要近機場、西區，能接受還在洛杉磯市、學區走 LAUSD 的自住或派駐。",
        "propertyCaveats": "郵區含住宅跟機場相關用地，帶看分清住商、航道。",
        "taxCaveats": "縣稅單；特別稅逐案。",
        "schoolReality": "LAUSD，不要套 Culver City Unified。",
        "pitchLine": "西徹斯特不是市，是洛杉磯市社區。客人說 90045，普查也用這個郵區，範圍含機場周邊。全類型大約 168 萬級，獨立屋我還沒跟他城對上同一口徑，所以那一格先空著。",
        "compareLine": "Culver 是獨立市、自己的學區。這裡還在洛杉磯市、LAUSD。Playa Vista 更新、更規劃，但是同一個市的框架。",
        "trendLine": "郵區人口四萬二左右，家戶所得中位大約十三萬五。這是郵區不是口語社區，百分比別講太滿。",
        "explainZh": "先講不是市。地圖看左下角小圖。別把機場地標說成人人在機場上班。",
        "sfhRange": "獨立屋還沒跟他城對上同一口徑，對照條先空著。",
        "condoRange": "社區全類型大約 168 萬（至 2026-06）。這是社區、全類型，不是獨立屋軸。",
        "ageProfile": "戰後郊區屋跟更新案混在一起。",
        "hoaMello": "部分規劃村有 HOA；機場噪音、航道要現場看。",
    },
    "playa-vista": {
        "chineseBelt": "洛杉磯市裡比較新的規劃社區，不是市。普查用很小的 90094，人口基數小，百分比會跳。",
        "schoolBand": "LAUSD。附近常聽到 Playa Vista Elementary，仍不是整區保證。",
        "jobs": "西區通勤敘事常見。基數小，數字只作方向：專業服務、教育醫療、資訊。",
        "amenities": "常跟 Culver、Westchester 放在同一張西區比較表。",
        "safetyNote": "治安分數沒核過就不講。規劃社區夜間節奏跟市區不同。",
        "buyerFit": "要較新規劃、接受 HOA 跟 Condo 比重，並拿來跟 Culver 比總價的客人。",
        "propertyCaveats": "郵區很小，listing 可能跨相鄰 ZIP；HOA 跟出租規則先讀。",
        "taxCaveats": "縣稅單；特別稅逐案。",
        "schoolReality": "LAUSD，不是 Culver City Unified。",
        "pitchLine": "Playa Vista 是洛杉磯市的規劃社區，不是市。常跟 Culver 一起比，可是市府跟學區是兩套。全類型大約 128 萬級，獨立屋格子空著是因為產品偏 Condo，我沒辦法跟山市獨立屋並排。",
        "compareLine": "Culver 有自己的市府跟學區。這裡更新、HOA 更密，但仍是洛杉磯市。別把兩格人口加總成一座西區市。",
        "trendLine": "郵區人口只有一萬出頭，百分比不穩。拿來看方向就好。",
        "explainZh": "小郵區、數字別講太滿。重點是規劃社區加洛杉磯市，不是再造一個市名。",
        "sfhRange": "獨立屋沒有跟他城同口徑的分拆，對照條先空著。",
        "condoRange": "社區全類型大約 128 萬（資料較舊，至 2026-03）。Condo 比重高。",
        "ageProfile": "2000 年代後規劃為主。",
        "hoaMello": "HOA 幾乎必讀，費用跟租賃限制逐案。",
    },
    "culver-city": {
        "chineseBelt": "西區獨立市，不是洛杉磯市。90230 只是客人常講的郵遞區號之一，講全市數字不要只用這個郵區。",
        "schoolBand": "Culver City Unified，地址還是要向學區確認。",
        "jobs": "電影、電視製作很有名，Sony Pictures 是公開地標。住這裡的人，工作前三是專業服務、教育醫療、資訊，不是人人在片場。",
        "amenities": "公園不少，Downtown、Washington 可以吃飯逛街。",
        "safetyNote": "治安分數沒核過就不講。舊城跟 Fox Hills 差很多。",
        "buyerFit": "要西區獨立市、Culver City 學區，也接受獨立屋總價明顯高於東聖蓋博中段的客人。",
        "propertyCaveats": "90230、90232 要分區看，別用一個郵遞區號概括。",
        "taxCaveats": "縣稅單；特別稅逐案。",
        "schoolReality": "主軸 CCUSD，仍用地址確認。",
        "pitchLine": "Culver City 是西區獨立市，不是洛杉磯市。學區 Culver City Unified。獨立屋大約 180 萬，Condo 大約 60 萬。跟西徹斯特最大的差別，就是這裡有自己的市府跟學區。",
        "compareLine": "從聖蓋博過來：這是西區就業跟總價，不是 210 名校故事。隔壁西徹斯特還在洛杉磯市。",
        "trendLine": "人口大約四萬，家戶所得中位大約十二萬。學士比例高。普查五年估計。",
        "explainZh": "先報獨立市跟學區，再講獨立屋跟 Condo 價差。隔壁兩塊是郵區，不要加總。",
        "sfhRange": "獨立屋中位大約 180 萬（Redfin）。",
        "condoRange": "Condo 大約 60 萬、聯排大約 120 萬。全類型大約 140 萬。",
        "ageProfile": "舊城、Fox Hills、媒體園區周邊差很大。",
        "hoaMello": "Condo、部分規劃區有 HOA。",
    },
    "san-marino": {
        "chineseBelt": "北聖蓋博很小、很貴的獨立市。華語家庭在，客人衝的是學區跟總價，不是逛街。盤面小，百分比會跳。",
        "schoolBand": "San Marino Unified。只報學區名，不報排名。",
        "jobs": "自住小城，就業多半通勤。居民前三是教育醫療、專業服務、金融地產。",
        "amenities": "亨廷頓圖書館、Lacy Park。開場用地標，不包裝成保證學區分數。",
        "safetyNote": "治安分數沒核過就不講。成交筆數少，別把低筆數講成低風險。",
        "buyerFit": "預算對得上北聖蓋博最高總價帶、鎖定 SMUSD 的自住家庭。",
        "propertyCaveats": "近月成交大約三十筆量級，中位容易被單筆豪宅拉動。",
        "taxCaveats": "縣稅單；特別評估逐案。",
        "schoolReality": "SMUSD，不要用帕薩迪納或亞凱迪亞學區名套過來。",
        "pitchLine": "聖馬利諾是獨立小城，不是帕薩迪納一區。獨立屋大約 345 萬。我先講 San Marino Unified 跟總價，再拿南帕、亞凱迪亞比。",
        "compareLine": "亞凱獨立屋大約 195 萬、南帕大約 184 萬。聖馬更小、更貴、另一套學區。",
        "trendLine": "人口只有一萬二，家戶所得中位二十萬出頭，學士比例很高。小城數字波動大。",
        "explainZh": "這是總價錨點。筆數少，中位敏感。學區只報 SMUSD，排名我沒核過就不講。",
        "sfhRange": "獨立屋中位大約 345 萬（Redfin）。庫存幾乎都是獨立屋，所以跟全類型幾乎同一量級。",
        "condoRange": "Condo 分拆不穩，小城庫存少，逐案看 MLS。",
        "ageProfile": "經典住宅街區跟改建並存，規範問市府。",
        "hoaMello": "多數是獨立屋地稅，HOA 不是全市預設。",
    },
    "south-pasadena": {
        "chineseBelt": "夾在帕薩迪納跟洛杉磯市中間的獨立小城。生活尺度像老街區，華語密集商圈多半還是往東。",
        "schoolBand": "South Pasadena Unified，不是帕薩迪納那套。",
        "jobs": "近市區、靠 110。居民前三是教育醫療、專業服務、金融地產。",
        "amenities": "Mission、Fair Oaks 可以走路吃飯，還有 Garfield Park、Arroyo 綠帶。",
        "safetyNote": "治安分數沒核過就不講。老街區夜間跟主幹道不一樣。",
        "buyerFit": "要老街區尺度、SPUSD、能接受小城庫存的自住比較。",
        "propertyCaveats": "歷史街區改建、停車規範問市府，別承諾能加蓋。",
        "taxCaveats": "縣稅單；特別稅逐案。",
        "schoolReality": "SPUSD，跟帕薩迪納、LAUSD 都不同。",
        "pitchLine": "南帕是獨立市，不是「帕薩迪納南邊某區」。學區 South Pasadena Unified，通勤走 110。獨立屋大約 184 萬。",
        "compareLine": "跟聖馬都是小城，學區不同、總價差一截。跟亞凱比，南帕更靠 110 跟洛杉磯市邊界。",
        "trendLine": "人口兩萬六左右，學士比例高。小城，普查數字當結構看。",
        "explainZh": "三句話：獨立市、110、SPUSD。老屋改建別承諾。",
        "sfhRange": "獨立屋中位大約 184 萬（Redfin）。",
        "condoRange": "Condo 大約 91 萬、聯排大約 137 萬。全類型大約 165 萬。",
        "ageProfile": "老街區、歷史建築常見。",
        "hoaMello": "Condo、少數規劃案有 HOA。",
    },
    "arcadia": {
        "chineseBelt": "北聖蓋博華語客人很熟的一座市。超市、補習、住家都有，盤面比聖馬大。",
        "schoolBand": "主軸 Arcadia Unified，交界仍要對址。",
        "jobs": "自住郊區市。居民前三是教育醫療、專業服務、金融地產。",
        "amenities": "Santa Anita、植物園、Baldwin 一帶商業。",
        "safetyNote": "治安分數沒核過就不講。平地跟山麓差很多。",
        "buyerFit": "鎖定 AUSD、需要比聖馬更大盤面的自住家庭。",
        "propertyCaveats": "91006、91007，山邊跟平地屋況不同。",
        "taxCaveats": "縣稅單；特別稅逐案。",
        "schoolReality": "多數指向 AUSD，不是全市單一保證。",
        "pitchLine": "亞凱迪亞獨立屋大約 195 萬，學區主軸 Arcadia Unified。往上比聖馬、往下比天普市，我把它當北聖蓋博的標尺。",
        "compareLine": "若你熟鑽石吧、Walnut：亞凱是 210 那一套，不是 60 廊道延伸，總價帶也更高。",
        "trendLine": "人口五萬五左右，家戶所得中位大約十一萬。普查五年估計。",
        "explainZh": "先對 Arcadia Unified，再把聖馬（更貴更小）跟天普市（比較好接近）放到同一句。",
        "sfhRange": "獨立屋中位大約 195 萬（Redfin）。",
        "condoRange": "Condo 大約 83 萬、聯排大約 92 萬。全類型大約 174 萬。",
        "ageProfile": "平地跟山麓差很大。",
        "hoaMello": "Condo、部分社區有 HOA。",
    },
    "temple-city": {
        "chineseBelt": "同廊道裡比較好接近的自住市。華語客人常拿來跟亞凱、聖馬比預算，也常跟羅斯密一起問。",
        "schoolBand": "Temple City Unified。交界別誤以為亞凱迪亞。",
        "jobs": "自住加區域通勤。居民前三是教育醫療、金融地產、專業服務。",
        "amenities": "山茶花節、Las Tunas、Rosemead Blvd 一帶吃飯，還有公園。",
        "safetyNote": "治安分數沒核過就不講。交界帶看分清門牌所在市。",
        "buyerFit": "要北聖蓋博自住、預算低於亞凱跟聖馬、學區走 TCUSD 的比較。",
        "propertyCaveats": "跟羅斯密、亞凱迪亞交界，門牌所在市要看清。",
        "taxCaveats": "縣稅單；特別稅逐案。",
        "schoolReality": "主軸 TCUSD，交界可能被誤以為亞凱，必須對址。",
        "pitchLine": "天普市獨立屋大約 119 萬，學區 Temple City Unified。常跟羅斯密一起被問，可是市政跟學區不是同一套。",
        "compareLine": "亞凱大約 195 萬、聖馬大約 345 萬；天普市是同廊道比較好接近的自住市。羅斯密更偏商業帶，學區更複雜。",
        "trendLine": "人口三萬五左右，家戶所得中位大約十萬四。普查五年估計。",
        "explainZh": "先講 TCUSD，再把羅斯密當隔壁對照，不是同一座城。",
        "sfhRange": "獨立屋中位大約 119 萬（Redfin）。",
        "condoRange": "Condo 大約 75 萬、聯排大約 99 萬。全類型大約 117 萬（至 2026-09）。",
        "ageProfile": "戰後郊區屋為主，屋況差大。",
        "hoaMello": "Condo 較常見 HOA。",
    },
    "rosemead": {
        "chineseBelt": "Valley、Garvey 商業帶很滿。華語機能強，可是別用聖馬那套客群來套。",
        "schoolBand": "小學可能是 Garvey 或 Rosemead School District，高中常走 El Monte Union（Rosemead High）。一定要用地址查，我不會報單一學區。",
        "jobs": "Edison 總部在本市，那是地標，不是全市職業結構。居民前三是教育醫療、餐旅、製造。",
        "amenities": "週末吃飯買菜很滿。Rosemead Park 那些是日常。",
        "safetyNote": "治安分數沒核過就不講。主幹道商業跟巷內住宅感受不同。",
        "buyerFit": "要聖蓋博生活圈機能、總價低於聖馬跟亞凱、能接受學區對址功課的客人。",
        "propertyCaveats": "商業走廊跟住宅混，帶看分清幹道跟巷內。",
        "taxCaveats": "縣稅單；特別稅逐案。",
        "schoolReality": "K-8 可能是兩套，高中多為 EMUHSD，成交條件寫明對址。",
        "pitchLine": "羅斯密獨立屋大約 92 萬，商業帶很滿，學區是拼圖。小學可能是 Garvey 或 Rosemead，高中常走 El Monte Union。先對地址，再拿天普市比。",
        "compareLine": "隔壁天普市、客群重疊，可是羅斯密不是單一學區故事，總價也較低。拿聖馬來比，街廓跟總價完全不是同一檔。",
        "trendLine": "人口五萬左右，家戶所得中位大約七萬四。餐旅、製造比重比旁邊自住市高一點。普查五年估計。",
        "explainZh": "先講學區拼圖，再講 Valley Blvd 機能。聖馬那套標籤這裡套不上。",
        "sfhRange": "獨立屋中位大約 92 萬（Redfin）。",
        "condoRange": "Condo 大約 66 萬、聯排大約 75 萬。全類型大約 92 萬（至 2026-09），跟獨立屋很接近。",
        "ageProfile": "主幹道商業、巷內住宅混在一起。",
        "hoaMello": "Condo、少數新案有 HOA。",
    },
}


def main():
    data = json.loads(REGIONS.read_text(encoding="utf-8"))
    data["subtitleZh"] = "帶看用的南加生活圈對照 · 數字都有出處"
    data["dataNotesZh"] = (
        "盤點日 2026-10-15。人口、所得是普查五年估計，不是今年行情。"
        "普查亞裔不是台籍、陸籍。西徹斯特、Playa Vista 用郵區。"
        "獨立屋對照只放 Redfin 同一頁的獨立屋中位。"
    )
    blurbs = {
        "westside-lax": "西徹斯特、Playa Vista 還在洛杉磯市；Culver 才是獨立市。前兩格獨立屋先不並排。",
        "core-sgv-north": "南帕、聖馬、亞凱、天普市、羅斯密。學區各做各的，羅斯密還是拼圖。",
        "east-sgv-60": "鑽石吧、Walnut、羅蘭崗、哈仙達崗。哈仙達崗獨立屋先不並排，口徑還沒對齊。",
        "west-ie": "奇諾崗、安大略、波莫納。跨縣、物流、舊城，別當東聖蓋博延伸。",
        "west-southbay-oc": "南灣、橙縣以後再補，這張大圖先不放。",
    }
    for cl in data["clusters"]:
        if cl["id"] in blurbs:
            cl["blurbZh"] = blurbs[cl["id"]]

    by_id = {r["id"]: r for r in data["regions"]}
    for rid, voice in VOICE.items():
        r = by_id[rid]
        r["feelAxes"] = FEEL[rid]
        b = r.setdefault("basics", {})
        p = r.setdefault("priceBand", {})
        h = r.setdefault("highlights", {})
        c = r.setdefault("caveats", {})
        b["chineseBelt"] = voice["chineseBelt"]
        b["schoolBand"] = voice["schoolBand"]
        h["jobs"] = voice["jobs"]
        h["amenities"] = voice["amenities"]
        h["safetyNote"] = voice["safetyNote"]
        h["buyerFit"] = voice["buyerFit"]
        c["propertyCaveats"] = voice["propertyCaveats"]
        c["taxCaveats"] = voice["taxCaveats"]
        c["schoolReality"] = voice["schoolReality"]
        c["pitchLine"] = voice["pitchLine"]
        r["compareLine"] = voice["compareLine"]
        r["trendLine"] = voice["trendLine"]
        r["explainZh"] = voice["explainZh"]
        p["sfhRange"] = voice["sfhRange"]
        p["condoRange"] = voice["condoRange"]
        p["ageProfile"] = voice["ageProfile"]
        p["hoaMello"] = voice["hoaMello"]
        r["lastReviewed"] = "2026-10-15"

    REGIONS.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("updated", len(VOICE), "cities")


if __name__ == "__main__":
    main()
