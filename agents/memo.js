const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat, TabStopType, TabStopPosition,
  HeadingLevel, BorderStyle, WidthType, ShadingType, VerticalAlign,
  PageNumber, PageBreak
} = require("docx");

// House palette
const NAVY = "12263A", STEEL = "2E5266", GOLD = "C8A04B";
const LIGHT = "EDF1F5", GREYLINE = "CCCCCC";

const CONTENT_W = 9360;

// ---- deal data (from IC drafter's deal.json; Hamburg fallbacks) ----
let D = {};
try { D = JSON.parse(fs.readFileSync(__dirname + "/deal.json", "utf8")); } catch (e) {}
const dv = (k, fb) => (D[k] != null ? D[k] : fb);
const levIRR = dv("levered_irr", "~18.5%"), unlevIRR = dv("unlevered_irr", "~17.7%");
const totalCap = dv("total_cap", "~$10.0M"), exitVal = dv("exit_value", "~$13.3M");
const noiStr = dv("noi", "~$669K"), exitCap = dv("exit_cap", "5.5%");
const pctComplete = dv("pct_complete", "61%"), remaining = dv("remaining", "$3.44M"), committed = dv("committed", "$8.90M");
const devBudget = dv("dev_budget", "$9.57M"), equityStr = dv("equity", "$5.77M"), debtStr = dv("debt", "$4.26M"), debtRate = dv("debt_rate", "6.5%");
const gpPct = dv("gp_pct", "11%"), lpPct = dv("lp_pct", "89%");
const acres = dv("acres", "11.16"), nrsf = dv("nrsf", "63,500"), units = dv("units", "544");
const ccSf = dv("cc_sf", "37,090"), nccSf = dv("ncc_sf", "26,450"), changeOrders = dv("change_orders", "$224,963");
const ccRate = dv("cc_rate", "$18.49"), nccRate = dv("ncc_rate", "$14.27");

const cellBorder = { style: BorderStyle.SINGLE, size: 1, color: GREYLINE };
const borders = { top: cellBorder, bottom: cellBorder, left: cellBorder, right: cellBorder };
const pad = { top: 80, bottom: 80, left: 120, right: 120 };

function txt(text, opts = {}) { return new TextRun({ text, font: "Calibri", ...opts }); }

function cell(content, { w, fill, bold, color, align, header } = {}) {
  const runs = Array.isArray(content) ? content : [content];
  return new TableCell({
    borders, width: { size: w, type: WidthType.DXA }, margins: pad,
    verticalAlign: VerticalAlign.CENTER,
    shading: fill ? { fill, type: ShadingType.CLEAR } : undefined,
    children: [new Paragraph({
      alignment: align || AlignmentType.LEFT,
      children: runs.map(r => typeof r === "string"
        ? txt(r, { bold: !!bold || !!header, color: color || (header ? "FFFFFF" : undefined), size: 20 })
        : r)
    })]
  });
}

function headerRow(labels, widths) {
  return new TableRow({
    tableHeader: true,
    children: labels.map((l, i) => cell(l, { w: widths[i], fill: NAVY, header: true }))
  });
}

function bodyRow(values, widths, alt) {
  return new TableRow({
    children: values.map((v, i) => cell(v, { w: widths[i], fill: alt ? LIGHT : undefined }))
  });
}

function h1(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text, font: "Cambria", color: NAVY })] });
}
function h2(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text, font: "Cambria", color: STEEL })] });
}
function body(text) {
  return new Paragraph({ spacing: { after: 120 }, children: [txt(text, { size: 22 })] });
}
function bullet(runsOrText) {
  const runs = Array.isArray(runsOrText) ? runsOrText : [txt(runsOrText, { size: 22 })];
  return new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 40 }, children: runs });
}
function label(text) {
  return new TextRun({ text, font: "Calibri", bold: true, color: STEEL, size: 22 });
}
function tbd(text) { return new TextRun({ text, font: "Calibri", italics: true, color: "B05A00", size: 22 }); }

const PLACEHOLDER = () => tbd("[TBD]");

const doc = new Document({
  creator: "D1 Real Estate",
  styles: {
    default: { document: { run: { font: "Calibri", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 30, bold: true, font: "Cambria", color: NAVY },
        paragraph: { spacing: { before: 280, after: 140 }, outlineLevel: 0,
          border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: GOLD, space: 4 } } } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: "Cambria", color: STEEL },
        paragraph: { spacing: { before: 180, after: 100 }, outlineLevel: 1 } },
    ]
  },
  numbering: {
    config: [
      { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 460, hanging: 260 } } } }] },
      { reference: "conds", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 460, hanging: 260 } } } }] },
    ]
  },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    headers: { default: new Header({ children: [new Paragraph({
      tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
      border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: NAVY, space: 2 } },
      children: [
        new TextRun({ text: "D1 REAL ESTATE", font: "Cambria", bold: true, color: NAVY, size: 18 }),
        new TextRun({ text: "  \u00B7  Rgentic", font: "Calibri", color: STEEL, size: 16 }),
        new TextRun({ text: "\tINVESTMENT COMMITTEE \u2014 CONFIDENTIAL", font: "Calibri", color: STEEL, size: 16 }),
      ]
    })] }) },
    footers: { default: new Footer({ children: [new Paragraph({
      tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
      children: [
        new TextRun({ text: "IC Memorandum \u00B7 Draft for review", font: "Calibri", color: "888888", size: 16 }),
        new TextRun({ text: "\tPage ", font: "Calibri", color: "888888", size: 16 }),
        new TextRun({ children: [PageNumber.CURRENT], font: "Calibri", color: "888888", size: 16 }),
      ]
    })] }) },
    children: [
      // ===== TITLE BLOCK =====
      new Paragraph({ spacing: { before: 120, after: 40 }, children: [
        new TextRun({ text: "Investment Committee Memorandum", font: "Cambria", bold: true, color: NAVY, size: 40 }) ] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun({ text: "Hamburg Self-Storage Development \u2014 Anchor Asset", font: "Cambria", color: STEEL, size: 26 }) ] }),

      new Table({
        width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: [2340, 2340, 2340, 2340],
        rows: [
          new TableRow({ children: [
            cell([label("Deal"), txt("  Hamburg Self-Storage", { size: 20 })], { w: 4680, fill: LIGHT }),
            cell([label("IC Date"), new TextRun({ text: "  ", size: 20 }), PLACEHOLDER()], { w: 4680, fill: LIGHT }),
          ]}),
          new TableRow({ children: [
            cell([label("Sponsor"), txt("  D1 Real Estate", { size: 20 })], { w: 4680 }),
            cell([label("Prepared by"), new TextRun({ text: "  ", size: 20 }), PLACEHOLDER()], { w: 4680 }),
          ]}),
          new TableRow({ children: [
            cell([label("Market"), txt("  Hamburg, NY (Erie County)", { size: 20 })], { w: 4680, fill: LIGHT }),
            cell([label("Stage"), txt("  In construction (~61% complete)", { size: 20 })], { w: 4680, fill: LIGHT }),
          ]}),
          new TableRow({ children: [
            cell([label("Recommendation"), new TextRun({ text: "  ", size: 20 }),
              new TextRun({ text: "GO / NO-GO", font: "Calibri", bold: true, color: NAVY, size: 22 })], { w: 4680 }),
            cell([label("Levered IRR"), new TextRun({ text: "  ", size: 20 }),
              new TextRun({ text: levIRR + "  (unlevered " + unlevIRR + ")", font: "Calibri", size: 20 })], { w: 4680 }),
          ]}),
        ]
      }),

      // ===== 1. RECOMMENDATION =====
      h1("1.  Recommendation & Summary"),
      new Paragraph({ spacing: { before: 80, after: 120 }, shading: { fill: LIGHT, type: ShadingType.CLEAR },
        border: { left: { style: BorderStyle.SINGLE, size: 18, color: GOLD, space: 8 } }, children: [
        new TextRun({ text: "Recommendation:  ", font: "Calibri", bold: true, color: NAVY, size: 22 }),
        new TextRun({ text: "GO / NO-GO \u2014 ", font: "Calibri", bold: true, size: 22 }),
        tbd("one-line rationale (e.g. \u201Clevered IRR ~18.5%, well above the >4% floor; project ~61% complete and on-plan\u201D)") ]}),
      body("This memorandum presents the Hamburg, NY self-storage development \u2014 the anchor asset in D1\u2019s storage program \u2014 for Investment Committee review. The ground-up project (" + acres + " acres; ~" + nrsf + " net rentable SF across " + ccSf + " climate-controlled and " + nccSf + " non-climate SF; " + units + " units) is currently in construction at roughly " + pctComplete + " of committed cost. It underwrites to a levered IRR of approximately " + levIRR.replace("~", "") + " (unlevered " + unlevIRR + ")."),
      h2("Key takeaways"),
      bullet([label("Strategic fit:  "), tbd("anchor asset for the WNY storage program?")]),
      bullet([label("Return:  "), txt("Levered IRR " + levIRR + ", unlevered " + unlevIRR + " \u2014 well above the >4% internal floor. Stabilized NOI " + noiStr + "; exit value " + exitVal + " at a " + exitCap + " cap.", { size: 22 })]),
      bullet([label("Status:  "), txt("~" + pctComplete + " complete by cost; " + remaining + " of " + committed + " committed remaining.", { size: 22 })]),
      bullet([label("Primary risk:  "), txt("cost overrun \u2014 " + changeOrders + " of change orders to date (unsuitable soils / over-excavation); ", { size: 22 }), tbd("plus lease-up & market saturation")]),

      // ===== 2. OPPORTUNITY OVERVIEW =====
      h1("2.  Opportunity Overview"),
      body("Ground-up development of a self-storage facility in Hamburg, NY (Erie County). Total development budget is approximately " + devBudget + " (" + committed + " of committed construction cost), with total capitalization near " + totalCap + ". The project is currently in construction at roughly " + pctComplete + " of committed cost."),
      new Table({
        width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: [3120, 6240],
        rows: [
          headerRow(["Item", "Detail"], [3120, 6240]),
          bodyRow(["Asset type", "Self-storage development (climate + non-climate controlled)"], [3120, 6240], false),
          bodyRow([[label("Location / site")], ["Hamburg, NY (Erie County) \u00B7 " + acres + " acres"]], [3120, 6240], true),
          bodyRow([[label("Program")], ["~" + nrsf + " NRSF \u2014 " + ccSf + " CC SF + ~" + nccSf + " NCC SF; " + units + " units"]], [3120, 6240], false),
          bodyRow([[label("Development budget")], ["~" + devBudget + " (" + committed + " committed construction cost)"]], [3120, 6240], true),
          bodyRow([[label("Total capitalization")], ["~" + totalCap]], [3120, 6240], false),
          bodyRow([[label("Capital stack")], ["Equity ~" + equityStr + " (GP " + gpPct + " / LP " + lpPct + ") + perm debt ~" + debtStr + " @ " + debtRate]], [3120, 6240], true),
        ]
      }),
      new Paragraph({ spacing: { before: 160, after: 60 }, children: [ label("Construction status (latest snapshot)") ]}),
      body("~" + pctComplete + " complete by cost, with " + remaining + " of " + committed + " committed remaining to be paid. Change orders total " + changeOrders + ", driven by unsuitable-soils and over-excavation conditions."),

      // ===== 3. STRATEGIC FIT =====
      h1("3.  Strategic Fit"),
      body("Does this business plan support and extend the existing modular-homes + storage-unit platform?"),
      bullet([label("Platform synergy:  "), tbd("how the acquisition reinforces the existing book")]),
      bullet([label("Geographic fit:  "), txt("WNY footprint (Lewiston / Hamburg / ACV). ", { size: 22 }), tbd("note clustering / operating leverage")]),
      bullet([label("Scalability:  "), tbd("is this a repeatable template for future sites?")]),

      // ===== 4. MARKET OPPORTUNITY =====
      h1("4.  Market Opportunity"),
      new Table({
        width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: [3120, 6240],
        rows: [
          headerRow(["Dimension", "Assessment"], [3120, 6240]),
          bodyRow([[label("Market size")], [PLACEHOLDER()]], [3120, 6240], false),
          bodyRow([[label("Growth rate")], [tbd("can mod-home / storage grow at a steady rate?")]], [3120, 6240], true),
          bodyRow([[label("Competitive landscape")], [tbd("what do our competitors look like?")]], [3120, 6240], false),
          bodyRow([[label("Avg cost / unit economics")], [PLACEHOLDER()]], [3120, 6240], true),
          bodyRow([[label("Industry trends")], [PLACEHOLDER()]], [3120, 6240], false),
        ]
      }),

      // ===== 5. MANAGEMENT TEAM =====
      h1("5.  Management Team"),
      body("Assessment of the operating team\u2019s track record and ability to execute the business plan."),
      bullet([label("Track record:  "), tbd("how has the team performed on previous projects / facilities?")]),
      bullet([label("Industry experience:  "), PLACEHOLDER()]),
      bullet([label("Reference & background checks:  "), tbd("status / findings")]),

      // ===== 6. FINANCIAL PROFILE =====
      h1("6.  Financial Profile"),
      body("Returns are the core of the IC decision. The internal screen rejects opportunities below a ~4% return; this project underwrites well above that."),
      new Table({
        width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: [3120, 2080, 2080, 2080],
        rows: [
          headerRow(["Metric", "Underwrite", "Floor", "Source"], [3120, 2080, 2080, 2080]),
          new TableRow({ children: [
            cell([label("Levered IRR")], { w: 3120 }), cell(levIRR, { w: 2080, align: AlignmentType.CENTER }),
            cell(">4%", { w: 2080, align: AlignmentType.CENTER }), cell("Zach Model", { w: 2080, align: AlignmentType.CENTER }) ]}),
          new TableRow({ children: [
            cell([label("Unlevered IRR")], { w: 3120, fill: LIGHT }), cell(unlevIRR, { w: 2080, fill: LIGHT, align: AlignmentType.CENTER }),
            cell("\u2014", { w: 2080, fill: LIGHT, align: AlignmentType.CENTER }), cell("Zach Model", { w: 2080, fill: LIGHT, align: AlignmentType.CENTER }) ]}),
          new TableRow({ children: [
            cell([label("Stabilized NOI")], { w: 3120 }), cell(noiStr, { w: 2080, align: AlignmentType.CENTER }),
            cell("\u2014", { w: 2080, align: AlignmentType.CENTER }), cell("Pro forma", { w: 2080, align: AlignmentType.CENTER }) ]}),
          new TableRow({ children: [
            cell([label("Exit value (" + exitCap + " cap)")], { w: 3120, fill: LIGHT }), cell(exitVal, { w: 2080, fill: LIGHT, align: AlignmentType.CENTER }),
            cell("\u2014", { w: 2080, fill: LIGHT, align: AlignmentType.CENTER }), cell("Pro forma", { w: 2080, fill: LIGHT, align: AlignmentType.CENTER }) ]}),
          new TableRow({ children: [
            cell([label("Development budget")], { w: 3120 }), cell(devBudget, { w: 2080, align: AlignmentType.CENTER }),
            cell("\u2014", { w: 2080, align: AlignmentType.CENTER }), cell("Budget Hist.", { w: 2080, align: AlignmentType.CENTER }) ]}),
          new TableRow({ children: [
            cell([label("Stabilized yield on cost")], { w: 3120, fill: LIGHT }), cell([tbd("confirm")], { w: 2080, fill: LIGHT, align: AlignmentType.CENTER }),
            cell("\u2014", { w: 2080, fill: LIGHT, align: AlignmentType.CENTER }), cell([tbd("\u2014")], { w: 2080, fill: LIGHT, align: AlignmentType.CENTER }) ]}),
        ]
      }),
      new Paragraph({ spacing: { before: 120 }, children: [
        label("Underwriting evolution:  "),
        txt("Levered IRR has moved from ~" + (D.irr_stages ? D.irr_stages["Initial feas."] : 20.1) + "% (initial feasibility) to ~" + (D.irr_stages ? D.irr_stages["Final feas."] : 18.9) + "% (final feasibility) to " + levIRR + " in the current model \u2014 a tightening worth noting to the committee. Rents underwritten at " + ccRate + "/SF (CC) and " + nccRate + "/SF (NCC).", { size: 22 }) ]}),

      // ===== 7. RISK PROFILE =====
      h1("7.  Risk Profile & Mitigants"),
      new Table({
        width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: [3120, 3120, 3120],
        rows: [
          headerRow(["Risk", "Description", "Mitigant"], [3120, 3120, 3120]),
          bodyRow([["Construction cost overrun"], [changeOrders + " change orders to date (unsuitable soils / over-excavation)"], [tbd("$400K hard-cost contingency; ~" + pctComplete + " complete de-risks remainder")]], [3120, 3120, 3120], false),
          bodyRow([["Lease-up / absorption"], [tbd("speed to stabilized occupancy across " + units + " units")], [PLACEHOLDER()]], [3120, 3120, 3120], true),
          bodyRow([["Market saturation"], ["Erie County ranks #200/246 on the development model; pipeline ~22%"], [tbd("infill location / unit mix")]], [3120, 3120, 3120], false),
          bodyRow([["Refinance / rate"], ["Perm debt ~" + debtStr + " @ " + debtRate], [PLACEHOLDER()]], [3120, 3120, 3120], true),
          bodyRow([["Dependency"], [tbd("single-asset \u2014 anchor of a broader program")], [PLACEHOLDER()]], [3120, 3120, 3120], false),
        ]
      }),

      // ===== 8. DUE DILIGENCE =====
      new Paragraph({ children: [new PageBreak()] }),
      h1("8.  Due Diligence \u2014 Deep Dive"),
      body("Why we accepted this deal, and what we passed on \u2014 the comparison that frames the recommendation."),
      h2("What we accepted (and why)"),
      bullet([tbd("this deal cleared the return floor, fit the platform, repeatable IRR \u2014 fill in")]),
      h2("What we passed on (and why)"),
      new Table({
        width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: [2600, 3380, 3380],
        rows: [
          headerRow(["Opportunity", "Reason passed", "Lens that flagged it"], [2600, 3380, 3380]),
          bodyRow([[PLACEHOLDER()], [tbd("e.g. <4% return")], ["Financial Profile"]], [2600, 3380, 3380], false),
          bodyRow([[PLACEHOLDER()], [PLACEHOLDER()], [PLACEHOLDER()]], [2600, 3380, 3380], true),
          bodyRow([[PLACEHOLDER()], [PLACEHOLDER()], [PLACEHOLDER()]], [2600, 3380, 3380], false),
        ]
      }),
      h2("Diligence completed by workstream"),
      bullet([label("Strategic fit diligence:  "), tbd("would the business plan support the existing platform?")]),
      bullet([label("Market opportunity diligence:  "), tbd("steady growth? competitor set? avg cost?")]),
      bullet([label("Management team diligence:  "), tbd("reference checks on facility performance, background checks")]),
      bullet([label("Financial diligence:  "), tbd("audit review per unit, EBITDA review, forecast review")]),
      bullet([label("Risk diligence:  "), tbd("legal review, customer concentration, regulatory issues")]),

      // ===== 9. RECOMMENDATION & NEXT STEPS =====
      h1("9.  Recommendation, Conditions & Next Steps"),
      body("Subject to IC approval, the following conditions and next steps apply prior to Board approval:"),
      new Paragraph({ numbering: { reference: "conds", level: 0 }, spacing: { after: 40 }, children: [tbd("Condition precedent (e.g. final financing terms confirmed)")] }),
      new Paragraph({ numbering: { reference: "conds", level: 0 }, spacing: { after: 40 }, children: [tbd("Condition precedent (e.g. close outstanding diligence items)")] }),
      new Paragraph({ numbering: { reference: "conds", level: 0 }, spacing: { after: 40 }, children: [tbd("Next step \u2192 Board approval")] }),
      new Paragraph({ spacing: { before: 200, after: 60 }, children: [ label("IC decision") ]}),
      new Table({
        width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: [3120, 3120, 3120],
        rows: [
          new TableRow({ children: [
            cell("Approve", { w: 3120, align: AlignmentType.CENTER, bold: true }),
            cell("Approve w/ conditions", { w: 3120, align: AlignmentType.CENTER, bold: true }),
            cell("Decline", { w: 3120, align: AlignmentType.CENTER, bold: true }) ]}),
          new TableRow({ children: [
            cell(" ", { w: 3120 }), cell(" ", { w: 3120 }), cell(" ", { w: 3120 }) ]}),
        ]
      }),
    ]
  }]
});

Packer.toBuffer(doc).then(buf => { fs.writeFileSync(require("path").join(__dirname, "out", "IC_Memo.docx"), buf); console.log("memo written"); });
