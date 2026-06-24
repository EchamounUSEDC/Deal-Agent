"""
D1 Real Estate — IC Agent Toolkit
Shared framework: house standard, IC constants, and data loaders.

All four agents import from here so the IC framework (five lenses,
screening criteria, house palette, verticals) is defined in ONE place.

Changelog vs. original:
  - lru_cache on load_market + extract_deal (one parse per process)
  - MARKET_CSV fast-path: screening agent reads ~80 KB CSV, not the 16 MB workbook
  - export_market_csv() + build_market_cache.py expose the cache-build step
  - Named constants for verdict thresholds and BH column indices
  - _detect_current_col() auto-discovers the rightmost underwriting stage
  - _infer_deal_name() derives deal name from workbook path (no hardcoding)
  - All workbook opens use context managers (no leaked file handles)
  - _find_header() includes file path in the ValueError message
  - _extract_status() takes last ratio candidate instead of first (more robust)
  - os.makedirs(OUT) on import so agents can write without pre-creating the dir
  - load_dev_model() — reads Dev Model 11 Markets (captive housing platform)
  - load_factory_model() — reads Factory Model Standalone (HF P&L + waterfall)
"""
from __future__ import annotations
import os, csv, re, warnings
from contextlib import contextmanager
from functools import lru_cache
from openpyxl import load_workbook

warnings.filterwarnings("ignore")


@contextmanager
def _open_wb(path, **kw):
    """Open a workbook and guarantee it is closed.

    openpyxl's *read-only* workbooks do not implement the context-manager
    protocol on every release (a bare ``with load_workbook(... read_only=True)``
    raises ``TypeError: 'Workbook' object does not support the context manager
    protocol``).  Wrapping the open here gives us ``with``-style cleanup that
    works for read-only and read-write workbooks alike, on every version.
    """
    wb = load_workbook(path, **kw)
    try:
        yield wb
    finally:
        wb.close()

# ---------------------------------------------------------------- paths
HERE         = os.path.dirname(os.path.abspath(__file__))
DATA         = os.path.join(HERE, "data")
OUT          = os.path.join(HERE, "out")
MARKET_MODEL   = os.path.join(DATA, "market_model.xlsx")
MARKET_CSV     = os.path.join(DATA, "market_ranking.csv")   # pre-extracted cache
HAMBURG        = os.path.join(DATA, "hamburg_cashflow.xlsx")
DEAL_LOG       = os.path.join(DATA, "deal_log.csv")
DEV_MODEL      = os.path.join(DATA, "dev_model_11_markets.xlsx")
FACTORY_MODEL  = os.path.join(DATA, "factory_model_standalone.xlsx")

os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- house standard
NAVY, STEEL, GOLD    = "12263A", "2E5266", "C8A04B"
LIGHT, INK, MUTE     = "EEF2F6", "1B2733", "5B6B7A"
HEAD_FONT, BODY_FONT = "Cambria", "Calibri"

# ---------------------------------------------------------------- IC framework
FIVE_LENSES = [
    "Strategic Fit", "Market Opportunity", "Management Team",
    "Financial Profile", "Risk Profile",
]

PIPELINE = [
    "Opportunities Sourced", "RFQ Screening", "Qualified Opportunities",
    "Due Diligence", "IC Review", "Go/No-Go Decision", "Board Approval",
]

# Screening criteria (threshold, direction, human label)
CRITERIA = {
    "min_population":  (200_000, "ge", "County population \u2265 200k"),
    "pop_growth_t12":  (0.05,    "ge", "T12 population growth \u2265 5%"),
    "dev_pipeline":    (0.05,    "le", "Development pipeline < 5% of existing NRSF"),
    "op_ex_ratio":     (0.30,    "le", "Operating-expense ratio < 30%"),
    "return_floor":    (0.04,    "ge", "Pro forma return > 4% (internal floor)"),
}

# Verdict thresholds — IC policy parameters.
# Adjust these here; screening_agent.py uses them by name (no magic numbers there).
ADVANCE_PERCENTILE  = 0.80   # model rank \u2265 80th pctile eligible for ADVANCE
CONSIDER_PERCENTILE = 0.50   # 50th\u201380th pctile -> CONSIDER
ADVANCE_MIN_PASS    = 3      # must pass \u2265 this many criteria for ADVANCE

# Deal verticals for the hopper / dashboard
VERTICALS = [
    "Self-Storage", "Industrial / Warehouse", "Triple-Net Lease",
    "Commercial", "Housing", "Experiential",
]

DEAL_STATUSES = [
    "Sourced", "Screening", "Qualified", "Due Diligence",
    "IC Review", "Approved", "Rejected",
]

# Budget History column indices (0-based).
# Typical layout: col 4=Initial feas., 5=Final feas., 6=PPM,
#                 7=PayApp1, 8=PayApp2, 9=Current underwriting
# _detect_current_col() auto-discovers the rightmost populated column at runtime.
BH_COL_INITIAL = 4
BH_COL_FINAL   = 5
BH_COL_PPM     = 6
BH_COL_CURRENT = 9   # fallback when auto-detection finds nothing better


# ---------------------------------------------------------------- market model

def _find_header(rows, must_have, path="<workbook>"):
    """Return the index of the first row whose cells include all must_have labels.

    Raises ValueError (with the file path) if none is found, so the caller
    gets a useful message instead of an opaque traceback.
    """
    for i, r in enumerate(rows):
        cells = [str(c) for c in r if c is not None]
        if all(any(m == c for c in cells) for m in must_have):
            return i
    raise ValueError(
        f"Header row not found in {path!r}.  "
        f"Expected columns: {must_have}"
    )


def _coerce(s):
    """Restore None / int / float from a CSV string cell; leave real strings as str."""
    if s is None or s == "":
        return None
    try:
        return int(s)
    except (ValueError, TypeError):
        pass
    try:
        return float(s)
    except (ValueError, TypeError):
        return s


def export_market_csv(path=MARKET_MODEL, out=MARKET_CSV):
    """Build step: pre-extract the WeightedRanking sheet to a flat CSV.

    Run once whenever market_model.xlsx is updated (or via pipeline.py
    --rebuild-cache).  The screening agent then reads this ~80 KB CSV
    instead of opening the 16 MB workbook, giving a 10\u201320\u00d7 speed-up.
    """
    with _open_wb(path, read_only=True, data_only=True) as wb:
        rows = list(wb["WeightedRanking"].iter_rows(values_only=True))

    h      = _find_header(rows, ["County / City", "Rank (1 = Best)"], path)
    full   = list(rows[h])
    keep   = [i for i, c in enumerate(full) if c is not None]
    header = [full[i] for i in keep]
    ci     = header.index("County / City")
    ri     = header.index("Rank (1 = Best)")

    n = 0
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        for r in rows[h + 1:]:
            vals = ["" if (i >= len(r) or r[i] is None) else r[i] for i in keep]
            if vals[ci] != "" and vals[ri] != "":
                w.writerow(vals)
                n += 1

    load_market.cache_clear()   # force next call to pick up the fresh CSV
    return out, n


def _load_market_xlsx(path):
    with _open_wb(path, read_only=True, data_only=True) as wb:
        rows = list(wb["WeightedRanking"].iter_rows(values_only=True))
    h   = _find_header(rows, ["County / City", "Rank (1 = Best)"], path)
    col = {name: i for i, name in enumerate(rows[h]) if name}
    data = [
        r for r in rows[h + 1:]
        if r[col["County / City"]] and r[col["Rank (1 = Best)"]] is not None
    ]
    data.sort(key=lambda r: r[col["Rank (1 = Best)"]])
    return col, tuple(data)


def _load_market_csv(path):
    with open(path, newline="") as fh:
        rd     = csv.reader(fh)
        header = next(rd)
        rows   = [tuple(_coerce(v) for v in row) for row in rd]
    col  = {name: i for i, name in enumerate(header) if name}
    data = [
        r for r in rows
        if r[col["County / City"]] and r[col["Rank (1 = Best)"]] is not None
    ]
    data.sort(key=lambda r: r[col["Rank (1 = Best)"]])
    return col, tuple(data)


@lru_cache(maxsize=4)
def load_market(path=MARKET_MODEL):
    """Return (col:dict, ranked_rows:tuple) from the WeightedRanking data.

    Reads the pre-extracted CSV cache when present (fast path), else falls back
    to the source workbook.  Memoized: one parse per process.
    """
    if os.path.exists(MARKET_CSV):
        return _load_market_csv(MARKET_CSV)
    return _load_market_xlsx(path)


def lookup_market(query, path=MARKET_MODEL):
    """Find ranked markets whose county / state / CBSA matches query (case-insensitive)."""
    col, data = load_market(path)
    q    = query.lower()
    hits = []
    for r in data:
        blob = " ".join(
            str(r[col[k]]) for k in ("County / City", "State", "CBSA")
        ).lower()
        if q in blob:
            hits.append(_row_to_market(r, col, len(data)))
    return hits


_STATE_ABBR = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR",
    "california": "CA", "colorado": "CO", "connecticut": "CT", "delaware": "DE",
    "district of columbia": "DC", "florida": "FL", "georgia": "GA", "hawaii": "HI",
    "idaho": "ID", "illinois": "IL", "indiana": "IN", "iowa": "IA", "kansas": "KS",
    "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
    "massachusetts": "MA", "michigan": "MI", "minnesota": "MN", "mississippi": "MS",
    "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV",
    "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM", "new york": "NY",
    "north carolina": "NC", "north dakota": "ND", "ohio": "OH", "oklahoma": "OK",
    "oregon": "OR", "pennsylvania": "PA", "rhode island": "RI",
    "south carolina": "SC", "south dakota": "SD", "tennessee": "TN", "texas": "TX",
    "utah": "UT", "vermont": "VT", "virginia": "VA", "washington": "WA",
    "west virginia": "WV", "wisconsin": "WI", "wyoming": "WY",
}
_ABBR_STATE = {v: k for k, v in _STATE_ABBR.items()}


def state_abbr(name):
    """'New York' -> 'NY'.  Returns the first two letters upper-cased if unknown."""
    if not name:
        return ""
    return _STATE_ABBR.get(str(name).strip().lower(), str(name).strip()[:2].upper())


def state_matches(market_state, query):
    """True if `query` (postal abbr OR full name, case-insensitive) names this state.

    Lets the screening agent accept ``--state NY`` against a model whose State
    column stores ``New York``.
    """
    if not query:
        return True
    ms = str(market_state or "").strip().lower()
    q  = str(query).strip().lower()
    if ms == q:
        return True
    # query is a postal abbreviation -> expand it
    if len(q) == 2 and q.upper() in _ABBR_STATE:
        return ms == _ABBR_STATE[q.upper()]
    # market state is the full name; query may be a prefix
    return ms.startswith(q)


def all_markets(path=MARKET_MODEL):
    """Return every ranked market in the model as a list of market dicts (rank order).

    Powers the screening agent's discovery / leaderboard mode: rather than only
    scoring markets you name, you can rank the whole model and surface the best
    opportunities you have not looked at yet.
    """
    col, data = load_market(path)
    return [_row_to_market(r, col, len(data)) for r in data]


def _g(r, col, name):
    return r[col[name]] if name in col else None


def _row_to_market(r, col, total):
    return {
        "rank":           int(_g(r, col, "Rank (1 = Best)")),
        "total_markets":  total,
        "county":         _g(r, col, "County / City"),
        "state":          _g(r, col, "State"),
        "cbsa":           _g(r, col, "CBSA"),
        "region":         _g(r, col, "Economic Region"),
        "population":     _g(r, col, "2024 Population"),
        "pop_growth_t12": _g(r, col, "T12 Population Growth Rate"),
        "pop_growth_t60": _g(r, col, "T60 Population Growth Rate"),
        "sf_per_capita":  _g(r, col, "Average 2026 SF per Capita"),
        "dev_pipeline":   _g(r, col, "Development Pipeline % Existing NRSF"),
        "cc_rate":        _g(r, col, "Average CC $/NRSF per Year"),
        "op_ex_ratio":    _g(r, col, "Average Op Ex Ratio"),
        "yield_on_cost":  _g(r, col, "Stabilized Yield on Cost"),
        "dev_spread":     _g(r, col, "Dev. Spread"),
        "pro_forma_irr":  _g(r, col, "Pro Forma IRR"),
        "score":          _g(r, col, "Total Weighted Score"),
    }


# ---------------------------------------------------------------- deal extraction

_PLACEHOLDER_COL = re.compile(r"^Column\d+$")   # openpyxl names blank columns "ColumnN"


def _detect_current_col(bh_rows):
    """Find the column index of the current (rightmost real) underwriting stage.

    The workbook grows one labelled column per underwriting stage
    ("Initial Feasibility", "Final Feasibility", "PPM", ... "Zach Model").
    The current stage is the *rightmost column that carries a real header* in
    the Budget History header rows.

    The previous heuristic ("rightmost populated cell") was wrong: openpyxl
    materialises trailing blank columns as ``Column6``, ``Column7`` ... filled
    with zeros, so it selected an all-zero placeholder column and every
    extracted field came back as ``[TBD]`` / 0.  We instead read the header
    rows (those carrying a ``Cost Type`` label) and take the rightmost column
    at index >= BH_COL_INITIAL whose header is a genuine string label \u2014 not
    ``None`` and not an openpyxl ``ColumnN`` placeholder.

    Falls back to BH_COL_CURRENT (9) if no header row is found.
    """
    best_col = None
    for r in bh_rows[:15]:
        # A header row labels the stages; it carries a "Cost Type" cell near the left.
        if not any(isinstance(c, str) and c.strip() == "Cost Type" for c in r[:4]):
            continue
        for i, v in enumerate(r):
            if i < BH_COL_INITIAL:
                continue
            if (isinstance(v, str) and v.strip()
                    and not _PLACEHOLDER_COL.match(v.strip())):
                if best_col is None or i > best_col:
                    best_col = i
    return best_col if best_col is not None else BH_COL_CURRENT


def _infer_deal_name(path):
    """Derive a human-readable name from the workbook file name.

    Examples:
        'hamburg_cashflow.xlsx'     ->  'Hamburg'
        'Monroe_County_SS.xlsx'     ->  'Monroe County SS'
        'Springfield_v3_final.xlsx' ->  'Springfield'

    Teams can override by adding a 'Deal Name' row to Budget History.
    """
    stem = os.path.splitext(os.path.basename(path))[0]
    for suffix in (
        "_cashflow", "_model", "_workbook", "_cf",
        "_v2", "_v3", "_v4", "_final", "_draft",
    ):
        if stem.lower().endswith(suffix):
            stem = stem[: -len(suffix)]
            break
    return stem.replace("_", " ").title()


@lru_cache(maxsize=8)
def extract_deal(path=HAMBURG):
    """Extract a structured deal record from a Hamburg-style project workbook.

    Reads Budget History (capital stack, returns, program) and the latest
    CF snapshots.  Memoized: the drafter and the monitor share one parse
    per process when run via pipeline.py.

    \u26a0  Callers must treat the returned dict as read-only; mutating it
       corrupts the shared cache.  Use dict(extract_deal(path)) for a copy.
    """
    with _open_wb(path, read_only=True, data_only=True) as wb:
        bh  = list(wb["Budget History"].iter_rows(values_only=True))
        cur = _detect_current_col(bh)

        # Allow workbooks to supply an explicit name via a 'Deal Name' row
        explicit_name = None
        for r in bh[:20]:
            label = str(r[1]).strip().lower() if r and len(r) > 1 and r[1] else ""
            if label in ("deal name", "project name", "asset name"):
                v = r[cur] if cur < len(r) else None
                v = v or (r[2] if len(r) > 2 else None)
                if isinstance(v, str):
                    explicit_name = v.strip()
                    break

        def find(label, col_idx):
            for r in bh:
                if (
                    r and len(r) > 1 and r[1]
                    and str(r[1]).strip().lower().startswith(label.lower())
                ):
                    v = r[col_idx] if col_idx < len(r) else None
                    return v if isinstance(v, (int, float)) else None
            return None

        name = explicit_name or _infer_deal_name(path)

        deal = {
            "name":          name,
            "subtitle":      f"{name} Development",
            "asset_type":    "Self-storage development (climate + non-climate controlled)",
            "location":      name,   # teams can enrich via the 'Deal Name' row convention
            "_current_col":  cur,    # exposed for diagnostics / troubleshooting
            "site_acres":    find("Site Acreage", cur),
            "cc_sf":         find("CC SF", cur),
            "ncc_sf":        find("NCC SF", cur),
            "cc_units":      find("CC Units", cur),
            "ncc_units":     find("NCC Units", cur),
            "dev_budget":    find("Development Bud", cur),
            "total_cap":     find("Partnership Lev", cur),
            "equity":        find("Equity", cur),
            "gp_pct":        find("GP%", cur),
            "lp_pct":        find("LP %", cur),
            "perm_debt":     find("Permanent Debt", cur),
            "debt_rate":     find("Perm Debt Intere", cur),
            "noi":           find("Net Operating In", cur),
            "exit_cap":      find("Exit Cap Rate", cur),
            "exit_value":    find("Exit Value", cur),
            "unlevered_irr": find("Unlevered IRR", cur),
            "levered_irr":   find("Levered IRR", cur),
            "cc_rate":       find("CC Rate", cur),
            "ncc_rate":      find("NCC Rate", cur),
            "irr_stages": {
                "Initial feas.": find("Levered IRR", BH_COL_INITIAL),
                "Final feas.":   find("Levered IRR", BH_COL_FINAL),
                "PPM":           find("Levered IRR", BH_COL_PPM),
                "Current":       find("Levered IRR", cur),
            },
        }
        deal["nrsf"]  = (deal["cc_sf"]    or 0) + (deal["ncc_sf"]    or 0)
        deal["units"] = (deal["cc_units"] or 0) + (deal["ncc_units"] or 0)
        deal.update(_extract_status(wb))

    return deal


def _extract_status(wb):
    """Build per-snapshot progress series + latest status from CF-* sheets."""
    cf     = [s for s in wb.sheetnames if s.startswith("CF-")]
    series = []   # (label, committed, costs_incurred_ratio)

    for sheet_name in cf:
        ws = wb[sheet_name]
        for r in ws.iter_rows(values_only=True):
            if not any(isinstance(c, str) and c == "Grand Total" for c in r):
                continue
            nums = [c for c in r if isinstance(c, (int, float))]

            # Completion ratio: take the FIRST float in (0, 1) in the Grand Total
            # row.  In these workbooks the leading cell of the Grand Total row is
            # the costs-incurred percentage; trailing fractions are stray
            # column ratios that are *not* monotonic across snapshots (taking the
            # last one produced a 33%→39%→13%→54% zig-zag).  The first cell gives
            # the true monotonic progress curve (0.334 → 0.391 → 0.540).
            ratio_cands = [c for c in nums if 0 < c < 1]
            ratio = ratio_cands[0] if ratio_cands else None

            # Committed cost: the largest dollar amount (> $1 M) in the row.
            committed_cands = [c for c in nums if c > 1_000_000]
            committed = max(committed_cands) if committed_cands else None

            if committed is not None:
                series.append((sheet_name.replace("CF-", ""), committed, ratio or 0.0))
            break   # only the Grand Total row matters per sheet

    # Change-order net total from the latest CF snapshot
    co = None
    if cf:
        for r in wb[cf[-1]].iter_rows(values_only=True):
            lab = " ".join(str(c) for c in r if isinstance(c, str))
            if "Change Orders Total" in lab:
                co_cands = [c for c in r if isinstance(c, (int, float)) and abs(c) > 1_000]
                if co_cands:
                    co = co_cands[0]
                break

    latest    = series[-1] if series else (None, None, None)
    committed = latest[1]
    ratio     = latest[2]
    return {
        "snapshot_series":    series,
        "latest_snapshot":    latest[0],
        "committed":          committed,
        "costs_incurred_pct": ratio,
        "completed":  round(committed * ratio)       if committed and ratio else None,
        "remaining":  round(committed * (1 - ratio)) if committed and ratio else None,
        "change_orders": co,
    }


# ---------------------------------------------------------------- formatting helpers

def usd(v, m=False):
    if v is None:
        return "[TBD]"
    if m:
        return f"${v / 1e6:.2f}M"
    return f"${v:,.0f}"


def pct(v, d=1):
    return "[TBD]" if v is None else f"{v * 100:.{d}f}%"


# ---------------------------------------------------------------- dev model loader

# Market column order in the Dev Model workbook (B→L, 0-based offset from col 1)
_DEV_MARKET_CODES = ["OK", "NE", "TX", "NM", "GA", "AR", "KS", "AL", "TN", "AZ", "IA"]

def _dev_row(rows_dict, label):
    """Return the data row whose first non-None cell starts with `label` (case-insensitive)."""
    for r in rows_dict:
        first = next((str(c).strip() for c in r if c is not None), "")
        if first.lower().startswith(label.lower()):
            return r
    return None

@lru_cache(maxsize=4)
def load_dev_model(path=DEV_MODEL):
    """Load the Dev Model 11 Markets workbook and return a structured dict.

    Returns
    -------
    dict with keys:
      "markets"  : list of per-market dicts (see below), sorted by project IRR desc
      "platform" : aggregate + Phase 1 roll-up values
      "meta"     : workbook title, version, date

    Each market dict contains:
      code, name, tier, premium, distance_mi,
      rent_2br, rent_3br, blended_rent,
      land_cost, site_work_unit, soft_costs_unit, kit_cost_unit,
      total_project_cost, lp_equity, gp_equity,
      stabilized_noi, perm_loan, refi_recap_y3,
      exit_cap, exit_value, net_exit_proceeds,
      project_irr, project_moic, lp_irr, lp_moic, gp_irr, gp_moic,
      phase1, phase2, phase3           (bool — recommended phase)
      nhf_take, usedc_take, newco_take  (40/40/20 GP split)

    ⚠  Callers must treat the returned dict as read-only (lru_cache shared).
    """
    wb = load_workbook(path, read_only=True, data_only=True)

    # ── Market Inputs sheet ───────────────────────────────────────────────────
    mi_rows = list(wb["Market Inputs"].iter_rows(values_only=True))
    def mi(label):
        return _dev_row(mi_rows, label)

    codes_row   = mi("Market")
    names_row   = mi("Market name")
    tier_row    = mi("Tier")
    prem_row    = mi("Premium market")
    dist_row    = mi("Distance to nearest")
    rent2_row   = mi("2BR Stabilized Rent")
    rent3_row   = mi("3BR Stabilized Rent")
    blend_row   = mi("Blended Avg Rent")
    land_row    = mi("Land Cost (Total")
    site_row    = mi("Site Work Cost")
    soft_row    = mi("Soft Costs / Unit")
    cap_row     = mi("Exit Cap Rate")
    leasup_row  = mi("Lease-Up Period")

    # ── Per-Market Economics sheet ────────────────────────────────────────────
    pe_rows = list(wb["Per-Market Economics"].iter_rows(values_only=True))
    def pe(label):
        return _dev_row(pe_rows, label)

    kit_row    = pe("HF Kit Cost")
    tpc_row    = pe("TOTAL PROJECT COST")
    lpe_row    = pe("LP Equity (90%)")
    gpe_row    = pe("GP Equity (10%)")
    noi_row    = pe("Stabilized NOI (Y3+)")
    perm_row   = pe("Perm Loan Sized")
    refi_row   = pe("Y3 Refi Recap")
    exitv_row  = pe("Y5 Exit Value")
    netp_row   = pe("Net Exit Proceeds")
    irr_row    = pe("Project IRR")
    moic_row   = pe("Project MOIC")

    # ── Side-by-Side Comparison sheet ────────────────────────────────────────
    sb_rows = list(wb["Side-by-Side Comparison"].iter_rows(values_only=True))
    def sb(label):
        return _dev_row(sb_rows, label)

    lp_irr_row  = sb("LP IRR")
    lp_moic_row = sb("LP MOIC")
    gp_irr_row  = sb("GP IRR")
    gp_moic_row = sb("GP MOIC")
    nhf_row     = sb("HF Take")
    use_row     = sb("USEDC Take")
    new_row     = sb("NewCo Take")
    ph1_row     = sb("Phase 1")
    ph2_row     = sb("Phase 2")
    ph3_row     = sb("Phase 3")

    # ── Platform Roll-Up sheet ────────────────────────────────────────────────
    ru_rows = list(wb["Platform Roll-Up"].iter_rows(values_only=True))
    def ru(label):
        return _dev_row(ru_rows, label)

    plat_tpc   = ru("Total Project Cost")
    plat_lpeq  = ru("LP Equity Raised")
    plat_noi   = ru("Stabilized NOI")
    plat_exit  = ru("Y5 Exit Value")
    plat_lpirr = ru("Platform Avg LP IRR")
    plat_lpmin = ru("Platform LP IRR — Min")
    plat_lpmax = ru("Platform LP IRR — Max")
    ph1_irr    = ru("Phase 1 Avg LP IRR")
    ph1_moic   = ru("Phase 1 Avg LP MOIC")
    ph1_lpeq   = ru("Phase 1 Total LP Equity")

    wb.close()

    def _v(row, col_idx):
        """Safely extract value at 1-based column index from a data row."""
        if row is None or col_idx >= len(row):
            return None
        v = row[col_idx]
        return v if isinstance(v, (int, float)) else None

    def _s(row, col_idx):
        """Safely extract string value."""
        if row is None or col_idx >= len(row):
            return None
        v = row[col_idx]
        return str(v).strip() if v is not None else None

    # Build per-market dicts (columns 1..11 = B..L in the workbook)
    markets = []
    for i, code in enumerate(_DEV_MARKET_CODES):
        ci = i + 1   # 1-based column index in the data rows
        markets.append({
            "code":            code,
            "name":            _s(names_row, ci) or code,
            "tier":            _s(tier_row, ci),
            "premium":         (_s(prem_row, ci) or "").upper() == "YES",
            "distance_mi":     _v(dist_row, ci),
            # rents
            "rent_2br":        _v(rent2_row, ci),
            "rent_3br":        _v(rent3_row, ci),
            "blended_rent":    _v(blend_row, ci),
            # costs
            "land_cost":       _v(land_row, ci),
            "site_work_unit":  _v(site_row, ci),
            "soft_costs_unit": _v(soft_row, ci),
            "kit_cost_unit":   _v(kit_row, ci),
            # project summary
            "total_project_cost": _v(tpc_row, ci),
            "lp_equity":       _v(lpe_row, ci),
            "gp_equity":       _v(gpe_row, ci),
            "stabilized_noi":  _v(noi_row, ci),
            "perm_loan":       _v(perm_row, ci),
            "refi_recap_y3":   _v(refi_row, ci),
            "exit_cap":        _v(cap_row, ci),
            "exit_value":      _v(exitv_row, ci),
            "net_exit_proceeds": _v(netp_row, ci),
            "lease_up_months": _v(leasup_row, ci),
            # returns
            "project_irr":     _v(irr_row, ci),
            "project_moic":    _v(moic_row, ci),
            "lp_irr":          _v(lp_irr_row, ci),
            "lp_moic":         _v(lp_moic_row, ci),
            "gp_irr":          _v(gp_irr_row, ci),
            "gp_moic":         _v(gp_moic_row, ci),
            # GP / NHF split (40/40/20)
            "nhf_take":        _v(nhf_row, ci),
            "usedc_take":      _v(use_row, ci),
            "newco_take":      _v(new_row, ci),
            # sequencing flags
            "phase1":          _s(ph1_row, ci) == "YES",
            "phase2":          _s(ph2_row, ci) == "YES",
            "phase3":          (_s(ph3_row, ci) or "").upper() == "YES",
        })

    markets.sort(key=lambda m: (m["project_irr"] or 0), reverse=True)

    # Platform roll-up scalars (column 1 = "Sum (11 mkts)", col 2 = "Avg / Mkt")
    def _ru_scalar(row, col=1):
        return _v(row, col) if row else None

    platform = {
        "total_project_cost":  _ru_scalar(plat_tpc),
        "lp_equity_total":     _ru_scalar(plat_lpeq),
        "stabilized_noi_total":_ru_scalar(plat_noi),
        "exit_value_total":    _ru_scalar(plat_exit),
        "avg_lp_irr":          _ru_scalar(plat_lpirr, 1),
        "min_lp_irr":          _ru_scalar(plat_lpmin, 1),
        "max_lp_irr":          _ru_scalar(plat_lpmax, 1),
        "phase1_avg_lp_irr":   _ru_scalar(ph1_irr, 1),
        "phase1_avg_lp_moic":  _ru_scalar(ph1_moic, 1),
        "phase1_lp_equity":    _ru_scalar(ph1_lpeq, 1),
        "n_markets":           len(_DEV_MARKET_CODES),
    }

    return {
        "markets":  tuple(markets),    # immutable — safe with lru_cache
        "platform": platform,
        "meta": {
            "title":   "Captive Dev Model — 11 Markets",
            "version": "v1.0",
            "date":    "May 28, 2026",
        },
    }


# ---------------------------------------------------------------- factory model loader

@lru_cache(maxsize=4)
def load_factory_model(path=FACTORY_MODEL):
    """Load the Factory Model Standalone workbook and return a structured dict.

    Returns
    -------
    dict with keys:
      "assumptions"  : fund structure, kit pricing, production schedule, capex
      "pnl"          : Y1–Y5 P&L (revenue, COGS, gross_profit, overhead, ebitda)
      "waterfall"    : LP/GP 10-yr fund returns
      "sensitivities": gross-margin table, EBITDA table
      "meta"         : workbook title, version, date

    ⚠  Callers must treat the returned dict as read-only (lru_cache shared).
    """
    wb = load_workbook(path, read_only=True, data_only=True)

    # ── Assumptions sheet ─────────────────────────────────────────────────────
    as_rows = list(wb["Assumptions"].iter_rows(values_only=True))
    def _as(label):
        return _dev_row(as_rows, label)

    def _asv(label, col=4):
        row = _as(label)
        if row is None or col >= len(row):
            return None
        v = row[col]
        return v if isinstance(v, (int, float)) else None

    # ── HF P&L sheet ──────────────────────────────────────────────────────────
    pl_rows = list(wb["HF P&L"].iter_rows(values_only=True))
    def _pl(label):
        return _dev_row(pl_rows, label)

    years = ["Y1", "Y2", "Y3", "Y4", "Y5"]
    def _pl_vec(label):
        """Extract Y1..Y5 values for a P&L row (columns 1..5, 0-based)."""
        row = _pl(label)
        if row is None:
            return [None] * 5
        return [row[i] if i < len(row) and isinstance(row[i], (int, float)) else None
                for i in range(1, 6)]

    revenue   = _pl_vec("TOTAL REVENUE")
    cogs      = _pl_vec("COGS =")
    gp        = _pl_vec("GROSS PROFIT")
    overhead  = _pl_vec("TOTAL OVERHEAD")
    ebitda    = _pl_vec("EBITDA")
    ebitda_m  = _pl_vec("EBITDA margin")

    # ── Factory Fund Waterfall sheet ──────────────────────────────────────────
    wf_rows = list(wb["Factory Fund Waterfall"].iter_rows(values_only=True))
    def _wfv(label, col=4):
        row = _dev_row(wf_rows, label)
        if row is None or col >= len(row):
            return None
        v = row[col]
        return v if isinstance(v, (int, float)) else None

    # ── Sensitivities sheet ───────────────────────────────────────────────────
    sv_rows = list(wb["Sensitivities"].iter_rows(values_only=True))

    def _extract_table(sv_rows, header_label, n_data_rows):
        """Return (col_headers, row_headers, values_matrix) for a sensitivity table."""
        start = None
        for i, r in enumerate(sv_rows):
            if any(isinstance(c, str) and header_label.lower() in c.lower()
                   for c in r if c is not None):
                start = i
                break
        if start is None:
            return None, None, None
        col_hdr_row = sv_rows[start + 1]
        col_hdrs = [c for c in col_hdr_row if c is not None][1:]
        row_hdrs, matrix = [], []
        for r in sv_rows[start + 2: start + 2 + n_data_rows]:
            vals = [c for c in r if c is not None]
            if vals:
                row_hdrs.append(vals[0])
                matrix.append(vals[1:])
        return col_hdrs, row_hdrs, matrix

    gm_cols, gm_rows, gm_vals = _extract_table(sv_rows, "Gross Margin", 6)
    eb_cols, eb_rows, eb_vals = _extract_table(sv_rows, "Steady-State EBITDA", 6)

    wb.close()

    assumptions = {
        "fund_equity":         _asv("Factory Fund Target", 4),
        "lp_commit":           _asv("LP Capital Commit", 4),
        "gp_commit":           _asv("GP Capital Commit", 4),
        "hurdle":              _asv("Hurdle Rate", 4),
        "promote":             _asv("Promote / Incentive", 4),
        "hold_years":          _asv("Hold Period", 4),
        "exit_multiple":       _asv("Exit Multiple", 4),
        "dev_fee_pct":         _asv("Development Fee", 4),
        "am_fee_pct":          _asv("Asset Management Fee", 4),
        # Kit pricing tiers
        "kit_tier1":           _asv("Tier 1 Price", 4),   # 1–49 units
        "kit_tier2":           _asv("Tier 2 Price", 4),   # 50–149 units
        "kit_tier3":           _asv("Tier 3 Price", 4),   # 150–199 units
        "kit_tier4":           _asv("Tier 4 Price", 4),   # 200+ / captive
        "kit_cost_unit":       _asv("Cost / Unit", 4),    # all-in COGS
        "single_shift_cap":    _asv("Single-Shift Capacity", 4),
        "two_shift_cap":       _asv("Two-Shift Capacity", 4),
        # Facility capex
        "land_building_capex": _asv("Land + Building CapEx", 4),
        "equip_capex":         _asv("Equipment / Build-Out", 4),
        "op_reserve":          _asv("12-Month Operating Reserve", 4),
        "total_startup_cost":  _asv("TOTAL Factory Startup Cost", 4),
        "facility_cost_yr":    _asv("Facility Mortgage + Lease", 4),
    }

    pnl = {yr: {
        "revenue":      revenue[i],
        "cogs":         cogs[i],
        "gross_profit": gp[i],
        "overhead":     overhead[i],
        "ebitda":       ebitda[i],
        "ebitda_margin":ebitda_m[i],
    } for i, yr in enumerate(years)}

    waterfall = {
        "fund_equity":       _wfv("Total Fund Equity"),
        "fund_irr_10yr":     _wfv("Project IRR (10-yr)"),
        "fund_moic":         _wfv("Project MOIC"),
        "total_distributable":_wfv("Total Distributable"),
        "lp_total":          _wfv("LP TOTAL Distribution"),
        "gp_total":          _wfv("GP TOTAL Distribution"),
        "lp_moic":           _wfv("LP MOIC"),
        "gp_moic":           _wfv("GP MOIC"),
        "lp_8pct_pref":      _wfv("Tier 2 — LP 8%"),
        "gp_catchup":        _wfv("Tier 3 — GP Catch-Up"),
        "tier4_residual":    _wfv("Tier 4 — Residual after"),
        "tier4_lp_share":    _wfv("Tier 4 — LP Share"),
        "tier4_gp_share":    _wfv("Tier 4 — GP Share"),
    }

    sensitivities = {
        "gross_margin": {
            "col_headers": gm_cols,
            "row_headers": gm_rows,
            "values":      gm_vals,
        },
        "ebitda_capacity": {
            "col_headers": eb_cols,
            "row_headers": eb_rows,
            "values":      eb_vals,
        },
    }

    return {
        "assumptions":   assumptions,
        "pnl":           pnl,
        "waterfall":     waterfall,
        "sensitivities": sensitivities,
        "meta": {
            "title":   "Factory Model — Standalone",
            "version": "v2.0",
            "date":    "May 28, 2026",
        },
    }
