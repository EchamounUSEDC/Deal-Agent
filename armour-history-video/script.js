/* ==========================================================================
   script.js — animation engine, audio system, controls, and video export
   --------------------------------------------------------------------------
   The film is rendered deterministically: render(t) can draw any moment in
   time, which makes play/pause/seek/export straightforward and keeps the
   animation correct while MediaRecorder captures the canvas stream.
   ========================================================================== */

(() => {
  'use strict';

  const W = 1920, H = 1080;
  const EXPORT_FPS = 30;
  const TRANS = 1.5;           // seconds an exit transition occupies at scene end
  const BOIL_FPS = 8;          // hand-drawn "boiling line" refresh rate

  const canvas = document.getElementById('paper');
  const mainCtx = canvas.getContext('2d');
  let ctx = mainCtx; // element renderers draw through this; it is temporarily
                     // pointed at the offscreen scene layer during renderFrame
  const measurePath = document.getElementById('measure-path');

  /* ------------------------------------------------------------------------
     Deterministic pseudo-random (keeps wobble stable per element per frame)
     ------------------------------------------------------------------------ */
  function hashNoise(a, b) {
    let h = (a * 374761393 + b * 668265263) | 0;
    h = (h ^ (h >> 13)) * 1274126177;
    h = h ^ (h >> 16);
    return ((h >>> 0) % 10000) / 10000 - 0.5; // [-0.5, 0.5)
  }

  const easeInOut = (p) => (p < 0.5 ? 2 * p * p : 1 - Math.pow(-2 * p + 2, 2) / 2);
  const clamp01 = (v) => Math.max(0, Math.min(1, v));

  /* ------------------------------------------------------------------------
     Timeline assembly
     ------------------------------------------------------------------------ */
  let TOTAL = 0;
  function buildTimeline() {
    let t = 0;
    for (const s of SCENES) {
      s.start = t;
      t += s.duration;
      s.end = t;
    }
    TOTAL = t;
  }

  /* ------------------------------------------------------------------------
     Element preparation: Path2D + measured length + sampled tip points
     ------------------------------------------------------------------------ */
  function prepareElements() {
    let idx = 0;
    for (const scene of SCENES) {
      for (const e of scene.elements) {
        e.seed = idx++;
        if (e.type === 'path' || e.type === 'wash') {
          e.path2d = new Path2D(e.d);
          measurePath.setAttribute('d', e.d);
          try {
            e.len = measurePath.getTotalLength() || 1;
            if (e.type === 'path') {
              const N = 48;
              e.pts = [];
              for (let i = 0; i <= N; i++) {
                const p = measurePath.getPointAtLength((e.len * i) / N);
                e.pts.push([p.x, p.y]);
              }
            }
          } catch (_) {
            e.len = 800;
            e.pts = [];
          }
        }
      }
    }
  }

  /* ------------------------------------------------------------------------
     Paper background (pre-rendered grain layer)
     ------------------------------------------------------------------------ */
  const grain = document.createElement('canvas');
  grain.width = W; grain.height = H;
  function buildGrain() {
    const g = grain.getContext('2d');
    g.clearRect(0, 0, W, H);
    // fine noise
    for (let i = 0; i < 8200; i++) {
      const x = (hashNoise(i, 1) + 0.5) * W;
      const y = (hashNoise(i, 2) + 0.5) * H;
      const a = 0.025 + (hashNoise(i, 3) + 0.5) * 0.04;
      g.fillStyle = `rgba(84, 68, 44, ${a.toFixed(3)})`;
      g.fillRect(x, y, 1.6, 1.6);
    }
    // paper fibres
    g.strokeStyle = 'rgba(120, 100, 66, 0.05)';
    g.lineWidth = 1;
    for (let i = 0; i < 130; i++) {
      const x = (hashNoise(i, 4) + 0.5) * W;
      const y = (hashNoise(i, 5) + 0.5) * H;
      const dx = hashNoise(i, 6) * 60, dy = hashNoise(i, 7) * 14;
      g.beginPath(); g.moveTo(x, y); g.lineTo(x + dx, y + dy); g.stroke();
    }
  }

  function drawPaper() {
    const grad = ctx.createRadialGradient(W * 0.5, H * 0.42, H * 0.2, W * 0.5, H * 0.5, W * 0.72);
    grad.addColorStop(0, INK.ivory);
    grad.addColorStop(1, INK.ivoryDeep);
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, W, H);
    ctx.drawImage(grain, 0, 0);
  }

  /* ------------------------------------------------------------------------
     Element renderers
     ------------------------------------------------------------------------ */
  function drawPathElement(e, sceneT, exitUndraw) {
    let p = clamp01((sceneT - e.at) / e.dur);
    if (p <= 0) return;
    const fadeOut = e.until ? 1 - clamp01((sceneT - e.until) / 0.8) : 1;
    if (fadeOut <= 0) return;
    // Varying, human drawing speed: eased with a per-element phase wobble.
    let pd = easeInOut(p);
    pd = clamp01(pd + 0.028 * Math.sin(pd * 7 + e.seed) * (1 - pd) * pd * 4);
    if (exitUndraw > 0) pd = clamp01(Math.min(pd, 1 - exitUndraw * 1.15));
    if (pd <= 0) return;

    const boil = Math.floor(sceneT * BOIL_FPS);
    const jx = hashNoise(e.seed, boil) * e.wobble * 2;
    const jy = hashNoise(e.seed + 991, boil) * e.wobble * 2;

    ctx.save();
    ctx.translate(jx, jy);
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.strokeStyle = e.stroke;
    ctx.globalAlpha *= e.alpha * fadeOut;
    ctx.setLineDash([e.len, e.len]);
    ctx.lineDashOffset = e.len * (1 - pd);
    ctx.lineWidth = e.width;
    ctx.stroke(e.path2d);
    // Pencil-texture second pass: slightly offset, faint
    ctx.globalAlpha *= 0.32;
    ctx.translate(0.8, -0.6);
    ctx.lineWidth = Math.max(1, e.width * 0.55);
    ctx.stroke(e.path2d);
    ctx.setLineDash([]);
    ctx.restore();

    // Pencil dust at the moving tip
    if (e.tip && pd > 0.02 && pd < 0.985 && e.pts && e.pts.length) {
      const i = Math.min(e.pts.length - 1, Math.floor(pd * (e.pts.length - 1)));
      const [tx, ty] = e.pts[i];
      ctx.save();
      ctx.fillStyle = 'rgba(43, 40, 35, 0.35)';
      for (let k = 0; k < 3; k++) {
        const ox = hashNoise(e.seed + k, boil + k) * 10;
        const oy = hashNoise(e.seed + 40 + k, boil + k) * 10;
        ctx.globalAlpha = 0.30 - k * 0.08;
        ctx.fillRect(tx + jx + ox, ty + jy + oy, 2.1, 2.1);
      }
      ctx.restore();
    }
  }

  function drawWashElement(e, sceneT) {
    const p = clamp01((sceneT - e.at) / e.dur);
    if (p <= 0) return;
    const fadeOut = e.until ? 1 - clamp01((sceneT - e.until) / 0.8) : 1;
    if (fadeOut <= 0) return;
    ctx.save();
    ctx.globalCompositeOperation = 'multiply';
    ctx.globalAlpha *= e.alpha * easeInOut(p) * fadeOut;
    ctx.fillStyle = e.color;
    // soft, bled edge
    ctx.shadowColor = e.color;
    ctx.shadowBlur = 26;
    ctx.fill(e.path2d);
    ctx.restore();
  }

  function fontFor(e) {
    if (e.style === 'title') return `600 ${e.size}px Georgia, 'Times New Roman', serif`;
    if (e.style === 'label') return `${e.size}px Georgia, 'Times New Roman', serif`;
    return `italic ${e.size}px Georgia, 'Times New Roman', serif`; // 'hand'
  }

  function drawTextElement(e, sceneT) {
    const p = clamp01((sceneT - e.at) / e.dur);
    if (p <= 0) return;
    const str = e.text;
    const chars = Math.max(1, Math.round(str.length * easeInOut(p)));
    const visible = str.slice(0, chars);
    const boil = Math.floor(sceneT * BOIL_FPS);
    const fadeOut = e.until ? 1 - clamp01((sceneT - e.until) / 0.8) : 1;
    if (fadeOut <= 0) return;
    ctx.save();
    ctx.font = fontFor(e);
    ctx.fillStyle = e.color;
    ctx.globalAlpha *= e.alpha * fadeOut;
    ctx.textBaseline = 'alphabetic';
    if (e.style === 'title' || e.style === 'label') {
      // measured centering on the full string so it doesn't shift while writing
      const full = ctx.measureText(str).width;
      let x = e.align === 'center' ? e.x - full / 2 : e.x;
      const jy = hashNoise(e.seed, boil) * 0.8;
      if (e.style === 'title') {
        ctx.save();
        ctx.font = `600 ${e.size}px Georgia, serif`;
      }
      ctx.fillText(visible, x, e.y + jy);
      if (e.style === 'title') ctx.restore();
    } else {
      // handwritten: per-character jitter
      const full = ctx.measureText(str).width;
      let x = e.align === 'center' ? e.x - full / 2 : e.x;
      for (let i = 0; i < visible.length; i++) {
        const chW = ctx.measureText(visible[i]).width;
        const jy = hashNoise(e.seed + i, boil) * 1.6;
        const rot = hashNoise(e.seed + i * 7, 3) * 0.05;
        ctx.save();
        ctx.translate(x + chW / 2, e.y + jy);
        ctx.rotate(rot);
        ctx.fillText(visible[i], -chW / 2, 0);
        ctx.restore();
        x += chW;
      }
    }
    ctx.restore();
  }

  /* ------------------------------------------------------------------------
     Scene rendering with camera + exit transition
     ------------------------------------------------------------------------ */
  const sceneLayer = document.createElement('canvas');
  sceneLayer.width = W; sceneLayer.height = H;
  const sceneCtx = sceneLayer.getContext('2d');

  function renderSceneContent(scene, sceneT, exitP) {
    const undraw = scene.exit === 'undraw' || scene.exit === 'eraser' ? exitP : 0;
    for (const e of scene.elements) {
      if (e.type === 'path') drawPathElement(e, sceneT, undraw);
      else if (e.type === 'wash') drawWashElement(e, sceneT);
      else if (e.type === 'text') drawTextElement(e, sceneT);
    }
  }

  function cameraFor(scene, sceneT, exitP) {
    // Gentle default drift; zoomfade exits push in.
    let s = 1 + 0.012 * Math.sin((sceneT / Math.max(1, scene.duration)) * Math.PI);
    let x = 0, y = 0;
    if (scene.exit === 'zoomfade' && exitP > 0) {
      s *= 1 + exitP * 0.16;
      y -= exitP * 30;
    }
    return { s, x, y };
  }

  function renderFrame(t) {
    // Which scene?
    let scene = SCENES[SCENES.length - 1];
    for (const s of SCENES) {
      if (t < s.end) { scene = s; break; }
    }
    const sceneT = Math.min(t - scene.start, scene.duration);
    const exitP = clamp01((sceneT - (scene.duration - TRANS)) / TRANS);

    // Base paper on the visible canvas
    ctx = mainCtx;
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    drawPaper();

    // Scene content on its own layer (needed for wipes/fades)
    sceneCtx.setTransform(1, 0, 0, 1, 0, 0);
    sceneCtx.clearRect(0, 0, W, H);
    const cam = cameraFor(scene, sceneT, exitP);
    sceneCtx.save();
    sceneCtx.translate(W / 2 + cam.x, H / 2 + cam.y);
    sceneCtx.scale(cam.s, cam.s);
    sceneCtx.translate(-W / 2, -H / 2);
    ctx = sceneCtx; // point element renderers at the layer
    renderSceneContent(scene, sceneT, exitP);
    ctx = mainCtx;
    sceneCtx.restore();

    // Composite the layer with the exit effect
    compositeLayer(scene, sceneT, exitP);

    // Vignette
    ctx.save();
    const v = ctx.createRadialGradient(W / 2, H / 2, H * 0.42, W / 2, H / 2, W * 0.75);
    v.addColorStop(0, 'rgba(0,0,0,0)');
    v.addColorStop(1, 'rgba(58, 44, 26, 0.16)');
    ctx.fillStyle = v;
    ctx.fillRect(0, 0, W, H);
    ctx.restore();
  }

  function compositeLayer(scene, sceneT, exitP) {
    if (exitP <= 0 || scene.exit === 'undraw') {
      ctx.drawImage(sceneLayer, 0, 0);
      return;
    }
    switch (scene.exit) {
      case 'fade': {
        ctx.save();
        ctx.globalAlpha = 1 - easeInOut(exitP);
        ctx.drawImage(sceneLayer, 0, 0);
        ctx.restore();
        break;
      }
      case 'zoomfade': {
        ctx.save();
        ctx.globalAlpha = 1 - easeInOut(exitP);
        ctx.drawImage(sceneLayer, 0, 0);
        ctx.restore();
        break;
      }
      case 'dust': {
        ctx.save();
        ctx.globalAlpha = 1 - easeInOut(exitP);
        ctx.drawImage(sceneLayer, 0, 0);
        ctx.restore();
        // sweeping dust streaks
        ctx.save();
        ctx.strokeStyle = 'rgba(120, 100, 66, 0.5)';
        ctx.lineWidth = 2;
        const n = 26;
        for (let i = 0; i < n; i++) {
          const yy = (i / n) * H + hashNoise(i, 8) * 40;
          const sweep = exitP * (W + 700) - 350;
          const x0 = sweep - (hashNoise(i, 9) + 0.5) * 460;
          ctx.globalAlpha = 0.35 * (1 - exitP * 0.4);
          ctx.beginPath();
          ctx.moveTo(x0, yy);
          ctx.quadraticCurveTo(x0 + 120, yy - 12, x0 + 260, yy + 6);
          ctx.stroke();
        }
        ctx.restore();
        break;
      }
      case 'wipe': {
        // diagonal paper wipe with a sketchy leading edge
        const px = easeInOut(exitP) * (W + 500);
        ctx.save();
        ctx.beginPath();
        ctx.moveTo(px, -50);
        ctx.lineTo(W + 50, -50);
        ctx.lineTo(W + 50, H + 50);
        ctx.lineTo(px - 320, H + 50);
        ctx.closePath();
        ctx.clip();
        ctx.drawImage(sceneLayer, 0, 0);
        ctx.restore();
        // leading sketch line
        ctx.save();
        ctx.strokeStyle = 'rgba(43, 40, 35, 0.5)';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(px + 6, -20);
        for (let yy = 0; yy <= H; yy += 60) {
          ctx.lineTo(px + 6 - (yy / H) * 320 + hashNoise(yy, 12) * 26, yy);
        }
        ctx.stroke();
        ctx.restore();
        break;
      }
      case 'eraser': {
        // big eraser passes: horizontal ivory bands scrub across
        ctx.drawImage(sceneLayer, 0, 0);
        ctx.save();
        const bands = 7;
        for (let i = 0; i < bands; i++) {
          const bandP = clamp01(exitP * 1.5 - i * 0.08);
          if (bandP <= 0) continue;
          const y0 = (i / bands) * H;
          const dir = i % 2 === 0 ? 1 : -1;
          const wpx = bandP * (W + 400);
          const x0 = dir === 1 ? -200 : W + 200 - wpx;
          ctx.fillStyle = INK.ivory;
          ctx.globalAlpha = 0.94;
          ctx.fillRect(dir === 1 ? x0 : x0, y0, wpx, H / bands + 2);
          // eraser crumbs
          ctx.fillStyle = 'rgba(120, 100, 66, 0.4)';
          for (let k = 0; k < 5; k++) {
            const cx = (dir === 1 ? x0 + wpx : x0) + hashNoise(i * 10 + k, 5) * 60;
            const cy = y0 + (hashNoise(i * 20 + k, 6) + 0.5) * (H / bands);
            ctx.fillRect(cx, cy, 3, 2);
          }
        }
        ctx.restore();
        break;
      }
      default:
        ctx.drawImage(sceneLayer, 0, 0);
    }
  }

  /* ========================================================================
     AUDIO — narration (speech synthesis or files), procedural music, SFX
     ======================================================================== */
  const audio = {
    ctx: null,
    master: null, music: null, narr: null, sfx: null,
    recDest: null,
    buffers: {},       // sceneId -> AudioBuffer (professional narration)
    musicBuffer: null, // optional background.mp3
    started: false,
    currentNarrSource: null,
    musicNodes: [],
    muted: false,
  };

  function initAudio() {
    if (audio.ctx) return;
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return;
    audio.ctx = new AC();
    audio.master = audio.ctx.createGain();
    audio.music = audio.ctx.createGain();
    audio.narr = audio.ctx.createGain();
    audio.sfx = audio.ctx.createGain();
    audio.music.gain.value = 0.16;
    audio.narr.gain.value = 1.0;
    audio.sfx.gain.value = 0.5;
    audio.music.connect(audio.master);
    audio.narr.connect(audio.master);
    audio.sfx.connect(audio.master);
    audio.master.connect(audio.ctx.destination);
    audio.recDest = audio.ctx.createMediaStreamDestination();
    audio.master.connect(audio.recDest);
  }

  async function probeNarration() {
    // Load professional narration files when present; missing files are fine.
    const jobs = Object.entries(AUDIO_MANIFEST).map(async ([sceneId, url]) => {
      try {
        const res = await fetch(url);
        if (!res.ok) return;
        const buf = await res.arrayBuffer();
        audio.buffers[sceneId] = await audio.ctx.decodeAudioData(buf);
      } catch (_) { /* placeholder narration will be used */ }
    });
    try {
      const res = await fetch(MUSIC_FILE);
      if (res.ok) {
        audio.musicBuffer = await audio.ctx.decodeAudioData(await res.arrayBuffer());
      }
    } catch (_) { /* procedural bed will be used */ }
    await Promise.allSettled(jobs);
    // Synchronize scene duration to available audio.
    for (const s of SCENES) {
      const b = audio.buffers[s.id];
      if (b && b.duration + 1.6 > s.duration) s.duration = Math.ceil(b.duration + 2);
    }
    buildTimeline();
  }

  function duckMusic(down) {
    if (!audio.ctx) return;
    const target = down ? 0.055 : 0.16;
    audio.music.gain.cancelScheduledValues(audio.ctx.currentTime);
    audio.music.gain.linearRampToValueAtTime(target, audio.ctx.currentTime + 0.6);
  }

  function stopNarration() {
    if (audio.currentNarrSource) {
      try { audio.currentNarrSource.stop(); } catch (_) {}
      audio.currentNarrSource = null;
    }
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
    duckMusic(false);
  }

  function playNarration(scene, offset = 0) {
    stopNarration();
    if (audio.muted) return;
    duckMusic(true);
    const buf = audio.ctx && audio.buffers[scene.id];
    if (buf) {
      const src = audio.ctx.createBufferSource();
      src.buffer = buf;
      src.connect(audio.narr);
      src.onended = () => { if (audio.currentNarrSource === src) duckMusic(false); };
      try { src.start(0, Math.min(offset, Math.max(0, buf.duration - 0.05))); } catch (_) {}
      audio.currentNarrSource = src;
      return;
    }
    // Placeholder: browser speech synthesis (not captured in exports).
    if ('speechSynthesis' in window && offset < 1.0) {
      const u = new SpeechSynthesisUtterance(scene.narration);
      u.rate = 0.94; u.pitch = 0.85; u.volume = 0.95;
      const voices = window.speechSynthesis.getVoices();
      const pick = voices.find(v => /en[-_]US/i.test(v.lang) && /male|David|Alex|Daniel/i.test(v.name))
        || voices.find(v => /en[-_]US/i.test(v.lang)) || voices[0];
      if (pick) u.voice = pick;
      u.onend = () => duckMusic(false);
      try { window.speechSynthesis.speak(u); } catch (_) {}
    }
  }

  /* --- Procedural music bed (placeholder until background.mp3 is added) --- */
  function startMusic() {
    if (!audio.ctx) return;
    stopMusicNodes();
    if (audio.musicBuffer) {
      const src = audio.ctx.createBufferSource();
      src.buffer = audio.musicBuffer;
      src.loop = true;
      src.connect(audio.music);
      src.start();
      audio.musicNodes.push(src);
      return;
    }
    const now = audio.ctx.currentTime;
    // Warm pad: two detuned triangles through a gentle lowpass.
    const lp = audio.ctx.createBiquadFilter();
    lp.type = 'lowpass'; lp.frequency.value = 640; lp.Q.value = 0.4;
    const padGain = audio.ctx.createGain();
    padGain.gain.value = 0.05;
    lp.connect(padGain); padGain.connect(audio.music);
    [[110, 0], [164.8, 3], [220, -2]].forEach(([f, det]) => {
      const o = audio.ctx.createOscillator();
      o.type = 'triangle'; o.frequency.value = f; o.detune.value = det;
      o.connect(lp); o.start(now);
      audio.musicNodes.push(o);
    });
    // slow breathing on the pad
    const lfo = audio.ctx.createOscillator();
    const lfoGain = audio.ctx.createGain();
    lfo.frequency.value = 0.07; lfoGain.gain.value = 0.02;
    lfo.connect(lfoGain); lfoGain.connect(padGain.gain); lfo.start(now);
    audio.musicNodes.push(lfo);
    // Sparse pentatonic plucks (guitar-ish): scheduled loop.
    const scale = [220, 261.6, 293.7, 329.6, 392, 440];
    let step = 0;
    const pluckTimer = setInterval(() => {
      if (!audio.ctx || audio.muted) return;
      if (hashNoise(step, 77) > 0.18) { step++; return; } // sparse
      const f = scale[Math.abs(Math.floor(hashNoise(step, 31) * 12)) % scale.length];
      const o = audio.ctx.createOscillator();
      const g = audio.ctx.createGain();
      const bp = audio.ctx.createBiquadFilter();
      bp.type = 'bandpass'; bp.frequency.value = f * 2; bp.Q.value = 1.4;
      o.type = 'sawtooth'; o.frequency.value = f;
      const t0 = audio.ctx.currentTime;
      g.gain.setValueAtTime(0.05, t0);
      g.gain.exponentialRampToValueAtTime(0.0008, t0 + 1.6);
      o.connect(bp); bp.connect(g); g.connect(audio.music);
      o.start(t0); o.stop(t0 + 1.7);
      step++;
    }, 1400);
    audio.musicNodes.push({ stop: () => clearInterval(pluckTimer) });
  }

  function stopMusicNodes() {
    for (const n of audio.musicNodes) { try { n.stop(); } catch (_) {} }
    audio.musicNodes = [];
  }

  /* --- Tiny procedural sound effects --- */
  function playSfx(type) {
    if (!audio.ctx || audio.muted) return;
    const t0 = audio.ctx.currentTime;
    if (type === 'whistle') {
      [660, 553].forEach((f) => {
        const o = audio.ctx.createOscillator();
        const g = audio.ctx.createGain();
        o.type = 'sine'; o.frequency.setValueAtTime(f, t0);
        o.frequency.linearRampToValueAtTime(f * 0.94, t0 + 1.4);
        g.gain.setValueAtTime(0.0001, t0);
        g.gain.linearRampToValueAtTime(0.05, t0 + 0.15);
        g.gain.linearRampToValueAtTime(0.0001, t0 + 1.6);
        o.connect(g); g.connect(audio.sfx);
        o.start(t0); o.stop(t0 + 1.7);
      });
    } else if (type === 'wind' || type === 'cattle') {
      const len = type === 'wind' ? 5 : 1.4;
      const buf = audio.ctx.createBuffer(1, audio.ctx.sampleRate * len, audio.ctx.sampleRate);
      const data = buf.getChannelData(0);
      for (let i = 0; i < data.length; i++) data[i] = (Math.random() * 2 - 1) * 0.6;
      const src = audio.ctx.createBufferSource(); src.buffer = buf;
      const f = audio.ctx.createBiquadFilter();
      f.type = type === 'wind' ? 'bandpass' : 'lowpass';
      f.frequency.value = type === 'wind' ? 420 : 130;
      f.Q.value = type === 'wind' ? 0.5 : 2;
      const g = audio.ctx.createGain();
      g.gain.setValueAtTime(0.0001, t0);
      g.gain.linearRampToValueAtTime(type === 'wind' ? 0.035 : 0.06, t0 + 0.4);
      g.gain.linearRampToValueAtTime(0.0001, t0 + len);
      src.connect(f); f.connect(g); g.connect(audio.sfx);
      src.start(t0);
    } else if (type === 'hammer') {
      for (let k = 0; k < 3; k++) {
        const buf = audio.ctx.createBuffer(1, audio.ctx.sampleRate * 0.08, audio.ctx.sampleRate);
        const data = buf.getChannelData(0);
        for (let i = 0; i < data.length; i++) data[i] = (Math.random() * 2 - 1) * Math.exp(-i / (data.length * 0.18));
        const src = audio.ctx.createBufferSource(); src.buffer = buf;
        const g = audio.ctx.createGain(); g.gain.value = 0.09;
        src.connect(g); g.connect(audio.sfx);
        src.start(t0 + k * 0.34);
      }
    }
  }

  /* ========================================================================
     PLAYBACK ENGINE
     ======================================================================== */
  const engine = {
    t: 0,
    playing: false,
    lastTs: 0,
    activeSceneId: null,
    firedSfx: new Set(),
    exporting: false,
    recorder: null,
    finished: false,
  };

  function currentScene(t) {
    for (const s of SCENES) if (t < s.end) return s;
    return SCENES[SCENES.length - 1];
  }

  function tick(ts) {
    requestAnimationFrame(tick);
    if (!engine.playing) return;
    if (!engine.lastTs) engine.lastTs = ts;
    const dt = Math.min(0.05, (ts - engine.lastTs) / 1000);
    engine.lastTs = ts;
    engine.t += dt;

    if (engine.t >= TOTAL) {
      engine.t = TOTAL;
      renderFrame(TOTAL - 0.001);
      setPlaying(false);
      engine.finished = true;
      stopNarration();
      if (engine.exporting) finishExport();
      updateHud();
      return;
    }

    const scene = currentScene(engine.t);
    const sceneT = engine.t - scene.start;

    // Scene boundary: trigger narration
    if (scene.id !== engine.activeSceneId) {
      engine.activeSceneId = scene.id;
      playNarration(scene, sceneT > 0.6 ? sceneT : 0);
    }
    // SFX cues
    for (const cue of scene.sfx || []) {
      const key = `${scene.id}:${cue.type}:${cue.at}`;
      if (!engine.firedSfx.has(key) && sceneT >= cue.at && sceneT < cue.at + 0.4) {
        engine.firedSfx.add(key);
        playSfx(cue.type);
      }
    }

    renderFrame(engine.t);
    updateHud();
  }

  function setPlaying(on) {
    engine.playing = on;
    engine.lastTs = 0;
    playBtn.textContent = on ? '❚❚' : '▶';
    if (audio.ctx && audio.ctx.state === 'suspended') audio.ctx.resume();
    if (!on) {
      stopNarration();
    } else {
      engine.finished = false;
      // resume narration mid-scene when audio files are present
      const scene = currentScene(engine.t);
      engine.activeSceneId = scene.id;
      playNarration(scene, engine.t - scene.start);
    }
  }

  function seek(t, { silent = false } = {}) {
    engine.t = Math.max(0, Math.min(TOTAL - 0.001, t));
    engine.firedSfx = new Set();
    engine.activeSceneId = null;
    stopNarration();
    renderFrame(engine.t);
    updateHud();
    if (!silent && engine.playing) {
      const scene = currentScene(engine.t);
      engine.activeSceneId = scene.id;
      playNarration(scene, engine.t - scene.start);
    }
  }

  /* ========================================================================
     EXPORT — canvas.captureStream + MediaRecorder (WebM)
     ======================================================================== */
  function startExport() {
    if (engine.exporting) return;
    if (!('MediaRecorder' in window)) {
      alert('MediaRecorder is not supported in this browser. Try Chrome or Edge.');
      return;
    }
    const stream = canvas.captureStream(EXPORT_FPS);
    if (audio.recDest) {
      for (const track of audio.recDest.stream.getAudioTracks()) stream.addTrack(track);
    }
    const mime = ['video/webm;codecs=vp9,opus', 'video/webm;codecs=vp8,opus', 'video/webm']
      .find(m => MediaRecorder.isTypeSupported(m)) || '';
    const chunks = [];
    const rec = new MediaRecorder(stream, mime ? { mimeType: mime, videoBitsPerSecond: 9_000_000 } : undefined);
    rec.ondataavailable = (ev) => { if (ev.data && ev.data.size) chunks.push(ev.data); };
    rec.onstop = () => {
      const blob = new Blob(chunks, { type: 'video/webm' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'armour-building-history.webm';
      a.click();
      setTimeout(() => URL.revokeObjectURL(a.href), 4000);
    };
    engine.recorder = rec;
    engine.exporting = true;
    recIndicator.classList.remove('hidden');
    exportBtn.disabled = true;
    // restart from the top and play straight through
    seek(0, { silent: true });
    rec.start(400);
    setPlaying(true);
  }

  function finishExport() {
    if (!engine.exporting) return;
    engine.exporting = false;
    recIndicator.classList.add('hidden');
    exportBtn.disabled = false;
    if (engine.recorder && engine.recorder.state !== 'inactive') engine.recorder.stop();
    engine.recorder = null;
  }

  /* ========================================================================
     HUD / CONTROLS
     ======================================================================== */
  const playBtn = document.getElementById('play-btn');
  const restartBtn = document.getElementById('restart-btn');
  const muteBtn = document.getElementById('mute-btn');
  const fsBtn = document.getElementById('fs-btn');
  const exportBtn = document.getElementById('export-btn');
  const progress = document.getElementById('progress');
  const progressFill = document.getElementById('progress-fill');
  const progressTicks = document.getElementById('progress-ticks');
  const sceneLabel = document.getElementById('scene-label');
  const timeLabel = document.getElementById('time-label');
  const recIndicator = document.getElementById('rec-indicator');
  const loading = document.getElementById('loading');
  const beginBtn = document.getElementById('begin-btn');
  const loadingStatus = document.getElementById('loading-status');

  function fmt(t) {
    const m = Math.floor(t / 60), s = Math.floor(t % 60);
    return `${m}:${String(s).padStart(2, '0')}`;
  }

  function updateHud() {
    progressFill.style.width = `${(engine.t / TOTAL) * 100}%`;
    const scene = currentScene(engine.t);
    sceneLabel.textContent = scene.title;
    timeLabel.textContent = `${fmt(engine.t)} / ${fmt(TOTAL)}`;
  }

  function buildTicks() {
    progressTicks.innerHTML = '';
    for (const s of SCENES.slice(1)) {
      const tick = document.createElement('div');
      tick.className = 'tick';
      tick.style.left = `${(s.start / TOTAL) * 100}%`;
      progressTicks.appendChild(tick);
    }
  }

  playBtn.addEventListener('click', () => setPlaying(!engine.playing));
  restartBtn.addEventListener('click', () => { finishExport(); seek(0, { silent: true }); setPlaying(true); });
  muteBtn.addEventListener('click', () => {
    audio.muted = !audio.muted;
    if (audio.master) audio.master.gain.value = audio.muted ? 0 : 1;
    if (audio.muted) stopNarration();
    else if (engine.playing) {
      const scene = currentScene(engine.t);
      playNarration(scene, engine.t - scene.start);
    }
    muteBtn.textContent = audio.muted ? '🔇' : '🔊';
  });
  fsBtn.addEventListener('click', () => {
    const wrap = document.getElementById('stage-wrap');
    if (document.fullscreenElement) document.exitFullscreen();
    else wrap.requestFullscreen && wrap.requestFullscreen();
  });
  exportBtn.addEventListener('click', startExport);
  progress.addEventListener('click', (ev) => {
    if (engine.exporting) return; // keep exports continuous
    const r = progress.getBoundingClientRect();
    seek(((ev.clientX - r.left) / r.width) * TOTAL);
  });
  window.addEventListener('keydown', (ev) => {
    if (ev.code === 'Space') { ev.preventDefault(); setPlaying(!engine.playing); }
    if (ev.key === 'm') muteBtn.click();
    if (ev.key === 'f') fsBtn.click();
  });

  /* ========================================================================
     BOOT
     ======================================================================== */
  async function boot() {
    buildTimeline();
    prepareElements();
    buildGrain();
    renderFrame(0.001);
    updateHud();

    loadingStatus.textContent = 'Sharpening pencils…';
    initAudio();
    if (audio.ctx) {
      loadingStatus.textContent = 'Checking for narration recordings…';
      await Promise.race([probeNarration(), new Promise(res => setTimeout(res, 2500))]);
    }
    buildTicks();
    updateHud();

    loadingStatus.textContent = 'Ready';
    beginBtn.disabled = false;

    // Screenshot/debug hook: ?shot=<seconds> renders a still and skips audio.
    const params = new URLSearchParams(location.search);
    if (params.has('shot')) {
      loading.classList.add('hidden');
      const t = parseFloat(params.get('shot')) || 0;
      seek(t, { silent: true });
      return;
    }

    beginBtn.addEventListener('click', () => {
      loading.classList.add('fade-out');
      if (audio.ctx && audio.ctx.state === 'suspended') audio.ctx.resume();
      // Prime speech synthesis voices (some browsers populate lazily)
      if ('speechSynthesis' in window) window.speechSynthesis.getVoices();
      startMusic();
      seek(0, { silent: true });
      setPlaying(true);
    });
  }

  // Expose for debugging / automated tests
  window.ENGINE = { seek, setPlaying, renderFrame, get t() { return engine.t; }, get total() { return TOTAL; }, scenes: SCENES };

  requestAnimationFrame(tick);
  boot();

  /* ------------------------------------------------------------------------
     IMPORTANT implementation note about `ctx` binding:
     The element renderers reference the shared `ctx` variable. renderOnLayer
     temporarily swaps it so scene content is drawn onto the offscreen layer.
     ------------------------------------------------------------------------ */
})();
