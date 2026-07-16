# HOUSE FACTORY PLATFORM — MASTER FINANCIAL MODEL
## Reverse-Engineering Report, Build Blueprint & Validation Memorandum

**v1.0 · July 2026 · Confidential — Draft for Management Review**
Deliverables: `HFP_Master_Model.xlsx` (22-tab integrated pro forma, fully formula-driven) + `build_hfp_model.py` (deterministic generator — the model's audit trail) + this memorandum.

---

# PART I — SOURCE FILE REVIEW (Step 1)

## 1.1 What each source actually is

| # | File | What it is | What it is NOT |
|---|------|-----------|----------------|
| S1 | `House_Factory_Platform.xlsx` | **Entity/org diagram** (2 sheets, no calculations): Platform LLC over 5 regional QSBS C-corps (Central/East/West/Southwest/Southeast); management fee + ownership arrows; per-region staffing (GM, Plant/Production/Quality Mgr ×2 factories); "Second Factory Funded by Cash Flow of first one"; staggered 10/9/8/7/6-yr holds; fees-to-capital-raise note; Sheet2 sketches a separate Development Fund fed by "Fees"/"HF Plat Dev". | A financial model — it contains zero numbers. |
| S2 | `07.08.26_19_Regional_Factory_Model.xlsx` (v2.0, 14 sheets) | **Factory-strategy & fund-structure workbook**: 5 regions (TX/SC/SE/MW/SW), 17 factories 2026-2036, per-factory capacity (anchors 700 u/yr 1-shift, others 500; 2-shift 700-1,400), regional fund sizes ($30/12/30/30/25M = $127M), LP terms (90/10 LP/GP, 8% pref, 20% promote w/ catch-up, 80/20 residual), capital flywheel (raise once, subsequent factories from retained CF + debt), factory EBITDA ramp **$2M→$6M→$12M+ (Y1/Y2/Y3+)**, OKC = existing plant + **$10M modernization**, §1202 exit math at **Y5 8× / Y10 10×** with 23.8% federal tax saved, LP share heuristic = 65% of fund value. | An operating model — no P&L below EBITDA, no COGS build, no statements. |
| S3 | `07.08.26_21_Dev_Model_25_Markets.xlsx` (8 sheets, live formulas) | **Downstream build-to-rent development-fund model**: 25 markets × 300-unit rental communities buying **HF kits at $54,000 (+10% premium markets)**; rents ($1,650–2,400 2BR), 70/30 2BR/3BR mix, land/site ($65-80K/u)/soft costs ($70-95K/u); 65% LTC construction debt @7.5%; perm loan 7%/30yr/1.25 DSCR/75% LTV; 5.75-6.5% exit caps; Y3 refi recap; 5-yr hold; same 90/10 + 8% pref + 20% promote waterfall; **NHF GP split 40/40/20 HF/USEDC/NewCo**. | The factory business. It is the *customer* of the factory. Management explicitly deferred it ("development funds — leave it blank for now"). |
| S4 | `HFP_Business_Model_Report.docx` | **The governing normalization document**: 24 sections + 4 tables resolving conflicts: 60/40 parent split (fixes the "16%" mis-transcription); $25-30M standard raise; 90/10; 7% fee; lease-only; 2 factories/region base case; OKC = relaunch w/ asset contribution; price-scope bridge ($85-175K factory-wholesale vs $54-59.4K kit vs ~$95-99K public-comp ASP); management-transition rule; 15 management questions, 10 model changes, 10 plan changes, 30-day workplan. | Final — it deliberately leaves 15 open items for management. |
| S5 | Meeting transcript (July 2026) | **Management intent**: OKC first and special; one raise/region; retain earnings, no dividends; Factory 2 "two or three years later, depending on when the cash flow shows it"; one GM per region; lease-only ("make sure we're not using both" lease AND P&I); build the business before the investment ("if we self-funded the entire $150 million, how would it work?"); unitize to per-share later; waterfall (20%) last; ~10-yr consolidated exit (PE recap or IPO). | — |

## 1.2 Conflicts, duplicates and gaps found (and how each was resolved)

| # | Topic | S1 | S2 | S3 | S4/S5 | Resolution (source of truth) |
|---|-------|----|----|----|-------|------------------------------|
| 1 | Region map | Central/E/W/SW/SE | TX/SC/SE/MW/SW, TX anchor first | 4-factory roadmap (OKC first) | 5 regions, OKC (Central) first; final names open | **S4/S5**: 5 regions, OKC first 2026. Names beyond Central/Texas flagged `<<Management Input Required>>` |
| 2 | Factory count | 2/region (10) | 17 at maturity | 4 factories | 2/region base case; more = upside addendum | **S4/S5**: 10 factories. S2's 17-factory map kept as upside addendum |
| 3 | First factory | — | TX-DFW 2026 (OKC = #5) | OKC existing | OKC 2026 | **S4/S5**: OKC is Factory #1 |
| 4 | Capitalization | — | $127M platform (30/12/30/30/25) | $606M dev equity (different business) | $25-30M/region, one raise | **S4/S5**: $30M standard (top of range — required by liquidity validation), inflation-indexed at launch per S4 §10. OKC special |
| 5 | Real estate | — | Buys land+building ("$28M build: land + building + equipment") | Buys land | **Lease-only** | **S4/S5** override: lease-only; all land/building purchase and mortgage P&I stripped |
| 6 | Debt | — | "Retained CF + debt" flywheel | 65% LTC + perm debt | Fully equity; no P&I | **S4/S5**: zero-debt base case. Debt Schedule kept dormant (S2's option preserved as a lever) |
| 7 | Price driver | — | — | Kit $54-59.4K | ASP $85K/$175K factory-wholesale home-only | **S4/S5**: $85K/$175K. Kit price is a *component* price of a different scope — never mixed (S4 price-scope bridge) |
| 8 | Product mix | — | — | 70/30 2BR/3BR (rental) | not specified | **Gap**: 70/30 used as analog placeholder — `<<Management Input Required>>` |
| 9 | Fee | fee arrow, no % | — | — | 7% of regional revenue | **S5/S4**: 7%, built as a lever |
| 10 | Ownership | arrows only | LP 90 / GP 10 | LP 90 / GP 10 | investors ~90 / platform ~10 (no cash) | Consistent across sources — CONFIRMED |
| 11 | Parent split | Lance/T&W/USPD boxes | GP = "40/40/20 HF/USEDC/NewCo" | NHF 40/40/20 | **60% Lance / 40% USPD**; Tommy/Wes 0% | **S4** (explicitly resolves transcript's "16%"). S2/S3's 40/40/20 relates to a different GP entity (NHF) — flagged for counsel |
| 12 | Waterfall | — | 8% pref, 20% promote, catch-up, 80/20; but LP share hard-coded 65% | same terms, computed properly | promote "built at the end" | **S2 terms** + true tiered computation (S2's flat 65% shown as disclosed cross-check) |
| 13 | Exit | staggered holds 6-10y | Y5 8× / Y10 10× per region | Y5 cap-rate sale | one big ~Y10 consolidated transaction | **S4/S5** structure (single roll-up) with **S2 multiples** (10× base, 8× Y5 alt) |
| 14 | Factory EBITDA | — | $12M steady state (500 u/yr) | — | prove EBITDA first | **S2 $12M anchor** used to calibrate the missing COGS stack (see 1.3) |
| 15 | OKC capitalization | — | $12M raise incl $10M modernization | — | asset contribution + cash; appraisal required | **S4 structure** + S2's $10M modernization; values flagged MIR |

**Duplicated assumptions** (now live in exactly one cell each): 90/10 split (S2, S3, S4), 8% pref & 20% promote (S2, S3), 500 u/yr capacity (S2 ×3 sheets), OKC-first sequencing (S3 cover vs S2 timeline — contradictory *between* files, identical *within* the master).

## 1.3 The critical gap

**The founders' factory pro forma (S4 Appendix C — cost/sq-ft, fixed vs variable detail, labor build) was NOT among the provided files.** The transcript references it ("Wes has done all the work… cost per square foot… all the fixed and variable cost"); the Word report lists it as required material. Consequence: the entire COGS stack is `<<Management Input Required>>`. Rather than leaving the model dead, placeholders were **calibrated so a mature standard factory produces $12.035M pre-fee EBITDA (2026$) vs S2's ~$12M anchor** — solving `variable% = 0.985 − (12.0M + fixed costs)/factory revenue → ≈70%` (materials 47%, direct labor 15%, freight 4%, other variable 4%; fixed OH $2.0M + lease $1.2M per factory). Every one of these cells is orange-flagged and swaps out 1-for-1 when the real pro forma arrives.

---

# PART II — MASTER WORKBOOK ARCHITECTURE (Step 2)

## 2.1 Tab map and dependency flow

```
Cover & Sources ─┐            (documentation layer)
Executive Dashboard ◄────────────────────────────────────────────┐
                                                                 │
Global Assumptions (every named input)                           │
      │                                                          │
      ▼                                                          │
Factory Rollout (10 factories; open years = only other input)    │
      │                                                          │
      ▼                                                          │
Production Model ──► Revenue Model ──► COGS ──► SG&A             │
      │                   │              │        │              │
      │                   ▼              ▼        ▼              │
      │            Platform Revenue   Working Capital            │
      │                   │              │                       │
      ▼                   │        CapEx ──► Debt (dormant)      │
      │                   │           │  └──► Depreciation       │
      ▼                   ▼           ▼            │             │
Regional Rollup (5 independent C-corp engines) ◄───┘             │
      │                   │                                      │
      ▼                   ▼                                      │
OKC Factory Model   Platform Rollup                              │
Standard Regional         │                                      │
      │                   ▼                                      │
      └──► Income Statement ──► Cash Flow ──► Balance Sheet      │
                          │                                      │
                          ▼                                      │
                     Exit Model ──► Sensitivity Analysis ────────┘
```

Build order follows management's rule: **factory economics → regional economics → platform economics → consolidated statements → investor returns → exit.**

## 2.2 Sheet-by-sheet specification & formula logic

**Conventions:** years 2026–2036 in columns C:M on every grid tab; **inputs exist only on Global Assumptions (named ranges) + Factory Rollout column E (open years) + Debt draws + template F2 offset**; blue font = input, gold = sourced, orange = `<<Management Input Required>>`; no circular references anywhere; `t = year − Model_Start` powers all inflation.

| Tab | Purpose | Core formula logic |
|-----|---------|--------------------|
| **1. Executive Dashboard** | IC-ready summary: investment summary (capital, EV, equity value, proceeds, MOIC, IRR, NPV, §1202 savings, platform value w/ 60/40 split), 14 KPI rows × 11 yrs, rollout timeline (● grid), 14 live integrity checks, 3 charts + tornado on Tab 21 | All display-only references |
| **2. Global Assumptions** | 60+ named drivers in 11 sections, each with value, unit, **status (CONFIRMED / DERIVED / MIR)** and source citation | e.g. `Blend_ASP0 = Mix_Single*ASP_Single + (1−Mix_Single)*ASP_3BR`; `Tax_Rate = Fed_Tax + State_Tax`; `OKC_Plat_Own = OKC_Asset_Val / OKC_TotCap` |
| **3. Factory Rollout** | 10 factories: region, open year (INPUT), capacity, capital, lease, equipment, FTEs, status, funding source; network counts; transition trigger | `Operational = SUMPRODUCT((OpenYears ≤ yr))`; `Trans_Year = INDEX(years, COUNTIF(counts,"<2")+1)` — first year network ≥ 2 factories |
| **4. Production Model** | Homes by factory/total/cumulative, capacity & utilization, sq ft, monthly (36-mo) + quarterly ramp views | `Units = IF(yr<open,0, Cap×Util×IF(age=1, Ramp_Y1|OKC_Ramp_Y1, IF(age=2, Ramp_Y2, Ramp_Y3)))`; monthly: linear ramp to full over `Ramp_Months`, with a reconciliation cell vs the annual ramp |
| **5. Revenue Model** | Revenue by factory → region → total; management fee; **intercompany elimination**; product-type split w/ tie-out | `Rev_f = Units_f × Blend_ASP0×(1+Infl_ASP)^t`; consolidated revenue = external regional revenue (fee eliminates) |
| **6. COGS** | By region and by component (materials/labor/freight/other variable; fixed OH; leases); GP & GM% | `COGS_r = Rev_r×Var_Pct + OpFactories_r×(Fixed_OH+Lease_Cost)×(1+Infl_Gen)^t`; component detail ties to regional total (check = 0) |
| **7. SG&A** | Regional SG&A (fixed + GM + S&M% + pre-opening) and platform overhead — with the **one-time management transition** | Region 1 staff cost = `IF(yr < Trans_Year, CEO+COO, GM)`; platform payroll = `IF(yr ≥ Trans_Year, Plat_Payroll×(1+Infl_Wage)^t, 0)` — salaries can never double-count by construction |
| **8. Platform Revenue** | Fee by region; other revenue (MIR, $0); fee per factory; **non-cash equity accrual memo** showing compounding | `Fee_r = MgmtFee_Pct × Rev_r`; accrual = `OKC_Plat_Own×NI_R1 + Plat_Own×ΣNI_R2..5` |
| **9. Working Capital** | AR/Inv/AP → NWC → ΔNWC, consolidated + per region | `AR=DSO/365×Rev; Inv=DIO/365×COGS; AP=DPO/365×COGS`; regional Δ feeds regional FCF; Σ regional = consolidated (check = 0) |
| **10. CapEx** | Growth (equipment+leasehold at each opening; OKC $10M modernization), maintenance (% rev), **non-cash OKC contribution**, equipment/technology split, per-region PP&E additions | `Growth_r = (Equip+Leasehold)×(1+Infl_Gen)^t` at each open year |
| **11. Debt Schedule** | **Dormant** — fully equity-funded base case; draws input row, principal, interest at avg balance | Begin/draws/repay/end + interest; all zero until draws entered |
| **12. Depreciation** | **100% derived from CapEx** — no manual dep inputs | `Dep_r = SUMPRODUCT(Additions_r × (yr_placed ≤ yr) × (yr − yr_placed < Life)) / Life` (SL, per region, includes contributed assets) |
| **13. Income Statement** | Consolidated annual 2026-2036 w/ elimination; margins; EBITDA tie-out check | Tax line = Σ regional cash taxes (platform is a pass-through LLC — flagged); EBITDA identity check vs Σ region + platform = 0 |
| **14. Cash Flow** | Indirect method: CFO (NI+D&A−ΔNWC), CFI (capex), CFF (raises; dividends locked at 0 per QSBS strategy); non-cash contribution disclosed | Ending cash ties to Σ entity cash (check = 0) |
| **15. Balance Sheet** | Cash/AR/Inv/PP&E vs AP/debt/PIC/RE | PIC = cumulative raises + contributed assets; RE = cumulative NI (no dividends). **Balances automatically — check row = 0 all years** |
| **16. OKC Factory Model** | Special launch: capitalization (assets + cash → pro-rata ownership), $10M modernization, employee-transition table, live P&L pull, 5 open items | Ownership derives from contribution values — updates itself when the appraisal lands |
| **17. Standard Regional Model** | The reusable archetype in relative years & 2026$: one raise, 90/10, 7% fee, F2 at year `F2_Offset` funded by retained earnings, full P&L→FCF→cash, **months 1-24 operating view**, self-funding checks, $12M-anchor calibration cell | Same engine as rollup but timeline-independent — the "does one region work?" proof |
| **18. Regional Rollup** | **The consolidation engine**: 5 identical blocks (Rev→COGS→SG&A→fee→EBITDA→D&A→EBT→cumEBT→tax→NI→raise→capex→ΔNWC→FCF→cash→homes→factories) + totals + liquidity checks | Tax with **closed-form NOL carryforward**: `Tax_t = Rate × (MAX(0,cumEBT_t) − MAX(0,cumEBT_{t−1}))` — full loss carryforward, no circularity, per C-corp. **No cross-region cash anywhere (QSBS independence)** |
| **19. Platform Rollup** | Platform LLC standalone (fees − payroll − opex = EBITDA; pass-through) + consolidated network summary | Platform carries no factory capex/debt — capital-light by construction |
| **20. Exit Model** | Y10 base (10×) and Y5 alternative (8×) per region: EBITDA→EV→equity; **true LPA waterfall** (capital → 8% compounded pref → GP catch-up → 80/20 residual); investor MOIC/IRR/§1202; platform value (equity + promotes + capitalized fee stream + cash) split 60/40; aggregate IRR (`IRR()` over flow vector), investor NPV, project NPV | `Catch-up = MIN(MAX(0, profit−pref), pref×20%/80%)`; `LP = MIN(gross, C + MIN(profit⁺, pref) + 80%×residual)`; robust to all profit regimes |
| **21. Sensitivity Analysis** | 40+ live scenario rows through a mini-engine mirroring the full chain (revenue→EBITDA→EV→waterfall→MOIC/IRR): ASP ±20%, materials ±5pts, labor ±4pts, utilization 80-120%, fee 5-9%, platform ownership 5-15%, exit multiple 6-14×, raise size, inflation, Y5-vs-Y10, ramp; **tornado table + bar chart** | Engine base row reproduces the main model's mature-region EBITDA to the dollar (validated) |

---

# PART III — MISSING ASSUMPTIONS (Step 3)

Every item below is orange-flagged `<<Management Input Required>>` in the workbook with a placeholder so the model still calculates. ⚑ = blocking for investor distribution.

| # | Missing item | Placeholder | Why needed / impact | Where it should come from |
|---|--------------|-------------|---------------------|---------------------------|
| ⚑1 | Founders' factory pro forma: materials/labor/freight %, fixed overhead | 47%/15%/4%/4% + $2.0M (calibrated to S2 $12M EBITDA anchor) | Drives gross margin, every EBITDA figure, exit value ~1:1 | S4 Appendix C (Wes's factory workbook); Friday partners meeting per transcript |
| ⚑2 | OKC contributed-asset value & final ownership split | $8M assets / $20M cash; ownership pro-rata (28.6%/71.4%) | Sets OKC investor returns & platform stake; QSBS basis | Independent appraisal (S4 §22.A.6) |
| ⚑3 | Product mix & price-scope bridge | 70/30 single/3BR (Dev-Model analog); $85K/$175K confirmed factory-wholesale | Blended ASP $112K drives all revenue; a 60/40 mix ⇒ +$9K ASP ⇒ ~+8% revenue | Management + founders' price list |
| 4 | Split of the raise (equipment / leasehold / pre-opening / WC) | $12M / $5M / $2M / balance | Sizes depreciation, PP&E, startup expense | Founders' build budget |
| 5 | Facility lease terms | $1.2M/yr/factory, 10-yr | Fixed-cost base; lease-only policy needs real quotes | Broker LOIs per market |
| 6 | Working capital days | DSO 15 / DIO 45 / DPO 30 | Cash trough depth at ramp; F2 timing feasibility | Founders' historical OKC data |
| 7 | Maintenance capex, asset lives | 1.5% of revenue; 10-yr SL | FCF and steady-state D&A | Equipment vendor schedules |
| 8 | State tax by region | 4% blended | After-tax retention → F2 self-funding speed | Tax counsel per final region map |
| 9 | Inflation set (general/wage/ASP) | 2.5% / 3.0% / 2.0% | Later-launch economics (S4 §10 requires) | Management economics view |
| 10 | Discount rate | 12% | NPV only (transcript: hurdle "well above" pref) | IC policy |
| 11 | Region 2/4/5 names, territories, dates | Placeholder rows, input years | Final region map = S4 open item #2 | Management |
| 12 | Salaries (exec suite, GM, platform opex components) | $400K/300K/350K/250K/200K; GM $250K; opex $1.0M | Platform EBITDA; transition mechanics | Comp benchmarking |
| 13 | Platform fee-stream exit multiple | 10× (= regional multiple) | Platform valuation at exit; capital-light streams often price higher | Banker guidance at exit |
| 14 | Management incentive pool (Tommy/Wes) | 0% (S4 Table 2) | Dilution of parent economics | Management decision (S4 §22.A.11) |
| 15 | Freight/set-install perimeter | Freight inside regional COGS | QSBS 80% qualified-use test; margin geography | Tax counsel (S4 §22.A.9) |

---

# PART IV — NORMALIZED ASSUMPTION SET (Step 4)

The single recommended value for every contested category (full conflict log in Part I.2):

| Category | Standardized value | Why |
|----------|-------------------|-----|
| Regions / factories | 5 regions × 2 factories | Latest management direction (S5/S4); S2's 17 = addendum upside |
| Sequencing | OKC 2026; new region each 1-2 yrs; F2 at +3 yrs | Transcript "two **or three** years"; +2 fails the cash test (validated) |
| Standard raise | **$30M, inflation-indexed at launch** | Top of S4's $25-30M; $25M breaches min-cash before F2 self-funds; indexation required by S4 §10 and fixes later regions' inflated capex |
| Ownership | 90% investors / 10% platform (no cash); OKC negotiated | All sources agree; OKC per appraisal |
| Fee | 7% of regional revenue (lever) | S5/S4; sensitivity spans 5-9% |
| Facilities | Lease only; zero mortgage debt | S5 explicit instruction; removes S2/S3 double-count risk (lease AND P&I) |
| Capacity / ramp | 500 u/yr 1-shift; 50%/80%/100%; OKC Y1 60% | S2 capacity; ramp reproduces S2's $2M/$6M/$12M EBITDA path |
| Pricing | $85K / $175K factory-wholesale home-only, +2%/yr | S5/S4; kit and rent prices quarantined to the (deferred) dev-fund addendum |
| Waterfall | Capital → 8% compounded pref → 100% catch-up → 80/20 | S2 fund terms, computed as a true waterfall (not the 65% heuristic) |
| Exit | Y10 (2036) consolidated @ 10×; Y5 @ 8× alternative | S2 multiples inside S4/S5's single-transaction structure |
| Tax | 21% federal + 4% state placeholder, NOL c/f, no dividends | Statutory + QSBS retention strategy |
| Parent | 60% Lance / 40% USPD | S4 resolves the transcript ambiguity in writing |

---

# PART V — VALIDATION RESULTS (Step 5)

Executed mechanically: the workbook was recalculated headlessly (LibreOffice Calc) and every check read back. **All 14 checks PASS:**

| Check | Result |
|-------|--------|
| Balance sheet balances (Σ\|A−L−E\|, 11 yrs) | **0** |
| Cash flow ending cash = Σ entity cash | **0** |
| COGS component detail = Σ regional COGS | **0** |
| IS EBITDA = Σ regional EBITDA + platform EBITDA (fee elimination proof) | **0** |
| Product-type revenue split = total revenue | **0** |
| Σ regional ΔNWC = consolidated ΔNWC | **0** (float ε < $1) |
| Region 1-5 single-raise sufficiency (min cash ≥ 0, no second raise) | **PASS ×5** |
| Template Factory-2 self-funded from retained earnings | **PASS** (min cash +$3.9M) |
| First positive-FCF year | **Year 2** — matches S4/S5 "cash-positive around Year 2" |
| Steady per-factory pre-fee EBITDA (2026$) vs S2 ~$12M anchor | **$12.035M** |
| Sensitivity engine base vs main model mature-region EBITDA | Ties to the dollar ($23.38M nominal 2036) |
| Investor ownership / platform ownership / fee | Single named cells; ownership sums = 100% by construction; OKC derives from contribution values |
| Factory timing | Rollout inputs propagate through every schedule (spot-shifted in testing) |
| Exit calc | Waterfall reconciles: LP + GP promote + platform equity = equity value ×(0.9+0.1) exactly |

**Base-case headline outputs (placeholder-dependent):** 2036 revenue $683M, EBITDA $138M (20.1%), GM 24.0%; 5,000 homes/yr, 33,050 cumulative; investor capital $149M → proceeds $696M (**4.66× / 22.2% IRR**, Y5 alt ~3.7-4.3× / 30-34% IRR per region); EV at exit $964M; platform value **$917M** (60% Lance $550M / 40% USPD $367M); §1202 federal tax saved ~$131M pre-cap.

**Independent convergence checks vs S2** (built bottom-up, not copied): total capital $149M vs S2 $127M platform raise; S2 Y10 LP 10.3×/26.3% IRR vs our 4.66×/22.2% — theirs is higher because it (a) valued LP share at a flat 65% with no waterfall, (b) had 17 factories, and (c) ignored SG&A/fee drag below factory EBITDA. The master model is deliberately the more conservative, defensible number.

**Material inconsistencies flagged during validation (and resolved):**
1. **$25M raise + F2 at +2 yrs is infeasible** — regional cash dips $2.6-8.8M negative. Fixed with $30M indexed raise + F2 at +3 yrs. This is a genuine IC finding: the flywheel works, but only at the top of management's stated capitalization range.
2. OKC cash of $12M was insufficient against the $10M modernization + ramp; placeholder reset to $20M cash + $8M assets (still MIR pending appraisal).
3. S2's "LP share = 65%" heuristic vs true waterfall: variance disclosed line-by-line on the Exit tab.
4. S2 buys land/buildings while S4/S5 mandate leases — S2's $28M "build" cost is NOT comparable to the master model's $19M equipment+leasehold+startup; documented, not blended.

---

# PART VI — OPTIMIZATION & INSTITUTIONAL RECOMMENDATIONS (Step 6)

**Already implemented to bank standard:** single input sheet with named ranges + status/source columns; input color code; zero hardcodes downstream; no circularity (closed-form NOL tax; interest on dormant debt uses average balance but base case is zero-debt); intercompany elimination; per-entity tax; automatic depreciation from capex; live error-check block on the dashboard; deterministic generator script (perfect audit trail — the entire model rebuilds from `python3 build_hfp_model.py`); monthly/quarterly/annual production granularity; archetype tab proving the unit of replication.

**Recommended next upgrades (priority order):**
1. **Scenario manager** — add a scenario column block (Base / Management / Downside) on Global Assumptions with `CHOOSE()` switching; the named-range architecture makes this a 1-day retrofit.
2. **Per-share unitization** (transcript requirement): add shares-outstanding per region and divide the Exit tab through — trivial once share counts exist.
3. **Front-end fees & waterfall to the fund vehicles** ("like Hamburg/Springfield"): model placement fees/load between investor cash and region equity when management specifies them (S1 notes "Fees to Capital Raise").
4. **Development-fund addendum**: S3 is already a working model of the demand channel; attach as the "first buyer" pipeline (Omaha Port Authority / Habitat conversations) — keep it in a separate vehicle to protect the QSBS 80% test.
5. **Quarterly consolidated statements** for the first 8 quarters once OKC opening data exists.
6. **Two-shift expansion case**: S2 gives 2-shift capacities (700-1,400); model as `Util_Steady > 1` scenario before committing Factory-2 capital — it may dominate building F2 in some regions.
7. Excel-native polish if desired: convert integrity checks to conditional-format traffic lights, add a true DATA TABLE for two-way ASP × multiple sensitivity (requires Excel, not scriptable), print ranges.

**Key risks for the IC memo** (model-evidenced): (1) sales pipeline is the binding constraint, not capacity — management's own view; utilization sensitivity shows MOIC falling ~1.6× per 10 pts of utilization; (2) COGS stack is unverified until the founders' pro forma arrives — ±5 pts of materials moves investor MOIC ~±1.3×; (3) QSBS execution risk — regional independence, 80% qualified-use, redemption limits, and the consolidated exit must all be engineered in advance (S4 §19); (4) later regions launch into inflated cost bases with fixed nominal pricing power assumptions; (5) Cavco/American Homestar pushes an incumbent directly into the OKC/Texas footprint; (6) the platform's $917M valuation is ~47% fee-stream capitalization — the 7% fee must survive arm's-length scrutiny (S4's commercial-reasonableness defense).

---

# PART VII — HOW TO FINISH THE BUILD (the 30-day path)

1. **Week 1** — obtain founders' factory pro forma; overwrite orange COGS cells; re-read the $12M-anchor check cell (Standard Regional Model C36) — it should now be diagnostic, not calibrated.
2. **Week 1** — OKC appraisal values into GA §11; ownership auto-derives; hand to counsel with the OKC tab's open-items list.
3. **Week 2** — confirm region map (rename Rollout rows, set open years); confirm mix/price scope; set lease quotes.
4. **Week 3** — management review of the Dashboard + sensitivity tornado; lock Base scenario; add scenario manager + per-share unitization.
5. **Week 4** — layer front-end fees and final exit waterfall; produce investor package (this memorandum Parts II/IV/V become the model appendix).

*Regenerate the workbook at any time with `python3 hfp_model/build_hfp_model.py` — every change is code-reviewed, diff-able, and reproducible.*
