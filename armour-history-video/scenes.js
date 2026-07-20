/* ==========================================================================
   scenes.js — story data, historical facts, narration, and artwork
   --------------------------------------------------------------------------
   Every scene is a plain data object consumed by the engine in script.js.
   All drawings are original vector line art generated in code (no
   copyrighted photos, footage, or logos).
   ========================================================================== */

/* --------------------------------------------------------------------------
   HISTORICAL FACTS — the single editable source for every claim on screen
   or in narration. Verify with U.S. Energy before publication.
   -------------------------------------------------------------------------- */
const HISTORICAL_FACTS = {
  // Broad verified anchors (safe to state):
  railroadsTransformedFortWorth: true,          // late-19th-century cattle & rail growth
  stockYardsCompanyIncorporated: '1893',        // Fort Worth Stock Yards Company
  meatpackersArrive: 'Armour and Swift',        // both established major operations
  cattlePerYearBy1907: '≈1,000,000 cattle a year by 1907',
  usEnergyMoveYear: '2025',                     // HQ move into the renovated Armour Building

  /* ======================================================================
     FACTS TO VERIFY BEFORE FINAL EXPORT
     ----------------------------------------------------------------------
     - Exact construction year of the current Armour Building (intentionally
       NOT stated anywhere in this film).
     - Which original industrial features survive in the restored building
       (narration says "carefully preserved … reimagined", nothing more).
     - Precise renovation scope, architects, and completion date.
     - U.S. Energy move-in year (2025 used per project brief).
     - Any employee counts, square footage, or investment figures — none are
       claimed in this film; add only with confirmation.
     ====================================================================== */
};

/* --------------------------------------------------------------------------
   NARRATION — editable text per scene. Spoken via browser speech synthesis
   unless a professional recording exists at the manifest path below.
   -------------------------------------------------------------------------- */
const AUDIO_MANIFEST = {
  scene1: 'assets/narration/scene-01.mp3',
  scene2: 'assets/narration/scene-02.mp3',
  scene3: 'assets/narration/scene-03.mp3',
  scene4: 'assets/narration/scene-04.mp3',
  scene5: 'assets/narration/scene-05.mp3',
  scene6: 'assets/narration/scene-06.mp3',
  scene7: 'assets/narration/scene-07.mp3',
  scene8: 'assets/narration/scene-08.mp3',
};

const MUSIC_FILE = 'assets/music/background.mp3'; // optional; procedural bed plays otherwise

/* --------------------------------------------------------------------------
   Palette (canvas colors)
   -------------------------------------------------------------------------- */
const INK = {
  ivory: '#f4ecd9',
  ivoryDeep: '#e9dec4',
  navy: '#1b2a4a',
  navyDeep: '#101b33',
  brick: '#8a4436',
  tan: '#c8a878',
  charcoal: '#2b2823',
  gold: '#b08d3f',
};

/* ==========================================================================
   Small path builders — return SVG path strings in 1920x1080 space
   ========================================================================== */

function line(x1, y1, x2, y2) { return `M ${x1} ${y1} L ${x2} ${y2}`; }

function poly(points, close = false) {
  const [first, ...rest] = points;
  return `M ${first[0]} ${first[1]} ` + rest.map(p => `L ${p[0]} ${p[1]}`).join(' ') + (close ? ' Z' : '');
}

function rectPath(x, y, w, h) {
  return `M ${x} ${y} L ${x + w} ${y} L ${x + w} ${y + h} L ${x} ${y + h} Z`;
}

/** Gently wobbly horizon-style line. */
function wavyLine(x1, y, x2, amp = 6, waves = 4) {
  const seg = (x2 - x1) / waves;
  let d = `M ${x1} ${y}`;
  for (let i = 0; i < waves; i++) {
    const cx = x1 + seg * (i + 0.5);
    const cy = y + (i % 2 === 0 ? -amp : amp);
    d += ` Q ${cx} ${cy} ${x1 + seg * (i + 1)} ${y}`;
  }
  return d;
}

/** Simple side-view longhorn (hero foreground animal). */
function longhorn(x, y, s) {
  // Body, legs, head, and the signature horn sweep. Origin: chest, scale s.
  return [
    // horns — one continuous elegant sweep
    `M ${x - 168 * s} ${y - 118 * s} C ${x - 120 * s} ${y - 168 * s}, ${x - 60 * s} ${y - 158 * s}, ${x - 20 * s} ${y - 128 * s}` +
    ` C ${x + 22 * s} ${y - 158 * s}, ${x + 84 * s} ${y - 170 * s}, ${x + 132 * s} ${y - 122 * s}`,
    // head
    `M ${x - 32 * s} ${y - 128 * s} C ${x - 44 * s} ${y - 96 * s}, ${x - 40 * s} ${y - 60 * s}, ${x - 16 * s} ${y - 40 * s}` +
    ` C ${x + 2 * s} ${y - 26 * s}, ${x + 26 * s} ${y - 30 * s}, ${x + 34 * s} ${y - 52 * s}` +
    ` C ${x + 42 * s} ${y - 76 * s}, ${x + 36 * s} ${y - 108 * s}, ${x + 16 * s} ${y - 126 * s}`,
    // eye + nostril
    `M ${x - 6 * s} ${y - 96 * s} a ${2.1 * s} ${2.1 * s} 0 1 0 0.1 0 M ${x - 4 * s} ${y - 50 * s} a ${1.7 * s} ${1.7 * s} 0 1 0 0.1 0`,
    // body
    `M ${x + 30 * s} ${y - 90 * s} C ${x + 120 * s} ${y - 122 * s}, ${x + 260 * s} ${y - 112 * s}, ${x + 330 * s} ${y - 72 * s}` +
    ` C ${x + 366 * s} ${y - 48 * s}, ${x + 368 * s} ${y + 6 * s}, ${x + 340 * s} ${y + 36 * s}`,
    `M ${x + 20 * s} ${y - 34 * s} C ${x + 60 * s} ${y + 4 * s}, ${x + 130 * s} ${y + 18 * s}, ${x + 210 * s} ${y + 14 * s}`,
    // legs
    line(x + 76 * s, y + 12 * s, x + 72 * s, y + 118 * s),
    line(x + 116 * s, y + 16 * s, x + 118 * s, y + 118 * s),
    line(x + 268 * s, y + 20 * s, x + 262 * s, y + 118 * s),
    line(x + 318 * s, y + 24 * s, x + 322 * s, y + 118 * s),
    // tail
    `M ${x + 340 * s} ${y - 40 * s} C ${x + 372 * s} ${y - 10 * s}, ${x + 370 * s} ${y + 40 * s}, ${x + 352 * s} ${y + 84 * s}`,
  ];
}

/** Distant grazing cow — two-stroke shorthand. */
function cowFar(x, y, s) {
  return [
    `M ${x} ${y} c ${8 * s} ${-10 * s} ${30 * s} ${-10 * s} ${38 * s} 0 c ${6 * s} ${8 * s} ${-2 * s} ${14 * s} ${-8 * s} ${14 * s}` +
    ` l ${-24 * s} 0 c ${-8 * s} 0 ${-12 * s} ${-6 * s} ${-6 * s} ${-14 * s} Z`,
    `M ${x + 4 * s} ${y + 14 * s} l ${-1 * s} ${10 * s} M ${x + 28 * s} ${y + 14 * s} l ${1 * s} ${10 * s}` +
    ` M ${x - 2 * s} ${y - 2 * s} l ${-8 * s} ${-6 * s}`,
  ];
}

/** Simple standing figure (worker / employee). pose: 'walk' | 'stand' | 'work' */
function person(x, y, s, pose = 'stand') {
  const lean = pose === 'walk' ? 6 * s : 0;
  const arm = pose === 'work'
    ? `M ${x} ${y - 52 * s} L ${x + 26 * s} ${y - 40 * s}`
    : `M ${x} ${y - 52 * s} L ${x + 10 * s} ${y - 26 * s}`;
  const legs = pose === 'walk'
    ? `M ${x + lean} ${y - 24 * s} L ${x - 12 * s} ${y} M ${x + lean} ${y - 24 * s} L ${x + 16 * s} ${y}`
    : `M ${x} ${y - 24 * s} L ${x - 6 * s} ${y} M ${x} ${y - 24 * s} L ${x + 7 * s} ${y}`;
  return [
    `M ${x} ${y - 78 * s} a ${9 * s} ${9 * s} 0 1 0 0.1 0`,           // head
    `M ${x} ${y - 68 * s} L ${x + lean} ${y - 24 * s}`,               // torso
    arm,
    `M ${x} ${y - 52 * s} L ${x - 12 * s} ${y - 30 * s}`,             // other arm
    legs,
  ];
}

/** Cowboy on horseback, side view. */
function rider(x, y, s) {
  return [
    // horse body + neck + head
    `M ${x - 70 * s} ${y - 10 * s} C ${x - 40 * s} ${y - 46 * s}, ${x + 44 * s} ${y - 46 * s}, ${x + 66 * s} ${y - 16 * s}`,
    `M ${x + 60 * s} ${y - 26 * s} C ${x + 84 * s} ${y - 48 * s}, ${x + 92 * s} ${y - 62 * s}, ${x + 104 * s} ${y - 66 * s}` +
    ` l ${16 * s} ${8 * s} l ${-8 * s} ${10 * s}`,
    `M ${x - 66 * s} ${y - 8 * s} C ${x - 84 * s} ${y - 2 * s}, ${x - 86 * s} ${y + 24 * s}, ${x - 76 * s} ${y + 44 * s}`, // tail
    `M ${x - 58 * s} ${y - 6 * s} C ${x - 40 * s} ${y + 8 * s}, ${x + 30 * s} ${y + 8 * s}, ${x + 50 * s} ${y - 8 * s}`,   // belly
    // legs
    line(x - 46 * s, y + 2 * s, x - 52 * s, y + 46 * s),
    line(x - 16 * s, y + 6 * s, x - 12 * s, y + 46 * s),
    line(x + 26 * s, y + 6 * s, x + 22 * s, y + 46 * s),
    line(x + 52 * s, y + 2 * s, x + 58 * s, y + 46 * s),
    // rider
    `M ${x - 4 * s} ${y - 42 * s} L ${x - 2 * s} ${y - 78 * s}`,
    `M ${x - 2 * s} ${y - 84 * s} a ${7 * s} ${7 * s} 0 1 0 0.1 0`,
    `M ${x - 14 * s} ${y - 92 * s} l ${26 * s} 0 M ${x - 8 * s} ${y - 96 * s} l ${14 * s} 0`, // hat
    `M ${x - 3 * s} ${y - 66 * s} L ${x + 24 * s} ${y - 56 * s}`,     // rein arm
    `M ${x - 3 * s} ${y - 44 * s} L ${x + 6 * s} ${y - 20 * s}`,      // leg
  ];
}

/** Steam locomotive, side view, moving right-to-left toward town. */
function locomotive(x, y, s) {
  return [
    rectPath(x, y - 44 * s, 120 * s, 44 * s),                          // boiler block
    rectPath(x + 96 * s, y - 78 * s, 44 * s, 78 * s),                  // cab
    `M ${x + 6 * s} ${y - 44 * s} L ${x + 6 * s} ${y - 66 * s} L ${x + 26 * s} ${y - 66 * s} L ${x + 26 * s} ${y - 44 * s}`, // stack
    `M ${x - 16 * s} ${y} L ${x + 4 * s} ${y - 22 * s}`,               // cowcatcher
    `M ${x - 16 * s} ${y} L ${x + 8 * s} ${y}`,
    `M ${x + 18 * s} ${y} a ${13 * s} ${13 * s} 0 1 0 26 0 a ${13 * s} ${13 * s} 0 1 0 -26 0`,
    `M ${x + 62 * s} ${y} a ${13 * s} ${13 * s} 0 1 0 26 0 a ${13 * s} ${13 * s} 0 1 0 -26 0`,
    `M ${x + 104 * s} ${y} a ${11 * s} ${11 * s} 0 1 0 22 0 a ${11 * s} ${11 * s} 0 1 0 -22 0`,
  ];
}

function smokePuffs(x, y, s, n = 3) {
  const out = [];
  for (let i = 0; i < n; i++) {
    const px = x - i * 34 * s, py = y - i * 30 * s, r = (10 + i * 6) * s;
    out.push(`M ${px} ${py} a ${r} ${r} 0 1 0 ${r * 0.2} ${-r * 0.4}`);
  }
  return out;
}

/** Rail track in perspective toward a vanishing point. */
function railTracks(vx, vy, spread, baseY, sleepers = 7) {
  const paths = [
    line(vx - spread, baseY, vx - spread * 0.05, vy),
    line(vx + spread, baseY, vx + spread * 0.05, vy),
  ];
  for (let i = 1; i <= sleepers; i++) {
    const t = Math.pow(i / (sleepers + 1), 2.2);
    const y = baseY + (vy - baseY) * t;
    const half = spread * (1 - t * 0.95) * 1.14;
    paths.push(line(vx - half, y, vx + half, y));
  }
  return paths;
}

/** Grid of stockyard pens in mild perspective. */
function penGrid(x, y, w, h, cols, rows, skew = 0.16) {
  const paths = [];
  for (let r = 0; r <= rows; r++) {
    const t = r / rows;
    const yy = y + h * t;
    const inset = w * skew * t * 0.5;
    paths.push(line(x + inset, yy, x + w - inset, yy));
  }
  for (let c = 0; c <= cols; c++) {
    const t = c / cols;
    paths.push(line(x + w * t, y, x + w * skew * 0.5 + (w - w * skew) * t, y + h));
  }
  return paths;
}

/** Boxcar / railcar. */
function boxcar(x, y, s, w = 130) {
  return [
    rectPath(x, y - 54 * s, w * s, 54 * s),
    line(x + (w / 2 - 12) * s, y - 54 * s, x + (w / 2 - 12) * s, y),
    line(x + (w / 2 + 12) * s, y - 54 * s, x + (w / 2 + 12) * s, y),
    `M ${x + 22 * s} ${y} a ${8 * s} ${8 * s} 0 1 0 16 0 a ${8 * s} ${8 * s} 0 1 0 -16 0`,
    `M ${x + (w - 38) * s} ${y} a ${8 * s} ${8 * s} 0 1 0 16 0 a ${8 * s} ${8 * s} 0 1 0 -16 0`,
  ];
}

/** Row of arched factory windows. */
function windowRow(x, y, count, w, h, gap) {
  const out = [];
  for (let i = 0; i < count; i++) {
    const wx = x + i * (w + gap);
    out.push(`M ${wx} ${y + h} L ${wx} ${y + h * 0.35} Q ${wx + w / 2} ${y - h * 0.28} ${wx + w} ${y + h * 0.35} L ${wx + w} ${y + h}`);
  }
  return out;
}

/** Smokestack with cap. */
function smokestack(x, y, hgt, w) {
  return [
    `M ${x} ${y} L ${x + w * 0.28} ${y - hgt} L ${x + w * 0.72} ${y - hgt} L ${x + w} ${y}`,
    line(x + w * 0.2, y - hgt * 0.9, x + w * 0.8, y - hgt * 0.9),
  ];
}

/** Drilling derrick (oil). */
function derrick(x, baseY, s) {
  return [
    poly([[x - 54 * s, baseY], [x, baseY - 190 * s], [x + 54 * s, baseY]]),
    line(x - 40 * s, baseY - 52 * s, x + 40 * s, baseY - 52 * s),
    line(x - 28 * s, baseY - 104 * s, x + 28 * s, baseY - 104 * s),
    line(x - 16 * s, baseY - 150 * s, x + 16 * s, baseY - 150 * s),
    line(x - 40 * s, baseY - 52 * s, x + 28 * s, baseY - 104 * s),
    line(x + 40 * s, baseY - 52 * s, x - 28 * s, baseY - 104 * s),
    rectPath(x - 10 * s, baseY - 214 * s, 20 * s, 24 * s),
  ];
}

/** Pumpjack, side view. */
function pumpjack(x, baseY, s) {
  return [
    poly([[x - 34 * s, baseY], [x, baseY - 74 * s], [x + 34 * s, baseY]]),
    line(x - 58 * s, baseY - 88 * s, x + 52 * s, baseY - 76 * s),
    `M ${x + 62 * s} ${baseY - 74 * s} a ${13 * s} ${13 * s} 0 1 0 0.1 0`,
    line(x - 58 * s, baseY - 88 * s, x - 58 * s, baseY - 60 * s),
    line(x - 70 * s, baseY, x + 70 * s, baseY),
  ];
}

/** Modern skyline silhouette (simple downtown block shapes). */
function skyline(x, baseY, s) {
  return [
    poly([[x, baseY], [x, baseY - 150 * s], [x + 46 * s, baseY - 150 * s], [x + 46 * s, baseY]]),
    poly([[x + 58 * s, baseY], [x + 58 * s, baseY - 230 * s], [x + 78 * s, baseY - 258 * s], [x + 98 * s, baseY - 230 * s], [x + 98 * s, baseY]]),
    poly([[x + 112 * s, baseY], [x + 112 * s, baseY - 190 * s], [x + 160 * s, baseY - 190 * s], [x + 160 * s, baseY]]),
    poly([[x + 172 * s, baseY], [x + 172 * s, baseY - 120 * s], [x + 206 * s, baseY - 120 * s], [x + 206 * s, baseY]]),
    line(x + 10 * s, baseY - 118 * s, x + 36 * s, baseY - 118 * s),
    line(x + 122 * s, baseY - 158 * s, x + 150 * s, baseY - 158 * s),
  ];
}

/** The Armour Building — stylized brick block elevation. detail: 0 rough, 1 restored. */
function armourBuilding(x, y, s, detail = 0) {
  // x,y = bottom-left corner of main mass; s scales a 560x330 design.
  const W = 560 * s, H = 330 * s;
  const paths = [
    rectPath(x, y - H, W, H),                                        // main mass
    line(x, y - H + 44 * s, x + W, y - H + 44 * s),                  // parapet band
    line(x, y - 96 * s, x + W, y - 96 * s),                          // lower band
    rectPath(x + W * 0.42, y - 66 * s, W * 0.16, 66 * s),            // entry
  ];
  // window rows
  paths.push(...windowRow(x + 34 * s, y - H + 70 * s, 6, 52 * s, 54 * s, 32 * s));
  paths.push(...windowRow(x + 34 * s, y - H + 156 * s, 6, 52 * s, 54 * s, 32 * s));
  if (detail > 0) {
    paths.push(line(x + 20 * s, y - H - 16 * s, x + W - 20 * s, y - H - 16 * s));   // restored cornice
    if (detail === 1) {
      paths.push(rectPath(x + W * 0.40, y - H - 46 * s, W * 0.2, 30 * s));          // small sign board
    }
    paths.push(...windowRow(x + 48 * s, y - 88 * s, 5, 60 * s, 44 * s, 40 * s));    // street level
  }
  return paths;
}

/** Calendar page. */
function calendarPage(x, y, s, label) {
  return {
    paths: [
      rectPath(x, y, 150 * s, 120 * s),
      line(x, y + 30 * s, x + 150 * s, y + 30 * s),
      `M ${x + 34 * s} ${y} L ${x + 34 * s} ${y - 14 * s} M ${x + 116 * s} ${y} L ${x + 116 * s} ${y - 14 * s}`,
    ],
    label,
  };
}

/* ==========================================================================
   Element helpers — produce engine elements with staggered timing
   ========================================================================== */

let __elIdCounter = 0;

function el(d, opts = {}) {
  return {
    id: `e${__elIdCounter++}`,
    type: 'path',
    d,
    stroke: opts.stroke || INK.charcoal,
    width: opts.width || 3.2,
    at: opts.at ?? 0,
    dur: opts.dur ?? 1.2,
    alpha: opts.alpha ?? 1,
    wobble: opts.wobble ?? 1.4,
    tip: opts.tip !== false, // pencil-dust particles at the drawing tip
  };
}

/** Register a list of path strings with a common style, staggering start times. */
function group(paths, opts = {}) {
  const stagger = opts.stagger ?? 0.22;
  const dur = opts.dur ?? 0.9;
  return paths.map((d, i) =>
    el(d, { ...opts, at: (opts.at ?? 0) + i * stagger, dur: Array.isArray(dur) ? dur[i] : dur })
  );
}

function text(str, x, y, opts = {}) {
  return {
    id: `e${__elIdCounter++}`,
    type: 'text',
    text: str,
    x, y,
    size: opts.size ?? 42,
    at: opts.at ?? 0,
    dur: opts.dur ?? 1.4,
    color: opts.color || INK.navyDeep,
    style: opts.style || 'title', // 'title' | 'hand' | 'label'
    align: opts.align || 'center',
    alpha: opts.alpha ?? 1,
  };
}

function wash(d, opts = {}) {
  return {
    id: `e${__elIdCounter++}`,
    type: 'wash',
    d,
    color: opts.color || INK.tan,
    at: opts.at ?? 0,
    dur: opts.dur ?? 1.6,
    alpha: opts.alpha ?? 0.16,
  };
}

/* ==========================================================================
   SCENES
   ========================================================================== */

const SCENES = [];

/* ---- Scene 1 — The Beginning of Cowtown (≈16s) --------------------------- */
{
  const els = [];
  // Horizon and prairie
  els.push(el(wavyLine(60, 690, 1860, 7, 6), { width: 3.4, at: 0.3, dur: 2.2, stroke: INK.charcoal }));
  els.push(el(wavyLine(160, 640, 760, 10, 3), { width: 2.4, at: 1.4, dur: 1.2, stroke: INK.charcoal, alpha: 0.65 })); // distant hills
  els.push(el(wavyLine(1180, 648, 1760, 9, 3), { width: 2.4, at: 1.7, dur: 1.1, stroke: INK.charcoal, alpha: 0.65 }));
  // Rail tracks toward vanishing point
  els.push(...group(railTracks(700, 692, 170, 1045, 5), { at: 2.2, stagger: 0.16, dur: 0.7, width: 2.8, stroke: INK.navyDeep, alpha: 0.9 }));
  // Locomotive + smoke
  els.push(...group(locomotive(560, 660, 0.62), { at: 4.0, stagger: 0.24, dur: 0.8, width: 3, stroke: INK.navyDeep }));
  els.push(...group(smokePuffs(560, 596, 0.7, 3), { at: 5.4, stagger: 0.3, dur: 0.7, width: 2.4, stroke: INK.charcoal, alpha: 0.55 }));
  // Herd + rider
  els.push(...group([...cowFar(1150, 630, 1.0), ...cowFar(1240, 646, 1.15), ...cowFar(1330, 628, 0.9), ...cowFar(1420, 642, 1.05)],
    { at: 5.6, stagger: 0.16, dur: 0.55, width: 2.4, stroke: INK.charcoal, alpha: 0.8 }));
  els.push(...group(rider(320, 900, 1.05), { at: 6.6, stagger: 0.18, dur: 0.7, width: 3.2, stroke: INK.navyDeep }));
  // Hero longhorn foreground
  els.push(...group(longhorn(1400, 900, 1.0), { at: 7.6, stagger: 0.34, dur: 1.05, width: 4.2, stroke: INK.charcoal }));
  // Washes
  els.push(wash(rectPath(60, 400, 1800, 290), { color: INK.tan, alpha: 0.10, at: 10.6, dur: 1.6 }));
  els.push(wash(rectPath(60, 700, 1800, 330), { color: INK.brick, alpha: 0.07, at: 11.2, dur: 1.6 }));
  els.push(wash(poly([[1240, 800], [1740, 780], [1760, 1010], [1300, 1020]], true), { color: INK.brick, alpha: 0.14, at: 11.6, dur: 1.4 }));
  // Title
  els.push(text('From Cowtown to a New Era of Energy', 960, 190, { size: 66, at: 9.4, dur: 2.4, style: 'title', color: INK.navyDeep }));
  els.push(el(wavyLine(560, 236, 1360, 4, 3), { width: 3, at: 11.6, dur: 1.0, stroke: INK.brick }));

  SCENES.push({
    id: 'scene1',
    title: 'The Beginning of Cowtown',
    duration: 16,
    narration:
      'In the late nineteenth century, railroads, cattle drives, and the livestock trade transformed Fort Worth ' +
      'into one of the most important cattle centers in the American West.',
    exit: 'dust',
    sfx: [{ type: 'wind', at: 0.2 }, { type: 'whistle', at: 5.2 }, { type: 'cattle', at: 8.2 }],
    elements: els,
  });
}

/* ---- Scene 2 — The Fort Worth Stockyards (≈18s) -------------------------- */
{
  const els = [];
  els.push(el(wavyLine(80, 470, 1840, 6, 6), { width: 3, at: 0.2, dur: 1.6 }));
  // Pens
  els.push(...group(penGrid(150, 500, 900, 330, 6, 4), { at: 1.2, stagger: 0.11, dur: 0.55, width: 2.8, stroke: INK.navyDeep }));
  // Cattle in pens
  els.push(...group([
    ...cowFar(300, 590, 1.0), ...cowFar(430, 640, 1.1), ...cowFar(600, 580, 0.95),
    ...cowFar(740, 660, 1.05), ...cowFar(520, 720, 1.1), ...cowFar(330, 730, 0.9),
  ], { at: 3.4, stagger: 0.12, dur: 0.5, width: 2.3, alpha: 0.85 }));
  // Workers on the walkways
  els.push(...group([...person(910, 560, 0.85, 'walk'), ...person(210, 520, 0.8, 'work')],
    { at: 4.6, stagger: 0.14, dur: 0.5, width: 2.6, stroke: INK.navyDeep }));
  // Rail cars top right + exchange-style building
  els.push(...group([...boxcar(1220, 430, 0.9), ...boxcar(1360, 430, 0.9), ...boxcar(1500, 430, 0.9)],
    { at: 3.0, stagger: 0.14, dur: 0.55, width: 2.7, stroke: INK.navyDeep }));
  els.push(el(line(1180, 430, 1700, 430), { at: 3.9, dur: 0.6, width: 2.7, stroke: INK.navyDeep }));
  els.push(...group([
    rectPath(1250, 250, 300, 120),
    poly([[1250, 250], [1400, 190], [1550, 250]]),
    'M 1400 190 L 1400 152 L 1432 162 L 1400 172',
    ...windowRow(1272, 290, 4, 44, 44, 22),
  ], { at: 5.2, stagger: 0.2, dur: 0.7, width: 2.9, stroke: INK.brick }));
  // Historical timeline
  els.push(el(line(160, 930, 1760, 930), { at: 7.4, dur: 1.1, width: 3.2, stroke: INK.brick }));
  const ticks = [
    { x: 350, t: '1880s', s: 'Livestock trade expands near the railroads' },
    { x: 950, t: '1893', s: 'Fort Worth Stock Yards Company is incorporated' },
    { x: 1520, t: 'Early 1900s', s: 'A major meatpacking center' },
  ];
  ticks.forEach((tk, i) => {
    els.push(el(line(tk.x, 916, tk.x, 944), { at: 8.6 + i * 1.1, dur: 0.3, width: 3.4, stroke: INK.brick }));
    els.push(text(tk.t, tk.x, 900, { size: 34, at: 8.8 + i * 1.1, dur: 0.7, style: 'title', color: INK.brick }));
    els.push(text(tk.s, tk.x, 972, { size: 23, at: 9.1 + i * 1.1, dur: 0.9, style: 'hand', color: INK.charcoal }));
  });
  // Handwritten annotation (verified anchor)
  els.push(text('≈ one million cattle a year by 1907', 1430, 700, { size: 30, at: 13.2, dur: 1.3, style: 'hand', color: INK.navy }));
  els.push(el(`M 1210 706 C 1180 690, 1160 660, 1168 622`, { at: 13.9, dur: 0.6, width: 2.2, stroke: INK.navy, alpha: 0.7 })); // little arrow flourish
  // Washes
  els.push(wash(rectPath(150, 500, 900, 330), { color: INK.tan, alpha: 0.10, at: 12.2, dur: 1.6 }));
  els.push(wash(rectPath(1250, 190, 300, 180), { color: INK.brick, alpha: 0.12, at: 12.6, dur: 1.4 }));

  SCENES.push({
    id: 'scene2',
    title: 'The Fort Worth Stockyards',
    duration: 18,
    narration:
      'With direct access to the railroad, the Fort Worth Stockyards grew rapidly. By the early twentieth century, ' +
      'the district had become a center for livestock sales, shipping, and meat production.',
    exit: 'wipe',
    sfx: [{ type: 'cattle', at: 2.6 }, { type: 'wind', at: 0.2 }],
    elements: els,
  });
}

/* ---- Scene 3 — Armour Comes to Fort Worth (≈18s) ------------------------- */
{
  const els = [];
  // Drafting guide lines that "compress" from the pens
  els.push(el(line(120, 820, 1800, 820), { at: 0.2, dur: 1.0, width: 2.2, alpha: 0.5 }));
  els.push(el(line(240, 300, 240, 820), { at: 0.6, dur: 0.8, width: 2.0, alpha: 0.4 }));
  els.push(el(line(1360, 260, 1360, 820), { at: 0.8, dur: 0.8, width: 2.0, alpha: 0.4 }));
  // Main industrial mass
  els.push(...group(armourBuilding(300, 820, 1.35, 0), { at: 1.6, stagger: 0.16, dur: 0.8, width: 3.4, stroke: INK.navyDeep }));
  // Smokestacks + smoke
  els.push(...group([...smokestack(1130, 375, 195, 74), ...smokestack(1250, 375, 150, 64)],
    { at: 5.2, stagger: 0.22, dur: 0.8, width: 3, stroke: INK.brick }));
  els.push(...group(smokePuffs(1185, 150, 0.8, 3), { at: 6.4, stagger: 0.3, dur: 0.8, width: 2.3, alpha: 0.5 }));
  // Signage
  els.push(text('ARMOUR & CO.', 810, 400, { size: 58, at: 6.8, dur: 1.6, style: 'title', color: INK.brick }));
  // Rail spur with cars leaving
  els.push(el(line(120, 950, 1800, 950), { at: 8.0, dur: 0.9, width: 3, stroke: INK.navyDeep }));
  els.push(...group([...boxcar(1420, 942, 1.0), ...boxcar(1590, 942, 1.0)], { at: 8.6, stagger: 0.15, dur: 0.55, width: 2.8, stroke: INK.navyDeep }));
  // Workers + cattle entering ramp
  els.push(...group([...person(430, 948, 0.9, 'work'), ...person(520, 948, 0.9, 'walk'), ...person(1330, 948, 0.9, 'stand')],
    { at: 9.4, stagger: 0.16, dur: 0.5, width: 2.6 }));
  els.push(el(poly([[220, 948], [330, 900], [330, 948]]), { at: 10.2, dur: 0.6, width: 2.8, stroke: INK.navyDeep })); // ramp
  els.push(...group([...cowFar(150, 920, 1.0), ...cowFar(240, 928, 0.95)], { at: 10.6, stagger: 0.14, dur: 0.5, width: 2.3, alpha: 0.85 }));
  // Crates at the dock
  els.push(...group([rectPath(1130, 900, 60, 48), rectPath(1200, 914, 46, 34), line(1130, 924, 1190, 924)],
    { at: 11.2, stagger: 0.16, dur: 0.45, width: 2.5, stroke: INK.charcoal }));
  // Washes
  els.push(wash(rectPath(300, 380, 756, 440), { color: INK.brick, alpha: 0.16, at: 12.4, dur: 2.0 }));
  els.push(wash(rectPath(300, 380, 756, 60), { color: INK.navy, alpha: 0.12, at: 13.2, dur: 1.4 }));

  SCENES.push({
    id: 'scene3',
    title: 'Armour Comes to Fort Worth',
    duration: 18,
    narration:
      'Major meatpacking companies, including Armour and Swift, established operations in Fort Worth. ' +
      'Their arrival helped turn the Stockyards into a nationally significant center of American industry.',
    exit: 'zoomfade',
    sfx: [{ type: 'whistle', at: 9.0 }],
    elements: els,
  });
}

/* ---- Scene 4 — The Building's Original Purpose (≈18s) -------------------- */
{
  const els = [];
  // Cutaway shell
  els.push(...group([
    rectPath(360, 220, 1200, 640),
    line(360, 540, 1560, 540),
    line(960, 220, 960, 860),
    poly([[360, 220], [430, 150], [1630, 150], [1560, 220]]),
  ], { at: 0.3, stagger: 0.3, dur: 1.0, width: 3.4, stroke: INK.navyDeep }));
  // Quadrant 1 — administration (desk, ledger)
  els.push(...group([
    rectPath(470, 420, 150, 24), line(490, 444, 490, 500), line(600, 444, 600, 500),
    rectPath(505, 380, 70, 40), line(515, 392, 565, 392), line(515, 404, 565, 404),
    ...person(680, 505, 0.85, 'work'),
  ], { at: 2.2, stagger: 0.15, dur: 0.5, width: 2.6 }));
  els.push(text('Administration & Ledgers', 660, 300, { size: 27, at: 3.4, dur: 0.9, style: 'hand', color: INK.brick }));
  // Quadrant 2 — processing (symbolic: pulleys, barrels — no graphic imagery)
  els.push(...group([
    `M 1080 300 a 26 26 0 1 0 0.1 0`, line(1080, 274, 1080, 240), line(1050, 340, 1110, 340),
    rectPath(1180, 430, 66, 76), `M 1180 452 L 1246 452 M 1180 484 L 1246 484`,
    rectPath(1280, 440, 60, 66),
    ...person(1420, 505, 0.85, 'work'),
  ], { at: 4.4, stagger: 0.15, dur: 0.5, width: 2.6 }));
  els.push(text('Processing & Cold Storage', 1260, 300, { size: 27, at: 5.6, dur: 0.9, style: 'hand', color: INK.brick }));
  // Quadrant 3 — labor & shipments
  els.push(...group([
    ...person(520, 800, 0.9, 'walk'), ...person(610, 800, 0.9, 'work'),
    rectPath(680, 740, 62, 50), rectPath(752, 756, 44, 34),
  ], { at: 6.8, stagger: 0.15, dur: 0.5, width: 2.6 }));
  els.push(text('Labor & Shipments', 640, 620, { size: 27, at: 7.9, dur: 0.9, style: 'hand', color: INK.brick }));
  // Quadrant 4 — rail distribution across the country
  els.push(...group([
    ...boxcar(1060, 806, 0.9), line(1030, 806, 1530, 806),
    `M 1250 760 C 1330 700, 1430 690, 1500 720`,
    `M 1500 720 l -20 -4 M 1500 720 l -8 16`,
  ], { at: 8.9, stagger: 0.18, dur: 0.55, width: 2.6, stroke: INK.navyDeep }));
  els.push(text('Rail Distribution Nationwide', 1270, 620, { size: 27, at: 10.0, dur: 0.9, style: 'hand', color: INK.brick }));
  // Flow arrows across the system
  els.push(el(`M 430 480 C 700 560, 1200 560, 1500 480`, { at: 11.4, dur: 1.2, width: 2.4, stroke: INK.gold, alpha: 0.9 }));
  // Washes per quadrant
  els.push(wash(rectPath(360, 220, 600, 320), { color: INK.tan, alpha: 0.10, at: 12.4, dur: 1.2 }));
  els.push(wash(rectPath(960, 220, 600, 320), { color: INK.navy, alpha: 0.07, at: 12.8, dur: 1.2 }));
  els.push(wash(rectPath(360, 540, 600, 320), { color: INK.brick, alpha: 0.07, at: 13.2, dur: 1.2 }));
  els.push(wash(rectPath(960, 540, 600, 320), { color: INK.tan, alpha: 0.10, at: 13.6, dur: 1.2 }));

  SCENES.push({
    id: 'scene4',
    title: "The Armour Building's Original Purpose",
    duration: 18,
    narration:
      'The Armour facilities were built to support a massive meatpacking operation. The buildings connected livestock, ' +
      'labor, rail transportation, administration, processing, and distribution under one industrial system.',
    exit: 'fade',
    sfx: [],
    elements: els,
  });
}

/* ---- Scene 5 — An Industry Changes (≈15s) -------------------------------- */
{
  const els = [];
  // Calendar pages advancing
  const cals = [calendarPage(240, 200, 1.0, '1920s'), calendarPage(430, 180, 1.0, '1940s'), calendarPage(620, 200, 1.0, '1960s')];
  cals.forEach((c, i) => {
    els.push(...group(c.paths, { at: 0.4 + i * 1.5, stagger: 0.12, dur: 0.4, width: 2.6, stroke: INK.charcoal, alpha: 0.9 - i * 0.12 }));
    els.push(text(c.label, 240 + i * 190 + 75, 275 - (i === 1 ? 20 : 0), { size: 40, at: 0.8 + i * 1.5, dur: 0.6, style: 'title', color: INK.charcoal }));
  });
  // Truck replacing rail
  els.push(...group([
    rectPath(1120, 380, 150, 76), rectPath(1270, 402, 84, 54),
    `M 1150 456 a 15 15 0 1 0 30 0 a 15 15 0 1 0 -30 0`,
    `M 1288 456 a 15 15 0 1 0 30 0 a 15 15 0 1 0 -30 0`,
    line(1060, 456, 1780, 456),
  ], { at: 3.4, stagger: 0.2, dur: 0.6, width: 2.9, stroke: INK.navyDeep }));
  els.push(...group(boxcar(1500, 448, 0.9), { at: 4.6, stagger: 0.14, dur: 0.5, width: 2.2, alpha: 0.35 })); // fading railcar
  els.push(text('trucks take to the highways', 1330, 530, { size: 26, at: 5.2, dur: 1.0, style: 'hand', color: INK.charcoal }));
  // Quiet pens (light lines) + building staying strong
  els.push(...group(penGrid(190, 640, 640, 240, 5, 3), { at: 5.8, stagger: 0.08, dur: 0.4, width: 2.0, alpha: 0.35 }));
  els.push(text('the yards grow quiet', 500, 950, { size: 26, at: 7.4, dur: 1.0, style: 'hand', color: INK.charcoal }));
  els.push(...group(armourBuilding(1050, 940, 0.86, 0), { at: 7.2, stagger: 0.1, dur: 0.5, width: 3.4, stroke: INK.navyDeep }));
  els.push(text('the Armour Building remains', 1420, 990, { size: 27, at: 10.2, dur: 1.1, style: 'hand', color: INK.navy }));
  // Reflective wash
  els.push(wash(rectPath(80, 120, 1760, 880), { color: INK.tan, alpha: 0.07, at: 10.8, dur: 2.0 }));

  SCENES.push({
    id: 'scene5',
    title: 'An Industry Changes',
    duration: 15,
    narration:
      'As the livestock and meatpacking industries changed, activity at the Stockyards gradually declined. Yet the historic ' +
      'buildings remained, preserving the story of the people and industries that helped build Fort Worth.',
    exit: 'eraser',
    sfx: [{ type: 'wind', at: 0.4 }],
    elements: els,
  });
}

/* ---- Scene 6 — Restoration Begins (≈19s) --------------------------------- */
{
  const els = [];
  // The building outline persists (drawn quickly as if left by the eraser)
  els.push(...group(armourBuilding(480, 860, 1.35, 0), { at: 0.2, stagger: 0.08, dur: 0.4, width: 3.2, stroke: INK.navyDeep, alpha: 0.5 }));
  // Split line: weathered left, restored right
  els.push(el(line(960, 160, 960, 980), { at: 1.6, dur: 0.8, width: 2.4, stroke: INK.brick, alpha: 0.7 }));
  els.push(text('then', 700, 200, { size: 30, at: 2.2, dur: 0.6, style: 'hand', color: INK.charcoal }));
  els.push(text('now', 1220, 200, { size: 30, at: 2.5, dur: 0.6, style: 'hand', color: INK.brick }));
  // Restoration redraw (crisper detail) on the right half
  els.push(...group(armourBuilding(480, 860, 1.35, 1).map(d => d), { at: 3.2, stagger: 0.2, dur: 0.8, width: 3.6, stroke: INK.navyDeep }));
  // Scaffolding + crane + crews
  els.push(...group([
    line(430, 860, 430, 380), line(400, 860, 400, 430), line(400, 500, 430, 500), line(400, 640, 430, 640), line(400, 780, 430, 780),
  ], { at: 5.4, stagger: 0.14, dur: 0.5, width: 2.4, stroke: INK.charcoal }));
  els.push(...group([
    line(1620, 900, 1620, 300), line(1620, 300, 1370, 300), line(1370, 300, 1370, 340),
    `M 1370 340 L 1352 340 L 1388 340`, line(1620, 420, 1560, 300),
  ], { at: 6.2, stagger: 0.18, dur: 0.6, width: 2.6, stroke: INK.charcoal }));
  els.push(...group([...person(560, 905, 0.9, 'work'), ...person(1240, 905, 0.9, 'work'), ...person(1460, 905, 0.9, 'walk')],
    { at: 7.4, stagger: 0.16, dur: 0.5, width: 2.6 }));
  // Interior framing + warm light in the restored windows
  els.push(...group([
    line(1000, 700, 1240, 700), line(1040, 700, 1040, 620), line(1120, 700, 1120, 600), line(1200, 700, 1200, 620),
  ], { at: 9.0, stagger: 0.14, dur: 0.5, width: 2.4, stroke: INK.gold }));
  els.push(text('historic masonry preserved', 700, 1000, { size: 27, at: 10.4, dur: 1.0, style: 'hand', color: INK.charcoal }));
  els.push(text('interiors reimagined', 1290, 1000, { size: 27, at: 11.2, dur: 1.0, style: 'hand', color: INK.brick }));
  // Washes: aged left / clean warm right
  els.push(wash(rectPath(480, 415, 480, 445), { color: INK.tan, alpha: 0.15, at: 12.2, dur: 1.6 }));
  els.push(wash(rectPath(960, 415, 275, 445), { color: INK.gold, alpha: 0.13, at: 12.8, dur: 1.6 }));

  SCENES.push({
    id: 'scene6',
    title: 'Restoration Begins',
    duration: 19,
    narration:
      "More than a century after the Stockyards' industrial rise, the Armour Building began a new chapter. Its historic " +
      'character was carefully preserved while its interiors were reimagined for a modern workplace.',
    exit: 'fade',
    sfx: [{ type: 'hammer', at: 6.0 }, { type: 'hammer', at: 8.4 }],
    elements: els,
  });
}

/* ---- Scene 7 — U.S. Energy Moves Home (≈20s) ----------------------------- */
{
  const els = [];
  // Completed building
  els.push(...group(armourBuilding(280, 840, 1.3, 2), { at: 0.3, stagger: 0.13, dur: 0.7, width: 3.6, stroke: INK.navyDeep }));
  // Signage (text placeholder per brand guidance — official logo goes in assets/logo/)
  els.push(el(rectPath(414, 300, 460, 78), { at: 3.0, dur: 0.8, width: 3, stroke: INK.brick }));
  els.push(text('U.S. ENERGY', 644, 344, { size: 38, at: 3.6, dur: 1.1, style: 'title', color: INK.brick }));
  els.push(text('DEVELOPMENT CORPORATION', 644, 368, { size: 15, at: 4.4, dur: 0.9, style: 'label', color: INK.navy }));
  // Employees entering
  els.push(...group([...person(560, 905, 0.95, 'walk'), ...person(640, 905, 0.95, 'walk'), ...person(760, 905, 0.95, 'stand')],
    { at: 5.0, stagger: 0.18, dur: 0.55, width: 2.7 }));
  // Interior vignette (right): brick wall + glass meeting room + desks.
  // It holds, then fades out so the U.S. map can take its place.
  const V_UNTIL = 13.0;
  els.push(...group([
    rectPath(1130, 300, 640, 560),
    line(1130, 480, 1770, 480),
    rectPath(1180, 540, 220, 24), line(1200, 564, 1200, 640), line(1380, 564, 1380, 640),  // desk
    rectPath(1480, 520, 240, 150), line(1480, 570, 1720, 570),                              // glass meeting room
    ...person(1300, 720, 0.85, 'work'), ...person(1580, 730, 0.85, 'stand'),
    line(1160, 330, 1300, 330), line(1160, 360, 1260, 360),                                 // exposed brick coursing
  ], { at: 6.4, stagger: 0.16, dur: 0.6, width: 2.8, stroke: INK.navyDeep }).map(e => ({ ...e, until: V_UNTIL })));
  els.push({ ...text('historic brick, modern workplace', 1450, 900, { size: 27, at: 9.4, dur: 1.1, style: 'hand', color: INK.brick }), until: V_UNTIL });
  // The restoration line becomes a derrick at the building's side
  els.push(...group(derrick(980, 980, 0.62), { at: 10.6, stagger: 0.14, dur: 0.5, width: 2.8, stroke: INK.brick }));
  // Mini U.S. map takes the vignette's place, with arcs from Fort Worth
  els.push(el(
    'M 982 322 L 1265 322 L 1327 335 L 1374 357 L 1370 389 L 1400 411 L 1384 468 ' +
    'L 1332 511 L 1335 549 L 1290 535 L 1265 570 L 1220 544 L 1181 517 L 1140 494 ' +
    'L 1081 482 L 1023 478 L 986 462 L 966 421 L 954 365 Z',
    { at: 13.6, dur: 1.4, width: 2.6, stroke: INK.navy, alpha: 0.85 }
  ));
  els.push(el('M 1181 475 l 8 -11 l 5 13 l 13 2 l -11 9 l 3 14 l -11 -7 l -12 7 l 4 -13 l -10 -10 Z',
    { at: 14.8, dur: 0.5, width: 2.2, stroke: INK.brick })); // Fort Worth star
  els.push(...group([
    'M 1181 475 C 1138 421, 1081 396, 1030 393',
    'M 1181 475 C 1204 421, 1236 396, 1274 385',
    'M 1181 475 C 1236 462, 1286 462, 1327 475',
  ], { at: 15.3, stagger: 0.24, dur: 0.6, width: 2.2, stroke: INK.gold }));
  els.push(text('connected to producing regions nationwide', 1180, 640, { size: 25, at: 16.2, dur: 1.1, style: 'hand', color: INK.navy }));
  // Washes
  els.push(wash(rectPath(280, 411, 728, 429), { color: INK.brick, alpha: 0.13, at: 8.6, dur: 1.8 }));
  els.push({ ...wash(rectPath(1130, 300, 640, 560), { color: INK.gold, alpha: 0.07, at: 9.2, dur: 1.4 }), until: 13.0 });

  SCENES.push({
    id: 'scene7',
    title: 'U.S. Energy Moves Home',
    duration: 20,
    narration:
      'In 2025, the restored Armour Building became the new headquarters of U.S. Energy Development Corporation — bringing a ' +
      "company with decades of energy experience into one of Fort Worth's most historic industrial landmarks.",
    exit: 'zoomfade',
    sfx: [],
    elements: els,
  });
}

/* ---- Scene 8 — Past and Future (≈19s) ------------------------------------ */
{
  const els = [];
  // One continuous panorama: prairie horizon reprised
  els.push(el(wavyLine(60, 700, 1860, 7, 7), { width: 3.4, at: 0.2, dur: 1.8 }));
  els.push(...group(railTracks(600, 702, 130, 1035, 4), { at: 1.4, stagger: 0.12, dur: 0.5, width: 2.5, stroke: INK.navyDeep, alpha: 0.8 }));
  // Longhorn foreground left
  els.push(...group(longhorn(215, 930, 0.62), { at: 2.6, stagger: 0.2, dur: 0.7, width: 3.4, stroke: INK.charcoal }));
  // Armour Building center
  els.push(...group(armourBuilding(770, 700, 0.62, 1), { at: 4.2, stagger: 0.12, dur: 0.55, width: 3.0, stroke: INK.navyDeep }));
  // Modern skyline behind right
  els.push(...group(skyline(1280, 700, 1.0), { at: 6.0, stagger: 0.16, dur: 0.6, width: 2.7, stroke: INK.navy, alpha: 0.8 }));
  // Pumpjack right foreground + employees
  els.push(...group(pumpjack(1650, 940, 1.1), { at: 7.2, stagger: 0.16, dur: 0.55, width: 3.0, stroke: INK.brick }));
  els.push(...group([...person(1180, 940, 0.95, 'walk'), ...person(1260, 940, 0.95, 'stand')],
    { at: 8.2, stagger: 0.18, dur: 0.5, width: 2.7 }));
  // Gold sun rays
  els.push(...group([
    line(960, 120, 960, 40), line(860, 140, 810, 70), line(1060, 140, 1110, 70),
  ], { at: 9.0, stagger: 0.2, dur: 0.5, width: 2.4, stroke: INK.gold, alpha: 0.9 }));
  // Washes uniting old and new
  els.push(wash(rectPath(60, 420, 1800, 280), { color: INK.tan, alpha: 0.10, at: 9.6, dur: 1.6 }));
  els.push(wash(rectPath(770, 495, 347, 205), { color: INK.brick, alpha: 0.13, at: 10.2, dur: 1.4 }));
  els.push(wash(rectPath(60, 700, 1800, 330), { color: INK.gold, alpha: 0.05, at: 10.6, dur: 1.6 }));
  // Final text
  els.push(text('Historic Roots. A New Era of Energy.', 960, 210, { size: 58, at: 11.6, dur: 2.0, style: 'title', color: INK.navyDeep }));
  els.push(el(wavyLine(680, 254, 1240, 4, 3), { width: 3, at: 13.2, dur: 0.8, stroke: INK.brick }));
  els.push(text('U.S. Energy Development Corporation', 960, 320, { size: 34, at: 14.0, dur: 1.6, style: 'title', color: INK.brick }));
  els.push(text('[ official U.S. Energy logo placement — assets/logo/ ]', 960, 372, { size: 19, at: 15.4, dur: 1.0, style: 'label', color: INK.charcoal, alpha: 0.55 }));

  SCENES.push({
    id: 'scene8',
    title: 'Past and Future',
    duration: 19,
    narration:
      'Once built to support the industries that shaped Cowtown, the Armour Building now supports a new generation of people, ' +
      "partnerships, and American energy. Its purpose has evolved, but its connection to Fort Worth's working spirit remains.",
    exit: 'fade',
    sfx: [{ type: 'wind', at: 0.4 }],
    elements: els,
  });
}
