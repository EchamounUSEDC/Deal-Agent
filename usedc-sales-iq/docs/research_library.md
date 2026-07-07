# Sales School Research Library (source document)

> Uploaded reference for the AI coaching engine. The machine-readable
> encoding lives in `utils/research.py`; this file preserves the full
> source text (citations, tiers, contested findings) for provenance and
> future retrieval-grounding in live mode.

Part A — The Psychology of First Conversations

A.1 Thin-Slicing: How Fast Credibility Forms

Authors: Nalini Ambady & Robert Rosenthal

Organization: Originating research at Harvard University; foundational study published in Journal of Personality and Social Psychology (1993); subsequent coverage in American Psychologist and APA's own Monitor on Psychology

Link: https://www.apa.org/monitor/mar05/slices ; https://www.harvardmagazine.com/2001/07/snap-judgments-work-html

Credibility: Tier 1 — peer-reviewed, APA-published, one of the most replicated findings in social psychology.

Key findings: Ambady and Rosenthal found that silent video clips as short as two, five, or ten seconds produced viewer judgments that correlated strongly (r = .76) with evaluations formed over an entire semester of interaction — and five-second clips were shown to be just as predictively accurate as five-minute clips, with the very first moments of an interaction carrying the most weight. This effect has since been replicated across strangers' self-ratings, salespeople and trust, interviewers and job applicants, and supervisor-student relationships.

Important nuance (contested/limits of the finding): A Columbia Business School methodological review cautions that while thin-slice judgments are statistically significant predictors, the magnitude of that predictive accuracy is often modest rather than large, and sweeping claims of "accuracy" can be misleading if the difference between statistical significance and effect size isn't kept clear. Recommend your model documentation state the finding precisely: early impressions are real, measurable, and hard to reverse — but not infallible or all-determining.

Practical application: This is the strongest evidence base for the "capture attention in the first 15–30 seconds" requirement in your brief. It also implies coaching should weight the opening segment of a call disproportionately in scoring, since it has outsized influence on the advisor's downstream judgment of competence and trustworthiness — independent of what's said later.

AI coaching metrics:

Opening-segment composite score: pace stability, absence of filler words, and clarity of self-introduction, scored specifically on the first 10–15 seconds of audio (not blended into the whole-call average).

Recovery tracking: since first impressions are hard but not impossible to reverse, flag calls with a poor opening but strong recovery separately from calls with a poor opening and no recovery — useful for coaching (recovery skill is a distinct, trainable behavior).

A.2 Vocal/Conversational Dynamics Predicting Outcomes

(Full citation detail in Phase 1, Section 5 — MIT Pentland/Curhan "Honest Signals" research; Journal of Applied Psychology, 2007. Referenced here for the cold-call application.)

Practical application to cold calling specifically: Nonverbal conversational dynamics — activity level, engagement, prosodic emphasis, and vocal mirroring — predicted 30% of outcome variance in a negotiation context independent of literal content. For a cold call, this supports scoring energy/engagement and mirroring (matching the advisor's pace and tone once they start speaking) as legitimate, evidence-linked "credibility fast" behaviors — separate from, and additive to, the content of the pitch.

A.3 Gatekeeper & Voicemail Conversations — An Honest Evidence Assessment

This is the one area of your brief where high-quality Tier 1 academic research is genuinely thin. What exists is mostly sales-industry operational data (Tier 2/3) rather than peer-reviewed study. Rather than dress this up as more rigorous than it is, here is what's defensible:

Voicemail callback/engagement data (Tier 2 — large-sample proprietary analytics, methodologically transparent, not peer-reviewed):

Gong Labs' analysis of 300+ million cold calls found leaving a voicemail reduces the future phone connect rate by roughly 28%, but more than doubles email reply rates — from about 2.73% to 5.87% — and using three or more voicemails per prospect actually drops reply rates below the no-voicemail baseline. Consistent finding across multiple secondary sources citing this dataset: one early voicemail plus one later "breakup" voicemail captures most of the benefit, with diminishing and even negative returns beyond that.

Pew Research Center (Tier 1, legitimate survey research organization) data, cited via industry sources: 81% of calls from unknown numbers go to voicemail, and 67% of recipients check voicemail from an unknown number — meaning voicemail is heard even when not returned, supporting its role as a "primer" rather than a direct conversion channel.

Practical application: Reframe voicemail success metrics away from "did they call back" (a low-base-rate, weak signal) toward "did engagement increase on the next touch" (email open/reply, next-call pickup) — this is both the better-supported metric and consistent with your relationship-first, multi-touch philosophy.

Gatekeeper conversation research: No Tier 1 peer-reviewed research was found specific to this topic; the available material is entirely sales-operations blog content (Tier 3). The consistent theme across sources — gatekeepers form a judgment about whether a caller is worth their principal's time within roughly the first fifteen seconds, and respond better to callers who treat them as informed, valuable contacts rather than obstacles — is plausible and consistent with the Ambady/Rosenthal thin-slicing research above (A.1), but should be documented in your model card as an inference from adjacent research, not a directly studied claim. Recommend this category be scored with lower confidence weighting than categories with direct peer-reviewed backing, and flagged for periodic re-review as better data becomes available.

AI coaching metrics for this section:

Voicemail-to-next-touch engagement rate (not raw callback rate) as the primary success metric.

Gatekeeper respect language: does the rep use the gatekeeper's name, thank them, and avoid pressuring or deceptive framing? (directly measurable from transcript, consistent with the one theme that recurs across all available sources)

Part B — Advisor Pain-Point Playbooks

Each pain point follows your requested structure: why it matters, affected client profiles, common advisor concerns, discovery questions, educational framing, common wholesaler mistakes, engagement/pivot indicators, and the research backing.

B.1 Concentrated Stock Positions

Why it matters: Concentrated positions — commonly defined as a single security representing 30% or more of portfolio value — create tax inefficiency, elevated volatility, firm-level risk exposure, and potential for poor client outcomes if left unmanaged, whether the position originates from a business sale, executive compensation, or inheritance.

Client profiles affected: Executives with equity compensation, founders/business sellers, inheritors of legacy single-stock positions, long-tenured employees of publicly traded companies.

Key psychological insight for wholesalers (this is the important research-backed nuance): Envestnet's research identifies a "concentration paradox": for many high-net-worth clients, concentration is precisely what built the wealth in the first place, so what advisors are trained to flag as risk is often what the client experiences as validation of their own judgment and success — meaning clients often resist diversification even when the statistical case is clear.

Discovery questions that naturally uncover the issue: "Do you have any clients where more than 20–25% of their net worth sits in a single name?" / "How did that position build up — compensation, a sale, or inheritance?" / "Has anyone run a downside scenario with them — what a 30–50% drawdown in that one name would mean for their broader goals?"

Educational ways to introduce the topic: Lead with the asymmetry of outcomes research rather than a generic "diversify" message — individual stocks experience significantly higher volatility and deeper drawdowns than diversified indices, with some individual stocks declining 50% or more during market cycles — and connect this to the specific mechanics (exchange funds, direct indexing, structured/staged sales, charitable strategies) rather than a single generic solution, since best practice is running an actual scenario model with the client showing what a 20–30% decline in that one name would mean for their stated goals.

Common wholesaler mistakes: Treating this as purely an investment/tax problem and skipping the psychological one (the "concentration paradox" above); leading with a single product (e.g., only pitching an exchange fund) instead of presenting it as a menu of tax-aware options matched to the client's specific restrictions and goals.

Engagement indicators: Advisor volunteers a specific client name/situation unprompted; asks about tax mechanics of a specific strategy (exchange funds, direct indexing) rather than staying abstract.

Pivot indicators: Advisor states they've already run this analysis and has a plan in place — shift to a different pain point rather than re-covering ground.

Follow-up questions: "Would it help to have a scenario model ready before your next meeting with that client?" — ties directly back to the discovery-question research from Phase 1 (Rackham's need-payoff questions).

B.2 Roth Conversion Planning

Why it matters: For many retirees, the window between retirement and age 73 (when RMDs begin) is often the single most valuable tax-planning opportunity they will ever have, but sizing and timing it correctly is genuinely complex.

Client profiles affected: Recent or near-term retirees in the "trough years" before RMDs; clients with year-to-year income volatility (business owners, those with variable comp); high earners anticipating higher future tax brackets or concerned about legacy/estate tax exposure.

Research backing (Tier 1 — peer-reviewed practitioner-academic journal): Research by McQuarrie and DiLellio published in the Journal of Financial Planning found that converting earlier in life produces substantially larger after-tax wealth than converting later, and identified two "robust" conversion windows: converting up to the top of the current 12% bracket, and converting up to the 24% bracket specifically before age 63 to avoid Medicare IRMAA surcharges.

Contested/nuanced point (report honestly, per your brief's instruction): A separate peer-reviewed analysis by Edward McQuarrie (professor emeritus, Santa Clara University), published through the Financial Planning Association, frames RMD-reducing Roth conversions as a long-duration financial wager rather than a guaranteed win — a large tax payment today is traded for a stream of future tax savings that may not fully pay off for 20–30 years, so clients need to be comfortable with a slow, uncertain payoff that may be modest in present-value terms. This is an important corrective to any pitch that frames Roth conversions as an unambiguous, always-correct move — supporting your "conservative expectations" philosophy directly.

Discovery questions: "Do you have clients in a gap year between retiring and RMDs starting?" / "Are you currently modeling conversions bracket-by-bracket, or is it more of a one-time decision for your clients?" / "How are you funding the tax bill on conversions — from the IRA itself, or an outside account?" (the "outside account" answer matters enormously to the economics).

Educational framing: Present the NPV/long-horizon-wager framing (McQuarrie) alongside the bracket-optimization framing (McQuarrie & DiLellio) — this two-sided, research-grounded picture is more credible and more consistent with your fiduciary philosophy than a one-sided "just convert" pitch.

Common wholesaler mistakes: Presenting conversions as a universal recommendation rather than bracket- and circumstance-specific; not asking how the tax bill will be funded (using IRA assets to pay the tax meaningfully changes the math and should always be flagged).

Engagement/pivot indicators: Advisor asks about specific bracket thresholds or IRMAA cliffs = high engagement, continue. Advisor says all their retiree clients are already well past the optimal window = pivot to estate/legacy framing of conversions instead.

B.3 Retirement Income & Withdrawal Strategy

Why it matters: This is one of the most heavily and rigorously researched areas in financial planning, giving your AI unusually strong material to draw on.

Foundational research: William Bengen's original 1994 research, "Determining Withdrawal Rates Using Historical Data," published in the Journal of Financial Planning, used historical market data back to the 1920s and found a 4% initial withdrawal rate (with inflation adjustments thereafter) gave retirees a high probability of not outliving a 50/50 stock/bond portfolio over 30 years.

Updated/evolving research (Tier 1 — ongoing, forward-looking): Morningstar's research team re-examined the question starting in 2021 using forward-looking capital-market return forecasts rather than historical averages, and has published updated "safe withdrawal rate" estimates annually since; their most recent analysis puts a fixed, non-flexible starting withdrawal rate at roughly 3.9%, while flexible "guardrails" approaches that adjust spending in response to market conditions can support withdrawal rates as high as 5.7%.

Guardrails methodology specifics: The Guyton-Klinger guardrails approach (developed by financial planner Jonathan Guyton and professor William Klinger) sets upper and lower bounds around a target withdrawal rate — commonly 20% above and below — and triggers a defined spending adjustment (e.g., a 10% increase or cut) whenever the portfolio's actual withdrawal rate crosses a guardrail.

Practical application: This is a strong, research-dense pain point for education-first positioning — a wholesaler who can accurately explain the difference between a fixed 4%-style rule and a dynamic guardrails approach, and why the "safe" number has moved over time as return expectations changed, demonstrates real expertise (the "ability" trust dimension from Phase 1) without pitching any specific product.

Discovery questions: "Are your retiree clients on a fixed percentage withdrawal, or something more dynamic like guardrails?" / "How are you handling sequence-of-returns risk for clients retiring into a down market?"

Common wholesaler mistakes: Quoting "4%" as a fixed, timeless rule without noting that the research itself has evolved substantially — this risks an "unrealistic projections" flag under your own evaluation criteria, and is now factually outdated relative to current forward-looking research.

Follow-up questions/pivot: If the advisor already uses a dynamic/guardrails framework, pivot to how they communicate guardrail adjustments to clients (a trust/communication angle) rather than re-explaining the mechanics.

B.4 Charitable Planning (Donor-Advised Funds & Appreciated-Asset Giving)

Why it matters: One of the few tax strategies that is simultaneously tax-efficient, values-aligned, and essentially uncontested in the research — a good fit for education-first conversations since there's little need to oversell it.

Research base: The National Study on Donor Advised Funds (2024), produced by the Donor Advised Fund Research Collaborative — a Tier 1 academic partnership including researchers at DePaul University — is the leading empirical study of DAF donor behavior. Mechanically: donating appreciated securities held more than a year avoids capital gains tax entirely while still allowing a fair-market-value deduction of up to 30% of AGI, with a five-year carry-forward for amounts exceeding that limit.

Client profiles affected: Clients with appreciated concentrated stock (direct overlap with B.1 — donating appreciated shares can be part of a concentration-reduction strategy), high-income-year clients wanting to smooth a large tax bill, clients with an existing giving pattern who haven't formalized it.

Discovery questions: "Do any of your clients give to charity in a fairly ad hoc way that could be formalized?" / "Have any of your clients had an unusually high-income year where a larger charitable deduction would help?" / "Is anyone sitting on appreciated stock that would make more sense to give than sell?"

Educational framing: A DAF's core advantage is that it separates the tax-planning decision (make the contribution and take the deduction this year) from the philanthropic decision (decide which charities to support later) — useful for clients who know they want a deduction this year but haven't decided where the money should ultimately go.

Contested point to flag honestly: DAF growth and payout-rate transparency is a live policy debate — some academic researchers studying the flow of money between donors and nonprofits have raised concerns, in peer-reviewed venues like Nonprofit Policy Forum, about how much DAF-held money is actually distributed to operating charities versus held indefinitely. This doesn't change the mechanics or tax benefit for your clients, but it's worth your compliance team being aware of the broader policy conversation.

B.5 Qualified Opportunity Zones (QOZs) — Report the Genuine Research Conflict

Your brief specifically asks that contested research be presented with differing viewpoints and the strongest empirical support flagged. QOZs are the clearest case of this in the entire pain-point list, so this section is deliberately balanced rather than promotional.

The investor-level tax mechanics are real and well-documented: Original TCJA structure allowed deferral of capital gains tax until 2026 or sale of the QOF stake, a 10–15% exclusion of the original gain for 5–7 year holds, and full exclusion of new gains on the QOZ investment itself if held at least 10 years (subsequent legislation has adjusted specific dates/parameters — verify current-year mechanics before client conversations, since this area changes with tax law).

The community-impact research is genuinely negative-to-mixed, and this matters for a fiduciary-communication AI: Peer-reviewed-adjacent economic research (Kennedy & Wheeler, cited by the Center for American Progress) found no evidence that opportunity zones increased job postings relative to comparable non-designated areas, including within construction and real estate specifically. Multiple research bodies — including Brookings and the Tax Policy Center — found investment has concentrated disproportionately in zones with higher incomes, lower unemployment, and more college graduates than typical distressed communities, and a GAO report found insufficient data was being collected to properly evaluate the program's actual performance. The Treasury Department's own study authors cautioned that even where measured economic activity increased, that does not necessarily mean the low-income residents the program targets actually benefited.

Practical application for your AI's compliance/ethics scoring: A wholesaler discussing QOZs in a fiduciary, education-first way should accurately describe the investor tax deferral/exclusion mechanics (real and well-documented) without characterizing the investment as delivering clear, well-evidenced community/social benefit (a claim the current research does not support). This is a good test case for your "compliance-conscious communication" and "conservative expectations" scoring categories — the AI should flag claims about QOZ community impact as unsupported, while treating claims about the investor-level tax mechanics as factual.

Cross-Cutting Notes for Phase 2

Where the evidence is genuinely strong vs. genuinely thin. Retirement income withdrawal strategy (B.3) and Roth conversion bracket optimization (B.2) sit on some of the best peer-reviewed practitioner research in the entire financial-planning field. Gatekeeper conversation tactics (A.3) sit on almost none. Your model documentation should carry this distinction through to confidence-weighting in the scoring engine — don't let a category with thin evidence get the same confidence treatment as one with decades of Journal of Financial Planning research behind it.

The "concentration paradox" (B.1) and the Roth "wager" framing (B.2) are the two most valuable psychological insights in this phase — both directly support your stated philosophy, because both explain why a purely rational, purely technical pitch tends to fail: clients resist good advice for identity/psychological reasons (concentration) or because the payoff structure genuinely involves real uncertainty that shouldn't be oversold (Roth conversions as a wager). Recommend weighting these two insights prominently into rep training materials, not just the scoring model.

Not yet covered from your original pain-point list: business-owner exit/succession tax planning, estate and legacy/wealth-transfer planning specifically (beyond the charitable-giving overlap above), broad portfolio diversification/alternative investment allocation research, and client-retention/practice-differentiation research beyond the Vanguard Advisor's Alpha and Envestnet Capital Sigma value-of-advice studies referenced in Phase 1's cross-cutting notes. Recommend these anchor a short Phase 2b, or get folded into Phase 3 alongside the full metrics/scoring architecture — happy to proceed either way.

Full Source List (Phase 2)

#

Source

Author/Org

Year

Tier

1

Thin slices of expressive behavior (teacher ratings study)

Ambady & Rosenthal / Harvard, JPSP

1993

1

2

Methodological review of thin-slice accuracy

Columbia Business School

2007

1

3

Thin Slices of Negotiation

Curhan & Pentland / MIT, J. Applied Psych.

2007

1

4

Cold-call voicemail dataset (300M+ calls)

Gong Labs (cited via secondary sources)

ongoing

2

5

Voicemail-checking behavior

Pew Research Center (cited via secondary sources)

2020

1 (primary data) / 3 (aggregator)

6

Managing concentrated stock risk / "concentration paradox"

Envestnet

2026

2

7

Roth conversion bracket-optimization research

McQuarrie & DiLellio / Journal of Financial Planning

—

1

8

Roth conversions as long-horizon wager (NPV analysis)

McQuarrie / Financial Planning Association Journal

2024

1

9

Determining Withdrawal Rates Using Historical Data

Bengen / Journal of Financial Planning

1994

1

10

Reevaluating the 4% Withdrawal Rule (ongoing series)

Morningstar Research

2021–2026

1

11

Guardrails decision rules

Guyton & Klinger / Journal of Financial Planning

2004/2006

1

12

National Study on Donor Advised Funds

DAF Research Collaborative / DePaul University

2024

1

13

DAF payout/policy debate

Nonprofit Policy Forum (peer-reviewed)

forthcoming

1

14

Opportunity Zone job-posting impact study

Kennedy & Wheeler, cited via CAP

2022

1 (underlying study) / 2 (summary source)

15

Opportunity Zone targeting/effectiveness

Brookings, Tax Policy Center, GAO, Tax Foundation

2020–2023

1

16

Vanguard Advisor's Alpha (value of advice)

Vanguard Research

2001–2022, ongoing

1 (full detail in Phase 1 companion notes)

AI Wholesaler Coaching Platform — Research Library

Phase 2b: Business-Owner, Estate/Wealth-Transfer, Alternatives & Retention Pain Points

Prepared for: USEDC Wholesaling Division AI Coaching Platform Completes the advisor pain-point playbook set started in Phase 2. Same tiering/citation conventions apply.

B.6 Business-Owner Exit & Succession Planning

Why it matters: For many business-owner clients, the business is both their largest asset and their retirement plan rolled into one — making this simultaneously a tax, retirement-income, and estate-planning conversation, not just a transaction.

Research base (Tier 1 — major consulting-firm survey research, matches your brief's explicit PwC/institutional research request): PwC's US Family Business Survey found that while 78% of respondents rank protecting the business as their most important long-term goal, and 72% want the business to stay in the family, as of the 2021 survey only 34% had a robust, documented, and communicated succession plan in place. A separate secondary summary of the same PwC research puts it starkly: nearly two-thirds of family businesses still lack a documented succession plan.

The regret/outcome data (useful, but tiering matters here): Frequently cited statistics — that roughly half of business exits happen unexpectedly due to death, disability, divorce, disagreement, or distress, that only 20–30% of small businesses listed for sale successfully sell, and that 75% of owners who do sell report "profound regret" a year later — trace back primarily to the Exit Planning Institute's proprietary research rather than a peer-reviewed academic source. Treat as Tier 2 (credible, widely used industry research body, but not academic peer review) and present with appropriate confidence.

Client profiles affected: Owners within 3–10 years of a planned exit; owners with no documented succession plan; family businesses transitioning to a next generation; owners facing an unplanned trigger event (health, partner dispute, unsolicited offer).

Advisor concerns: Coordinating across CPA, attorney, and valuation professionals; balancing the owner's financial needs against family/employee continuity; timing the transition around tax law and market conditions.

Discovery questions: "Do you have clients where the business is more than half their net worth and there's no documented exit plan yet?" / "Has anyone run an actual third-party valuation, or is it still a guess?" / "Are they thinking family succession, employee/ESOP, or an outside sale — or genuinely undecided?"

Educational framing: The distinction between succession planning ("who leads without me") and exit planning ("how do I transition on my terms, with what result") is a useful, research-grounded frame for an educational conversation — it reframes the conversation from a single transaction to two related but separate planning problems, which fits your discovery-before-solution philosophy well.

Common wholesaler mistakes: Jumping straight to a product (e.g., an ESOP pitch) before establishing which of the two problems (succession vs. exit) the advisor's client is actually facing; ignoring the emotional/identity dimension — many owners struggle with loss of identity after a sale, so lifestyle and purpose planning matters alongside the financial mechanics.

Engagement indicators: Advisor mentions a specific client's timeline or business type unprompted; asks about valuation methodology or a specific structure (ESOP, installment sale, etc.).

Follow-up questions: "Would a framework for the succession-vs-exit conversation be useful before your next meeting with that client?"

B.7 Estate & Legacy / Wealth-Transfer Planning

Why it matters: This is arguably the single largest structural opportunity in wealth management over the coming decades, and it is unusually well quantified.

Research base (Tier 1 — leading institutional wealth-management research firm, matches your brief's explicit request for institutional wealth management research): Cerulli Associates projects $124 trillion in wealth will transfer through 2048, with $105 trillion flowing to heirs and $18 trillion to charity; roughly 81% of transfers will come from Baby Boomers and older generations. Approximately $62 trillion — 50% of the total — will come from high-net-worth and ultra-high-net-worth households, which together represent only about 2% of all households — meaning this opportunity is heavily concentrated rather than evenly distributed. A large intra-generational component exists too: an estimated $54 trillion will pass to spouses first, with roughly $40 trillion of that going to widowed women, before ultimately transferring intergenerationally.

The advisor-retention angle (directly relevant to your "differentiating practice" and "client retention" categories): A Natixis Center for Investor Insights report found 41% of U.S. advisors believe the Great Wealth Transfer presents an existential threat to their business — because assets frequently leave a firm when the primary client relationship-holder passes away and the family has no independent relationship with the advisor. Cerulli's own research identifies family meetings and regular communication as the most-effective wealth-transfer planning strategy (cited by 81% of high-net-worth practices), ahead of educational support (59%) and organized succession planning (31%).

Client profiles affected: Aging clients without documented multi-generational planning; clients with heirs who have no relationship with the advisor; blended families; clients who are themselves about to become heirs (the Gen X/Millennial "receiver" side of the transfer).

Discovery questions: "Do you have a relationship with your clients' adult children, or is it really just the primary account holder?" / "Has anyone talked with your clients about what their spouse would do if something happened to them?" / "Are any of your clients themselves expecting a significant inheritance in the next 5–10 years?"

Educational framing: Position this as a retention/relationship conversation as much as a technical one — survey research found that while the vast majority of both givers and receivers agree it's important to discuss an inheritance in advance, only 39% of "givers" have actually provided guidelines or direction to their beneficiaries — a genuine, common planning gap, not a manufactured one.

Common wholesaler mistakes: Treating this purely as an estate-tax/trust mechanics conversation and skipping the relationship/communication dimension, which the research (above) identifies as the actual highest-leverage strategy.

Contested/context point: The often-cited "70% of family wealth is lost by the second generation, 90% by the third" statistic traces back to Williams and Preisser's "Preparing Heirs" research (2010) — a respected but non-peer-reviewed source. Present it as a widely cited industry finding rather than an unambiguous academic fact.

Engagement/pivot indicators: Advisor volunteers that they've never met a client's adult children = high-value pivot point to a family-meeting/multi-generational relationship conversation rather than a product pitch.

B.8 Alternative Investments & Portfolio Diversification

Why it matters: This pain point is less about a single client conversation and more about a structural allocation gap between institutional practice and typical advisor practice.

Research base (Tier 1/2 — major asset manager institutional research, cross-referencing Cerulli): Fidelity's Study of Allocations to Alternative Investments found institutions have historically held far higher average allocations to alternatives than financial advisors do (roughly 25% vs. 5%), a gap attributed to manager access, perceived costs, liquidity considerations, and high investment minimums rather than a fundamental disagreement about the value of alternatives.

Supporting institutional-adoption data: By 2014, the largest pension schemes and sovereign wealth/public pension reserve funds across 36 OECD countries allocated over 30% of a combined $10.3 trillion in assets to alternative and other assets, up from roughly 5% in 1995 — a long, steady institutional trend toward alternatives as a diversification tool.

Contested point (report honestly, as your brief requests): Not all research is uniformly positive. A peer-reviewed paper titled "Harmful diversification: Evidence from alternative investments" (ScienceDirect) directly challenges the assumption that adding alternatives is automatically beneficial — the existence of a peer-reviewed paper with this title and framing signals that the diversification benefit of alternatives is asset-, structure-, and time-period-dependent, not a universal truth. Recommend the AI never let a wholesaler present "alternatives always diversify/reduce risk" as an uncontested claim — the accurate, defensible claim is narrower: certain alternative categories have shown diversification benefits in certain conditions (e.g., Fidelity's own 2005–2024 historical study found certain liquid alternative strategies provided strong diversification benefits especially during periods of poor public equity performance, while private alternatives showed higher returns than most other categories), not a blanket statement.

Client profiles affected: High-net-worth clients concentrated entirely in traditional stock/bond allocations; clients nearing retirement seeking additional diversification/income sources; sophisticated/accredited investors underexposed relative to institutional norms.

Discovery questions: "Are your clients' portfolios closer to the institutional norm on alternatives, or more traditional?" / "What's held them back — access, liquidity concerns, or client comfort?"

Educational framing: Lead with the access/structural-barrier framing (institutions allocate more because of access advantages, not necessarily superior judgment) rather than a "you're missing out" framing — this keeps the conversation in the education-first, non-urgency register your philosophy requires.

Common wholesaler mistakes: Presenting a single alternative product as a universal diversifier without acknowledging that the diversification benefit is strategy- and period-specific (per the contested research above); ignoring legitimate liquidity/complexity trade-offs.

B.9 Client Retention & Practice Differentiation

(This connects directly to the Vanguard Advisor's Alpha research already detailed in Phase 1 — cross-referenced here specifically for the "differentiating practice" and "demonstrating value beyond portfolio management" pain points.)

Research base (Tier 2 — major fintech/research platform used industry-wide, proprietary but methodologically transparent): Envestnet's Capital Sigma research (a widely cited companion/complement to Vanguard's Advisor's Alpha) quantifies advisor-created value similarly, in the same 2–3% annual range referenced in Phase 1's cross-source comparison. Broader Envestnet research indicates that clients who view their advisor as a comprehensive "financial architect" rather than solely a portfolio manager tend to form stickier, longer relationships and consolidate more assets with that advisor over time.

Fee/positioning trend data (Tier 2 — large annual industry survey, useful as current market context): A 2026 industry study found average financial-planning retainer fees have risen 52% since 2023, with subscription-fee models nearly tripling, reflecting an industry-wide shift toward pricing comprehensive planning relationships rather than bundling everything into an asset-based fee — relevant context for wholesalers discussing how advisors demonstrate and price their value.

Practical application: This is the direct evidentiary link between "educate, don't sell" and business outcomes for the advisor — the research consistently shows that advisors who position as comprehensive planning relationships (not transaction-based portfolio managers) retain clients longer and consolidate more assets, which is the legitimate, non-manipulative business case a wholesaler can make for expanding into planning conversations (tax, estate, business-owner topics) beyond pure investment selection.

Discovery questions: "How much of your client relationship is planning-led versus purely portfolio management right now?" / "Are you pricing comprehensive planning separately, or is it bundled into an AUM fee?"

Common wholesaler mistakes: Presenting differentiation/value-demonstration as a marketing or sales-technique problem rather than tying it to the underlying research on what actually drives retention (planning depth and multi-generational relationships, per B.7 and this section) — this is the point where a wholesaler's message should feel like practice-management insight, not a pitch.

Cross-Cutting Notes for Phase 2b

The wealth-transfer and business-owner sections are the two highest-leverage, most defensible opportunities in this entire pain-point library, because the underlying research (Cerulli, PwC) is both Tier 1 and directly quantifies the scale of the opportunity — useful for framing conversations with advisors around genuine, well-documented structural shifts rather than any single product.

Alternative investments is the pain point most in need of restrained, honest framing. The institutional-adoption gap (25% vs. 5%) is real and well-documented, but the "alternatives = better diversification, full stop" claim is not uniformly supported — the ScienceDirect "harmful diversification" research is a useful internal check to keep wholesaler messaging accurate and consistent with your no-overselling philosophy.

Tier-2 sources dominate this phase more than Phase 1 or the first half of Phase 2. Business-owner exit statistics (Exit Planning Institute), the "70/90%" generational wealth-loss statistic (Williams & Preisser), and Envestnet/Fidelity practice-management research are all credible, widely used industry sources — but not peer-reviewed academic research. This is disclosed consistently rather than smoothed over, per your original brief's instructions on differing viewpoints and empirical support.

This completes the advisor pain-point list from your original brief, with two exceptions worth flagging explicitly: (a) "capital gains tax mitigation" was covered distributed across the concentrated-stock (B.1, Phase 2) and charitable-giving (B.4, Phase 2) sections rather than as a standalone entry, since the strongest research treats it as a technique embedded in those contexts rather than a freestanding topic; (b) "keeping pace with tax law changes" is more of an ongoing operational/training requirement than a discrete research pain point — recommend handling it as a living update process (e.g., a quarterly tax-law-changes briefing pulled from IRS/Treasury primary sources) rather than a one-time research entry, and I'm happy to scope that process separately if useful.

Full Source List (Phase 2b)

#

Source

Author/Org

Year

Tier

1

US Family Business Survey

PwC

2021/2023

1

2

State of Owner Readiness / exit statistics

Exit Planning Institute

2025

2

3

U.S. High-Net-Worth and Ultra-High-Net-Worth Markets: The Great Wealth Transfer

Cerulli Associates

2024

1

4

Wealth transfer planning strategy effectiveness data

Cerulli Associates (cited via secondary sources)

2022/2024

1

5

Existential threat to advisor business from wealth transfer

Natixis Center for Investor Insights

—

2

6

Preparing Heirs (generational wealth-loss statistic)

Williams & Preisser

2010

2

7

Giver/Receiver inheritance communication survey

RBC Wealth Management

2024

2

8

Study of Allocations to Alternative Investments

Fidelity Institutional

2023–2025

2

9

Institutional alternative-asset allocation trend (OECD pension data)

OECD / Towers Watson, cited via ScienceDirect

2016

1

10

"Harmful diversification" (contested evidence)

ScienceDirect (peer-reviewed)

2018

1

11

Alternative Investments and Their Roles in Multi-Asset Portfolios

Fidelity Institutional

2024

2

12

Capital Sigma: The Return on Advice

Envestnet

—

2

13

HNW client retention / "financial architect" positioning research

Envestnet, citing Spectrem

2021/2026

2

14

2026 State of Financial Planning (fee trends)

Envestnet/Datos Insights

2026

2

AI Wholesaler Coaching Platform — Research Library

Phase 3: Metrics & Scoring Architecture

Prepared for: USEDC Wholesaling Division AI Coaching Platform This phase converts the research compiled in Phases 1, 2, and 2b into a detectable, weighted scoring architecture across the 20 categories from your original brief. New research introduced in this phase (FINRA rules, interruption science, speech-rate research) is cited in full; earlier findings are referenced back to their source phase rather than re-cited, to avoid duplication.

How This Architecture Works

Three layers, consistent across every category below:

Detectable signals — what the AI can actually pull from a transcript and/or audio stream (text features, timing features, acoustic features).

Scoring logic — how signals become a 0–5 category score, with the research-backed reasoning for why that threshold or weighting was chosen (not an arbitrary number).

Confidence tier — carried over from Phases 1/2/2b's tiering discipline. A category built on peer-reviewed, replicated research gets a High confidence weighting in the composite score; a category built on credible-but-non-academic industry data gets Medium; a category with genuinely thin evidence (flagged honestly in Phase 2) gets Low and should influence coaching feedback more than it influences a hard numeric score.

A category's confidence tier is not a judgment about how important the behavior is — it's a statement about how much weight the automated score should carry versus how much should be left to human coach review. Low-confidence categories still matter; they just shouldn't silently move a rep's aggregate score with the same authority as a category built on decades of replicated peer-reviewed research.

1. Active Listening

Research anchor: Phase 1, Section 3 (INSEAD listening meta-analysis; Journal of Business and Psychology meta-analysis; OARS/motivational interviewing)

Detectable signals: back-channel responses ("mm-hmm," "right," "I see") timed appropriately relative to advisor speech; paraphrase/reflection frequency; non-interruption during advisor turns; follow-up questions that reference specific content the advisor just said (vs. generic follow-ups).

Scoring logic: Adapt the Active-Empathetic Listening (AEL) three-part structure from Phase 1 — Sensing (did the rep let the advisor finish, minimal unwanted overlap), Processing (paraphrase/summary frequency), Responding (relevance of the next rep statement to what was just said). Each sub-score 0–5, averaged.

Confidence tier: High — built on a peer-reviewed meta-analysis and a validated psychometric instrument (AEL scale).

2. Discovery & Questioning

Research anchor: Phase 1, Section 3.4 (SPIN Selling); Phase 1, Section 3.3 (OARS open questions)

Detectable signals: open vs. closed question ratio; SPIN question-type classification (Situation / Problem / Implication / Need-payoff) per call; discovery-phase duration vs. solution-presentation duration.

Scoring logic: Reward Implication and Need-payoff questions more heavily than Situation questions, per Rackham's finding that these specific question types — not general information-gathering — correlated with success in complex, relationship-driven sales (Phase 1, Section 3.4). A call dominated by closed, Situation-only questions scores low even if the question count is high.

Confidence tier: Medium — Rackham's underlying research is a massive, rigorous field study but not peer-reviewed (Tier 2, per Phase 1's tiering).

3. Cold Call Openings

Research anchor: Phase 2, Section A.1 (Ambady & Rosenthal thin-slicing)

Detectable signals: filler-word rate, pace stability, and clarity score computed specifically on the first 10–15 seconds of audio, scored separately from the whole-call average; presence of a clear self-introduction and purpose statement within that window.

Scoring logic: Given the Harvard thin-slicing research showing five-second clips predict downstream judgment nearly as well as five-minute ones (Phase 2, A.1), weight the opening segment at roughly double the per-second influence of the rest of the call in the composite "Cold Call Opening" score. Track recovery separately — a poor opening with strong recovery should be coached differently than a poor opening with no recovery.

Confidence tier: High for the opening-weighting logic itself (Tier 1 research); Medium for the specific 2x weighting multiplier, which is a reasonable but not directly research-derived design choice — flag it as a tunable parameter, not a fixed finding.

4. Advisor Psychology

Research anchor: Phase 1, Section 4 (behavioral finance biases); Phase 2, Section B.1 (concentration paradox), B.2 (Roth conversion as wager)

Detectable signals: anchoring-risk flags (early, repeated numeric projections before context is established); loss-frame vs. gain-frame language ratio; overconfidence-validation vs. overconfidence-caveat language when the advisor expresses certainty.

Scoring logic: This category doesn't score the advisor's psychology — it scores whether the rep demonstrates awareness of common advisor/investor biases in how they frame information. A rep who frames a concentrated-stock conversation using the "concentration paradox" insight (identity/success framing, not just risk statistics) scores higher than one using a purely statistical pitch, because the research shows the former is more likely to land (Phase 2, B.1).

Confidence tier: Medium — bias existence is Tier 1 (NBER, peer-reviewed behavioral finance), but the specific claim that a given framing choice improves real-world outcomes for wholesaler conversations is inferred rather than directly studied in this context.

5. Trust Building

Research anchor: Phase 1, Section 2 (Mayer-Davis-Schoorman trust model; CFA Institute Investor Trust Study)

Detectable signals: Ability-signal density (specific, correct technical statements), Benevolence-language ratio (client/advisor-benefit framing vs. rep/firm-benefit framing), Integrity-consistency (contradiction detection within and across calls with the same advisor), Relationship-Trust language ratio (references to the advisor's specific clients/values vs. generic product talk).

Scoring logic: Composite Trust Score = weighted average of Ability, Benevolence, and Integrity sub-scores (Phase 1, Section 2.1), each independently classified from the transcript. This is the most research-dense category in the entire architecture and should anchor a meaningful share of the "Overall Advisor Experience" composite (see Section 20).

Confidence tier: High — the underlying model is the most-cited trust framework in management science with decades of independent validation.

6. Behavioral Finance (Communication Application)

Research anchor: Phase 1, Section 4

Detectable signals: same as Category 4 (Advisor Psychology) — these two categories overlap deliberately, since bias-aware communication is both a psychological-insight category and a behavioral-finance-literacy category. Recommend a shared underlying classifier with two different weighted views into the same signal set, rather than duplicating detection logic.

Scoring logic: Score whether the rep's claims about markets, risk, or client behavior are consistent with established behavioral finance findings (e.g., not asserting that education alone eliminates bias, per Phase 1's finding that financial literacy only partially moderates bias effects).

Confidence tier: High for the underlying research; Medium for automated detection accuracy, since this requires the AI to fact-check claims against a knowledge base, not just detect a pattern.

7. Tax-Planning Discussions

Research anchor: Phase 2, Sections B.2 (Roth), B.4 (charitable), B.5 (QOZ); Phase 2b, Section B.6 (business owner), B.7 (estate)

Detectable signals: presence of two-sided framing on contested topics (e.g., Roth conversions presented with both the bracket-optimization case and the NPV/wager caveat, per Phase 2 B.2); accuracy of claims against current-year tax mechanics; QOZ-specific flag distinguishing investor tax-mechanic claims (factual, low-risk) from community-impact claims (contested, higher-risk — Phase 2, B.5).

Scoring logic: This category should be treated as a compliance-adjacent category as much as an educational one — inaccurate tax claims carry real regulatory risk (see Category 14). Score for accuracy first, two-sided/conservative framing second, and relevance-to-advisor's-stated-client-base third.

Confidence tier: Medium-High — the underlying tax-planning research is strong (Journal of Financial Planning, Morningstar), but tax law changes yearly, so this category needs a living update process (flagged in Phase 2b's cross-cutting notes) rather than a static rule set.

8. Executive Presence

Research anchor: Phase 1, Section 5 (MIT "Honest Signals"; speech rate/pitch/credibility research)

Detectable signals: conversational activity balance, vocal mirroring/synchrony proxy, engagement consistency across the call (vs. spiking only during pitch moments), pitch stability/contour.

Scoring logic: Per Phase 1, Section 5.1, nonverbal conversational dynamics predicted 30% of outcome variance in a negotiation context independent of content — meaningful enough to score explicitly, but not overweighted relative to content-based categories (Trust Building, Discovery) which have stronger direct evidence in a financial-advice context specifically.

Confidence tier: High — Tier 1 (MIT/Journal of Applied Psychology), though originally studied in negotiation rather than wholesaler-advisor calls specifically, so treat as a well-supported analogy rather than a domain-specific finding.

9. Voice & Speech (Pace, Filler Words, Stuttering)

Research anchor: Phase 1, Section 5.2; new research this phase

New research grounding this phase — speech rate and persuasion (Tier 1, peer-reviewed, NIMH-funded): Miller, Maruyama, Beaber, and Valone's foundational 1976 study on speed of speech and persuasion established 120–180 words per minute as the normal range of human speech, with subsequent research (referenced in Phase 1, Section 5.2) showing an inverted-U relationship between pace and perceived credibility — both extremes reduce it.

Detectable signals: words-per-minute (computed per-segment, not just whole-call average, since pace variance matters more than a single number); filler-word frequency (per 100 words); stutter/disfluency rate; pitch contour (stable/falling vs. rising at sentence ends).

Scoring logic: Score against a band, not a single target — flag calls with sustained pace outside roughly 120–180 wpm (the established normal range) rather than optimizing toward one "ideal" number, since the research shows both over- and under-pace reduce credibility. Filler words: research cited in Phase 1 suggests roughly 2 per 100 words is a reasonable, unremarkable baseline — flag rates well above this, not zero-tolerance.

Confidence tier: High for the pace/credibility relationship (Tier 1, peer-reviewed); Medium for the specific filler-word threshold (Tier 2/3 sourcing in Phase 1).

10. Communication Clarity

Research anchor: Phase 1, Section 7 (Knowles' andragogy); Phase 2, Section A.1

Detectable signals: sentence-length variance, jargon-density (technical terms used without a plain-language restatement), problem-centered framing ratio (Phase 1, 7.1) — is new information tied to a client situation the advisor mentioned, or presented abstractly?

Scoring logic: A high jargon-density score is not automatically penalized — the category should check whether jargon is paired with a plain-language explanation (see Category 12, "Ability to Simplify"). Unexplained jargon scores low; explained jargon scores neutral-to-positive (demonstrates ability, per the Trust Building "ability" dimension).

Confidence tier: Medium — the andragogy research (Tier 1) supports the problem-centered framing logic, but jargon-density thresholds are an engineering judgment call, not directly derived from a cited study.

11. Objection Handling

Research anchor: Phase 1, Section 3.3 (motivational interviewing / OARS — "sustain talk"); Phase 1, Section 6 (Cialdini, ethical persuasion boundaries)

Detectable signals: does the rep reflect/acknowledge the objection before responding (OARS-consistent) vs. immediately counter it?; does the response include a caveat/limitation (integrity-consistent) or only counter-arguments?; scarcity/reciprocity-pressure language specifically in objection-handling moments (a common place for manipulative tactics to appear, per Phase 1, Section 6).

Scoring logic: Reward reflect-then-respond patterns over immediate-counter patterns, consistent with motivational interviewing's finding that reflective listening around resistance ("sustain talk") is associated with better outcomes than direct confrontation (Phase 1, Section 3.3). Flag any objection-handling turn that uses manufactured urgency or reciprocity pressure as a hard compliance flag, not just a coaching note.

Confidence tier: Medium — OARS mechanism-level evidence is Tier 1, but Phase 1 explicitly flagged that MI's outcome effect size evidence is mixed; treat the reflect-then-respond scoring logic as well-supported, but don't overstate expected impact magnitude in reporting.

12. Financial Education / Ability to Simplify Complex Concepts

Research anchor: Phase 1, Section 7 (andragogy); Phase 1, Section 1 (curiosity/information-gap theory)

Detectable signals: explanation complexity (readability-style metrics adapted for spoken transcript), presence of analogy/plain-language restatement after technical terms, "priming dose" pattern — does the rep give enough information to open curiosity without immediately over-explaining and collapsing the gap (Phase 1, Section 1.1)?

Scoring logic: This is one of the categories where two Phase 1 findings combine directly: Knowles' "problem-centered, not content-centered" principle (educate relative to the advisor's actual situation) and Loewenstein's priming-dose finding (partial information sustains curiosity better than complete information dumps). Score highest when a technical concept is explained in plain language and tied to the advisor's stated client situation and left appropriately open rather than exhaustively resolved.

Confidence tier: High — both underlying theories are Tier 1 and directly on-topic for this category specifically.

13. Relationship Management

Research anchor: Phase 2b, Section B.7 (Cerulli wealth-transfer/retention research), B.9 (Envestnet/Capital Sigma)

Detectable signals: references to multi-generational relationships (advisor's clients' spouses/heirs), references to comprehensive planning vs. pure portfolio management, follow-up commitment language and whether it's honored on subsequent calls.

Scoring logic: Per Phase 2b's research, family-meeting/multi-generational engagement is the single most-cited effective wealth-transfer retention strategy (81% of top HNW practices, per Cerulli) — reward reps who introduce this framing into advisor conversations, particularly in estate/wealth-transfer contexts.

Confidence tier: Medium — Tier 1 data on what correlates with retention (Cerulli), but Tier 2 on whether a wholesaler surfacing this in conversation causally improves outcomes (a reasonable inference, not a directly studied causal claim).

14. Compliance & Ethics

Research anchor: New research this phase — FINRA Rule 2210 and Rule 2111

New research grounding this category (Tier 1 — primary regulatory source): FINRA Rule 2210 (Communications with the Public) requires that all member communications be based on principles of fair dealing and good faith, be fair and balanced, and not omit material information concerning products or services, while prohibiting false, exaggerated, or misleading statements or claims. FINRA Rule 2111 (the Suitability Rule) requires a reasonable basis for believing a recommended transaction or strategy is suitable, based on the customer's full investment profile — age, other investments, financial situation, tax status, objectives, experience, time horizon, liquidity needs, and risk tolerance — collected via Rule 2090's "Know Your Customer" requirement to use reasonable diligence in gathering that information in the first place.

Detectable signals: unwarranted/exaggerated claims (absolute language: "guaranteed," "always," "never fails"); missing balance (benefit stated without a corresponding risk/limitation); scarcity/urgency language (cross-referenced with Category 11); QOZ-style claims that conflate investor tax mechanics with unsupported community-impact assertions (Phase 2, B.5); Roth-conversion or other tax claims presented as unambiguous rather than circumstance-dependent (Phase 2, B.2).

Scoring logic: This category should function as a flag-and-review system, not a pure numeric score — false/exaggerated claims and missing-balance language should generate a compliance review flag for human oversight, consistent with FINRA's own fair-and-balanced standard, rather than simply lowering a coaching score that a rep might not see until later.

Confidence tier: High — grounded directly in binding regulatory text, the strongest possible evidentiary basis in this entire architecture. This should be the one category where automated flags carry near-full weight, since the cost of a missed compliance issue is asymmetric compared to other coaching categories.

15. Gatekeeper Conversations

Research anchor: Phase 2, Section A.3

Detectable signals: use of gatekeeper's name, thank-you/respect language, absence of pressure or deceptive framing when asking to be connected.

Scoring logic: As documented honestly in Phase 2, no Tier 1 research exists specifically for this category — the scoring logic is inferred from the adjacent thin-slicing research (Category 3) plus the one consistent theme across available industry sources (respect-based language correlates with better outcomes).

Confidence tier: Low — score this category for coaching visibility, but do not let it carry meaningful weight in the aggregate composite score (see Section 20) until better-quality research becomes available. Recommend periodic re-review of this category specifically.

16. Voicemail Effectiveness

Research anchor: Phase 2, Section A.3

Detectable signals: voicemail length (research-supported ceiling: keep under ~30 seconds, consistent with the broader finding that 3+ voicemails per prospect reduce rather than improve reply rates); presence of a specific, personalized reason for calling (vs. generic script); explicit reference to a follow-up email (since voicemail's documented value is priming a subsequent channel, not the callback itself).

Scoring logic: Score against next-touch engagement (email open/reply rate, next-call pickup), not raw callback rate — per Phase 2's finding that voicemail callback rates are inherently low (4–5%) but voicemails meaningfully lift email reply rates when used sparingly (1–2 per prospect, not 3+).

Confidence tier: Medium — Tier 2 (large-sample proprietary analytics, not peer-reviewed, but methodologically transparent and consistent across multiple independent citations).

17. Curiosity Creation

Research anchor: Phase 1, Section 1 (full detail — Loewenstein information-gap theory, fMRI confirmation, workplace-gap research)

Detectable signals: Gap-Specificity Score (precise, client-relevant knowledge gap vs. vague claim); Priming Ratio (enough information to open curiosity without over-resolving it); Curiosity Follow-Through (does the advisor ask a follow-up question); Gap-Closure Latency (is an opened gap eventually resolved or scheduled for follow-up, or left dangling).

Scoring logic: This is the most theoretically well-grounded category in the entire architecture (three independent Tier-1 sources converge on the same mechanism in Phase 1, Section 1). Score all four sub-metrics and weight Gap-Closure Latency most heavily for compliance with your explicit philosophy — an opened-but-abandoned gap risks converting curiosity into frustration (Phase 1, Section 1.3), which is the one documented failure mode of this entire technique.

Confidence tier: High — the strongest research base of any category in this library.

18. Planning Opportunity Identification

Research anchor: Phase 2 and 2b in full (all pain-point sections); Phase 1, Section 3.4 (SPIN need-payoff questions)

Detectable signals: does the rep surface a planning opportunity tied to a specific pain-point category (concentrated stock, Roth conversion, retirement income, charitable, QOZ, business-owner exit, estate/wealth-transfer, alternatives)? Is it introduced via a question (need-payoff style) or a direct statement?

Scoring logic: Score higher when the opportunity is surfaced as a question that lets the advisor articulate it themselves (consistent with both the SPIN research in Phase 1 and the OARS "change talk" research — the advisor voicing their own recognition of the opportunity, not the rep declaring it) — this is the direct operationalization of your brief's stated goal: the advisor thinking "I wasn't aware that planning option existed" on their own.

Confidence tier: High for the underlying technique (multiple converging Tier 1/2 sources); Medium for whether a given pain-point claim is factually current, since tax-adjacent pain points require living updates (Category 7's caveat applies here too).

19. Conversation Structure

Research anchor: Phase 1, Section 3.4 (Rackham's four-phase structure); new research this phase (turn-taking/interruption science)

New research grounding this category — interruption and conversational fluency (Tier 1, peer-reviewed): Research on conversational fluency found that fluent conversations are associated with feelings of belonging and social validation, and that even a single brief instance of disrupted fluency (silence or interruption) produces negative emotions and feelings of rejection — an effect that holds even when the disrupted party is not consciously aware the disruption occurred. Separately, HCI research on perceived conversation quality found that conversational equality (balanced turn-taking) positively predicted perceived quality, while the number of unsuccessful interruptions was a significant negative predictor. Note the conversation-analysis literature's own distinction: researchers differentiate "overlap" (enthusiasm/solidarity, often positive) from "interruption" (turn-violation, typically negative) — the two are not identical even though they can look similar in raw transcript data.

Detectable signals: phase segmentation (preliminaries / investigation-discovery / capability-demonstration / commitment, per Rackham's structure in Phase 1) with time allocated to each; interruption count, split where possible into cooperative overlap (brief, supportive) vs. turn-violating interruption; silence/gap duration between turns.

Scoring logic: Reward calls where investigation/discovery dominates over premature solution-presentation (Rackham's core finding). Score interruptions using the overlap/interruption distinction rather than a flat interruption count — flag turn-violating interruptions specifically, since undifferentiated interruption-counting risks penalizing normal conversational engagement.

Confidence tier: High — both the phase-structure logic and the interruption-science grounding are now backed by Tier 1 sources (Rackham's field study is Tier 2, but the interruption/fluency research introduced this phase is genuinely Tier 1 peer-reviewed).

20. Follow-up Meeting Conversion / Overall Advisor Experience

Research anchor: synthesizes all prior categories

Detectable signals: explicit next-step commitment language: is a specific date/action agreed, or vague ("I'll follow up sometime")?; does the call end with an open information gap that has a scheduled resolution (Category 17's Gap-Closure Latency)?; overall composite of Categories 1–19.

Scoring logic — the composite "Overall Advisor Experience" score: Rather than a flat average across 19 categories, weight by confidence tier and research strength:

High-confidence categories (Trust Building, Curiosity Creation, Active Listening, Compliance & Ethics, Financial Education/Simplification, Executive Presence, Voice & Speech, Conversation Structure, Cold Call Openings): full weight.

Medium-confidence categories (Discovery & Questioning, Advisor Psychology, Tax-Planning Discussions, Objection Handling, Relationship Management, Planning Opportunity Identification, Voicemail Effectiveness, Communication Clarity): standard weight, but flagged in reporting as resting on Tier 2 or applied/adjacent research.

Low-confidence categories (Gatekeeper Conversations): included for coaching visibility, minimal weight in the composite score, explicitly labeled as directional rather than authoritative until better research is available.

Compliance & Ethics is the one exception to pure weighting logic: any hard compliance flag (false/exaggerated claim, scarcity/urgency manipulation, unsupported claim presented as fact) should override the composite score with a mandatory human-review flag, regardless of how well the rep scored elsewhere — consistent with FINRA's own standard that fair-and-balanced communication is a baseline requirement, not one input among many.

Confidence tier: This category is a synthesis, not an independent finding — its reliability is only as strong as its weakest heavily-weighted input.

Example Scoring Methodology (Illustrative)

For a single call, the platform would compute:

Twenty category sub-scores (0–5 scale), each generated by the detection logic above.

A confidence-weighted composite: Overall Score = Σ(category_score × confidence_weight) / Σ(confidence_weight), where High = 1.0, Medium = 0.7, Low = 0.3.

A separate, non-averaged Compliance Flag Layer that can suppress or annotate the Overall Score regardless of its numeric value.

A coaching report that surfaces the 2–3 lowest-scoring High-confidence categories first (since these carry the strongest evidentiary basis for coaching value), followed by Medium-confidence observations, with Low-confidence categories shown as "emerging/directional" rather than scored deficiencies.

This structure ensures the platform's authority scales with the actual strength of the research behind each judgment — exactly the discipline your original brief asked for.

Cross-Cutting Notes for Phase 3

This architecture is a design proposal, not a finished spec. Actual thresholds (e.g., the 2x opening-segment weighting, the exact confidence-weight multipliers) are reasonable starting points grounded in research direction, not research-derived exact values — they should be tuned against real call data and reviewed periodically, and that tuning process should itself be documented for audit purposes given the fiduciary/compliance context.

The Compliance & Ethics category (14) is architecturally different from every other category — it's the only one grounded in binding regulatory text rather than behavioral research, and it's the only one designed to override rather than blend into the composite score. This mirrors how compliance actually works in a regulated environment: it's a gate, not an input.

Three categories (17 Curiosity Creation, 5 Trust Building, 1 Active Listening) carry the strongest research foundations in the entire library and are good candidates for the platform's flagship, most-defensible scoring dimensions if you need to prioritize which categories to build and validate first.

This completes your original research request across all three phases. Phase 1 built the psychological/behavioral foundation; Phase 2 and 2b built the pain-point and cold-call playbooks; Phase 3 converts both into a defensible, tiered scoring architecture. Happy to go deeper on any single category (e.g., a full technical detection spec for the Compliance & Ethics flagging system, or a mockup of the coaching report itself) if useful next.

New Sources Introduced in Phase 3

#

Source

Author/Org

Year

Tier

1

FINRA Rule 2210 (Communications with the Public)

FINRA

current

1

2

FINRA Rule 2111 (Suitability) / Rule 2090 (Know Your Customer)

FINRA

current

1

3

Speed of Speech and Persuasion

Miller, Maruyama, Beaber & Valone / NIMH-funded

1976

1

4

Interruptions and Silences in Conversations (fluency/belonging effects)

peer-reviewed, cited via ResearchGate

2018

1

5

Perceived Conversation Quality in Spontaneous Interactions (turn-taking equality)

HCI research, arXiv

—

1

6

Turn-taking / conversation analysis foundations (Sacks, Schegloff, Jefferson)

foundational conversation-analysis literature

1970s

1 (concept)
