// =============================================================================
// THE WYDLE — 3D Falling Cards & Poker Chips (black-screen edition)
// -----------------------------------------------------------------------------
// A looping, full-screen 3D animation for a big screen in front of a casino.
// Playing cards and poker chips rain down through a black void, tumbling and
// fluttering with real physics, then recycle off-screen so it runs forever.
//
// Artwork: chip + card faces are drawn procedurally to match the classic
// "Casino Royale" crown design, branded as THE WYDLE. If you drop real image
// files into ./assets/ (see ASSET_FILES below) they are used instead, exactly.
//
// Tech: three.js (rendering) + cannon-es (rigid-body physics).
// =============================================================================

import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import * as CANNON from 'cannon-es';

// -----------------------------------------------------------------------------
// Tunables
// -----------------------------------------------------------------------------
const CONFIG = {
  spawnIntervalMs: 110,    // how often a new object drops (lower = denser stream)
  maxObjects: 180,         // hard cap on live objects
  cardChipRatio: 0.42,     // probability a spawned object is a card (vs chip)
  spawnHeight: 22,         // how high above center objects appear
  spawnSpreadX: 22,        // horizontal spread of the falling stream
  spawnSpreadZ: 14,        // depth spread
  recycleY: -24,           // recycle once an object falls below this
  gravity: -16,            // gentler gravity reads as heavier, slower fall
  background: 0x000000,    // pure black screen
};

// Chip denominations & colors, matched to the supplied chip set.
//   body  = main chip color, accent = edge-spot / motif color
const CHIP_STYLES = [
  { value: '1',     body: '#8d9094', accent: '#f3f3f0', edge: '#101418' }, // gray
  { value: '5',     body: '#8e1b1b', accent: '#e8d9c0', edge: '#d23b2a' }, // dark red
  { value: '10',    body: '#15489e', accent: '#f2d31b', edge: '#f2d31b' }, // blue/yellow
  { value: '25',    body: '#15171a', accent: '#37c08e', edge: '#37c08e' }, // black/green
  { value: '50',    body: '#9c2c6b', accent: '#f08a1d', edge: '#f08a1d' }, // magenta/orange
  { value: '100',   body: '#16181b', accent: '#d4452a', edge: '#d4452a' }, // black/red
  { value: '500',   body: '#123a52', accent: '#52d6b0', edge: '#52d6b0' }, // teal/mint
  { value: '1000',  body: '#c0314a', accent: '#16181b', edge: '#16181b' }, // crimson/black
  { value: '5000',  body: '#f3c623', accent: '#ec7a1c', edge: '#ec7a1c' }, // yellow/orange
  { value: '10000', body: '#ec7a1c', accent: '#37c0c0', edge: '#37c0c0' }, // orange/teal
  { value: '25000', body: '#5a3a2a', accent: '#efe6d8', edge: '#efe6d8' }, // brown/cream
];

const SUITS = [
  { s: '♠', red: false },
  { s: '♥', red: true  },
  { s: '♦', red: true  },
  { s: '♣', red: false },
];
const RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'];

// Optional exact-image overrides. Any file present in ./assets/ is used as-is;
// anything missing falls back to the procedural art below.
//   assets/card-back.png         -> card back for every card
//   assets/card-AH.png ...       -> specific face, named <RANK><SUIT letter>
//                                   (ranks A,2..10,J,Q,K ; suits S,H,D,C)
//   assets/chip-100.png ...      -> chip face for that denomination
const ASSET_DIR = './assets/';
const loadedAssets = new Map(); // key -> THREE.Texture

// =============================================================================
// Procedural texture factory
// =============================================================================
const TextureCache = (() => {
  const cache = new Map();
  const mk = (w, h) => { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; };

  function roundRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
  }

  // draw `text` centered on an arc; topArc=true bends like a smile at the top
  function arcText(ctx, text, radius, topArc, font, color) {
    ctx.save();
    ctx.fillStyle = color;
    ctx.font = font;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    const total = text.length;
    const spread = Math.min(Math.PI * 0.9, 0.22 * total); // angular width
    for (let i = 0; i < total; i++) {
      const frac = total === 1 ? 0.5 : i / (total - 1);
      const a = topArc
        ? (-Math.PI / 2) + (frac - 0.5) * spread
        : (Math.PI / 2) - (frac - 0.5) * spread;
      const x = Math.cos(a) * radius;
      const y = Math.sin(a) * radius;
      ctx.save();
      ctx.translate(x, y);
      ctx.rotate(topArc ? a + Math.PI / 2 : a - Math.PI / 2);
      ctx.fillText(text[i], 0, 0);
      ctx.restore();
    }
    ctx.restore();
  }

  function finalize(canvas, key) {
    const tex = new THREE.CanvasTexture(canvas);
    tex.anisotropy = 16;
    tex.colorSpace = THREE.SRGBColorSpace;
    cache.set(key, tex);
    return tex;
  }

  // --- Chip face (top / bottom) ---------------------------------------------
  function chipFace(style) {
    const key = `chip-${style.value}`;
    if (cache.has(key)) return cache.get(key);

    const S = 1024, R = S / 2, SS = 2; // SS = supersample the texture for crispness
    const c = mk(S * SS, S * SS);
    const ctx = c.getContext('2d');
    ctx.scale(SS, SS);
    ctx.translate(R, R);

    // body
    ctx.fillStyle = style.body;
    ctx.beginPath(); ctx.arc(0, 0, R - 2, 0, Math.PI * 2); ctx.fill();

    // subtle body shading for depth
    const g = ctx.createRadialGradient(0, 0, R * 0.2, 0, 0, R);
    g.addColorStop(0, 'rgba(255,255,255,0.06)');
    g.addColorStop(0.7, 'rgba(0,0,0,0)');
    g.addColorStop(1, 'rgba(0,0,0,0.28)');
    ctx.fillStyle = g;
    ctx.beginPath(); ctx.arc(0, 0, R - 2, 0, Math.PI * 2); ctx.fill();

    // edge spots (6 rectangular inserts around the rim)
    const spots = 6;
    for (let i = 0; i < spots; i++) {
      ctx.save();
      ctx.rotate((i / spots) * Math.PI * 2 + Math.PI / spots);
      ctx.fillStyle = style.edge;
      roundRect(ctx, -R * 0.085, -R + R * 0.02, R * 0.17, R * 0.2, R * 0.03);
      ctx.fill();
      ctx.restore();
    }

    // ring of small fleur/crown motifs in accent color
    const motifs = 18;
    ctx.fillStyle = style.accent;
    ctx.font = `${Math.round(R * 0.14)}px Georgia, serif`;
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    for (let i = 0; i < motifs; i++) {
      const a = (i / motifs) * Math.PI * 2;
      ctx.save();
      ctx.translate(Math.cos(a) * R * 0.7, Math.sin(a) * R * 0.7);
      ctx.rotate(a + Math.PI / 2);
      ctx.fillText('⚜', 0, 0);
      ctx.restore();
    }

    // white center disk with gold double ring
    ctx.fillStyle = '#f7f4ee';
    ctx.beginPath(); ctx.arc(0, 0, R * 0.54, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = '#c8a24a'; ctx.lineWidth = R * 0.018;
    ctx.beginPath(); ctx.arc(0, 0, R * 0.54, 0, Math.PI * 2); ctx.stroke();
    ctx.lineWidth = R * 0.01;
    ctx.beginPath(); ctx.arc(0, 0, R * 0.5, 0, Math.PI * 2); ctx.stroke();

    // crown at top of the white disk
    ctx.fillStyle = '#c8a24a';
    ctx.font = `${Math.round(R * 0.13)}px Georgia, serif`;
    ctx.fillText('♛', 0, -R * 0.4);

    // arched brand text:  THE  /  WYDLE
    arcText(ctx, 'THE',   R * 0.42, true,  `bold ${Math.round(R * 0.085)}px Georgia, serif`, '#8a6a22');
    arcText(ctx, 'WYLDE', R * 0.42, false, `bold ${Math.round(R * 0.075)}px Georgia, serif`, '#8a6a22');

    // inner decorative ring of dots around the number
    ctx.fillStyle = '#c8a24a';
    const dots = 20;
    for (let i = 0; i < dots; i++) {
      const a = (i / dots) * Math.PI * 2;
      ctx.beginPath();
      ctx.arc(Math.cos(a) * R * 0.3, Math.sin(a) * R * 0.3, R * 0.012, 0, Math.PI * 2);
      ctx.fill();
    }

    // denomination
    ctx.fillStyle = '#b8242b';
    const fs = style.value.length >= 5 ? 0.16 : style.value.length >= 3 ? 0.2 : 0.26;
    ctx.font = `bold ${Math.round(R * fs)}px Arial, sans-serif`;
    ctx.fillText(style.value, 0, R * 0.02);

    return finalize(c, key);
  }

  // --- Chip edge (rim stripes) ----------------------------------------------
  function chipEdge(style) {
    const key = `chip-edge-${style.value}`;
    if (cache.has(key)) return cache.get(key);
    const W = 1024, H = 96;
    const c = mk(W, H);
    const ctx = c.getContext('2d');
    ctx.fillStyle = style.body; ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = style.edge;
    const stripes = 16;
    for (let i = 0; i < stripes; i++) if (i % 2 === 0) ctx.fillRect((i / stripes) * W, 0, (W / stripes), H);
    // top/bottom shade for a rounded-edge feel
    const g = ctx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, 'rgba(0,0,0,0.35)');
    g.addColorStop(0.5, 'rgba(255,255,255,0.12)');
    g.addColorStop(1, 'rgba(0,0,0,0.35)');
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    return finalize(c, key);
  }

  // --- Card back (ornate red damask) ----------------------------------------
  function cardBack() {
    const key = 'card-back';
    if (cache.has(key)) return cache.get(key);
    const W = 716, H = 1024, SS = 2;
    const c = mk(W * SS, H * SS);
    const ctx = c.getContext('2d');
    ctx.scale(SS, SS);

    ctx.fillStyle = '#f7f4ee';
    roundRect(ctx, 0, 0, W, H, 60); ctx.fill();

    ctx.save();
    roundRect(ctx, 30, 30, W - 60, H - 60, 42); ctx.clip();
    ctx.fillStyle = '#9c0f1c';
    ctx.fillRect(30, 30, W - 60, H - 60);

    // filigree lattice
    ctx.strokeStyle = 'rgba(247,244,238,0.5)';
    ctx.lineWidth = 2.5;
    const step = 34;
    for (let x = -H; x < W + H; x += step) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x + H, H); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(x, H); ctx.lineTo(x + H, 0); ctx.stroke();
    }
    // floral scatter
    ctx.fillStyle = 'rgba(247,244,238,0.85)';
    ctx.font = '40px Georgia, serif';
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    for (let yy = 90; yy < H - 60; yy += 90) {
      for (let xx = 90; xx < W - 60; xx += 90) {
        ctx.save(); ctx.translate(xx, yy); ctx.rotate((xx + yy) * 0.01);
        ctx.fillText('❧', 0, 0); ctx.restore();
      }
    }
    ctx.restore();

    // border frame
    ctx.strokeStyle = '#f7f4ee'; ctx.lineWidth = 8;
    roundRect(ctx, 44, 44, W - 88, H - 88, 32); ctx.stroke();

    // center medallion
    ctx.fillStyle = 'rgba(120,8,16,0.95)';
    ctx.beginPath(); ctx.ellipse(W / 2, H / 2, 150, 200, 0, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = '#e6c053'; ctx.lineWidth = 6;
    ctx.beginPath(); ctx.ellipse(W / 2, H / 2, 150, 200, 0, 0, Math.PI * 2); ctx.stroke();

    // gold crown + "THE WYLDE", explicitly centered (textAlign was reset above)
    ctx.fillStyle = '#e6c053';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.font = '150px Georgia, serif';
    ctx.fillText('♛', W / 2, H / 2 - 64);
    ctx.font = 'bold 60px Georgia, serif';
    ctx.fillText('THE', W / 2, H / 2 + 44);
    ctx.fillText('WYLDE', W / 2, H / 2 + 116);

    return finalize(c, key);
  }

  // pip layouts (column x, row y in normalized -1..1; y negative = up)
  const PIP_LAYOUT = {
    '2': [[0, -0.62], [0, 0.62]],
    '3': [[0, -0.62], [0, 0], [0, 0.62]],
    '4': [[-0.34, -0.62], [0.34, -0.62], [-0.34, 0.62], [0.34, 0.62]],
    '5': [[-0.34, -0.62], [0.34, -0.62], [0, 0], [-0.34, 0.62], [0.34, 0.62]],
    '6': [[-0.34, -0.62], [0.34, -0.62], [-0.34, 0], [0.34, 0], [-0.34, 0.62], [0.34, 0.62]],
    '7': [[-0.34, -0.62], [0.34, -0.62], [0, -0.31], [-0.34, 0], [0.34, 0], [-0.34, 0.62], [0.34, 0.62]],
    '8': [[-0.34, -0.62], [0.34, -0.62], [0, -0.31], [-0.34, 0], [0.34, 0], [0, 0.31], [-0.34, 0.62], [0.34, 0.62]],
    '9': [[-0.34, -0.62], [0.34, -0.62], [-0.34, -0.21], [0.34, -0.21], [0, 0], [-0.34, 0.21], [0.34, 0.21], [-0.34, 0.62], [0.34, 0.62]],
    '10': [[-0.34, -0.62], [0.34, -0.62], [0, -0.42], [-0.34, -0.21], [0.34, -0.21], [-0.34, 0.21], [0.34, 0.21], [0, 0.42], [-0.34, 0.62], [0.34, 0.62]],
  };

  // --- Card face ------------------------------------------------------------
  function cardFace(rank, suit) {
    const key = `card-${rank}-${suit.s}`;
    if (cache.has(key)) return cache.get(key);

    const W = 716, H = 1024, SS = 2;
    const c = mk(W * SS, H * SS);
    const ctx = c.getContext('2d');
    ctx.scale(SS, SS);

    ctx.fillStyle = '#fbfbf7';
    roundRect(ctx, 0, 0, W, H, 60); ctx.fill();
    ctx.strokeStyle = 'rgba(0,0,0,0.1)'; ctx.lineWidth = 6;
    roundRect(ctx, 26, 26, W - 52, H - 52, 44); ctx.stroke();

    const color = suit.red ? '#c1121f' : '#16181b';
    ctx.fillStyle = color;
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';

    // corner indices (rank + small suit), top-left and bottom-right (rotated)
    const corner = (x, y, flip) => {
      ctx.save(); ctx.translate(x, y); if (flip) ctx.rotate(Math.PI);
      ctx.font = 'bold 110px Georgia, serif'; ctx.fillText(rank, 0, 0);
      ctx.font = 'bold 92px Georgia, serif'; ctx.fillText(suit.s, 0, 96);
      ctx.restore();
    };
    corner(96, 116, false);
    corner(W - 96, H - 116, true);

    const cx = W / 2, cy = H / 2;
    if (PIP_LAYOUT[rank]) {
      // number cards: lay out pips
      ctx.font = '150px Georgia, serif';
      const spanX = W * 0.26, spanY = H * 0.3;
      for (const [px, py] of PIP_LAYOUT[rank]) {
        ctx.save(); ctx.translate(cx + px * spanX, cy + py * spanY);
        if (py > 0.05) ctx.rotate(Math.PI); // flip lower-half pips
        ctx.fillText(suit.s, 0, 0); ctx.restore();
      }
    } else if (rank === 'A') {
      ctx.font = '420px Georgia, serif';
      ctx.fillText(suit.s, cx, cy);
    } else {
      // J / Q / K — framed monogram with crown
      ctx.save();
      ctx.strokeStyle = color; ctx.lineWidth = 8;
      roundRect(ctx, W * 0.2, H * 0.16, W * 0.6, H * 0.68, 28); ctx.stroke();
      ctx.fillStyle = '#c8a24a'; ctx.font = '150px Georgia, serif';
      ctx.fillText('♛', cx, H * 0.3);
      ctx.fillStyle = color; ctx.font = 'bold 300px Georgia, serif';
      ctx.fillText(rank, cx, cy + 30);
      ctx.font = '150px Georgia, serif';
      ctx.fillText(suit.s, cx, H * 0.72);
      ctx.restore();
    }

    return finalize(c, key);
  }

  return { chipFace, chipEdge, cardBack, cardFace };
})();

// Debug hook: lets tooling inspect a generated texture (e.g. the card back).
window.__TC = TextureCache;

// =============================================================================
// Optional asset preloading (exact images, if present in ./assets/)
// =============================================================================
function tryLoadTexture(url) {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => {
      const tex = new THREE.Texture(img);
      tex.colorSpace = THREE.SRGBColorSpace;
      tex.anisotropy = 16;
      tex.needsUpdate = true;
      resolve(tex);
    };
    img.onerror = () => resolve(null);
    img.src = url;
  });
}

async function preloadAssets() {
  const suitLetter = { '♠': 'S', '♥': 'H', '♦': 'D', '♣': 'C' };
  const jobs = [];
  const want = (key, file) => jobs.push(
    tryLoadTexture(ASSET_DIR + file).then(t => { if (t) loadedAssets.set(key, t); })
  );

  want('card-back', 'card-back.png');
  for (const s of SUITS) for (const r of RANKS) want(`card-${r}-${s.s}`, `card-${r}${suitLetter[s.s]}.png`);
  for (const st of CHIP_STYLES) want(`chip-${st.value}`, `chip-${st.value}.png`);

  await Promise.all(jobs);
  if (loadedAssets.size) console.log(`Loaded ${loadedAssets.size} exact asset image(s) from ${ASSET_DIR}`);
}

// =============================================================================
// Renderer / scene
// =============================================================================
const canvas = document.getElementById('scene');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 3)); // honor SSAA device scale
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.1;

const scene = new THREE.Scene();
scene.background = new THREE.Color(CONFIG.background);
scene.fog = new THREE.FogExp2(CONFIG.background, 0.018); // distance fade adds depth

const camera = new THREE.PerspectiveCamera(48, window.innerWidth / window.innerHeight, 0.1, 200);
camera.position.set(0, 3, 26);
camera.lookAt(0, 1, 0);

const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;

// Lighting tuned for objects glinting out of black.
scene.add(new THREE.AmbientLight(0xffffff, 0.45));

const key = new THREE.DirectionalLight(0xffffff, 2.0);
key.position.set(8, 18, 12);
scene.add(key);

const fill = new THREE.DirectionalLight(0xbfd4ff, 0.6);
fill.position.set(-10, 4, 6);
scene.add(fill);

const rimGold = new THREE.PointLight(0xffcf73, 700, 120, 2);
rimGold.position.set(-16, 10, 8);
scene.add(rimGold);

const rimCool = new THREE.PointLight(0x5aa0ff, 500, 120, 2);
rimCool.position.set(16, -6, 6);
scene.add(rimCool);

// =============================================================================
// Physics (no floor — objects fall through and recycle off-screen)
// =============================================================================
const world = new CANNON.World();
world.gravity.set(0, CONFIG.gravity, 0);
world.broadphase = new CANNON.SAPBroadphase(world);
world.allowSleep = false;
world.solver.iterations = 14;

const pieceMat = new CANNON.Material('piece');
world.addContactMaterial(new CANNON.ContactMaterial(pieceMat, pieceMat, { friction: 0.3, restitution: 0.4 }));

// =============================================================================
// Object pool
// =============================================================================
const pieces = [];

const CARD = { w: 2.5, h: 3.5, d: 0.05 };
const CHIP = { r: 1.15, h: 0.32 };
const cardGeo = new THREE.BoxGeometry(CARD.w, CARD.h, CARD.d, 1, 1, 1);
const chipGeo = new THREE.CylinderGeometry(CHIP.r, CHIP.r, CHIP.h, 48);

function faceTexture(key, drawFn) {
  return loadedAssets.get(key) || drawFn();
}

function makeCard() {
  const rank = RANKS[(Math.random() * RANKS.length) | 0];
  const suit = SUITS[(Math.random() * SUITS.length) | 0];
  const face = faceTexture(`card-${rank}-${suit.s}`, () => TextureCache.cardFace(rank, suit));
  const back = faceTexture('card-back', () => TextureCache.cardBack());
  const edge = new THREE.MeshStandardMaterial({ color: 0xf2efe8, roughness: 0.55, metalness: 0 });
  const faceMat = new THREE.MeshStandardMaterial({ map: face, roughness: 0.5, metalness: 0 });
  const backMat = new THREE.MeshStandardMaterial({ map: back, roughness: 0.5, metalness: 0 });
  const mesh = new THREE.Mesh(cardGeo, [edge, edge, edge, edge, faceMat, backMat]);

  const body = new CANNON.Body({ mass: 0.4, material: pieceMat });
  body.addShape(new CANNON.Box(new CANNON.Vec3(CARD.w / 2, CARD.h / 2, CARD.d / 2)));
  body.linearDamping = 0.45;   // air resistance -> cards flutter/float
  body.angularDamping = 0.12;
  return { mesh, body, type: 'card' };
}

function makeChip() {
  const style = CHIP_STYLES[(Math.random() * CHIP_STYLES.length) | 0];
  const face = faceTexture(`chip-${style.value}`, () => TextureCache.chipFace(style));
  const edgeTex = TextureCache.chipEdge(style);
  const faceMat = new THREE.MeshStandardMaterial({ map: face, roughness: 0.28, metalness: 0.2 });
  const edgeMat = new THREE.MeshStandardMaterial({ map: edgeTex, roughness: 0.35, metalness: 0.2 });
  const mesh = new THREE.Mesh(chipGeo, [edgeMat, faceMat, faceMat]); // side, top, bottom

  const body = new CANNON.Body({ mass: 1.1, material: pieceMat });
  body.addShape(new CANNON.Cylinder(CHIP.r, CHIP.r, CHIP.h, 18));
  body.linearDamping = 0.12;   // chips fall heavier/faster than cards
  body.angularDamping = 0.18;
  return { mesh, body, type: 'chip' };
}

function spawn() {
  if (pieces.filter(p => !p.dead).length >= CONFIG.maxObjects) recycleOldest();

  const obj = Math.random() < CONFIG.cardChipRatio ? makeCard() : makeChip();
  const { mesh, body } = obj;

  body.position.set(
    (Math.random() - 0.5) * CONFIG.spawnSpreadX,
    CONFIG.spawnHeight + Math.random() * 8,
    (Math.random() - 0.5) * CONFIG.spawnSpreadZ
  );
  body.quaternion.setFromEuler(Math.random() * 6.28, Math.random() * 6.28, Math.random() * 6.28);
  body.angularVelocity.set((Math.random() - 0.5) * 7, (Math.random() - 0.5) * 7, (Math.random() - 0.5) * 7);
  body.velocity.set((Math.random() - 0.5) * 1.5, -1 - Math.random() * 2, (Math.random() - 0.5) * 1.5);

  scene.add(mesh);
  world.addBody(body);
  pieces.push({ ...obj, dead: false });
}

function disposePiece(p) {
  scene.remove(p.mesh);
  world.removeBody(p.body);
  const mats = Array.isArray(p.mesh.material) ? p.mesh.material : [p.mesh.material];
  mats.forEach(m => { if (m && !m.map) m.dispose?.(); });
  p.dead = true;
}

function recycleOldest() {
  // recycle whatever has fallen lowest
  let low = null;
  for (const p of pieces) {
    if (p.dead) continue;
    if (!low || p.body.position.y < low.body.position.y) low = p;
  }
  if (low) disposePiece(low);
}

function dealBurst(n = 24) { for (let i = 0; i < n; i++) setTimeout(spawn, i * 35); }

// =============================================================================
// Post-processing
// =============================================================================
// Render into a MULTISAMPLED, HDR render target so geometry edges get true
// hardware anti-aliasing (the default EffectComposer target bypasses the
// renderer's antialias setting — that was the source of the jagged edges).
const dbs = renderer.getDrawingBufferSize(new THREE.Vector2());
const msaaTarget = new THREE.WebGLRenderTarget(dbs.x, dbs.y, {
  type: THREE.HalfFloatType,
  samples: 8,                 // 8x MSAA
});
const composer = new EffectComposer(renderer, msaaTarget);
composer.addPass(new RenderPass(scene, camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(window.innerWidth, window.innerHeight), 0.3, 0.75, 0.96);
composer.addPass(bloom);
composer.addPass(new OutputPass());

// =============================================================================
// Simulation step (shared by realtime + capture)
// =============================================================================
let lastSpawn = 0;
let lastTime = performance.now();

function step(now, dt, render = true) {
  if (now - lastSpawn > CONFIG.spawnIntervalMs) { spawn(); lastSpawn = now; }

  world.step(1 / 60, dt, 4);

  for (const p of pieces) {
    if (p.dead) continue;
    p.mesh.position.copy(p.body.position);
    p.mesh.quaternion.copy(p.body.quaternion);
    if (p.body.position.y < CONFIG.recycleY) disposePiece(p); // fell off-screen
  }
  if (pieces.length > CONFIG.maxObjects * 2) {
    for (let i = pieces.length - 1; i >= 0; i--) if (pieces[i].dead) pieces.splice(i, 1);
  }

  // gentle camera sway — keeps it alive without implying the pieces curve
  const t = now * 0.00012;
  camera.position.x = Math.sin(t) * 2.2;
  camera.position.y = 3 + Math.sin(t * 0.7) * 1.0;
  camera.lookAt(0, 1, 0);

  if (render) composer.render();
}

function animate(now) {
  requestAnimationFrame(animate);
  const dt = Math.min((now - lastTime) / 1000, 1 / 30);
  lastTime = now;
  step(now, dt);
}

// =============================================================================
// Resize / fullscreen / controls
// =============================================================================
function onResize() {
  const w = window.innerWidth, h = window.innerHeight;
  camera.aspect = w / h; camera.updateProjectionMatrix();
  renderer.setSize(w, h); composer.setSize(w, h);
}
window.addEventListener('resize', onResize);
onResize();

const hint = document.getElementById('hint');
let hintTimer = setTimeout(() => hint.classList.add('hide'), 6000);
window.addEventListener('keydown', (e) => {
  if (e.key === 'f' || e.key === 'F') {
    if (!document.fullscreenElement) document.documentElement.requestFullscreen?.();
    else document.exitFullscreen?.();
  }
  if (e.code === 'Space') { e.preventDefault(); dealBurst(); }
  if (e.key === 'h' || e.key === 'H') {
    const hl = document.getElementById('headline');
    hl.style.display = hl.style.display === 'none' ? '' : 'none';
  }
});
window.addEventListener('pointerdown', () => {
  hint.classList.remove('hide');
  clearTimeout(hintTimer);
  hintTimer = setTimeout(() => hint.classList.add('hide'), 4000);
});

// =============================================================================
// URL params (marquee text + capture mode)
// =============================================================================
const params = new URLSearchParams(location.search);
if (params.get('title')) document.querySelector('[data-title]').textContent = params.get('title');
if (params.get('subtitle')) document.querySelector('[data-subtitle]').textContent = params.get('subtitle');

const CAPTURE = params.get('capture') === '1';
const FPS = Math.max(1, parseInt(params.get('fps') || '60', 10));
const FRAME_DT = 1000 / FPS;
let vNow = 0;
window.__renderFrame = function () { vNow += FRAME_DT; step(vNow, FRAME_DT / 1000, true); };

// =============================================================================
// Boot
// =============================================================================
async function start() {
  await preloadAssets();
  document.getElementById('loading').classList.add('done');

  if (CAPTURE) {
    document.getElementById('hint').style.display = 'none';
    document.getElementById('loading').style.display = 'none'; // hide instantly, no fade

    lastSpawn = 0; lastTime = 0; vNow = 0;
    const warmupFrames = Math.round(FPS * 6);
    for (let i = 0; i < warmupFrames; i++) { vNow += FRAME_DT; step(vNow, FRAME_DT / 1000, false); }
    window.__captureReady = true;
    return;
  }

  dealBurst(36);
  requestAnimationFrame(animate);
}

setTimeout(start, 300);
