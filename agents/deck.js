const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const {
  FaMapMarkerAlt, FaPuzzlePiece, FaChartLine, FaUsers, FaCoins, FaShieldAlt,
  FaCheckCircle, FaTimesCircle, FaArrowRight, FaSearchDollar, FaGavel, FaWarehouse
} = require("react-icons/fa");

// ---- House palette ----
const NAVY = "12263A", STEEL = "2E5266", GOLD = "C8A04B";
const INK = "1B2733", MUTE = "5B6B7A", LINE = "DCE3EA", PAPER = "FFFFFF", TINT = "EEF2F6";
const HEAD = "Cambria", BODY = "Calibri";

// ---- deal data (from IC drafter's deal.json; falls back to Hamburg defaults) ----
const fs = require("fs");
let D = {};
try { D = JSON.parse(fs.readFileSync(__dirname + "/deal.json", "utf8")); } catch (e) {}
const dv = (k, fb) => (D[k] != null ? D[k] : fb);
const dealName = dv("name", "Hamburg Self-Storage");
const levIRR = dv("levered_irr", "~18.5%"), unlevIRR = dv("unlevered_irr", "~17.7%");
const totalCap = dv("total_cap", "$10.0M"), exitVal = dv("exit_value", "$13.3M");
const noiStr = dv("noi", "$669K"), exitCap = dv("exit_cap", "5.5%");
const pctComplete = dv("pct_complete", "61%"), remaining = dv("remaining", "$3.44M");
const committed = dv("committed", "$8.9M"), devBudget = dv("dev_budget", "$9.57M");
const equityStr = dv("equity", "$5.77M"), debtStr = dv("debt", "$4.26M"), debtRate = dv("debt_rate", "6.5%");
const gpPct = dv("gp_pct", "11%"), lpPct = dv("lp_pct", "89%");
const acres = dv("acres", "11.16"), nrsf = dv("nrsf", "63,500"), units = dv("units", "544");
const ccSf = dv("cc_sf", "37,090"), nccSf = dv("ncc_sf", "26,450"), changeOrders = dv("change_orders", "$224,963");
const irrStages = dv("irr_stages", { "Initial feas.": 20.1, "Final feas.": 18.9, "PPM": 16.9, "Current": 18.5 });

async function icon(Comp, color, size = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(Comp, { color, size: String(size) }));
  const png = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + png.toString("base64");
}

const mkShadow = () => ({ type: "outer", color: "000000", blur: 7, offset: 3, angle: 90, opacity: 0.12 });

(async () => {
  const I = {
    pin: await icon(FaMapMarkerAlt, "#" + GOLD),
    fit: await icon(FaPuzzlePiece, "#" + STEEL),
    mkt: await icon(FaChartLine, "#" + STEEL),
    team: await icon(FaUsers, "#" + STEEL),
    fin: await icon(FaCoins, "#" + STEEL),
    risk: await icon(FaShieldAlt, "#" + STEEL),
    check: await icon(FaCheckCircle, "#2E7D52"),
    x: await icon(FaTimesCircle, "#B23A3A"),
    dd: await icon(FaSearchDollar, "#" + GOLD),
    gold_fit: await icon(FaPuzzlePiece, "#" + GOLD),
    gold_mkt: await icon(FaChartLine, "#" + GOLD),
    gold_team: await icon(FaUsers, "#" + GOLD),
    gold_fin: await icon(FaCoins, "#" + GOLD),
    gold_risk: await icon(FaShieldAlt, "#" + GOLD),
    house: await icon(FaWarehouse, "#" + GOLD),
  };

  const p = new pptxgen();
  p.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
  p.author = "D1 Real Estate";
  p.title = "IC Review \u2014 Modular Homes & Storage";
  const W = 13.33, H = 7.5;

  // ---------- helpers ----------
  function kicker(s, txt, x = 0.7, color = GOLD) {
    s.addText(txt.toUpperCase(), { x, y: 0.52, w: 8, h: 0.3, fontFace: BODY, fontSize: 12, bold: true, color, charSpacing: 3, margin: 0 });
  }
  function title(s, txt, x = 0.7, w = 12) {
    s.addText(txt, { x, y: 0.82, w, h: 0.8, fontFace: HEAD, fontSize: 32, bold: true, color: NAVY, margin: 0 });
  }
  function footer(s, n) {
    s.addText("D1 Real Estate \u00B7 Investment Committee \u2014 Confidential", { x: 0.7, y: 7.06, w: 9, h: 0.3, fontFace: BODY, fontSize: 9, color: MUTE, margin: 0 });
    s.addText(String(n), { x: 12.4, y: 7.06, w: 0.4, h: 0.3, fontFace: BODY, fontSize: 9, color: MUTE, align: "right", margin: 0 });
  }
  function tbd(t) { return { text: t, options: { italic: true, color: "B05A00" } }; }

  // ============================================================ 1 TITLE
  let s = p.addSlide();
  s.background = { color: NAVY };
  s.addShape(p.shapes.RECTANGLE, { x: 0, y: 0, w: W, h: 0.12, fill: { color: GOLD } });
  s.addText("D1 REAL ESTATE", { x: 0.8, y: 0.7, w: 8, h: 0.3, fontFace: HEAD, fontSize: 14, bold: true, color: "FFFFFF", charSpacing: 4, margin: 0 });
  s.addText("Rgentic", { x: 0.8, y: 1.02, w: 8, h: 0.3, fontFace: BODY, fontSize: 12, color: GOLD, margin: 0 });
  s.addImage({ data: I.house, x: 11.4, y: 0.66, w: 1.0, h: 1.0 });

  s.addText("INVESTMENT COMMITTEE REVIEW", { x: 0.8, y: 2.85, w: 11, h: 0.4, fontFace: BODY, fontSize: 15, bold: true, color: GOLD, charSpacing: 3, margin: 0 });
  s.addText(dealName + " Development", { x: 0.8, y: 3.3, w: 11.7, h: 1.1, fontFace: HEAD, fontSize: 44, bold: true, color: "FFFFFF", margin: 0 });
  s.addText("Anchor Asset \u00B7 D1 Storage Program \u2014 Go / No-Go Decision", { x: 0.8, y: 4.45, w: 11, h: 0.5, fontFace: BODY, fontSize: 20, color: "C7D2DC", margin: 0 });

  // key facts row
  const facts0 = [["Hamburg, NY", I.pin], ["~" + nrsf + " NRSF \u00B7 " + units + " units", I.house], [acres + " acres", I.mkt]];
  facts0.forEach(([t, ic], i) => {
    const x = 0.8 + i * 4.0;
    s.addImage({ data: ic, x, y: 5.55, w: 0.32, h: 0.32 });
    s.addText(t, { x: x + 0.42, y: 5.54, w: 3.5, h: 0.34, fontFace: BODY, fontSize: 14, color: "FFFFFF", valign: "middle", margin: 0 });
  });
  s.addText([{ text: "Status:  ", options: { color: "8FA0AF" } }, { text: "In construction \u2014 ~" + pctComplete + " complete \u00B7 levered IRR " + levIRR, options: { color: "FFFFFF" } }],
    { x: 0.8, y: 6.35, w: 11, h: 0.4, fontFace: BODY, fontSize: 13, margin: 0 });

  // ============================================================ 2 RECOMMENDATION
  s = p.addSlide(); s.background = { color: PAPER };
  kicker(s, "Section 1"); title(s, "Recommendation & Summary");

  // recommendation banner
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 0.7, y: 1.75, w: 11.93, h: 1.0, fill: { color: NAVY }, rectRadius: 0.08, shadow: mkShadow() });
  s.addText("RECOMMENDATION", { x: 1.0, y: 1.95, w: 3, h: 0.3, fontFace: BODY, fontSize: 12, bold: true, color: GOLD, charSpacing: 2, margin: 0 });
  s.addText([{ text: "GO / NO-GO", options: { bold: true, color: "FFFFFF" } }, { text: "   \u2014   ", options: { color: "8FA0AF" } }, tbd("rationale: levered IRR " + levIRR + ", well above the >4% floor; ~" + pctComplete + " built and on-plan")],
    { x: 1.0, y: 2.24, w: 11.3, h: 0.45, fontFace: HEAD, fontSize: 19, valign: "middle", margin: 0 });

  // 4 stat cards
  const stats = [
    { k: "LEVERED IRR", v: levIRR.replace("~", ""), sub: "unlevered " + unlevIRR },
    { k: "TOTAL CAP", v: totalCap, sub: "equity " + equityStr + " + debt" },
    { k: "EXIT VALUE", v: exitVal, sub: "NOI ~" + noiStr + " @ " + exitCap },
    { k: "COMPLETE", v: pctComplete, sub: remaining + " remaining" },
  ];
  const cw = 2.85, gap = 0.21, x0 = 0.7;
  stats.forEach((c, i) => {
    const x = x0 + i * (cw + gap);
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y: 3.05, w: cw, h: 1.55, fill: { color: TINT }, rectRadius: 0.06 });
    s.addText(c.k, { x: x + 0.18, y: 3.22, w: cw - 0.36, h: 0.3, fontFace: BODY, fontSize: 10.5, bold: true, color: STEEL, charSpacing: 1, margin: 0 });
    s.addText(c.v, { x: x + 0.18, y: 3.5, w: cw - 0.36, h: 0.7, fontFace: HEAD, fontSize: 40, bold: true, color: NAVY, margin: 0 });
    s.addText(c.sub, { x: x + 0.18, y: 4.22, w: cw - 0.36, h: 0.3, fontFace: BODY, fontSize: 11, color: MUTE, margin: 0 });
  });

  // key takeaways
  s.addText("KEY TAKEAWAYS", { x: 0.7, y: 4.95, w: 6, h: 0.3, fontFace: BODY, fontSize: 12, bold: true, color: GOLD, charSpacing: 2, margin: 0 });
  const takes = [
    [{ text: "Return \u2014 ", options: { bold: true, color: INK } }, { text: "levered IRR " + levIRR + " (unlevered " + unlevIRR + "), far above the >4% floor", options: { color: INK } }],
    [{ text: "Value \u2014 ", options: { bold: true, color: INK } }, { text: "stabilized NOI ~" + noiStr + "; exit value " + exitVal + " at a " + exitCap + " cap", options: { color: INK } }],
    [{ text: "Status \u2014 ", options: { bold: true, color: INK } }, { text: "~" + pctComplete + " complete by cost; " + remaining + " of " + committed + " remaining", options: { color: INK } }],
    [{ text: "Primary risk \u2014 ", options: { bold: true, color: INK } }, { text: changeOrders + " change orders (soils); Erie County is a saturated, lower-ranked market", options: { color: INK } }],
  ];
  takes.forEach((t, i) => {
    const y = 5.32 + i * 0.42;
    s.addText(t.flat ? t : t, { x: 1.1, y, w: 11.4, h: 0.4, fontFace: BODY, fontSize: 14, bullet: { code: "2022", indent: 14 }, color: INK, margin: 0 });
  });
  footer(s, 2);

  // ============================================================ 3 PIPELINE
  s = p.addSlide(); s.background = { color: PAPER };
  kicker(s, "Section 2"); title(s, "Where This Deal Sits");
  s.addText("The D1 deal pipeline \u2014 each opportunity is screened, diligenced, and gated before capital is committed.", { x: 0.7, y: 1.62, w: 12, h: 0.4, fontFace: BODY, fontSize: 14, color: MUTE, margin: 0 });

  const stages = ["Opportunities\nSourced", "RFQ\nScreening", "Qualified\nOpportunities", "Due\nDiligence", "IC\nReview", "Go / No-Go\nDecision", "Board\nApproval"];
  const current = 5; // IC Review (1-indexed) — this deck IS the IC review
  const n = stages.length, bw = 1.6, bh = 1.05, bgap = (W - 1.4 - n * bw) / (n - 1);
  stages.forEach((st, i) => {
    const x = 0.7 + i * (bw + bgap), y = 2.5;
    const active = (i + 1) === current;
    const done = (i + 1) < current;
    const fill = active ? NAVY : (done ? STEEL : TINT);
    const tcol = active || done ? "FFFFFF" : STEEL;
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y, w: bw, h: bh, fill: { color: fill }, rectRadius: 0.06, shadow: active ? mkShadow() : undefined });
    s.addText(String(i + 1), { x, y: y + 0.1, w: bw, h: 0.3, fontFace: HEAD, fontSize: 13, bold: true, color: active ? GOLD : (done ? "C7D2DC" : MUTE), align: "center", margin: 0 });
    s.addText(st.replace("\n", " "), { x: x + 0.06, y: y + 0.38, w: bw - 0.12, h: 0.62, fontFace: BODY, fontSize: 11.5, bold: active, color: tcol, align: "center", valign: "middle", margin: 0 });
    if (i < n - 1) {
      s.addText("\u203A", { x: x + bw - 0.02, y: y + 0.22, w: bgap + 0.04, h: 0.6, fontFace: BODY, fontSize: 24, color: GOLD, align: "center", valign: "middle", margin: 0 });
    }
  });
  s.addText("\u25B2  WE ARE HERE", { x: 0.7 + (current - 1) * (bw + bgap), y: 3.62, w: bw, h: 0.3, fontFace: BODY, fontSize: 10, bold: true, color: GOLD, align: "center", margin: 0 });

  // five lenses strip
  s.addText("APPLIED AT EVERY GATE \u2014 THE FIVE LENSES", { x: 0.7, y: 4.45, w: 12, h: 0.3, fontFace: BODY, fontSize: 12, bold: true, color: GOLD, charSpacing: 2, margin: 0 });
  const lenses = [["Strategic Fit", I.fit], ["Market Opportunity", I.mkt], ["Management Team", I.team], ["Financial Profile", I.fin], ["Risk Profile", I.risk]];
  const lw = 2.3, lgap = (W - 1.4 - 5 * lw) / 4;
  lenses.forEach(([t, ic], i) => {
    const x = 0.7 + i * (lw + lgap), y = 4.9;
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y, w: lw, h: 1.35, fill: { color: TINT }, rectRadius: 0.06 });
    s.addShape(p.shapes.OVAL, { x: x + lw / 2 - 0.33, y: y + 0.18, w: 0.66, h: 0.66, fill: { color: "FFFFFF" }, shadow: mkShadow() });
    s.addImage({ data: ic, x: x + lw / 2 - 0.19, y: y + 0.32, w: 0.38, h: 0.38 });
    s.addText(t, { x: x + 0.1, y: y + 0.92, w: lw - 0.2, h: 0.38, fontFace: BODY, fontSize: 12, bold: true, color: NAVY, align: "center", valign: "middle", margin: 0 });
  });
  footer(s, 3);

  // ============================================================ 4 OPPORTUNITY
  s = p.addSlide(); s.background = { color: PAPER };
  kicker(s, "Section 3"); title(s, "Opportunity Overview");

  // left: narrative card
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 0.7, y: 1.8, w: 5.7, h: 4.7, fill: { color: NAVY }, rectRadius: 0.06, shadow: mkShadow() });
  s.addImage({ data: I.house, x: 1.0, y: 2.1, w: 0.7, h: 0.7 });
  s.addText("The Asset", { x: 1.85, y: 2.18, w: 4, h: 0.5, fontFace: HEAD, fontSize: 22, bold: true, color: "FFFFFF", valign: "middle", margin: 0 });
  s.addText("Ground-up self-storage development in Hamburg, NY (Erie County) \u2014 the anchor asset in D1\u2019s storage program.",
    { x: 1.0, y: 3.05, w: 5.1, h: 1.0, fontFace: BODY, fontSize: 14.5, color: "D7DEE6", margin: 0 });
  const facts = [
    [{ text: "Program \u2014 ", options: { bold: true, color: "FFFFFF" } }, { text: acres + " ac; ~" + nrsf + " NRSF; " + units + " units", options: { color: "C7D2DC" } }],
    [{ text: "Capital \u2014 ", options: { bold: true, color: "FFFFFF" } }, { text: totalCap + " cap; equity " + equityStr + " + debt " + debtStr + " @ " + debtRate, options: { color: "C7D2DC" } }],
    [{ text: "Return \u2014 ", options: { bold: true, color: "FFFFFF" } }, { text: "levered IRR " + levIRR + "; exit " + exitVal + " @ " + exitCap + " cap", options: { color: "C7D2DC" } }],
  ];
  facts.forEach((f, i) => s.addText(f, { x: 1.0, y: 4.25 + i * 0.6, w: 5.1, h: 0.55, fontFace: BODY, fontSize: 13, bullet: { code: "2022", indent: 12 }, margin: 0 }));

  // right: detail table
  const rows = [
    ["Asset type", "Self-storage development (CC + NCC)"],
    ["Location", "Hamburg, NY (Erie County) \u00B7 " + acres + " ac"],
    ["Program", ccSf + " CC SF + ~" + nccSf + " NCC SF \u00B7 " + units + " units"],
    ["Dev. budget", "~" + devBudget + " (" + committed + " committed)"],
    ["Capital stack", "Equity " + equityStr + " (GP " + gpPct + " / LP " + lpPct + ") + debt " + debtStr],
    ["Levered IRR", levIRR + "  (unlevered " + unlevIRR + ")"],
  ];
  const rx = 6.75, rw = 5.85, rh = 0.66, ry = 1.85;
  s.addText("DEAL TERMS", { x: rx, y: ry - 0.32, w: rw, h: 0.3, fontFace: BODY, fontSize: 12, bold: true, color: GOLD, charSpacing: 2, margin: 0 });
  rows.forEach((r, i) => {
    const y = ry + i * rh;
    const alt = i % 2 === 1;
    s.addShape(p.shapes.RECTANGLE, { x: rx, y, w: rw, h: rh, fill: { color: alt ? TINT : "FFFFFF" }, line: { color: LINE, width: 0.75 } });
    s.addText(r[0], { x: rx + 0.15, y, w: 2.2, h: rh, fontFace: BODY, fontSize: 13, bold: true, color: STEEL, valign: "middle", margin: 0 });
    const isTbd = r[1] === "[TBD]";
    s.addText(r[1], { x: rx + 2.35, y, w: rw - 2.5, h: rh, fontFace: BODY, fontSize: 13, italic: isTbd, color: isTbd ? "B05A00" : INK, valign: "middle", margin: 0 });
  });
  footer(s, 4);

  // ============================================================ 5 FIVE LENSES DETAIL
  s = p.addSlide(); s.background = { color: PAPER };
  kicker(s, "Section 4"); title(s, "Evaluation \u2014 The Five Lenses");
  const cards = [
    { ic: I.gold_fit, t: "Strategic Fit", d: "Does this extend the existing mod-home + storage platform?" },
    { ic: I.gold_mkt, t: "Market Opportunity", d: "Market size, growth rate, competitive landscape, avg cost." },
    { ic: I.gold_team, t: "Management Team", d: "Track record on prior facilities, industry experience, references." },
    { ic: I.gold_fin, t: "Financial Profile", d: "Return vs. floor, IRR repeatability, cash flow, EBITDA, profitability." },
    { ic: I.gold_risk, t: "Risk Profile", d: "Customer concentration, tenant grade, regulatory, legal, dependency." },
    { ic: I.dd, t: "Decision", d: "Deep dive on what we accepted \u2014 and what we passed on, and why." },
  ];
  const ccw = 3.86, cch = 2.15, cgx = 0.24, cgy = 0.28, cx0 = 0.7, cy0 = 1.8;
  cards.forEach((c, i) => {
    const col = i % 3, row = Math.floor(i / 3);
    const x = cx0 + col * (ccw + cgx), y = cy0 + row * (cch + cgy);
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y, w: ccw, h: cch, fill: { color: TINT }, rectRadius: 0.06, shadow: mkShadow() });
    s.addShape(p.shapes.OVAL, { x: x + 0.28, y: y + 0.3, w: 0.78, h: 0.78, fill: { color: NAVY } });
    s.addImage({ data: c.ic, x: x + 0.46, y: y + 0.48, w: 0.42, h: 0.42 });
    s.addText(c.t, { x: x + 1.25, y: y + 0.32, w: ccw - 1.4, h: 0.75, fontFace: HEAD, fontSize: 18, bold: true, color: NAVY, valign: "middle", margin: 0 });
    s.addText(c.d, { x: x + 0.3, y: y + 1.2, w: ccw - 0.6, h: 0.85, fontFace: BODY, fontSize: 12.5, color: STEEL, margin: 0 });
  });
  footer(s, 5);

  // ============================================================ 6 FINANCIAL
  s = p.addSlide(); s.background = { color: PAPER };
  kicker(s, "Section 4 \u00B7 Detail"); title(s, "Financial Profile");
  s.addText("The project underwrites to a levered IRR of " + levIRR + " \u2014 well above the >4% floor. IRR has tightened across underwriting cycles.", { x: 0.7, y: 1.62, w: 12, h: 0.4, fontFace: BODY, fontSize: 14, color: MUTE, margin: 0 });

  // chart: levered IRR across underwriting stages
  s.addChart(p.charts.BAR, [{ name: "Levered IRR", labels: Object.keys(irrStages), values: Object.values(irrStages) }], {
    x: 0.7, y: 2.3, w: 5.3, h: 3.9, barDir: "col",
    chartColors: Object.keys(irrStages).map((_, i, a) => i === a.length - 1 ? GOLD : STEEL), chartArea: { fill: { color: "FFFFFF" } },
    catAxisLabelColor: MUTE, catAxisLabelFontFace: BODY, catAxisLabelFontSize: 11,
    valAxisLabelColor: MUTE, valAxisHidden: false, valAxisMaxVal: 24, valAxisMinVal: 0,
    valGridLine: { color: "EAEEF2", size: 0.5 }, catGridLine: { style: "none" },
    showValue: true, dataLabelPosition: "outEnd", dataLabelColor: NAVY, dataLabelFontFace: BODY, dataLabelFontSize: 13, dataLabelFormatCode: '0.0"%"',
    showLegend: false, showTitle: false,
  });
  s.addText("Levered IRR by underwriting stage", { x: 0.7, y: 6.2, w: 5.3, h: 0.3, fontFace: BODY, fontSize: 10.5, italic: true, color: MUTE, align: "center", margin: 0 });

  // metrics table right
  const mrows = [
    ["Metric", "Underwrite", "Source", true],
    ["Levered IRR", levIRR, "Model", false],
    ["Unlevered IRR", unlevIRR, "Model", false],
    ["Stabilized NOI", "~" + noiStr, "Pro forma", false],
    ["Exit value (" + exitCap + ")", exitVal, "Pro forma", false],
    ["Dev. budget", "~" + devBudget, "Budget", false],
  ];
  const mx = 6.5, mw = 6.1, c1 = 2.9, c2 = 1.7, c3 = 1.5, mh = 0.62, my = 2.3;
  mrows.forEach((r, i) => {
    const y = my + i * mh;
    const head = r[3];
    s.addShape(p.shapes.RECTANGLE, { x: mx, y, w: c1, h: mh, fill: { color: head ? NAVY : (i % 2 ? TINT : "FFFFFF") }, line: { color: LINE, width: 0.75 } });
    s.addShape(p.shapes.RECTANGLE, { x: mx + c1, y, w: c2, h: mh, fill: { color: head ? NAVY : (i % 2 ? TINT : "FFFFFF") }, line: { color: LINE, width: 0.75 } });
    s.addShape(p.shapes.RECTANGLE, { x: mx + c1 + c2, y, w: c3, h: mh, fill: { color: head ? NAVY : (i % 2 ? TINT : "FFFFFF") }, line: { color: LINE, width: 0.75 } });
    s.addText(r[0], { x: mx + 0.12, y, w: c1 - 0.2, h: mh, fontFace: BODY, fontSize: 12.5, bold: head, color: head ? "FFFFFF" : INK, valign: "middle", margin: 0 });
    [[r[1], c2, mx + c1], [r[2], c3, mx + c1 + c2]].forEach(([val, cw2, cx]) => {
      s.addText(val, { x: cx, y, w: cw2, h: mh, fontFace: BODY, fontSize: 12.5, bold: head, color: head ? "FFFFFF" : INK, align: "center", valign: "middle", margin: 0 });
    });
  });
  s.addText([{ text: "Status:  ", options: { bold: true, color: STEEL } }, { text: "~" + pctComplete + " complete \u00B7 " + committed + " committed \u00B7 " + remaining + " remaining \u00B7 " + changeOrders + " change orders", options: { color: INK } }],
    { x: 6.5, y: my + 6 * mh + 0.18, w: 6.1, h: 0.7, fontFace: BODY, fontSize: 11.5, margin: 0 });
  footer(s, 6);

  // ============================================================ 7 RISK
  s = p.addSlide(); s.background = { color: PAPER };
  kicker(s, "Section 4 \u00B7 Detail"); title(s, "Risk Profile & Mitigants");
  const risks = [
    ["Customer concentration", "Exposure to a few key tenants / customers"],
    ["Tenant grade", "Credit quality of the tenant base"],
    ["Regulatory", "Zoning, permitting, regulatory issues"],
    ["Legal", "Outstanding legal review items"],
    ["Dependency", "Single-site or operator dependency"],
  ];
  const rcw = 5.85, rch = 1.0, rgy = 0.22;
  risks.forEach((r, i) => {
    const col = i % 2, rowi = Math.floor(i / 2);
    const x = 0.7 + col * (rcw + 0.23), y = 1.85 + rowi * (rch + rgy);
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y, w: rcw, h: rch, fill: { color: TINT }, rectRadius: 0.05, shadow: mkShadow() });
    s.addShape(p.shapes.OVAL, { x: x + 0.22, y: y + rch / 2 - 0.27, w: 0.54, h: 0.54, fill: { color: "FFFFFF" } });
    s.addImage({ data: I.risk, x: x + 0.34, y: y + rch / 2 - 0.15, w: 0.3, h: 0.3 });
    s.addText(r[0], { x: x + 0.95, y: y + 0.14, w: rcw - 1.1, h: 0.35, fontFace: HEAD, fontSize: 15, bold: true, color: NAVY, margin: 0 });
    s.addText([{ text: r[1] + "   ", options: { color: STEEL } }, { text: "\u2014 mitigant: ", options: { color: MUTE } }, tbd("TBD")],
      { x: x + 0.95, y: y + 0.5, w: rcw - 1.1, h: 0.4, fontFace: BODY, fontSize: 11.5, margin: 0 });
  });
  // last cell: legal/regulatory deep note
  const lx = 0.7 + 1 * (rcw + 0.23), ly = 1.85 + 2 * (rch + rgy);
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: lx, y: ly, w: rcw, h: rch, fill: { color: NAVY }, rectRadius: 0.05 });
  s.addImage({ data: I.dd, x: lx + 0.3, y: ly + rch / 2 - 0.22, w: 0.44, h: 0.44 });
  s.addText("Risk diligence: legal review, customer concentration, regulatory issues.", { x: lx + 0.95, y: ly + 0.1, w: rcw - 1.1, h: 0.8, fontFace: BODY, fontSize: 12.5, color: "FFFFFF", valign: "middle", margin: 0 });
  footer(s, 7);

  // ============================================================ 8 DD DEEP DIVE
  s = p.addSlide(); s.background = { color: PAPER };
  kicker(s, "Section 5"); title(s, "Due Diligence \u2014 Accepted vs. Passed");
  s.addText("Why we accepted this deal, and what we passed on. The contrast is what makes the recommendation credible.", { x: 0.7, y: 1.62, w: 12, h: 0.4, fontFace: BODY, fontSize: 14, color: MUTE, margin: 0 });

  // accepted (left, green-ish) / passed (right)
  const colW = 5.85, colY = 2.35, colH = 4.0;
  // accepted
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 0.7, y: colY, w: colW, h: colH, fill: { color: "F0F6F2" }, rectRadius: 0.06, shadow: mkShadow() });
  s.addImage({ data: I.check, x: 1.0, y: colY + 0.28, w: 0.5, h: 0.5 });
  s.addText("Accepted \u2014 this deal", { x: 1.65, y: colY + 0.3, w: colW - 1.2, h: 0.5, fontFace: HEAD, fontSize: 19, bold: true, color: "2E7D52", valign: "middle", margin: 0 });
  [
    "Levered IRR " + levIRR + " \u2014 far above the >4% floor",
    "Anchor asset for the WNY storage program",
    "~" + pctComplete + " built and on-plan; de-risked vs. pre-construction",
    "[add the 2\u20133 reasons that won the deal]",
  ].forEach((t, i) => {
    const isTbd = t.startsWith("[");
    s.addText(isTbd ? [tbd(t)] : t, { x: 1.05, y: colY + 1.05 + i * 0.7, w: colW - 0.7, h: 0.65, fontFace: BODY, fontSize: 13.5, color: INK, bullet: { code: "2022", indent: 14 }, valign: "top", margin: 0 });
  });
  // passed
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 6.78, y: colY, w: colW, h: colH, fill: { color: "F8F1F1" }, rectRadius: 0.06, shadow: mkShadow() });
  s.addImage({ data: I.x, x: 7.08, y: colY + 0.28, w: 0.5, h: 0.5 });
  s.addText("Passed \u2014 and why", { x: 7.73, y: colY + 0.3, w: colW - 1.2, h: 0.5, fontFace: HEAD, fontSize: 19, bold: true, color: "B23A3A", valign: "middle", margin: 0 });
  [
    ["[Opportunity]", "below 4% return \u2014 Financial Profile"],
    ["[Opportunity]", "[reason] \u2014 [lens]"],
    ["[Opportunity]", "[reason] \u2014 [lens]"],
  ].forEach((t, i) => {
    s.addText([tbd(t[0] + "  "), { text: t[1], options: { color: STEEL, italic: true } }],
      { x: 7.13, y: colY + 1.05 + i * 0.7, w: colW - 0.7, h: 0.65, fontFace: BODY, fontSize: 13.5, bullet: { code: "2022", indent: 14 }, valign: "top", margin: 0 });
  });
  footer(s, 8);

  // ============================================================ 9 NEXT STEPS / DECISION
  s = p.addSlide(); s.background = { color: NAVY };
  s.addShape(p.shapes.RECTANGLE, { x: 0, y: 0, w: W, h: 0.12, fill: { color: GOLD } });
  s.addText("SECTION 6", { x: 0.8, y: 0.62, w: 6, h: 0.3, fontFace: BODY, fontSize: 12, bold: true, color: GOLD, charSpacing: 3, margin: 0 });
  s.addText("Recommendation & Next Steps", { x: 0.8, y: 0.95, w: 12, h: 0.8, fontFace: HEAD, fontSize: 32, bold: true, color: "FFFFFF", margin: 0 });

  // conditions
  s.addText("CONDITIONS PRIOR TO BOARD APPROVAL", { x: 0.8, y: 2.05, w: 8, h: 0.3, fontFace: BODY, fontSize: 13, bold: true, color: GOLD, charSpacing: 2, margin: 0 });
  [
    "Confirm remaining draw schedule (" + remaining + " to complete)",
    "Close outstanding diligence items (legal, regulatory)",
    "Lease-up plan & stabilization timeline for " + units + " units",
  ].forEach((t, i) => {
    s.addText([{ text: (i + 1) + ".  ", options: { bold: true, color: GOLD } }, { text: t, options: { color: "E3E9EF" } }],
      { x: 1.0, y: 2.5 + i * 0.5, w: 11, h: 0.45, fontFace: BODY, fontSize: 15, margin: 0 });
  });

  // decision boxes
  s.addText("IC DECISION", { x: 0.8, y: 4.35, w: 6, h: 0.3, fontFace: BODY, fontSize: 13, bold: true, color: GOLD, charSpacing: 2, margin: 0 });
  const decs = [["APPROVE", GOLD], ["APPROVE WITH CONDITIONS", STEEL], ["DECLINE", "6B7C8C"]];
  const dw = 3.86, dgx = 0.24;
  decs.forEach(([t, col], i) => {
    const x = 0.8 + i * (dw + dgx), y = 4.8;
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y, w: dw, h: 1.2, fill: { color: "1B3350" }, line: { color: col, width: 1.75 }, rectRadius: 0.06 });
    s.addShape(p.shapes.OVAL, { x: x + 0.28, y: y + 0.42, w: 0.36, h: 0.36, fill: { color: "1B3350" }, line: { color: col, width: 1.75 } });
    s.addText(t, { x: x + 0.78, y, w: dw - 0.95, h: 1.2, fontFace: BODY, fontSize: 14, bold: true, color: "FFFFFF", valign: "middle", margin: 0 });
  });
  s.addText("Full analysis and figures: see accompanying IC Memorandum.", { x: 0.8, y: 6.4, w: 11, h: 0.3, fontFace: BODY, fontSize: 12, italic: true, color: "8FA0AF", margin: 0 });

  await p.writeFile({ fileName: require("path").join(__dirname, "out", "IC_Deck.pptx") });
  console.log("deck written");
})();
