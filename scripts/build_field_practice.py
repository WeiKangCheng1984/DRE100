#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build bilingual Field Practice data from structured lessons.

Outputs:
  - data/field_practice.json  (website module)
  - new function.md           (human-readable bilingual handbook)
"""
from __future__ import annotations

import json
from pathlib import Path

from field_form_guides import EXTRA_SCENARIOS, build_forms

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "data" / "field_practice.json"
OUT_MD = ROOT / "new function.md"

CHAPTERS = [
    {"id": "overview", "title": "總覽與表單速查", "titleEn": "Overview & Form Codes"},
    {"id": "contracts", "title": "標準合約與表單", "titleEn": "Contracts & Forms"},
    {"id": "disclosures", "title": "法定揭露與風險", "titleEn": "Disclosures & Compliance"},
    {"id": "escrow", "title": "產權與託管", "titleEn": "Title & Escrow"},
    {"id": "finance", "title": "房貸與估價", "titleEn": "Financing & Appraisal"},
    {"id": "inspections", "title": "檢查與修繕談判", "titleEn": "Inspections & Repairs"},
    {"id": "listing", "title": "上市與行銷", "titleEn": "Listing & Marketing"},
    {"id": "offers", "title": "CMA 與出價策略", "titleEn": "CMA & Offer Strategies"},
    {"id": "agency", "title": "代表權與倫理", "titleEn": "Representation & Ethics"},
    {"id": "closing", "title": "交屋與 Closing", "titleEn": "Walk-through & Closing"},
    {"id": "local", "title": "地方法規與特殊物業", "titleEn": "Local Rules & Property Types"},
]

# Enriched A+B form guides (sections / tips / mistakes / fictional samples)
FORMS = build_forms()

LESSONS = [
    {
        "id": "P001",
        "chapterId": "overview",
        "titleEn": "Transaction Lifecycle Map",
        "titleZh": "一筆交易的生命週期",
        "summaryEn": "Map the deal from representation → listing/touring → offer → acceptance → disclosures → investigations/loan/appraisal → repairs → contingency removal → CD/CTC → walk-through → recording/possession.",
        "summaryZh": "從代表協議、上市／找屋、出價、成交、揭露、調查／貸款／估價、修繕、移除條件、CD／CTC、最終驗房到過戶交屋。",
        "points": [
            {"en": "California residential resales usually run on C.A.R. forms, especially the RPA as both purchase contract and joint escrow instructions.", "zh": "加州住宅轉售多以 C.A.R. 表單運行，RPA 同時是買賣合約與聯合 Escrow 指示。"},
            {"en": "The three most common blow-ups: late/amended disclosures, contingencies not removed in writing, and late-stage wire/insurance/appraisal surprises.", "zh": "最易翻車三點：揭露晚到或修正、條件沒有書面移除、尾段電匯／保險／估價爆雷。"},
            {"en": "Oral side deals have almost no force—Delivery of signed writings controls deadlines and cancellation rights.", "zh": "口頭附帶協議幾乎無效；簽名文件的 Delivery 才控制期限與取消權。"},
        ],
        "judgments": [
            {"en": "If it is not in writing and delivered under the contract, treat it as not done.", "zh": "沒有依合約書面 Delivery，就當沒做過。"},
            {"en": "Track calendar days vs business days carefully (disclosures often use business-day rescission windows).", "zh": "分清日曆日與營業日（揭露撤銷常以營業日計算）。"},
        ],
        "englishPhrases": [
            {"en": "Time is of the essence.", "zh": "期限具重要性／應嚴格遵守時程。"},
            {"en": "Close of escrow / recording / possession", "zh": "結案過戶／縣府錄音／占有交屋"},
            {"en": "Clear to Close (CTC)", "zh": "貸方核准可結案"},
        ],
        "tags": ["timeline", "RPA", "escrow"],
    },
    {
        "id": "P002",
        "chapterId": "contracts",
        "titleEn": "RPA Skeleton: What Must Be Crystal Clear",
        "titleZh": "RPA 骨架：必須寫清楚的條款",
        "summaryEn": "An enforceable offer needs parties/property, price/deposit structure, financing, closing date, contingencies, liquidated damages/arbitration elections, and agency confirmation.",
        "summaryZh": "有效出價需寫清當事人與標的、價金／訂金、融資、過戶日、條件、違約金／仲裁勾選，以及代理確認。",
        "points": [
            {"en": "Prefer a specific closing date over vague language like “ASAP” or “30 days if possible.”", "zh": "Closing Date 應用明確日期，避免 ASAP 或含糊「約 30 天」。"},
            {"en": "Identify fixtures included and personal property excluded; attach inventories when needed.", "zh": "註明納入的 fixtures 與排除的動產；必要時附清單。"},
            {"en": "Deliver a copy of the accepted agreement to escrow, commonly within 3 business days after acceptance.", "zh": "成交後通常須在 3 個營業日內把合約副本交給 Escrow。"},
            {"en": "Liquidated damages generally require the parties to initial/sign the designated paragraph to be effective.", "zh": "違約預定損害賠償通常需雙方在指定段落簽名勾選才生效。"},
            {"en": "Mediation is typically required; arbitration is optional and usually waives jury trial if elected.", "zh": "調解多屬強制；仲裁需另行同意，同意後通常放棄陪審團審判。"},
        ],
        "judgments": [
            {"en": "Deposit size and liquidated-damages enforceability are related but not identical issues.", "zh": "「訂金多少」與「違約時能否留訂金」是相關但不同的問題。"},
            {"en": "Explain arbitration in plain English before asking a client to elect it.", "zh": "請客戶勾選仲裁前，先用白話說明利弊。"},
        ],
        "englishPhrases": [
            {"en": "Initial Deposit / Increased Deposit", "zh": "初始訂金／增加訂金"},
            {"en": "Joint Escrow Instructions", "zh": "聯合託管指示"},
            {"en": "Liquidated Damages", "zh": "違約預定損害賠償／違約金"},
            {"en": "Dispute Resolution: mediation / arbitration", "zh": "爭議解決：調解／仲裁"},
        ],
        "tags": ["RPA", "deposit", "arbitration"],
    },
    {
        "id": "P003",
        "chapterId": "contracts",
        "titleEn": "Contingency Clocks & CR/NBP Mechanics",
        "titleZh": "條件時鐘與 CR／NBP 機制",
        "summaryEn": "Default investigation is often 17 days; loan contingency often 21 days; seller disclosure delivery often 7 days. Contingencies do not auto-expire—use Form CR. After deadlines, seller may serve NBP.",
        "summaryZh": "調查期常見 17 天、貸款條件常見 21 天、賣方揭露常見 7 天。條件不會自動消失，須用 CR；逾期後賣方可發 NBP。",
        "points": [
            {"en": "No signed CR means the contingency is still alive.", "zh": "沒簽 CR＝條件還在。"},
            {"en": "Seller cancellation after a proper NBP typically requires releasing the deposit back to buyer under standard RPA logic.", "zh": "NBP 後賣方取消，依標準 RPA 邏輯通常須把訂金退回買方。"},
            {"en": "If buyer removed all contingencies but fails to close, seller’s path is usually Demand to Close Escrow (DCE), not NBP.", "zh": "買方已移除全部條件卻不 Closing，賣方通常走 DCE 而非 NBP。"},
            {"en": "Late seller disclosures can extend buyer’s removal/cancellation timing.", "zh": "賣方晚交揭露，可能延長買方移除／取消時程。"},
        ],
        "judgments": [
            {"en": "Never tell a client contingencies “automatically die” after day 17.", "zh": "絕不要跟客戶說條件在第 17 天會自動消失。"},
            {"en": "Calendar every CR, NBP, NSP, and deposit deadline the day of acceptance.", "zh": "成交當天就把 CR／NBP／NSP／訂金截止日期全部入曆。"},
        ],
        "englishPhrases": [
            {"en": "Investigation / appraisal / loan contingency", "zh": "調查／估價／貸款條件"},
            {"en": "Contingency Removal (CR)", "zh": "條件移除書"},
            {"en": "Notice to Buyer to Perform (NBP)", "zh": "催買方履約通知"},
            {"en": "Demand to Close Escrow (DCE)", "zh": "要求結案過戶"},
        ],
        "tags": ["CR", "NBP", "timeline"],
    },
    {
        "id": "P004",
        "chapterId": "disclosures",
        "titleEn": "Statutory vs Contractual Disclosure Stack",
        "titleZh": "法定 vs 合約揭露雙層結構",
        "summaryEn": "Statutory floor (TDS, NHD, Megan’s Law notice, lead paint, Mello-Roos, death-on-property, HOA package) plus contractual forms (SPQ, AVID, ESD) used in almost every C.A.R. deal.",
        "summaryZh": "法定底線（TDS、NHD、Megan’s Law、Lead、Mello-Roos、死亡揭露、HOA 文件）加上合約表單（SPQ、AVID、ESD）。",
        "points": [
            {"en": "TDS (CC 1102) is knowledge-based disclosure of material defects for most 1–4 unit transfers—not a warranty and not a substitute for inspections.", "zh": "TDS 是賣方「已知」重大瑕疵揭露，不是保固，也不能取代檢查。"},
            {"en": "NHD (CC 1103) covers six mapped hazard zones; use a current third-party NHD report rather than seller guesses.", "zh": "NHD 涵蓋六大災害區；應用即時第三方報告，不要靠賣方猜測。"},
            {"en": "Megan’s Law compliance is primarily the statutory notice text; sellers are not required to research specific nearby registrants.", "zh": "Megan’s Law 主要靠合約法定通知文字；賣方不必幫查附近具體人名。"},
            {"en": "Pre-1978 housing triggers federal lead-based paint disclosure + EPA pamphlet; buyers commonly get a 10-day inspection opportunity unless waived.", "zh": "1978 年前住宅觸發聯邦含鉛漆揭露與 EPA 手冊；買方通常有 10 天檢測機會（可書面放棄）。"},
            {"en": "SPQ is contractual and catches items TDS often misses (unpermitted work, claims, neighborhood issues).", "zh": "SPQ 屬合約揭露，補 TDS 常漏的項目（無許可工程、理賠、鄰里問題）。"},
        ],
        "judgments": [
            {"en": "“As-Is” never waives the duty to disclose known material facts.", "zh": "As-Is 絕對不能免除已知重大事實的揭露義務。"},
            {"en": "REO/probate TDS exemptions do not automatically wipe out NHD, lead, or Megan’s Law duties.", "zh": "REO／probate 的 TDS 豁免，不代表 NHD／Lead／Megan’s Law 也可免。"},
        ],
        "englishPhrases": [
            {"en": "Transfer Disclosure Statement (TDS)", "zh": "轉讓揭露書"},
            {"en": "Natural Hazard Disclosure (NHD)", "zh": "自然災害揭露"},
            {"en": "Seller Property Questionnaire (SPQ)", "zh": "賣方產權問卷"},
            {"en": "Agent Visual Inspection Disclosure (AVID)", "zh": "經紀人目視檢查揭露"},
        ],
        "tags": ["TDS", "NHD", "SPQ", "AVID"],
    },
    {
        "id": "P005",
        "chapterId": "disclosures",
        "titleEn": "Delivery Timing & Buyer Rescission Rights",
        "titleZh": "交付時程與買方撤銷權",
        "summaryEn": "Seller disclosures are commonly due within 7 days after acceptance. Late or amended material disclosures can reopen a buyer termination window (often 3 business days personal / 5 days mail).",
        "summaryZh": "賣方揭露常見 Acceptance 後 7 天內交付；晚交或重大修正可能重開買方終止權（親送常見 3 營業日／郵寄 5 日）。",
        "points": [
            {"en": "Even after inspection contingency removal, a material TDS amendment can revive cancellation rights.", "zh": "即使已移除檢查條件，重大 TDS 修正仍可能恢復取消權。"},
            {"en": "Best practice: complete TDS/SPQ/NHD/Lead at listing to avoid mid-escrow amendments.", "zh": "最佳實務：上市階段就完成 TDS／SPQ／NHD／Lead，避免 Escrow 中修正。"},
            {"en": "If a new material fact appears in escrow, disclose immediately in writing—do not wait for closing.", "zh": "Escrow 中出現新重大事實，立刻書面補充，不要拖到過戶。"},
        ],
        "judgments": [
            {"en": "Conflicts between AVID and TDS are red flags—investigate before removing contingencies.", "zh": "AVID 與 TDS 互相矛盾是紅旗，移除條件前先查清。"},
            {"en": "Write disclosures as if you may be deposed on them later.", "zh": "寫揭露時想像之後可能被宣誓作證追問。"},
        ],
        "englishPhrases": [
            {"en": "as soon as practicable before transfer of title", "zh": "於產權移轉前儘速"},
            {"en": "material amendment of disclosure", "zh": "揭露之重大修正"},
            {"en": "right to terminate / rescind the offer", "zh": "終止／撤銷要約之權利"},
        ],
        "tags": ["timeline", "rescission", "TDS"],
    },
    {
        "id": "P006",
        "chapterId": "disclosures",
        "titleEn": "How to Write an Objective AVID",
        "titleZh": "AVID：客觀目視紀錄寫法",
        "summaryEn": "Record observable conditions only. Do not diagnose causes, guarantee safety, or advocate for the seller.",
        "summaryZh": "只記錄看得見的現象；不要診斷因果、保證安全或幫賣方辯護。",
        "points": [
            {"en": "Good: “North roof slope shows displaced tiles and staining visible from ground; recommend roofing specialist.”", "zh": "佳：「北面屋頂從地面可見瓦片位移與污漬；建議請屋頂專家檢查。」"},
            {"en": "Bad: “Roof is fine / just old paint / seller says it was fixed so OK.”", "zh": "差：「屋頂沒問題／只是舊油漆／賣方說修過所以 OK。」"},
            {"en": "Listing agents should generally complete AVID after the seller completes the TDS inquiry sections.", "zh": "Listing Agent 宜在賣方完成 TDS 相關詢問後再完成 AVID。"},
        ],
        "judgments": [
            {"en": "If you cannot see it, do not invent it; if you saw it, do not omit it.", "zh": "看不見的別捏造；看見的別省略。"},
        ],
        "englishPhrases": [
            {"en": "reasonably competent and diligent visual inspection", "zh": "合理勝任且盡職的目視檢查"},
            {"en": "accessible areas of the property", "zh": "可進入／可接近之區域"},
            {"en": "recommend further professional inspection", "zh": "建議進一步由專業人士檢查"},
        ],
        "tags": ["AVID", "risk"],
    },
    {
        "id": "P007",
        "chapterId": "escrow",
        "titleEn": "Escrow vs Title & Reading the Prelim",
        "titleZh": "Escrow vs Title 與初步產權報告",
        "summaryEn": "Escrow is the neutral stakeholder; Title examines chain of title and issues insurance. Buyers must read Preliminary Title Report exceptions before removing contingencies.",
        "summaryZh": "Escrow 是中立保管方；Title 查產權並出保險。買方移除條件前必須讀 Prelim 的除外事項。",
        "points": [
            {"en": "Key prelim sections: legal description/APN, vesting, Schedule B exceptions, requirements, taxes/assessments.", "zh": "Prelim 關鍵：法定描述／APN、持有方式、Schedule B 例外、過戶條件、稅賦。"},
            {"en": "Utility easements are common; easements that block parking, expansion, or access need client counseling.", "zh": "公用事業地役權常見；影響停車／擴建／進出者要跟客戶說明。"},
            {"en": "Liens (judgment, mechanic’s, HOA) should be cleared or credited through escrow before closing.", "zh": "判決／技工／HOA 等留置權應在 Closing 前清償或經 Escrow 扣款處理。"},
        ],
        "judgments": [
            {"en": "Schedule B exceptions are not decorations—they define what the buyer takes subject to.", "zh": "Schedule B 例外不是裝飾，而是買方承受的產權限制。"},
        ],
        "englishPhrases": [
            {"en": "Preliminary Title Report (Prelim)", "zh": "初步產權報告"},
            {"en": "vesting / chain of title", "zh": "產權持有方式／產權鏈"},
            {"en": "exceptions / encumbrances / easements / liens", "zh": "除外事項／負擔／地役權／留置權"},
            {"en": "Owner’s Policy vs Lender’s Policy", "zh": "所有權人保單 vs 貸方保單"},
        ],
        "tags": ["title", "prelim", "easement"],
    },
    {
        "id": "P008",
        "chapterId": "escrow",
        "titleEn": "Closing Disclosure, Prorations & Wire Fraud SOP",
        "titleZh": "CD、按日分攤與電匯防詐 SOP",
        "summaryEn": "Financed buyers must receive the Closing Disclosure at least three business days before closing. Always verify wire instructions by calling a number you independently sourced.",
        "summaryZh": "有貸款買方 Closing 前至少 3 個完整營業日要收到 CD。電匯指示一律用獨立查到的電話回撥驗證。",
        "points": [
            {"en": "Compare Loan Estimate → Closing Disclosure for APR, points, cash to close, and fee changes.", "zh": "對照 LE→CD：APR、點數、現金結案額、費用變更。"},
            {"en": "Significant CD changes can restart the three-business-day clock and delay recording.", "zh": "重大 CD 變更可能重開 3 營業日時鐘並拖延過戶。"},
            {"en": "Escrow almost never changes wiring instructions by last-minute email—treat that as fraud until proven otherwise.", "zh": "Escrow 幾乎不會用最後一刻郵件改帳號；一律先當詐騙處理。"},
            {"en": "Give Wire Fraud Advisory at opening, again mid-escrow, and again before funds move.", "zh": "開案、中段、匯款前都要再做電匯防詐教育。"},
        ],
        "judgments": [
            {"en": "Never use a phone number that arrived inside the suspicious email itself.", "zh": "絕不要用可疑郵件裡提供的電話去「驗證」。"},
        ],
        "englishPhrases": [
            {"en": "Closing Disclosure (CD) / Settlement Statement", "zh": "結案揭露／結算清單"},
            {"en": "proration of taxes and HOA dues", "zh": "稅費與 HOA 費按日分攤"},
            {"en": "independently verify wiring instructions", "zh": "以獨立來源驗證電匯指示"},
            {"en": "business email compromise (BEC)", "zh": "商務郵件入侵詐騙"},
        ],
        "tags": ["CD", "wire fraud", "escrow"],
    },
    {
        "id": "P009",
        "chapterId": "finance",
        "titleEn": "Pre-Approval Quality & Loan Types",
        "titleZh": "預核含金量與貸款類型",
        "summaryEn": "Judge lender letters by documentation depth (credit pulled, DU/LP findings, conditions). Know Conventional vs FHA vs VA vs cash workflow impacts.",
        "summaryZh": "用文件深度判斷預核含金量（是否拉信用、DU／LP、條件清單）。理解 Conventional／FHA／VA／現金對成交流程的影響。",
        "points": [
            {"en": "Verbal estimates < pre-qual < documented pre-approval < DU/LP findings < property-specific conditional approval.", "zh": "口頭估 < 預審 < 書面預核 < DU／LP < 針對該屋條件核准。"},
            {"en": "FHA/VA appraisals can impose repair conditions that Conventional may not.", "zh": "FHA／VA 估價可能要求修繕，Conventional 不一定有。"},
            {"en": "Cash still needs proof of funds and usually still benefits from inspections and title review.", "zh": "現金單仍要資金證明，且通常仍應做檢查與產權審閱。"},
        ],
        "judgments": [
            {"en": "A weak pre-approval is a liability in multiple-offer combat.", "zh": "含金量弱的預核信在多方競標中是負擔。"},
        ],
        "englishPhrases": [
            {"en": "pre-qualification vs pre-approval", "zh": "預審 vs 預核"},
            {"en": "Desktop Underwriter (DU) / Loan Product Advisor (LP)", "zh": "自動承保系統"},
            {"en": "debt-to-income ratio (DTI) / loan-to-value (LTV)", "zh": "負債收入比／貸款價值比"},
            {"en": "private mortgage insurance (PMI)", "zh": "私人抵押貸款保險"},
        ],
        "tags": ["loan", "pre-approval", "FHA", "VA"],
    },
    {
        "id": "P010",
        "chapterId": "finance",
        "titleEn": "Appraisal Gap Playbook",
        "titleZh": "估價不足應對菜單",
        "summaryEn": "Plan gap responses before the report: seller price cut, buyer cash, split difference, ROV appeal, cancel under appraisal contingency, or honor a waived contingency with cash.",
        "summaryZh": "估價報告前先談缺口策略：降價、買方補現金、各讓一步、重新比價申訴、依條件取消，或放棄條件後自行補足。",
        "points": [
            {"en": "If appraisal contingency was waived, buyer generally must cover the shortfall to keep financing alive.", "zh": "若已放棄估價條件，買方通常必須自補缺口才能維持貸款。"},
            {"en": "Reconsideration of Value needs better comps/error analysis; success is uncertain.", "zh": "重新比價申訴需要更好 comps／錯誤分析，成功率不一定。"},
            {"en": "Write any agreed gap amount into the contract before emotions escalate.", "zh": "在情緒升高前就把同意的 gap 金額寫進合約。"},
        ],
        "judgments": [
            {"en": "Ask every buyer: “What is your maximum cash gap if the appraisal comes in low?”", "zh": "每個買方都要問：「估不足時，你最多能現金補多少？」"},
        ],
        "englishPhrases": [
            {"en": "appraisal gap / shortfall", "zh": "估價缺口"},
            {"en": "Reconsideration of Value (ROV)", "zh": "重新評估價值申請"},
            {"en": "waive the appraisal contingency", "zh": "放棄估價條件"},
            {"en": "rate lock expiration", "zh": "利率鎖定期到期"},
        ],
        "tags": ["appraisal", "negotiation"],
    },
    {
        "id": "P011",
        "chapterId": "inspections",
        "titleEn": "Inspection Menu & RR/RRRR Negotiation",
        "titleZh": "檢查組合與 RR／RRRR 談判",
        "summaryEn": "Use general, termite/WDO, roof, sewer, foundation and specialty inspections as needed. Negotiate with RR/RRRR or amend price via AEA. Seller has no duty to agree.",
        "summaryZh": "依需要安排通用、白蟻、屋頂、排污、地基等檢查；用 RR／RRRR 談判或 AEA 改價。賣方沒有義務同意修繕。",
        "points": [
            {"en": "Prioritize safety, lender kill-items, and near-term high-cost failures over cosmetic preferences.", "zh": "優先談安全、貸方卡關項、近期高額維修；別用美容問題破局。"},
            {"en": "Credits in lieu of repairs close faster but may hit lender credit caps and leave quality control to buyer.", "zh": "Credit 代替施工較快，但可能撞上貸方 credit 上限，品質也改由買方自控。"},
            {"en": "Seller responses often condition agreement on buyer removing the physical inspection contingency and signing a release.", "zh": "賣方同意修繕／折讓時，常要求買方移除實體檢查條件並簽署釋放條款。"},
        ],
        "judgments": [
            {"en": "In multiple offers, keep RR extremely disciplined or seller will pivot to backup.", "zh": "多方競標下 RR 要極克制，否則賣方轉 Backup。"},
        ],
        "englishPhrases": [
            {"en": "Request for Repair (RR)", "zh": "修繕請求"},
            {"en": "credit in lieu of repairs", "zh": "以折讓代替修繕"},
            {"en": "Wood-Destroying Organism (WDO) / termite report", "zh": "白蟻／木蛀蟲報告"},
            {"en": "sewer scope inspection", "zh": "排污管內視鏡檢查"},
        ],
        "tags": ["RR", "inspection", "negotiation"],
    },
    {
        "id": "P012",
        "chapterId": "listing",
        "titleEn": "Listing Launch, RLA & MLS Compliance",
        "titleZh": "上市啟動、RLA 與 MLS 合規",
        "summaryEn": "AD → RLA, gather docs, order NHD/HOA/photos, complete disclosures, then MLS. Post-NAR rules changed how buyer-broker compensation is offered; follow current MLS and C.A.R. guidance.",
        "summaryZh": "AD→RLA，收齊文件，下單 NHD／HOA／攝影，完成揭露後上 MLS。NAR 後買方經紀人報酬機制已變，依現行 MLS／C.A.R. 指引。",
        "points": [
            {"en": "Negotiate term, protection period, marketing authorizations, and cancellation terms in the listing agreement.", "zh": "在委託書中談妥期限、保護期、行銷授權與解約條款。"},
            {"en": "MLS remarks must avoid fair-housing steering language and misleading photos/amenities.", "zh": "MLS 備註避免公平住房引導用語與誤導照片／設施。"},
            {"en": "Pre-listing inspection can reduce later RR shocks but must be disclosed honestly.", "zh": "上市前檢查可減少後續 RR 衝擊，但必須誠實揭露。"},
        ],
        "judgments": [
            {"en": "Pricing strategy is a client decision; your job is evidence-based counseling via CMA.", "zh": "定價是客戶決策；你的工作是用 CMA 做有證據的諮詢。"},
        ],
        "englishPhrases": [
            {"en": "Residential Listing Agreement (RLA)", "zh": "住宅委託銷售協議"},
            {"en": "Days on Market (DOM)", "zh": "上市天數"},
            {"en": "Coming Soon / Active / Pending / Sold", "zh": "即將上市／在售／成交中／已售"},
            {"en": "procuring cause", "zh": "促成交易主因"},
        ],
        "tags": ["listing", "MLS", "RLA"],
    },
    {
        "id": "P013",
        "chapterId": "offers",
        "titleEn": "CMA Discipline & Multiple-Offer Tools",
        "titleZh": "CMA 紀律與多方出價工具",
        "summaryEn": "Build CMAs from recent nearby similar solds, plus actives/pendings/expireds. Competitive tools include escalation, deposits, shorter timelines, and contingency waivers—with explicit risk counseling.",
        "summaryZh": "CMA 用近期、近距、相似成交，並看在售／成交中／流案。競標工具含自動加價、訂金、縮短時程、放棄條件——必須明確風險告知。",
        "points": [
            {"en": "Adjust comps for condition, upgrades, ADU legality, and owned vs leased solar.", "zh": "依屋況、升級、ADU 合法性、太陽能自有／租賃調整 comps。"},
            {"en": "Escalation clauses need crisp definitions of what counts as a bona fide competing offer and the maximum cap.", "zh": "Escalation 必須清楚定義什麼算有效競爭出價與最高上限。"},
            {"en": "Love letters can create fair-housing risk; many brokerages discourage them.", "zh": "情感信可能引發公平住房風險；許多公司不建議。"},
        ],
        "judgments": [
            {"en": "Waiving contingencies can win the house and lose the client’s safety net—document informed consent.", "zh": "放棄條件可能贏下房子也丟掉安全網——務必書面告知並取得知情同意。"},
        ],
        "englishPhrases": [
            {"en": "Comparative Market Analysis (CMA)", "zh": "比較市場分析"},
            {"en": "escalation clause", "zh": "自動加價條款"},
            {"en": "waive contingencies", "zh": "放棄條件"},
            {"en": "Seller Multiple Counter Offer", "zh": "賣方多方還價"},
        ],
        "tags": ["CMA", "offers", "escalation"],
    },
    {
        "id": "P014",
        "chapterId": "agency",
        "titleEn": "Dual Agency, BRBC & AB 2992",
        "titleZh": "雙方代理、BRBC 與 AB 2992",
        "summaryEn": "Dual agency requires written disclosure/consent and careful confidentiality. Buyer-broker written agreements are now mandatory practice/law territory: MLS often before touring; CA law no later than offer; generally max 3 months; no auto-renewal.",
        "summaryZh": "雙方代理須書面揭露同意並嚴守機密。買方書面代表協議已成實務／法律重點：MLS 常要求帶看前；加州法律至遲出價時；一般最長 3 個月；不可自動續約。",
        "points": [
            {"en": "Compensation in the buyer agreement is a ceiling from any source; seller concessions may contribute but cannot exceed the agreed amount.", "zh": "買方協議中的報酬是任何來源的上限；賣方 concession 可貢獻但不可超過約定。"},
            {"en": "Discuss services, value, payment source, and what happens if seller will not pay.", "zh": "談清楚服務內容、價值、付款來源，以及賣方不付時怎麼辦。"},
            {"en": "Put buyer walk-away limits and contingency-waiver instructions in writing.", "zh": "把買方底線與放棄條件指示寫下來。"},
        ],
        "judgments": [
            {"en": "In dual agency, never share one party’s confidential negotiation ceiling with the other.", "zh": "雙方代理下，絕不可把一方機密談判底線泄露給另一方。"},
        ],
        "englishPhrases": [
            {"en": "dual agency / single agency", "zh": "雙方代理／單一代理"},
            {"en": "Buyer Representation and Broker Compensation Agreement (BRBC)", "zh": "買方代表與佣金協議"},
            {"en": "seller concession toward buyer broker compensation", "zh": "賣方折讓用於支付買方經紀人報酬"},
            {"en": "fiduciary duties: loyalty, confidentiality, disclosure, obedience, accounting, care", "zh": "受託義務：忠誠、保密、揭露、服從、財務交代、注意"},
        ],
        "tags": ["BRBC", "dual agency", "ethics"],
    },
    {
        "id": "P015",
        "chapterId": "closing",
        "titleEn": "Final Walk-through, SIP/RLAS & Possession",
        "titleZh": "最終驗房、SIP／RLAS 與交屋",
        "summaryEn": "Walk-through verifies agreed condition and repairs—not a brand-new full inspection. Use SIP/RLAS if seller remains after closing. Transfer keys, codes, utilities, and HOA access methodically.",
        "summaryZh": "最終驗房確認約定狀況與修繕，不是重新完整檢查。賣方續住用 SIP／RLAS。系統性交接鑰匙、密碼、水電與 HOA 權限。",
        "points": [
            {"en": "If walk-through finds problems: delay closing, escrow holdback, repair proof, credit, or cancel if contract rights allow.", "zh": "驗房有問題：延後 Closing、代管扣留、修繕證明、折讓，或依合約權利取消。"},
            {"en": "SIP/RLAS must specify days, rent/deposit, utilities, maintenance, insurance, and default remedies.", "zh": "SIP／RLAS 必須寫清天數、租金／押金、水電、維修、保險與違約救濟。"},
            {"en": "Common closing blockers: funds delay, CD restart, insurance denial, stale payoff, missing HOA demand, incomplete signatures.", "zh": "常見卡關：資金延誤、CD 重開、保險拒保、payoff 過期、HOA demand 未出、簽名不全。"},
        ],
        "judgments": [
            {"en": "Change gate/alarm codes after possession whenever feasible.", "zh": "交屋後盡可能立刻更改門禁／警報密碼。"},
        ],
        "englishPhrases": [
            {"en": "final walk-through / Verification of Property Condition (VP)", "zh": "交屋前最終驗房"},
            {"en": "Seller In Possession (SIP)", "zh": "賣方過戶後占用"},
            {"en": "Residential Lease After Sale (RLAS)", "zh": "售後租賃"},
            {"en": "recording and disbursement", "zh": "產權錄音與資金撥付"},
        ],
        "tags": ["closing", "VP", "SIP"],
    },
    {
        "id": "P016",
        "chapterId": "local",
        "titleEn": "HOA Packages, Local Ordinances & ADUs",
        "titleZh": "HOA 文件、地方法規與 ADU",
        "summaryEn": "Order CC 4525 packages early. Screen for reserve risk, litigation, rental caps, and assessments. Check city-specific retrofit/sewer/rent rules. Verify ADU permits and financeability.",
        "summaryZh": "及早下單 CC 4525 文件包；審查儲備金、訴訟、出租限制與特別徵收。查城市加固／排污／租金規則。核對 ADU 許可與可貸性。",
        "points": [
            {"en": "Association generally has about 10 days after written request to provide requested §4525 documents.", "zh": "協會接書面請求後通常約 10 天內交付所請求的 §4525 文件。"},
            {"en": "Red flags: underfunded reserves, high rental ratio, active litigation, strict short-term rental bans, unpaid assessments that can lien.", "zh": "紅旗：儲備不足、高出租比、訴訟中、嚴格短租禁令、可成留置權的欠費。"},
            {"en": "Ask whether an ADU has final permits, lawful rental use, separate metering, parking impacts, and HOA limits.", "zh": "ADU 必問：最終許可、合法出租、獨立計量、停車影響、HOA 限制。"},
            {"en": "Tenant-occupied, solar lease/PACE, trust/probate, and manufactured homes each add specialized paperwork.", "zh": "租客在住、太陽能租約／PACE、信託／遺產、組合屋各有特殊文件。"},
        ],
        "judgments": [
            {"en": "Local ordinances vary by city—never assume statewide uniformity.", "zh": "地方法規因市而異，絕不要假設全州一致。"},
        ],
        "englishPhrases": [
            {"en": "CC&Rs / bylaws / operating rules", "zh": "公約限制／章程／營運規則"},
            {"en": "reserve study / special assessment", "zh": "儲備金研究／特別徵收"},
            {"en": "Accessory Dwelling Unit (ADU) / Junior ADU (JADU)", "zh": "附屬住宅單元／小型附屬單元"},
            {"en": "soft-story retrofit / sewer lateral ordinance", "zh": "軟層加固／污水側管條例"},
        ],
        "tags": ["HOA", "ADU", "local"],
    },
]

CHECKLISTS = [
    {
        "id": "CL01",
        "chapterId": "contracts",
        "titleEn": "Offer Intake Checklist",
        "titleZh": "出價前檢查清單",
        "items": [
            {"en": "AD signed", "zh": "已簽署 AD（Agency Disclosure）"},
            {"en": "BRBC/PSRA signed; compensation source discussed", "zh": "已簽署買方代表協議並談妥佣金來源"},
            {"en": "Pre-approval or Proof of Funds attached (covers offer price)", "zh": "Pre-approval／Proof of Funds 已附（金額覆蓋報價）"},
            {"en": "Price, deposit, closing date, escrow/title filled", "zh": "報價、訂金、Closing Date、Escrow／Title 已填"},
            {"en": "Contingency periods matched to risk tolerance", "zh": "Contingency 天數已與風險承受度對齊"},
            {"en": "Any waiver/shortening of contingencies documented with risk disclosure", "zh": "放棄／縮短條件已書面風險告知"},
            {"en": "Liquidated damages / arbitration elections explained", "zh": "違約金／仲裁勾選已向客戶解釋"},
            {"en": "Escalation/appraisal gap addenda reviewed if used", "zh": "若有 Escalation／Gap 附件已審閱"},
            {"en": "HOA/ADU/tenant/solar issues asked", "zh": "HOA／ADU／租客／太陽能等特殊情況已問過"},
            {"en": "Client understands the clock starts at Acceptance", "zh": "客戶理解 Acceptance 後才開始正式時鐘"},
        ],
    },
    {
        "id": "CL02",
        "chapterId": "disclosures",
        "titleEn": "Buyer Disclosure Review Notes",
        "titleZh": "買方揭露審閱筆記",
        "items": [
            {"en": "TDS Yes answers listed and investigated", "zh": "TDS 勾選 Yes 的項目已列出並追查"},
            {"en": "SPQ claims / unpermitted work / neighborhood issues reviewed", "zh": "SPQ 理賠／無許可工程／鄰里問題已審"},
            {"en": "NHD zones checked; insurance feasibility quoted", "zh": "NHD 區域已確認；保險可否承保已詢價"},
            {"en": "AVID vs TDS conflicts flagged", "zh": "AVID 與 TDS 不一致處已標記"},
            {"en": "Lead / Megan’s Law / Mello-Roos / HOA package received", "zh": "Lead／Megan’s Law／Mello-Roos／HOA 已收齊"},
            {"en": "Additional specialty inspections selected", "zh": "需要的專項檢查已選定"},
            {"en": "3/5-day termination analysis completed if late/amended disclosures", "zh": "若晚交／修正揭露，已分析 3／5 日終止權"},
            {"en": "RR negotiation priorities drafted", "zh": "RR 談判重點已起草"},
        ],
    },
    {
        "id": "CL03",
        "chapterId": "escrow",
        "titleEn": "Wire Verification Call Log",
        "titleZh": "電匯驗證通話紀錄",
        "items": [
            {"en": "Called escrow using independently sourced phone number", "zh": "使用獨立來源電話回撥 Escrow"},
            {"en": "Verified bank name, routing, account, beneficiary", "zh": "已核對銀行名、Routing、帳號、收款人"},
            {"en": "Verified amount and cutoff time", "zh": "已核對金額與匯款截止時間"},
            {"en": "Confirmed no last-minute email change is valid", "zh": "已確認最後一刻郵件改帳無效／需重驗"},
            {"en": "Requested written confirmation after wire sent", "zh": "匯出後已要求書面入帳確認"},
        ],
    },
    {
        "id": "CL04",
        "chapterId": "escrow",
        "titleEn": "Escrow Coordination Checkpoint",
        "titleZh": "Escrow 時程協調檢查",
        "items": [
            {"en": "Contingency removals tracked", "zh": "條件移除狀態已追蹤"},
            {"en": "Lender conditional approval / CTC status known", "zh": "貸方 Cond／CTC 狀態已知"},
            {"en": "CD expected issue date checked vs weekends/holidays", "zh": "CD 預計發出日已避開週末／假日問題"},
            {"en": "Homeowner insurance binder confirmed", "zh": "屋主保險 Bind 已確認"},
            {"en": "Seller loan payoff figures current", "zh": "賣方貸款 payoff 數字為最新"},
            {"en": "HOA demand / transfer fees ordered", "zh": "HOA demand／移轉費已下單"},
            {"en": "Signing appointments set", "zh": "雙方 Signing 已预约"},
            {"en": "County recording cutoff considered", "zh": "已考慮縣府 Recording 截止時間"},
        ],
    },
    {
        "id": "CL05",
        "chapterId": "inspections",
        "titleEn": "Repair Priority Matrix",
        "titleZh": "修繕談判優先級",
        "items": [
            {"en": "A: Safety / code / lender kill-items identified", "zh": "A：安全／法規／貸方卡關項已列出"},
            {"en": "B: Near-term high-cost systems identified", "zh": "B：近 1–2 年高額支出項已列出"},
            {"en": "C: Maintenance items separated", "zh": "C：維護型項目已分開"},
            {"en": "D: Cosmetic preferences deprioritized", "zh": "D：偏好／美容項不作為破局理由"},
            {"en": "Ask credit vs price reduction vs seller repairs", "zh": "已決定要 Credit／降價／賣方施工哪一種"},
            {"en": "Seller response deadline set", "zh": "賣方回覆截止日期已設定"},
        ],
    },
    {
        "id": "CL06",
        "chapterId": "closing",
        "titleEn": "Possession & Keys Handoff",
        "titleZh": "交屋交接清單",
        "items": [
            {"en": "Door/mailbox/garage/pool/community keys counted", "zh": "各類鑰匙數量已清點"},
            {"en": "Remotes, fobs, codes transferred; password change planned", "zh": "遙控／門禁／密碼已交接；改密已規劃"},
            {"en": "Solar app/lease contacts provided", "zh": "太陽能 App／租約聯絡人已提供"},
            {"en": "Utilities transfer confirmed (power/gas/water/trash/internet)", "zh": "水電瓦斯垃圾網路移轉已確認"},
            {"en": "HOA portal / gate access requested", "zh": "HOA portal／門禁申請已送"},
            {"en": "Settlement statement and title policy copies retained", "zh": "結算單與產權保險副本已存檔"},
        ],
    },
    {
        "id": "CL07",
        "chapterId": "overview",
        "titleEn": "First 48 Hours After Opening Escrow",
        "titleZh": "開案後 48 小時行動",
        "items": [
            {"en": "Listing: deliver contract + seller contacts to escrow/title", "zh": "賣方端：合約與賣方聯絡資訊送 Escrow／Title"},
            {"en": "Listing: confirm disclosure status; order missing NHD/HOA", "zh": "賣方端：確認揭露；缺的 NHD／HOA 立刻下單"},
            {"en": "Listing: schedule inspection access windows", "zh": "賣方端：協調檢查看屋時段"},
            {"en": "Buyer: deposit funds; sign supplemental escrow instructions", "zh": "買方端：交訂金；簽 Escrow 補充指示"},
            {"en": "Buyer: book general + specialty inspections", "zh": "買方端：預約通用＋專項檢查"},
            {"en": "Buyer: send contract package to lender; start insurance quotes", "zh": "買方端：送貸方；開始保險詢價"},
            {"en": "Buyer: review prelim; educate on wire fraud", "zh": "買方端：讀 Prelim；做電匯防詐教育"},
        ],
    },
]

SCENARIOS = [
    {
        "id": "S01",
        "chapterId": "finance",
        "titleEn": "Appraisal $40,000 short after waiver",
        "titleZh": "已放棄估價條件，估價少了 $40,000",
        "promptEn": "Buyer waived appraisal contingency but still has a loan contingency. Appraisal is $40k below contract price. What options exist and what should the agent document?",
        "promptZh": "客戶已放棄 appraisal contingency，但還有 loan contingency。估價低於合約價 $40,000。客戶有哪些選項？經紀人應如何書面紀錄？",
        "answerEn": "Options: bring cash to cover the gap; renegotiate price/credit with seller; attempt ROV with better comps; if financing fails under remaining loan contingency, evaluate cancellation rights carefully; or walk if parties cannot bridge the gap. Document that appraisal contingency was waived, the cash-gap discussion, lender conditions, and any written amendment. Do not invent an appraisal exit that was already waived.",
        "answerZh": "選項：買方現金補缺口；與賣方重談降價／折讓；用更好 comps 做 ROV；若仍因貸款條件無法取得融資，再審慎評估貸款條件下的取消權；雙方無法銜接則破局。書面紀錄：已放棄估價條件、現金缺口討論、貸方條件、任何書面修正。不可假裝還有估價退出權。",
        "focusTags": ["appraisal", "loan contingency", "documentation"],
        "formPlaybook": [
            {
                "code": "AEA",
                "actionEn": "If parties renegotiate price/credit, amend in writing.",
                "actionZh": "若重談價格／折讓，以書面修正。",
                "checkMarks": [
                    {"en": "New price or credit amount exact", "zh": "新價格或折讓金額精確"},
                    {"en": "Notify lender + escrow same day", "zh": "當日通知貸方＋Escrow"},
                ],
            },
            {
                "code": "CR",
                "actionEn": "Review what was already removed—do not pretend appraisal contingency still exists.",
                "actionZh": "核對已移除項目——不可假裝估價條件還在。",
                "checkMarks": [
                    {"en": "Confirm appraisal was waived/removed earlier", "zh": "確認估價條件先前已放棄／移除"},
                ],
            },
            {
                "code": "CC",
                "actionEn": "If canceling under remaining loan contingency, use written cancellation + lender denial support.",
                "actionZh": "若依剩餘貸款條件取消，用書面取消＋貸方拒絕佐證。",
                "checkMarks": [
                    {"en": "Loan contingency still active on file", "zh": "檔案上貸款條件仍有效"},
                    {"en": "Deposit disposition stated", "zh": "訂金處置已載明"},
                ],
            },
            {
                "code": "MCA",
                "actionEn": "Point back to market advisory counseling already given on appraisal-gap risk.",
                "actionZh": "回指先前 MCA 對估價缺口風險的諮詢紀錄。",
                "checkMarks": [
                    {"en": "File contains signed MCA / strategy email", "zh": "檔案有已簽 MCA／策略電郵"},
                ],
            },
        ],
    },
    {
        "id": "S02",
        "chapterId": "disclosures",
        "titleEn": "Late TDS leak disclosure after contingency removal",
        "titleZh": "移除檢查條件後才補上滲水史",
        "promptEn": "Buyer already removed inspection contingency. Seller then amends TDS to disclose prior water intrusion. Does buyer regain a termination right? What do you send next?",
        "promptZh": "買方已移除檢查條件後，賣方才修正 TDS 補上曾經滲水。買方是否可能重新取得終止權？下一步送哪些文件？",
        "answerEn": "A material amended disclosure can reopen statutory termination timing (commonly 3 business days personal / 5 days mail). Advise buyer immediately, calendar the deadline, consider additional inspection, and decide cancel vs proceed/negotiate. Deliver the amended disclosure package with receipt tracking; consult broker/counsel on exact statute/form timing.",
        "answerZh": "重大揭露修正可能重開法定終止時程（親送常見 3 營業日／郵寄 5 日）。立刻告知買方、記入截止日期、考慮加做檢查，並決定取消或續談。交付修正揭露並保留送達證明；確切時程與表單請示經紀人／律師。",
        "focusTags": ["TDS", "rescission", "delivery"],
        "formPlaybook": [
            {
                "code": "TDS",
                "actionEn": "Deliver amended TDS with proof of delivery; calendar statutory window.",
                "actionZh": "交付修正 TDS 並保留送達證明；記入法定窗口。",
                "checkMarks": [
                    {"en": "Mark as amended / material update", "zh": "標明為修正／重大更新"},
                    {"en": "Buyer receipt time stamped", "zh": "買方簽收時間戳記"},
                ],
            },
            {
                "code": "SPQ",
                "actionEn": "Align SPQ answers with the new leak history if needed.",
                "actionZh": "必要時讓 SPQ 與新滲水史一致。",
                "checkMarks": [
                    {"en": "No remaining TDS/SPQ conflict", "zh": "TDS／SPQ 不再矛盾"},
                ],
            },
            {
                "code": "RR",
                "actionEn": "If buyer proceeds, may request credit/repair based on new info (while rights allow).",
                "actionZh": "若續談，可在權利允許下依新資訊請求折讓／修繕。",
                "checkMarks": [
                    {"en": "Cite amended disclosure + any new inspection", "zh": "引用修正揭露＋任何新檢查"},
                ],
            },
            {
                "code": "CC",
                "actionEn": "If buyer elects statutory termination within the window, cancel in writing.",
                "actionZh": "若買方在窗口內行使法定終止，書面取消。",
                "checkMarks": [
                    {"en": "Deadline not missed", "zh": "未錯過截止日"},
                    {"en": "Deposit instruction clear", "zh": "訂金指示清楚"},
                ],
            },
        ],
    },
    {
        "id": "S03",
        "chapterId": "escrow",
        "titleEn": "Escrow email changes wire account",
        "titleZh": "Escrow 郵件要求匯到新帳號",
        "promptEn": "An email claiming to be escrow says the old account is invalid and provides new wiring instructions. What is the correct SOP?",
        "promptZh": "一封聲稱來自 Escrow 的郵件說舊帳戶失效並提供新電匯指示。正確 SOP 是什麼？",
        "answerEn": "Stop. Do not click links or wire. Call escrow using a phone number from the official website or previously verified card—not from the email. Verify every digit. Report the attempt. Resend Wire Fraud Advisory to the client. Correct SOP prevents irreversible loss; wrong SOP can permanently divert closing funds.",
        "answerZh": "立刻停止，不要點連結、不要匯。用官網或先前核實名片上的電話回撥，不要用郵件裡的電話。逐位核對帳號並通報。再次發送電匯防詐告知。正確 SOP 可避免不可逆損失；錯誤 SOP 可能讓結案資金永久被轉走。",
        "focusTags": ["wire fraud", "escrow"],
        "formPlaybook": [
            {
                "code": "WFA",
                "actionEn": "Re-deliver WFA; walk client through callback verification before any wire.",
                "actionZh": "再次交付 WFA；匯款前帶客戶走回撥核實。",
                "checkMarks": [
                    {"en": "Do not use phone/account from the suspicious email", "zh": "不用可疑電郵內的電話／帳號"},
                    {"en": "Verify every digit verbally with known escrow number", "zh": "用已知 Escrow 電話口頭逐位核對"},
                    {"en": "Report fraud attempt to escrow/broker", "zh": "向 Escrow／經紀通報詐騙嘗試"},
                ],
            },
            {
                "code": "RPA",
                "actionEn": "Closing still follows contract—funding only to verified escrow instructions.",
                "actionZh": "結案仍依合約——只匯至已核實的 Escrow 指示。",
                "checkMarks": [
                    {"en": "No oral change to wire path", "zh": "不以口頭更改匯款路徑"},
                ],
            },
        ],
    },
    {
        "id": "S04",
        "chapterId": "offers",
        "titleEn": "Escalation + waived inspection in multiple offers",
        "titleZh": "多方出價：自動加價＋放棄檢查",
        "promptEn": "Client wants an escalation clause and to waive inspection to win. What risks must you disclose and what definitions are missing?",
        "promptZh": "客戶想寫 escalation 並放棄檢查來搶房。你要揭露哪些風險？合約還缺哪些定義？",
        "answerEn": "Disclose: may overpay vs appraisal, limited exit for defects, deposit risk if later default, insurance/repair unknowns. Define competing offer criteria, escalation increment, cap, proof of competing offer, and whether appraisal gap applies. Get written informed consent; consider shorter inspection instead of full waiver if client can accept.",
        "answerZh": "需揭露：可能高於估價、發現瑕疵難退出、日後違約訂金風險、保險／修繕未知。需定義：何謂有效競爭出價、加價幅度、上限、競爭出價證明、是否搭配 appraisal gap。取得書面知情同意；若可接受，可考慮縮短檢查而非完全放棄。",
        "focusTags": ["escalation", "contingency waiver", "fair counseling"],
        "formPlaybook": [
            {
                "code": "MCA",
                "actionEn": "Deliver MCA and document counseling on multiple-offer / waiver risks.",
                "actionZh": "交付 MCA，並紀錄多方出價／放棄條件風險諮詢。",
                "checkMarks": [
                    {"en": "Client acknowledges appraisal & defect exit risks", "zh": "客戶知悉估價與瑕疵退出風險"},
                ],
            },
            {
                "code": "BIA",
                "actionEn": "Reiterate inspection duty; if shortening/waiving, get informed consent in writing.",
                "actionZh": "重申檢查責任；若縮短／放棄，取得書面知情同意。",
                "checkMarks": [
                    {"en": "Prefer shorter period over full waiver when possible", "zh": "可能時優先縮短天數而非完全放棄"},
                ],
            },
            {
                "code": "BRBC",
                "actionEn": "Confirm representation/compensation before writing the aggressive offer.",
                "actionZh": "寫激進出價前確認代表／佣金。",
                "checkMarks": [
                    {"en": "BRBC signed with numeric compensation", "zh": "BRBC 已簽且佣金為數字"},
                ],
            },
            {
                "code": "RPA",
                "actionEn": "If escalation used, attach clear escalation terms; map contingency boxes carefully.",
                "actionZh": "若用自動加價，附清楚條款；仔細核對條件勾選。",
                "checkMarks": [
                    {"en": "Cap / increment / competing-offer definition filled", "zh": "上限／加幅／競爭出價定義已填"},
                    {"en": "Inspection waiver or shortened days match counseling", "zh": "放棄或縮短天數與諮詢一致"},
                ],
            },
            {
                "code": "SMCO",
                "actionEn": "If seller uses SMCO, warn buyer acceptance is not yet final selection.",
                "actionZh": "若賣方用 SMCO，告知買方接受尚非最終選定。",
                "checkMarks": [
                    {"en": "Explain SMCO vs ordinary COP", "zh": "說明 SMCO 與普通 COP 差異"},
                ],
            },
        ],
    },
    {
        "id": "S05",
        "chapterId": "local",
        "titleEn": "HOA reserve crisis and coming special assessment",
        "titleZh": "Condo 儲備金不足且將特別徵收",
        "promptEn": "HOA docs show critically underfunded reserves and a planned special assessment. How should this affect offer strategy and contingency timing?",
        "promptZh": "HOA 文件顯示儲備金嚴重不足且將有特別徵收。這如何影響出價策略與條件時程？",
        "answerEn": "Price in the assessment, confirm buyer/seller responsibility through close, verify lender project eligibility, and keep HOA/document contingency alive until reviewed. Possibly renegotiate credit or cancel if assessment/litigation risk exceeds client tolerance. Do not remove HOA contingencies blindly.",
        "answerZh": "把特別徵收計入成本，確認過戶前後由誰負擔，核對貸方對該社區是否可貸，並在審完前保留 HOA／文件條件。必要時重談折讓，或若風險超過客戶承受則取消。絕不要盲目移除 HOA 條件。",
        "focusTags": ["HOA", "special assessment", "contingency"],
        "formPlaybook": [
            {
                "code": "NSP",
                "actionEn": "If HOA package late, demand seller delivery via NSP.",
                "actionZh": "若 HOA 文件遲到，以 NSP 催賣方交付。",
                "checkMarks": [
                    {"en": "Itemize missing HOA docs", "zh": "列明缺的 HOA 文件"},
                ],
            },
            {
                "code": "RR",
                "actionEn": "Request credit/price adjustment for known special assessment if negotiating.",
                "actionZh": "若談判，就已知特別徵收請求折讓／調價。",
                "checkMarks": [
                    {"en": "State assessment amount and who pays through close", "zh": "載明徵收金額與過戶前後由誰負擔"},
                ],
            },
            {
                "code": "AEA",
                "actionEn": "Lock any agreed credit/price change in an amendment.",
                "actionZh": "合意之折讓／調價以修正書鎖定。",
                "checkMarks": [
                    {"en": "Escrow notified of assessment allocation", "zh": "已通知 Escrow 徵收分擔"},
                ],
            },
            {
                "code": "CR",
                "actionEn": "Do not remove HOA/document contingencies until review complete.",
                "actionZh": "審完前勿移除 HOA／文件條件。",
                "checkMarks": [
                    {"en": "Lender project eligibility checked", "zh": "已核貸方社區可貸性"},
                    {"en": "Client accepts residual assessment risk in writing if proceeding", "zh": "若續行，客戶書面接受剩餘徵收風險"},
                ],
            },
        ],
    },
]

# Append C-layer scenario drills from form guides module
SCENARIOS.extend(EXTRA_SCENARIOS)


def build_payload():
    lessons = []
    for lesson in LESSONS:
        ch = next(c for c in CHAPTERS if c["id"] == lesson["chapterId"])
        lessons.append(
            {
                **lesson,
                "chapter": ch["title"],
                "chapterEn": ch["titleEn"],
                "title": f"{lesson['titleEn']}｜{lesson['titleZh']}",
            }
        )
    scenarios = []
    for sc in SCENARIOS:
        ch = next(c for c in CHAPTERS if c["id"] == sc["chapterId"])
        scenarios.append({**sc, "chapter": ch["title"], "chapterEn": ch["titleEn"]})
    checklists = []
    for cl in CHECKLISTS:
        ch = next(c for c in CHAPTERS if c["id"] == cl["chapterId"])
        checklists.append({**cl, "chapter": ch["title"], "chapterEn": ch["titleEn"]})
    return {
        "titleEn": "CA Residential Field Practice Handbook",
        "titleZh": "加州住宅成交實務手冊",
        "subtitleEn": "Contracts → Closing: bilingual lessons, A+B form guides with fictional samples, checklists, and C-layer scenario playbooks.",
        "subtitleZh": "從合約到交屋：雙語課文、A+B 表單導覽與虛構成交範例、檢查清單、C 層情境表單手冊。",
        "disclaimerEn": "Study aid only—not legal advice and not official C.A.R. form replicas. Verify current forms, MLS rules, and local ordinances.",
        "disclaimerZh": "僅供學習複習，不構成法律意見，亦非 C.A.R. 官方表單複本。請以現行表單、MLS 規則與地方法規為準。",
        "chapters": CHAPTERS,
        "forms": FORMS,
        "lessons": lessons,
        "checklists": checklists,
        "scenarios": scenarios,
    }


def render_md(payload: dict) -> str:
    lines = []
    lines.append(f"# {payload['titleZh']}（{payload['titleEn']}）\n")
    lines.append(f"> **EN:** {payload['subtitleEn']}  ")
    lines.append(f"> **ZH:** {payload['subtitleZh']}  ")
    lines.append(f"> **Disclaimer:** {payload['disclaimerEn']} / {payload['disclaimerZh']}\n")
    lines.append("---\n")
    lines.append("## Form Code Quick Reference｜表單代號速查\n")
    lines.append("| Code | English | 中文 | When / 時機 |")
    lines.append("|---|---|---|---|")
    for f in payload["forms"]:
        lines.append(f"| **{f['code']}** | {f['en']} | {f['zh']} | {f['whenEn']}／{f['whenZh']} |")
    lines.append("\n---\n")

    lines.append("# Form Guides A+B｜表單導覽與填寫範例\n")
    lines.append(
        "> Study layouts only—not official C.A.R. replicas. Fictional deal: "
        "1284 Maple Ave, San Jose · Buyers Alex Chen / Jordan Lee · Seller Maria Santos · "
        "$1,285,000 · Escrow PC-2026-4481.\n"
    )
    for f in payload["forms"]:
        lines.append(f"## {f['code']} — {f['en']}｜{f['zh']}\n")
        if f.get("purposeEn"):
            lines.append(f"**Purpose EN:** {f['purposeEn']}  ")
            lines.append(f"**用途 ZH:** {f.get('purposeZh', '')}\n")
        if f.get("sections"):
            lines.append("### Key Sections｜關鍵欄位區\n")
            for s in f["sections"]:
                lines.append(f"- **{s['nameEn']}／{s['nameZh']}** — EN: {s['tipEn']} ／ ZH: {s['tipZh']}")
            lines.append("")
        if f.get("fillTips"):
            lines.append("### Fill Tips｜填寫要點\n")
            for t in f["fillTips"]:
                lines.append(f"- **EN:** {t['en']}  ")
                lines.append(f"  **ZH:** {t['zh']}")
            lines.append("")
        if f.get("commonMistakes"):
            lines.append("### Common Mistakes｜常見錯誤\n")
            for t in f["commonMistakes"]:
                lines.append(f"- **EN:** {t['en']}  ")
                lines.append(f"  **ZH:** {t['zh']}")
            lines.append("")
        sample = f.get("sample") or {}
        if sample:
            lines.append(f"### Sample Fill B｜虛構成交範例 — {sample.get('titleEn', '')}｜{sample.get('titleZh', '')}\n")
            if sample.get("scenarioEn"):
                lines.append(f"**Scenario EN:** {sample['scenarioEn']}  ")
                lines.append(f"**情境 ZH:** {sample.get('scenarioZh', '')}\n")
            if sample.get("fields"):
                lines.append("| Field｜欄位 | Value EN｜內容 | Value ZH｜中文 |")
                lines.append("|---|---|---|")
                for fld in sample["fields"]:
                    lines.append(
                        f"| {fld['labelEn']}／{fld['labelZh']} | {fld['valueEn']} | {fld.get('valueZh', '')} |"
                    )
                lines.append("")
            if sample.get("checkMarks"):
                lines.append("**Check / 勾選示範：**")
                for m in sample["checkMarks"]:
                    lines.append(f"- [x] **EN:** {m['en']} ／ **ZH:** {m['zh']}")
                lines.append("")
        if f.get("relatedForms"):
            lines.append(f"**Related／相關：** {', '.join(f['relatedForms'])}\n")

    lines.append("---\n")

    by_ch = {}
    for lesson in payload["lessons"]:
        by_ch.setdefault(lesson["chapterId"], []).append(lesson)

    for ch in payload["chapters"]:
        lines.append(f"# {ch['titleEn']}｜{ch['title']}\n")
        for lesson in by_ch.get(ch["id"], []):
            lines.append(f"## {lesson['id']} {lesson['titleEn']}\n")
            lines.append(f"**中文標題：** {lesson['titleZh']}\n")
            lines.append(f"**English summary:** {lesson['summaryEn']}  ")
            lines.append(f"**中文摘要：** {lesson['summaryZh']}\n")
            lines.append("### Key Points｜要點\n")
            for p in lesson["points"]:
                lines.append(f"- **EN:** {p['en']}  ")
                lines.append(f"  **ZH:** {p['zh']}")
            if lesson.get("judgments"):
                lines.append("\n### Field Judgments｜實務判斷\n")
                for j in lesson["judgments"]:
                    lines.append(f"- **EN:** {j['en']}  ")
                    lines.append(f"  **ZH:** {j['zh']}")
            if lesson.get("englishPhrases"):
                lines.append("\n### High-Frequency English｜高頻英文\n")
                for e in lesson["englishPhrases"]:
                    lines.append(f"- `{e['en']}` — {e['zh']}")
            lines.append("")

        ch_checks = [c for c in payload["checklists"] if c["chapterId"] == ch["id"]]
        for cl in ch_checks:
            lines.append(f"### Checklist: {cl['titleEn']}｜{cl['titleZh']}\n")
            for i, item in enumerate(cl["items"], 1):
                lines.append(f"{i}. [ ] **EN:** {item['en']} ／ **ZH:** {item['zh']}")
            lines.append("")

        ch_sc = [s for s in payload["scenarios"] if s["chapterId"] == ch["id"]]
        for sc in ch_sc:
            lines.append(f"### Scenario Drill: {sc['titleEn']}｜{sc['titleZh']}\n")
            lines.append(f"**Prompt EN:** {sc['promptEn']}  ")
            lines.append(f"**題幹 ZH:** {sc['promptZh']}\n")
            lines.append(f"**Model Answer EN:** {sc['answerEn']}  ")
            lines.append(f"**參考答案 ZH:** {sc['answerZh']}\n")
            if sc.get("formPlaybook"):
                lines.append("#### Form Playbook C｜表單操作手冊\n")
                for step in sc["formPlaybook"]:
                    lines.append(f"- **{step['code']}** — EN: {step['actionEn']} ／ ZH: {step['actionZh']}")
                    for m in step.get("checkMarks") or []:
                        lines.append(f"  - [ ] {m['en']}／{m['zh']}")
                lines.append("")

    lines.append("---\n")
    lines.append("## Version\n")
    lines.append(
        "- **v4 A+B+C:** Every form has purpose, key sections, fill tips, common mistakes, "
        "and a fictional filled sample (A+B). Scenarios include Form Playbook steps (C). "
        "Powers the website Field Practice module via `data/field_practice.json`. "
        "Not official C.A.R. form replicas.\n"
    )
    return "\n".join(lines)


def main():
    payload = build_payload()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_MD.write_text(render_md(payload), encoding="utf-8")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(
        f"lessons={len(payload['lessons'])} forms={len(payload['forms'])} "
        f"checklists={len(payload['checklists'])} scenarios={len(payload['scenarios'])}"
    )


if __name__ == "__main__":
    main()
