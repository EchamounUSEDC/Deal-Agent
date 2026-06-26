#!/usr/bin/env python3
"""
Build the U.S. Property Development Investment Committee Charter (Word).

The visual identity (colors + fonts) is lifted from the USPD Real Estate IC
PowerPoint deck theme so the charter matches the presentation:

    Deep navy / indigo   0F113C   (theme accent1)  -> titles, headings, table headers
    Brick red            AA2226   (theme accent2)  -> accent rules / step numbers
    Charcoal             292934   (theme dk1)       -> body text
    Slate gray           6A6A75                     -> captions / secondary text
    Parchment / cream    F4F2EC   (theme lt2)       -> section bands / alt rows
    White                FFFFFF
    Fonts: Calibri Light (headings)  ·  Calibri (body)

The four sections the client asked to leave unchanged -- Purpose, Voting
Members, Nonvoting Members, Responsibility -- are reproduced verbatim. The
Decision Making, Life Expectancy, and Communication sections are revamped.

Usage:  python tools/build_ic_charter.py [output.docx]
"""

import sys
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Twips
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ---------------------------------------------------------------- palette ----
NAVY     = "0F113C"
RED      = "AA2226"
CHARCOAL = "292934"
SLATE    = "6A6A75"
CREAM    = "F4F2EC"
CREAM2   = "F7F5F1"
LINE     = "D9D7CE"
WHITE    = "FFFFFF"

HEAD_FONT = "Calibri Light"
BODY_FONT = "Calibri"


# ------------------------------------------------------------- xml helpers ----
def _set_shading(element, fill):
    """Apply a solid fill to a paragraph (pPr) or table cell (tcPr)."""
    pr = element.get_or_add_pPr() if element.tag.endswith("}p") else element
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    pr.append(shd)


def _para_shading(paragraph, fill):
    pPr = paragraph._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    pPr.append(shd)


def _cell_shading(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tcPr.append(shd)


def _para_border(paragraph, edges):
    """edges: dict like {'bottom': (color, size_eighths)}."""
    pPr = paragraph._p.get_or_add_pPr()
    pbdr = OxmlElement("w:pBdr")
    for edge, (color, sz) in edges.items():
        e = OxmlElement(f"w:{edge}")
        e.set(qn("w:val"), "single")
        e.set(qn("w:sz"), str(sz))
        e.set(qn("w:space"), "4")
        e.set(qn("w:color"), color)
        pbdr.append(e)
    pPr.append(pbdr)


def _table_borders(table, color=LINE, sz=4):
    tbl = table._tbl
    tblPr = tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{edge}")
        e.set(qn("w:val"), "single")
        e.set(qn("w:sz"), str(sz))
        e.set(qn("w:space"), "0")
        e.set(qn("w:color"), color)
        borders.append(e)
    tblPr.append(borders)


def _no_table_borders(table):
    tblPr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{edge}")
        e.set(qn("w:val"), "none")
        borders.append(e)
    tblPr.append(borders)


def _cell_margins(cell, top=60, bottom=60, left=120, right=120):
    tcPr = cell._tc.get_or_add_tcPr()
    m = OxmlElement("w:tcMar")
    for name, val in (("top", top), ("bottom", bottom), ("start", left), ("end", right)):
        node = OxmlElement(f"w:{name}")
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        m.append(node)
    tcPr.append(m)


def _vmerge(cell, restart=False):
    tcPr = cell._tc.get_or_add_tcPr()
    vm = OxmlElement("w:vMerge")
    vm.set(qn("w:val"), "restart" if restart else "continue")
    tcPr.append(vm)


# ---------------------------------------------------------- text builders ----
def runs(paragraph, text, *, font=BODY_FONT, size=11, color=CHARCOAL,
         bold=False, italic=False, caps=False, spacing=None):
    r = paragraph.add_run(text)
    r.font.name = font
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.color.rgb = RGBColor.from_string(color)
    if caps:
        r.font.all_caps = True
    if spacing is not None:  # letter spacing in twips
        rPr = r._r.get_or_add_rPr()
        sp = OxmlElement("w:spacing")
        sp.set(qn("w:val"), str(spacing))
        rPr.append(sp)
    # ensure east-asian/complex use same face
    rPr = r._r.get_or_add_rPr()
    rfonts = rPr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rPr.insert(0, rfonts)
    rfonts.set(qn("w:ascii"), font)
    rfonts.set(qn("w:hAnsi"), font)
    rfonts.set(qn("w:cs"), font)
    return r


def body_para(doc, text, *, size=11, color=CHARCOAL, space_after=8,
              space_before=0, justify=True, italic=False, line=1.12):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.line_spacing = line
    if justify:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    runs(p, text, size=size, color=color, italic=italic)
    return p


def bullet(doc, text, *, color=CHARCOAL, size=11):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.1
    # recolor the bullet glyph + text
    runs(p, text, size=size, color=color)
    return p


def section_heading(doc, text, *, space_before=18):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    runs(p, text, font=HEAD_FONT, size=15, color=NAVY, bold=True, spacing=6)
    _para_border(p, {"bottom": (RED, 12)})
    return p


def sub_heading(doc, text, *, space_before=10):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    runs(p, text, font=HEAD_FONT, size=12, color=RED, bold=True)
    return p


# ----------------------------------------------------------------- build ----
def build(path):
    doc = Document()

    # base style
    normal = doc.styles["Normal"]
    normal.font.name = BODY_FONT
    normal.font.size = Pt(11)
    normal.font.color.rgb = RGBColor.from_string(CHARCOAL)

    sec = doc.sections[0]
    sec.top_margin = Inches(0.7)
    sec.bottom_margin = Inches(0.7)
    sec.left_margin = Inches(0.9)
    sec.right_margin = Inches(0.9)

    # ---- title banner (single-cell navy table, full content width) --------
    page_w = sec.page_width - sec.left_margin - sec.right_margin
    banner = doc.add_table(rows=1, cols=1)
    banner.alignment = WD_TABLE_ALIGNMENT.CENTER
    banner.autofit = False
    banner.columns[0].width = page_w
    bcell = banner.rows[0].cells[0]
    bcell.width = page_w
    _cell_shading(bcell, NAVY)
    _cell_margins(bcell, top=240, bottom=240, left=300, right=300)
    _no_table_borders(banner)

    p = bcell.paragraphs[0]
    p.paragraph_format.space_after = Pt(2)
    runs(p, "U.S. ENERGY DEVELOPMENT CORP  ·  U.S. PROPERTY DEVELOPMENT",
         font=HEAD_FONT, size=9.5, color="AEB4C7", caps=True, spacing=20)

    p2 = bcell.add_paragraph()
    p2.paragraph_format.space_after = Pt(2)
    runs(p2, "Investment Committee Charter",
         font=HEAD_FONT, size=26, color=WHITE, bold=True)

    p3 = bcell.add_paragraph()
    p3.paragraph_format.space_after = Pt(0)
    runs(p3, "Real Estate Investment Committee  ·  Effective for the 2026 calendar year",
         font=BODY_FONT, size=10.5, color="D8DBE6")

    # thin red rule beneath banner
    rule = doc.add_paragraph()
    rule.paragraph_format.space_before = Pt(0)
    rule.paragraph_format.space_after = Pt(10)
    _para_border(rule, {"bottom": (RED, 18)})

    # ===================================================== PURPOSE (verbatim)
    section_heading(doc, "Purpose", space_before=2)
    body_para(doc,
        "The U.S. Property Development Investment Committee’s (IC) purpose is to "
        "review real estate investment opportunities and decide if they are viable "
        "options for investment.  The IC will evaluate the investment on its merits, "
        "including the risk/return characteristics, the availability of capital from "
        "U.S. Energy Development Corp, the ability to syndicate the opportunity, and "
        "consistency with the U.S. Property Development business plan.  The process "
        "will be flexible to accommodate different investment opportunities.  For "
        "example, in a development deal, the IC will first review the project in its "
        "planning stage.  At that time the IC will approve the investment thesis and "
        "approve a capital budget for land acquisition, soft costs, entitlements, ect.  "
        "When the preconstruction work is completed, the IC will again review the "
        "project to determine if it makes sense to proceed with the full investment "
        "and how to raise the capital.")

    # ============================================ VOTING / NONVOTING MEMBERS
    section_heading(doc, "Voting Members")
    member_table(doc, "Voting Member",
                 ["Jordan Jayson", "Matthew Iak", "Brandon Standifird", "Todd Van Pelt"])

    section_heading(doc, "Nonvoting Members")
    member_table(doc, "Nonvoting Member", ["TBD"])

    body_para(doc,
        "The U.S. Property Development Investment Committee consists of voting and "
        "nonvoting members representing a cross-section of departments. The IC is "
        "scheduled to meet every other week, depending on a quorum of voting members "
        "present and programs to review.  A quorum will be defined as greater than "
        "50% of the voting committee members.", space_before=6)
    body_para(doc,
        "Voting Members are appointed their expertise in their respective areas or "
        "general industry knowledge, to serve a perpetual term. If a voting member is "
        "unable to serve, they may request to be replaced.")
    body_para(doc,
        "Nonvoting members are selected for their expertise in their respective areas "
        "or general industry knowledge.  A nonvoting Committee member may be requested "
        "to attend some meetings but not necessarily all meetings.")
    body_para(doc,
        "All members receive full-time compensation from U.S. Energy Development Corp "
        "and shall serve with no additional compensation for the performance of their "
        "duties as members of the committee. The Committee may determine to reimburse "
        "members for expenses properly and incurred.")

    # ======================================================= RESPONSIBILITY
    section_heading(doc, "Responsibility")
    body_para(doc,
        "The U.S. Property Development team (USPD) will be responsible for running and "
        "scheduling the meeting.", space_after=4)
    for t in [
        "The USPD team will be responsible for reviewing, screening, and analyzing "
        "investment opportunities including relevant documents, market information, "
        "and related parties on any proposed real estate investment offerings.",
        "The USPD team will maintain copies of documents related to the investments "
        "being reviewed.",
        "They will present each investment opportunity to the IC for consideration.",
        "The presenter should prepare and deliver a presentation that includes all "
        "relevant information.  If available, presentation material will be sent at "
        "least one calendar day before the presentation to allow voting members time "
        "for review.",
        "The USPD will bring material updates for previously reviewed projects to keep "
        "the Voting Members up to date on the status.",
        "The USPD will execute the plan as established by the IC.",
    ]:
        bullet(doc, t)

    body_para(doc,
        "The Voting Members will vote to approve, reject, or defer investment "
        "opportunities.", space_before=4, space_after=4)
    for t in [
        "Voting Members are expected to review this material before the presentation.",
        "Voting Members are expected to communicate availability to the USPD team in "
        "advance when possible so that a meeting can be canceled/rescheduled when "
        "there is not a quorum.",
        "The Voting Members may defer some investments due to requesting additional "
        "information, timing a capital availability, or timing of the opportunity.",
        "The Voting Members can also determine the sources of capital for any given "
        "investment opportunity, including on the balance sheet of the Firm, investor "
        "capital, debt, or personal capital from executives.",
        "The Voting Members will likely approve individual deals with parameters.  For "
        "example regarding leverage, they can approve conditions or ranges for terms "
        "and conditions (rate, amortization, term, lender, etc.) and if the executed "
        "debt is within those parameters, the IC does not have to oversee the actual "
        "debt placement.",
    ]:
        bullet(doc, t)

    body_para(doc,
        "In the event a multi-property perpetual offering is established, some of "
        "these responsibilities may evolve.", space_before=4, space_after=4)
    for t in [
        "The Investment Committee may choose to define parameters for investment and a "
        "defined group may be allowed to act within those guidelines without bringing "
        "every deal to the Committee.",
        "All transactions that may appear to be affiliated or related will still be "
        "reviewed by the Committee.",
        "Depending upon the nature of the capital raise or bling pool status, "
        "additional capital considerations may need to be included.",
    ]:
        bullet(doc, t)

    # ===================================================== DECISION MAKING
    section_heading(doc, "Decision Making")
    body_para(doc,
        "The Investment Committee reaches each decision through a structured, "
        "data-driven workflow. An opportunity moves from the investment deck, through "
        "the firm’s integrated Deal Agents and the shared Claude Dropbox, into the IC "
        "Go/No-Go Dashboard, and finally to a recorded vote. The three stages below "
        "describe how a deal is located, validated, and scored before the Committee "
        "ever raises a motion.")

    process_band(doc)

    sub_heading(doc, "1.  Locating the deal in the PowerPoint deck")
    body_para(doc,
        "Every opportunity the IC reviews begins as a standardized investment deck — "
        "the U.S. Property Development Real Estate IC Deck (for example, the Hamburg "
        "Self-Storage Development and Springfield DST summaries). The USPD team uses "
        "the deck as the single source for locating and framing each deal. Every deck "
        "follows the same layout, so members find the same information in the same "
        "place every time: the deal name and location (county / CBSA), a Total "
        "Position Overview, the Target / Overview, the project site map, an IRR "
        "sensitivity analysis, and a one-page Investment Summary carrying the key "
        "takeaway, returns, and capitalization. When more than one opportunity is "
        "live, the deck presents them side by side — development vs. stabilized income, "
        "as with Hamburg vs. Springfield — so the Committee can locate and compare "
        "deals at a glance before any underwriting detail is opened.")

    sub_heading(doc, "2.  Integrated agents compare the data in the Claude Dropbox")
    body_para(doc,
        "All supporting material behind the deck — proformas, rent rolls, operating "
        "statements, market studies, maps, and parcel data — is placed into the shared "
        "Claude Dropbox folder for that deal. The firm’s integrated Deal Agents then "
        "read and compare any data implemented into the Dropbox. A deal-orchestrator "
        "coordinates specialized agents: a financial-analyst interprets the "
        "spreadsheets (returns, NOI, cap rates, LTV, yield on cost), a land-surveyor "
        "reads the maps and parcel / acreage data, and a deal-strategist tests the "
        "valuation and structure against the market. The agents cross-check the "
        "figures shown in the PowerPoint against the underlying files in the Dropbox "
        "and against the firm’s underwriting standards and its 246-county market "
        "dataset, flagging any discrepancy between what the deck claims and what the "
        "source data supports. Because the agents read directly from the Dropbox, any "
        "document the team drops in — or later updates — is automatically picked up and "
        "re-compared, so the Committee always reviews against the latest data.")

    sub_heading(doc, "3.  From the PowerPoint to the Go/No-Go spreadsheet")
    body_para(doc,
        "Once the agents have reconciled the deck against the Dropbox data, the "
        "validated figures are mapped into the IC Go/No-Go Dashboard. Each deal’s "
        "metrics — deal type, market / county, total cost, equity and debt, LTV, "
        "going-in and exit cap, NOI, yield on cost, development spread, unlevered and "
        "levered IRR, and net rentable square footage — populate the Deals tab. The "
        "Dashboard automatically pulls market benchmarks (population, five-year growth, "
        "supply pipeline, and county rank) from the Market Data tab, and the Scores tab "
        "applies the Committee’s standard gates: IRR beats the exit cap, yield clears "
        "the floor, op-ex in range, population at least 200,000, positive population "
        "growth, contained supply pipeline, return clears target, market in the upper "
        "half, and size near the 75,000-NRSF target. The model returns a Score out of "
        "100 and a verdict — GO (70+), CONDITIONAL GO (50–69), or NO-GO (below 50, or "
        "an automatic veto when a critical-fail gate is tripped) — and the Ranking tab "
        "orders every live deal by score. This Go/No-Go output is the quantitative "
        "recommendation the Committee carries into the vote; it informs the members’ "
        "judgment but does not replace it.")

    sub_heading(doc, "Voting")
    body_para(doc,
        "After a presentation, if a vote from the IC is required, a member will make a "
        "motion. A motion will be deemed passed when:", space_after=4)
    for t in [
        "If 4 Voting Members are present, 3 votes are needed to pass a motion; and",
        "If 3 Voting Members are present, 3 votes are needed to pass a motion.",
        "If 3 Voting Members are present and 2 votes for and 1 against, the motion is "
        "deemed automatically deferred until a larger group of Voting Members can be "
        "convened.",
        "Any voting combination that results in a motion not passing will be deemed "
        "declined. For example, if 3 Voting Members are present and 1 votes for and 2 "
        "against, the motion is determined to have failed.",
    ]:
        bullet(doc, t)
    body_para(doc,
        "A record of the meeting and votes will be maintained by the U.S. Property "
        "Development team. If for any reason an Investment Committee quorum is not "
        "available and a time-sensitive matter exists, the Investment Committee may "
        "choose to meet virtually via email correspondence.", space_before=4)

    # ===================================================== LIFE EXPECTANCY
    section_heading(doc, "Life Expectancy")
    body_para(doc,
        "The U.S. Property Development Investment Committee is established as a "
        "standing, perpetual committee of U.S. Energy Development Corp. It remains in "
        "effect until it is dissolved or restructured by U.S. Energy Development Corp "
        "leadership.", space_after=4)
    for t in [
        "This Charter is effective for the 2026 calendar year and renews automatically "
        "each year unless amended.",
        "The Committee — its membership, quorum thresholds, scoring gates, and decision "
        "workflow — will be reviewed at least annually and may be updated by leadership "
        "as the U.S. Property Development platform, its deal pipeline, and its data and "
        "agent tooling evolve.",
        "Should a multi-property or perpetual offering be established, the Committee’s "
        "mandate and life may be extended or modified accordingly, with any change "
        "documented in an updated Charter.",
    ]:
        bullet(doc, t)

    # ======================================================= COMMUNICATION
    section_heading(doc, "Communication")
    body_para(doc,
        "The U.S. Property Development team is responsible for communicating the "
        "Committee’s decisions to every department affected by them.", space_after=4)
    for t in [
        "Each decision — GO, CONDITIONAL GO, NO-GO, or deferral — is communicated "
        "together with the deal’s Go/No-Go score, the deciding factors, and any "
        "conditions or parameters the Committee attached.",
        "The investment deck, the supporting files in the Claude Dropbox, and the "
        "Go/No-Go Dashboard output are retained as the official record of what was "
        "presented and decided, alongside the meeting minutes and vote tally "
        "maintained by the USPD team.",
        "Because the responsible team or department for executing a decision varies by "
        "opportunity and task, the Committee will clarify and communicate "
        "responsibilities as delegated, and the USPD team will confirm receipt and "
        "track execution against the parameters the Committee set.",
        "Material updates on previously approved deals are reported back to the Voting "
        "Members on the regular meeting cadence, closing the loop between decision and "
        "execution.",
    ]:
        bullet(doc, t)

    # footer
    add_footer(doc)

    doc.save(path)
    return path


def member_table(doc, header, names):
    """Two-column branded roster: navy header, cream alt rows."""
    sec = doc.sections[0]
    page_w = sec.page_width - sec.left_margin - sec.right_margin
    col1 = int(page_w * 0.55)
    col2 = page_w - col1

    t = doc.add_table(rows=1 + len(names), cols=2)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    _table_borders(t, color=LINE, sz=4)

    # header
    h0, h1 = t.rows[0].cells
    for c, label in ((h0, header), (h1, "Title / Department")):
        c.width = col1 if c is h0 else col2
        _cell_shading(c, NAVY)
        _cell_margins(c)
        p = c.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        runs(p, label, font=HEAD_FONT, size=10.5, color=WHITE, bold=True, caps=True, spacing=8)

    for i, name in enumerate(names):
        c0, c1 = t.rows[i + 1].cells
        fill = WHITE if i % 2 == 0 else CREAM
        for c, txt, col in ((c0, name, NAVY), (c1, "", CHARCOAL)):
            c.width = col1 if c is c0 else col2
            _cell_shading(c, fill)
            _cell_margins(c)
            p = c.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            runs(p, txt, size=11, color=col, bold=(c is c0))
    # spacer
    sp = doc.add_paragraph()
    sp.paragraph_format.space_after = Pt(2)
    return t


def process_band(doc):
    """Three-step PowerPoint -> Agents/Dropbox -> Go/No-Go visual strip."""
    sec = doc.sections[0]
    page_w = sec.page_width - sec.left_margin - sec.right_margin
    steps = [
        ("1", "LOCATE", "PowerPoint IC deck frames each deal"),
        ("2", "COMPARE", "Integrated agents reconcile Claude Dropbox data"),
        ("3", "SCORE", "Go/No-Go Dashboard returns the verdict"),
    ]
    t = doc.add_table(rows=1, cols=3)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    _no_table_borders(t)
    cw = int(page_w / 3)
    for i, (num, title, desc) in enumerate(steps):
        cell = t.rows[0].cells[i]
        cell.width = cw
        _cell_shading(cell, NAVY if i == 1 else CREAM)
        _cell_margins(cell, top=120, bottom=120, left=140, right=140)
        on_navy = (i == 1)
        num_col = WHITE if on_navy else RED
        title_col = WHITE if on_navy else NAVY
        desc_col = "D8DBE6" if on_navy else SLATE

        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_after = Pt(1)
        runs(p, f"STEP {num}", font=HEAD_FONT, size=9, color=num_col, bold=True, caps=True, spacing=14)
        p2 = cell.add_paragraph()
        p2.paragraph_format.space_after = Pt(2)
        runs(p2, title, font=HEAD_FONT, size=13, color=title_col, bold=True, spacing=4)
        p3 = cell.add_paragraph()
        p3.paragraph_format.space_after = Pt(0)
        p3.paragraph_format.line_spacing = 1.0
        runs(p3, desc, size=9.5, color=desc_col)
    sp = doc.add_paragraph()
    sp.paragraph_format.space_after = Pt(6)
    return t


def add_footer(doc):
    footer = doc.sections[0].footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    runs(p, "U.S. Property Development  ·  Investment Committee Charter  ·  Confidential",
         font=BODY_FONT, size=8.5, color=SLATE, caps=False, spacing=6)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "IC_Response.docx"
    build(out)
    print(f"wrote {out}")
