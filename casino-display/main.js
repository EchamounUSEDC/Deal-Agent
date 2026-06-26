// =============================================================================
// Casino Display — 3D Falling Cards & Poker Chips
// -----------------------------------------------------------------------------
// A looping, full-screen 3D animation built for a big screen in front of a
// casino. Playing cards and poker chips rain down, tumble, collide and pile up
// on a felt table, then gently recycle so it runs forever without growing.
//
// Tech: three.js (rendering) + cannon-es (rigid-body physics).
// All card/chip artwork is generated procedurally on <canvas> — no image files
// needed, so this is fully self-contained (aside from the two CDN libraries).
// =============================================================================

import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import * as CANNON from 'cannon-es';

// -----------------------------------------------------------------------------
// Tunables — tweak these to restyle the show.
// -----------------------------------------------------------------------------
const CONFIG = {
  spawnIntervalMs: 360,    // how often a new object drops
  maxObjects: 140,         // hard cap on live objects (older ones recycle)
  objectLifetimeMs: 16000, // how long an object lives before it fades & recycles
  cardChipRatio: 0.45,     // probability a spawned object is a card (vs a chip)
  spawnHeight: 26,         // how high above the table objects appear
  spawnRadius: 9,          // horizontal spread of the drop zone
  gravity: -28,            // world gravity (snappier than real-world -9.8)
  felt: 0x0b6623,          // table felt color
  background: 0x05060a,    // backdrop color
};

// Standard chip denominations & their classic casino colors.
const CHIP_STYLES = [
  { value: '1',   body: '#f5f5f5', accent: '#1565c0' }, // white
  { value: '5',   body: '#c62828', accent: '#ffffff' }, // red
  { value: '25',  body: '#2e7d32', accent: '#ffffff' }, // green
  { value: '100', body: '#1a1a1a', accent: '#d4af37' }, // black/gold
  { value: '500', body: '#6a1b9a', accent: '#ffd54f' }, // purple
  { value: '1K',  body: '#fbc02d', accent: '#1a1a1a' }, // gold
];

const SUITS = [
  { s: '♠', red: false }, // spade
  { s: '♥', red: true  }, // heart
  { s: '♦', red: true  }, // diamond
  { s: '♣', red: false }, // club
];
const RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'];

// =============================================================================
// Texture factory — draw cards & chips onto canvases, cache the results.
// =============================================================================
const TextureCache = (() => {
  const cache = new Map();

  function makeCanvas(w, h) {
    const c = document.createElement('canvas');
    c.width = w; c.height = h;
    return c;
  }

  function roundRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
  }

  // --- Card face -------------------------------------------------------------
  function cardFace(rank, suit) {
    const key = `card-${rank}-${suit.s}`;
    if (cache.has(key)) return cache.get(key);

    const W = 512, H = 716;
    const c = makeCanvas(W, H);
    const ctx = c.getContext('2d');

    // body
    ctx.fillStyle = '#fbfbf7';
    roundRect(ctx, 0, 0, W, H, 46); ctx.fill();
    // inner border
    ctx.strokeStyle = 'rgba(0,0,0,0.12)';
    ctx.lineWidth = 6;
    roundRect(ctx, 22, 22, W - 44, H - 44, 34); ctx.stroke();

    const color = suit.red ? '#c1121f' : '#1a1a1a';
    ctx.fillStyle = color;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    // corner pips (top-left and bottom-right rotated)
    const drawCorner = (x, y, flip) => {
      ctx.save();
      ctx.translate(x, y);
      if (flip) ctx.rotate(Math.PI);
      ctx.font = 'bold 92px Georgia, serif';
      ctx.fillText(rank, 0, 0);
      ctx.font = 'bold 78px Georgia, serif';
      ctx.fillText(suit.s, 0, 86);
      ctx.restore();
    };
    drawCorner(78, 92, false);
    drawCorner(W - 78, H - 92, true);

    // big center suit
    ctx.font = 'bold 300px Georgia, serif';
    ctx.globalAlpha = 0.92;
    ctx.fillText(suit.s, W / 2, H / 2);
    ctx.globalAlpha = 1;

    const tex = new THREE.CanvasTexture(c);
    tex.anisotropy = 8;
    tex.colorSpace = THREE.SRGBColorSpace;
    cache.set(key, tex);
    return tex;
  }

  // --- Card back -------------------------------------------------------------
  function cardBack() {
    const key = 'card-back';
    if (cache.has(key)) return cache.get(key);

    const W = 512, H = 716;
    const c = makeCanvas(W, H);
    const ctx = c.getContext('2d');

    ctx.fillStyle = '#fbfbf7';
    roundRect(ctx, 0, 0, W, H, 46); ctx.fill();

    // deep red panel
    ctx.fillStyle = '#8b0e1a';
    roundRect(ctx, 26, 26, W - 52, H - 52, 30); ctx.fill();

    // gold diamond lattice
    ctx.strokeStyle = 'rgba(233,196,106,0.55)';
    ctx.lineWidth = 3;
    const step = 46;
    for (let x = -H; x < W + H; x += step) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x + H, H); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(x, H); ctx.lineTo(x + H, 0); ctx.stroke();
    }
    // center medallion
    ctx.fillStyle = 'rgba(5,6,10,0.85)';
    ctx.beginPath(); ctx.ellipse(W / 2, H / 2, 120, 150, 0, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = '#e9c46a';
    ctx.font = 'bold 120px Georgia, serif';
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText('♠', W / 2, H / 2 + 8);

    const tex = new THREE.CanvasTexture(c);
    tex.anisotropy = 8;
    tex.colorSpace = THREE.SRGBColorSpace;
    cache.set(key, tex);
    return tex;
  }

  // --- Chip top/bottom face --------------------------------------------------
  function chipFace(style) {
    const key = `chip-face-${style.value}`;
    if (cache.has(key)) return cache.get(key);

    const S = 512, R = S / 2;
    const c = makeCanvas(S, S);
    const ctx = c.getContext('2d');
    ctx.translate(R, R);

    // base body
    ctx.fillStyle = style.body;
    ctx.beginPath(); ctx.arc(0, 0, R, 0, Math.PI * 2); ctx.fill();

    // outer dashed edge spots (classic chip look)
    const spots = 8;
    for (let i = 0; i < spots; i++) {
      ctx.save();
      ctx.rotate((i / spots) * Math.PI * 2);
      ctx.fillStyle = style.accent;
      roundRect(ctx, -34, -R + 6, 68, 64, 16); ctx.fill();
      ctx.restore();
    }

    // inner ring
    ctx.strokeStyle = style.accent;
    ctx.lineWidth = 10;
    ctx.beginPath(); ctx.arc(0, 0, R * 0.62, 0, Math.PI * 2); ctx.stroke();

    // center disk
    ctx.fillStyle = style.body;
    ctx.beginPath(); ctx.arc(0, 0, R * 0.5, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = style.accent;
    ctx.lineWidth = 6;
    ctx.beginPath(); ctx.arc(0, 0, R * 0.5, 0, Math.PI * 2); ctx.stroke();

    // value text
    ctx.fillStyle = style.accent;
    ctx.font = `bold ${style.value.length > 2 ? 150 : 190}px Arial, sans-serif`;
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText(style.value, 0, 6);

    const tex = new THREE.CanvasTexture(c);
    tex.anisotropy = 8;
    tex.colorSpace = THREE.SRGBColorSpace;
    cache.set(key, tex);
    return tex;
  }

  // --- Chip edge (side) ------------------------------------------------------
  function chipEdge(style) {
    const key = `chip-edge-${style.value}`;
    if (cache.has(key)) return cache.get(key);

    const W = 512, H = 64;
    const c = makeCanvas(W, H);
    const ctx = c.getContext('2d');
    ctx.fillStyle = style.body;
    ctx.fillRect(0, 0, W, H);
    // alternating accent stripes around the rim
    ctx.fillStyle = style.accent;
    const stripes = 24;
    for (let i = 0; i < stripes; i++) {
      if (i % 2 === 0) ctx.fillRect((i / stripes) * W, 0, (W / stripes) * 0.7, H);
    }
    const tex = new THREE.CanvasTexture(c);
    tex.colorSpace = THREE.SRGBColorSpace;
    cache.set(key, tex);
    return tex;
  }

  return { cardFace, cardBack, chipFace, chipEdge };
})();

// =============================================================================
// Scene setup
// =============================================================================
const canvas = document.getElementById('scene');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;

const scene = new THREE.Scene();
scene.background = new THREE.Color(CONFIG.background);
scene.fog = new THREE.FogExp2(CONFIG.background, 0.018);

const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 200);
camera.position.set(0, 14, 26);
camera.lookAt(0, 2, 0);

// Environment reflections for the glossy chips/cards (PBR look).
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;

// ---- Lighting: warm casino spotlights -----------------------------------
const ambient = new THREE.AmbientLight(0xffffff, 0.35);
scene.add(ambient);

const key = new THREE.DirectionalLight(0xfff2d6, 2.2);
key.position.set(12, 30, 16);
key.castShadow = true;
key.shadow.mapSize.set(2048, 2048);
key.shadow.camera.near = 1;
key.shadow.camera.far = 90;
key.shadow.camera.left = -30;
key.shadow.camera.right = 30;
key.shadow.camera.top = 30;
key.shadow.camera.bottom = -30;
key.shadow.bias = -0.0004;
scene.add(key);

const rimGold = new THREE.SpotLight(0xe9c46a, 600, 90, Math.PI / 5, 0.5, 1.4);
rimGold.position.set(-18, 26, -10);
scene.add(rimGold);

const rimBlue = new THREE.SpotLight(0x4a90d9, 400, 90, Math.PI / 5, 0.5, 1.4);
rimBlue.position.set(20, 22, -14);
scene.add(rimBlue);

// =============================================================================
// Physics world
// =============================================================================
const world = new CANNON.World();
world.gravity.set(0, CONFIG.gravity, 0);
world.broadphase = new CANNON.SAPBroadphase(world);
world.allowSleep = true;
world.solver.iterations = 12;

const feltMat = new CANNON.Material('felt');
const pieceMat = new CANNON.Material('piece');
world.addContactMaterial(new CANNON.ContactMaterial(feltMat, pieceMat, { friction: 0.4, restitution: 0.35 }));
world.addContactMaterial(new CANNON.ContactMaterial(pieceMat, pieceMat, { friction: 0.35, restitution: 0.25 }));

// ---- Table (visual + physics) -------------------------------------------
const TABLE_SIZE = 30;
const tableGeo = new THREE.CylinderGeometry(TABLE_SIZE, TABLE_SIZE, 1.2, 64);
const tableMat = new THREE.MeshStandardMaterial({ color: CONFIG.felt, roughness: 0.95, metalness: 0.0 });
const table = new THREE.Mesh(tableGeo, tableMat);
table.position.y = -0.6;
table.receiveShadow = true;
scene.add(table);

// felt subtle radial highlight ring
const ringGeo = new THREE.RingGeometry(TABLE_SIZE * 0.62, TABLE_SIZE * 0.66, 80);
const ringMat = new THREE.MeshBasicMaterial({ color: 0xe9c46a, transparent: true, opacity: 0.18, side: THREE.DoubleSide });
const ring = new THREE.Mesh(ringGeo, ringMat);
ring.rotation.x = -Math.PI / 2;
ring.position.y = 0.02;
scene.add(ring);

// ground physics plane
const groundBody = new CANNON.Body({ mass: 0, material: feltMat });
groundBody.addShape(new CANNON.Plane());
groundBody.quaternion.setFromEuler(-Math.PI / 2, 0, 0);
world.addBody(groundBody);

// invisible walls so pieces don't slide off the big screen edges
function addWall(nx, nz, dist) {
  const b = new CANNON.Body({ mass: 0, material: feltMat });
  b.addShape(new CANNON.Plane());
  const n = new CANNON.Vec3(nx, 0, nz);
  const q = new CANNON.Quaternion();
  q.setFromVectors(new CANNON.Vec3(0, 0, 1), n);
  b.quaternion.copy(q);
  b.position.set(-nx * dist, 0, -nz * dist);
  world.addBody(b);
}
const WALL = 16;
addWall(1, 0, WALL); addWall(-1, 0, WALL); addWall(0, 1, WALL); addWall(0, -1, WALL);

// =============================================================================
// Object pool — cards & chips
// =============================================================================
const pieces = []; // { mesh, body, bornAt, dead }

const CARD = { w: 2.5, h: 3.5, d: 0.06 };
const CHIP = { r: 1.15, h: 0.34 };

// shared geometries
const cardGeo = new THREE.BoxGeometry(CARD.w, CARD.h, CARD.d);
const chipGeo = new THREE.CylinderGeometry(CHIP.r, CHIP.r, CHIP.h, 40);

function makeCard() {
  const rank = RANKS[(Math.random() * RANKS.length) | 0];
  const suit = SUITS[(Math.random() * SUITS.length) | 0];
  const face = TextureCache.cardFace(rank, suit);
  const back = TextureCache.cardBack();
  const edge = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.6 });
  const faceMat = new THREE.MeshStandardMaterial({ map: face, roughness: 0.45, metalness: 0.0 });
  const backMat = new THREE.MeshStandardMaterial({ map: back, roughness: 0.45, metalness: 0.05 });
  // BoxGeometry face order: +x,-x,+y,-y,+z,-z  → front=+z, back=-z
  const mats = [edge, edge, edge, edge, faceMat, backMat];
  const mesh = new THREE.Mesh(cardGeo, mats);
  mesh.castShadow = true; mesh.receiveShadow = true;

  const body = new CANNON.Body({ mass: 0.6, material: pieceMat });
  body.addShape(new CANNON.Box(new CANNON.Vec3(CARD.w / 2, CARD.h / 2, CARD.d / 2)));
  body.linearDamping = 0.15;
  body.angularDamping = 0.2;
  return { mesh, body, type: 'card' };
}

function makeChip() {
  const style = CHIP_STYLES[(Math.random() * CHIP_STYLES.length) | 0];
  const faceTex = TextureCache.chipFace(style);
  const edgeTex = TextureCache.chipEdge(style);
  const faceMat = new THREE.MeshStandardMaterial({ map: faceTex, roughness: 0.35, metalness: 0.15 });
  const edgeMat = new THREE.MeshStandardMaterial({ map: edgeTex, roughness: 0.4, metalness: 0.15 });
  // CylinderGeometry material order: side, top, bottom
  const mesh = new THREE.Mesh(chipGeo, [edgeMat, faceMat, faceMat]);
  mesh.castShadow = true; mesh.receiveShadow = true;

  const body = new CANNON.Body({ mass: 0.9, material: pieceMat });
  body.addShape(new CANNON.Cylinder(CHIP.r, CHIP.r, CHIP.h, 16));
  body.linearDamping = 0.15;
  body.angularDamping = 0.25;
  return { mesh, body, type: 'chip' };
}

function spawn() {
  if (pieces.filter(p => !p.dead).length >= CONFIG.maxObjects) recycleOldest();

  const obj = Math.random() < CONFIG.cardChipRatio ? makeCard() : makeChip();
  const { mesh, body } = obj;

  // random position in the drop zone
  const ang = Math.random() * Math.PI * 2;
  const rad = Math.random() * CONFIG.spawnRadius;
  body.position.set(Math.cos(ang) * rad, CONFIG.spawnHeight + Math.random() * 6, Math.sin(ang) * rad);

  // random tumble
  body.quaternion.setFromEuler(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);
  body.angularVelocity.set((Math.random() - 0.5) * 8, (Math.random() - 0.5) * 8, (Math.random() - 0.5) * 8);
  body.velocity.set((Math.random() - 0.5) * 2, -2, (Math.random() - 0.5) * 2);

  scene.add(mesh);
  world.addBody(body);

  const piece = { ...obj, bornAt: performance.now(), dead: false };
  pieces.push(piece);
}

function disposePiece(p) {
  scene.remove(p.mesh);
  world.removeBody(p.body);
  // dispose per-mesh materials (textures are cached/shared, so leave them)
  const mats = Array.isArray(p.mesh.material) ? p.mesh.material : [p.mesh.material];
  mats.forEach(m => { if (m && !m.map) m.dispose?.(); });
  p.dead = true;
}

function recycleOldest() {
  let oldest = null;
  for (const p of pieces) {
    if (p.dead) continue;
    if (!oldest || p.bornAt < oldest.bornAt) oldest = p;
  }
  if (oldest) disposePiece(oldest);
}

// Manual "deal a burst" — fun for showing off / spacebar.
function dealBurst(n = 24) {
  for (let i = 0; i < n; i++) setTimeout(spawn, i * 40);
}

// =============================================================================
// Post-processing: subtle bloom so chips/lights glow on a big screen.
// =============================================================================
const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(window.innerWidth, window.innerHeight), 0.55, 0.7, 0.85);
composer.addPass(bloom);
composer.addPass(new OutputPass());

// =============================================================================
// Main loop
// =============================================================================
let lastSpawn = 0;
let lastTime = performance.now();
const camTarget = new THREE.Vector3(0, 3, 0);

function animate(now) {
  requestAnimationFrame(animate);
  const dt = Math.min((now - lastTime) / 1000, 1 / 30);
  lastTime = now;

  // spawn cadence
  if (now - lastSpawn > CONFIG.spawnIntervalMs) {
    spawn();
    lastSpawn = now;
  }

  // step physics
  world.step(1 / 60, dt, 4);

  // sync meshes + fade/recycle aged pieces
  for (const p of pieces) {
    if (p.dead) continue;
    p.mesh.position.copy(p.body.position);
    p.mesh.quaternion.copy(p.body.quaternion);

    const age = now - p.bornAt;
    if (age > CONFIG.objectLifetimeMs) disposePiece(p);
  }
  // compact the array occasionally
  if (pieces.length > CONFIG.maxObjects * 2) {
    for (let i = pieces.length - 1; i >= 0; i--) if (pieces[i].dead) pieces.splice(i, 1);
  }

  // slow cinematic camera orbit — great for an unattended big screen
  const t = now * 0.00007;
  camera.position.x = Math.sin(t) * 27;
  camera.position.z = Math.cos(t) * 27;
  camera.position.y = 14 + Math.sin(t * 1.7) * 2.5;
  camera.lookAt(camTarget);

  composer.render();
}

// =============================================================================
// Resize / fullscreen / controls
// =============================================================================
function onResize() {
  const w = window.innerWidth, h = window.innerHeight;
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  renderer.setSize(w, h);
  composer.setSize(w, h);
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
    document.getElementById('headline').style.display =
      (document.getElementById('headline').style.display === 'none') ? '' : 'none';
  }
});
// any interaction re-shows the hint briefly
window.addEventListener('pointerdown', () => {
  hint.classList.remove('hide');
  clearTimeout(hintTimer);
  hintTimer = setTimeout(() => hint.classList.add('hide'), 4000);
});

// =============================================================================
// Optional URL customization for the marquee text:
//   index.html?title=Your%20Casino&subtitle=Try%20Your%20Luck
// =============================================================================
const params = new URLSearchParams(location.search);
if (params.get('title')) document.querySelector('[data-title]').textContent = params.get('title');
if (params.get('subtitle')) document.querySelector('[data-subtitle]').textContent = params.get('subtitle');

// =============================================================================
// Kick things off
// =============================================================================
function start() {
  document.getElementById('loading').classList.add('done');
  // seed a nice opening pile
  dealBurst(40);
  requestAnimationFrame(animate);
}

// Give textures/env a tick to warm up, then go.
setTimeout(start, 400);
