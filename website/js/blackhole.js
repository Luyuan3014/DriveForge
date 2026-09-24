/**
 * DriveForge Web Landing Page - 3D Relativistic Black Hole & Accretion Engine
 * High-Fidelity General Relativity Physics, Gravitational Lensing & Hardware Telemetry Core
 * 
 * Key Features:
 * 1. Dual Gravitational Lensing (Interstellar Gargantua upper crown arch & underbelly arc)
 * 2. Multi-Layer Volumetric Plasma Flow (ambient bloom, core ionization stream & caustic filaments)
 * 3. Relativistic Doppler Beaming (approaching blueshift boost vs receding redshift dimming)
 * 4. Deep Void Event Horizon & Razor-Sharp Photon Sphere (Maximum UI Text Contrast)
 * 5. DriveForge Hardware Telemetry Integration (oscilloscope bus signal wavelets & peripheral infall)
 * 6. Spacetime Curvature Mouse Interaction (gravitational probe, 3D parallax tilt & shockwaves)
 * 7. Dynamic Text Clearance & Contrast Shield (Continuous smooth geodesics, zero text competition)
 */

(function (window, document) {
  'use strict';

  const canvas = document.getElementById('antigravity-canvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d', { alpha: true });
  if (!ctx) return;

  let prefersReducedMotion = document.documentElement.classList.contains('motion-reduced');
  let pageVisible = !document.hidden;
  let width = window.innerWidth;
  let height = window.innerHeight;
  let dpr = Math.min(window.devicePixelRatio || 1, 2.0);

  // Singularity & Horizon Physical Dimensions
  const blackHole = {
    x: width * 0.5,
    y: height * 0.22,
    targetX: width * 0.5,
    targetY: height * 0.22,
    rHorizon: 64,       // Event Horizon shadow radius (Rs)
    rPhoton: 88,        // Photon Sphere (~1.38 Rs)
    rIsco: 136,         // Innermost Stable Circular Orbit (~2.12 Rs)
    rOuter: 580         // Outer luminous accretion disk boundary
  };

  function updateBlackHoleMetrics() {
    const minDim = Math.min(width, height);
    const maxDim = Math.max(width, height);
    blackHole.rHorizon = Math.max(52, Math.min(minDim * 0.082, 78));
    blackHole.rPhoton = blackHole.rHorizon * 1.38;
    blackHole.rIsco = blackHole.rHorizon * 2.12;
    blackHole.rOuter = Math.max(blackHole.rHorizon * 6.4, Math.min(maxDim * 0.58, 800));
  }

  function resizeCanvas() {
    width = window.innerWidth;
    height = window.innerHeight;
    dpr = Math.min(window.devicePixelRatio || 1, 2.0);
    canvas.width = Math.round(width * dpr);
    canvas.height = Math.round(height * dpr);
    canvas.style.width = width + 'px';
    canvas.style.height = height + 'px';
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    updateBlackHoleMetrics();
  }

  // Pointer & Dynamic Motion State
  const mouse = {
    x: width * 0.5,
    y: height * 0.22,
    targetX: width * 0.5,
    targetY: height * 0.22,
    isHovering: false,
    lastActive: performance.now()
  };

  let pointerEnergy = 0;
  let scrollEnergy = 0;
  let interactionEnergy = 0;
  let lastFrameTime = performance.now();
  let time = 0;

  // Scroll & 3D Camera Angles
  let scrollY = window.scrollY || 0;
  let scrollVelocity = 0;
  let camPitch = 0;
  let targetCamPitch = 0;
  let camRoll = 0;
  let targetCamRoll = 0;
  let camYaw = 0;
  let targetCamYaw = 0;

  // Gravitational Wave Shockwaves from Clicks
  const shockwaves = [];

  function addShockwave(x, y) {
    if (shockwaves.length > 3) shockwaves.shift();
    shockwaves.push({
      x,
      y,
      radius: 14,
      maxRadius: Math.max(width * 0.42, 420),
      speed: 9.5,
      alpha: 0.90
    });
  }

  function isDarkMode() {
    return document.documentElement.classList.contains('dark');
  }

  // -------------------------------------------------------------
  // 1. Accretion Particles Pool (132 Relativistic Particles)
  // -------------------------------------------------------------
  const PARTICLE_COUNT = 132;
  const accretionParticles = [];

  for (let i = 0; i < PARTICLE_COUNT; i++) {
    const normR = Math.pow(Math.random(), 1.5);
    accretionParticles.push({
      normR: 0.05 + normR * 0.95,
      theta: Math.random() * Math.PI * 2,
      speedFactor: 0.0038 + Math.random() * 0.0030,
      vRadial: -(0.00010 + Math.random() * 0.00018),
      size: Math.random() * 1.2 + 0.60,
      zDisp: (Math.random() - 0.5) * 6 * (0.3 + normR * 0.7),
      baseAlpha: Math.random() * 0.48 + 0.28,
      tailLen: Math.random() * 2.0 + 0.9
    });
  }

  // -------------------------------------------------------------
  // 2. High-Tech Keplerian Streamlines & Digital Waveform Tracks
  // -------------------------------------------------------------
  const streamlines = [
    { normR: 0.03, width: 1.4, opacity: 0.45, hasPulse: true, label: 'EVIDENCE_GATE' },
    { normR: 0.22, width: 1.1, opacity: 0.32, hasPulse: true, label: 'CAN0_BUS' },
    { normR: 0.48, width: 0.90, opacity: 0.24, hasPulse: true, label: 'SPI1_CLK' },
    { normR: 0.78, width: 0.75, opacity: 0.16, hasPulse: false, label: 'UART_STREAM' }
  ];

  // Digital Waveform Packets (Simulating peripheral bus bitstream pulses)
  const busWavePackets = [
    { streamlineIdx: 0, angle: 0.4, speed: 0.0080, bitPattern: [1, 0, 1, 1, 0, 1, 0] },
    { streamlineIdx: 1, angle: 2.2, speed: 0.0062, bitPattern: [1, 1, 0, 1, 0, 0, 1] },
    { streamlineIdx: 2, angle: 4.1, speed: 0.0048, bitPattern: [1, 0, 1, 0, 1, 1] }
  ];

  // -------------------------------------------------------------
  // 3. DriveForge Peripheral Hardware Infall Tokens
  // -------------------------------------------------------------
  const PERIPHERAL_NAMES = ['CAN0', 'SPI1', 'UART2', 'GPIO', 'RCU', 'DMA0'];
  const peripheralTokens = [];
  const MAX_ACTIVE_TOKENS = 3;

  // Emerald verification quench rings
  const verificationFlashes = [];

  function spawnPeripheralToken() {
    const name = PERIPHERAL_NAMES[Math.floor(Math.random() * PERIPHERAL_NAMES.length)];
    return {
      name,
      normR: 0.96 + Math.random() * 0.04,
      theta: Math.random() * Math.PI * 2,
      vRadial: -(0.00014 + Math.random() * 0.00012),
      speedFactor: 0.0022 + Math.random() * 0.0010,
      alpha: 0.75
    };
  }

  for (let i = 0; i < MAX_ACTIVE_TOKENS; i++) {
    const tok = spawnPeripheralToken();
    tok.normR = 0.32 + (i / MAX_ACTIVE_TOKENS) * 0.60;
    peripheralTokens.push(tok);
  }

  // -------------------------------------------------------------
  // 4. Background Stars with 3D Parallax & Gravitational Lens Deflection
  // -------------------------------------------------------------
  const STAR_COUNT = 52;
  const stars = [];
  for (let i = 0; i < STAR_COUNT; i++) {
    stars.push({
      x: (Math.random() - 0.5) * 2600,
      y: (Math.random() - 0.5) * 1800,
      z: Math.random() * 1400 + 80,
      vx: (Math.random() - 0.5) * 0.07,
      vy: (Math.random() - 0.5) * 0.07,
      radius: Math.random() * 1.0 + 0.45,
      alpha: Math.random() * 0.32 + 0.12,
      twinkleSpeed: 0.02 + Math.random() * 0.03,
      twinklePhase: Math.random() * Math.PI * 2
    });
  }

  const fov = 460;
  function projectStar(x, y, z) {
    if (z <= -fov + 10) return null;
    const scale = fov / (fov + z);
    return {
      x: width * 0.5 + x * scale,
      y: height * 0.5 + y * scale,
      scale
    };
  }

  // -------------------------------------------------------------
  // 5. Hero Text Clearance & Readability Shield
  // Smoothly dampens background intensity behind headline without cutting curves
  // -------------------------------------------------------------
  function getTextClearance(px, py) {
    const textShieldX = width * 0.5;
    const textShieldY = height * 0.28;
    const textShieldRadiusX = Math.min(width * 0.45, 480);
    const textShieldRadiusY = 145;

    const dx = Math.abs(px - textShieldX);
    const dy = Math.abs(py - textShieldY);
    if (dx < textShieldRadiusX && dy < textShieldRadiusY) {
      const fx = dx / textShieldRadiusX;
      const fy = dy / textShieldRadiusY;
      const dist = Math.max(fx, fy);
      // Soft minimum of 0.25 so lines remain continuous rather than vanished
      return 0.25 + 0.75 * Math.pow(Math.min(Math.max(dist, 0), 1), 2.0);
    }
    return 1.0;
  }

  // -------------------------------------------------------------
  // 6. Relativistic 3D Space Projection & Lensing Math
  // -------------------------------------------------------------
  function projectRelativisticDiskPoint(r, theta, zDisp = 0, isUpperLensed = false, isLowerLensed = false) {
    const bhX = blackHole.x;
    const bhY = blackHole.y;
    const rH = blackHole.rHorizon;

    // Inclination ~76 degrees from normal
    const baseInclination = 1.32;
    const totalPitch = baseInclination + camPitch;
    const totalRoll = -0.10 + camRoll;
    const totalYaw = camYaw;

    const cosTheta = Math.cos(theta + totalYaw);
    const sinTheta = Math.sin(theta + totalYaw);
    const xd = r * cosTheta;
    const yd = r * sinTheta;
    const zd = zDisp;

    // 3D Tilt Transformation
    const cosPitch = Math.cos(totalPitch);
    const sinPitch = Math.sin(totalPitch);
    const cosRoll = Math.cos(totalRoll);
    const sinRoll = Math.sin(totalRoll);

    let X = xd;
    let Y = yd * cosPitch - zd * sinPitch;
    let Z = yd * sinPitch + zd * cosPitch;

    // Relativistic Gravitational Lensing Deflection:
    if (isUpperLensed) {
      // Upper crown arch: light from rear disk bent over the top of the event horizon
      const lensElevation = rH * (1.22 + (r - blackHole.rIsco) / (blackHole.rOuter - blackHole.rIsco) * 0.88);
      Y = -Math.abs(Y * 0.38) - lensElevation * cosPitch;
      Z = -12;
    } else if (isLowerLensed) {
      // Lower underbelly arc: light bent under the bottom of the event horizon
      const lowerElevation = rH * (0.68 + (r - blackHole.rIsco) / (blackHole.rOuter - blackHole.rIsco) * 0.32);
      Y = Math.abs(Y * 0.28) + lowerElevation * cosPitch;
      Z = -10;
    }

    let sx = bhX + X * cosRoll - Y * sinRoll;
    let sy = bhY + X * sinRoll + Y * cosRoll;

    // Relativistic Doppler Beaming Factor (I ~ delta^3.2)
    // Left side (approaching): intense blueshift & photon flux boost
    // Right side (receding): redshift & flux dimming
    const vOrbital = Math.min(0.50, Math.sqrt((blackHole.rIsco * 0.38) / Math.max(r, blackHole.rHorizon)));
    const vLos = -sinTheta * cosRoll + cosTheta * sinRoll * sinPitch;
    const doppler = Math.max(0.40, Math.min(2.2, 1.0 + vOrbital * vLos * 3.0));

    // Interactive Mouse Gravitational Probe Perturbation
    if (pointerEnergy > 0.02) {
      const mdx = sx - mouse.x;
      const mdy = sy - mouse.y;
      const mdist = Math.hypot(mdx, mdy);
      const probeRadius = 180;
      if (mdist < probeRadius) {
        const falloff = Math.pow(1 - mdist / probeRadius, 2) * pointerEnergy;
        const pull = falloff * 14;
        const swirlAngle = Math.atan2(mdy, mdx) + Math.PI * 0.5;
        sx += -(mdx / (mdist + 30)) * pull + Math.cos(swirlAngle) * (pull * 0.38);
        sy += -(mdy / (mdist + 30)) * pull + Math.sin(swirlAngle) * (pull * 0.38);
      }
    }

    // Shockwave Deflection
    for (let sw = 0; sw < shockwaves.length; sw++) {
      const shock = shockwaves[sw];
      const sDist = Math.hypot(sx - shock.x, sy - shock.y);
      const diff = Math.abs(sDist - shock.radius);
      if (diff < 32) {
        const wavePush = Math.sin((1 - diff / 32) * Math.PI) * shock.alpha * 7;
        const angle = Math.atan2(sy - shock.y, sx - shock.x);
        sx += Math.cos(angle) * wavePush;
        sy += Math.sin(angle) * wavePush;
      }
    }

    const clearance = getTextClearance(sx, sy);
    return {
      x: sx,
      y: sy,
      z: Z,
      doppler,
      clearance,
      isFront: Z >= -1.0
    };
  }

  // -------------------------------------------------------------
  // 7. Core Render Loop
  // -------------------------------------------------------------
  function renderAntigravity(frameTime = performance.now()) {
    if (!pageVisible) return;
    const frameDelta = Math.min(Math.max((frameTime - lastFrameTime) / 16.667, 0.25), 2.2);
    lastFrameTime = frameTime;

    ctx.clearRect(0, 0, width, height);

    // Energy Damping
    pointerEnergy *= Math.pow(0.95, frameDelta);
    scrollEnergy *= Math.pow(0.92, frameDelta);
    const targetEnergy = Math.max(pointerEnergy, scrollEnergy);
    interactionEnergy += (targetEnergy - interactionEnergy) * Math.min(0.12 * frameDelta, 1);

    const idleSpeed = 0.0032;
    const activeSpeedBoost = 0.009 * interactionEnergy;
    time += prefersReducedMotion ? 0 : (idleSpeed + activeSpeedBoost) * frameDelta;

    // Camera Rotation Easing
    camPitch += (targetCamPitch - camPitch) * 0.06;
    targetCamPitch *= 0.94;
    camRoll += (targetCamRoll - camRoll) * 0.06;
    camYaw += (targetCamYaw - camYaw) * 0.06;
    scrollVelocity *= Math.pow(0.92, frameDelta);

    // Subtle Parallax Position
    blackHole.targetX = width * 0.5 + (mouse.x - width * 0.5) * 0.030;
    blackHole.targetY = height * 0.22 + (mouse.y - height * 0.22) * 0.024 + Math.min(scrollY * 0.045, 65);
    blackHole.x += (blackHole.targetX - blackHole.x) * (prefersReducedMotion ? 1 : 0.04 * frameDelta);
    blackHole.y += (blackHole.targetY - blackHole.y) * (prefersReducedMotion ? 1 : 0.04 * frameDelta);

    const dark = isDarkMode();
    const bhX = blackHole.x;
    const bhY = blackHole.y;
    const rH = blackHole.rHorizon;
    const rPhot = blackHole.rPhoton;
    const rIsco = blackHole.rIsco;
    const rOut = blackHole.rOuter;

    // Update Shockwaves
    for (let sw = shockwaves.length - 1; sw >= 0; sw--) {
      const shock = shockwaves[sw];
      shock.radius += shock.speed * frameDelta;
      shock.alpha *= Math.pow(0.965, frameDelta);
      if (shock.radius > shock.maxRadius || shock.alpha < 0.02) {
        shockwaves.splice(sw, 1);
      }
    }

    // Update Verification Flashes
    for (let vf = verificationFlashes.length - 1; vf >= 0; vf--) {
      const v = verificationFlashes[vf];
      v.r += 2.5 * frameDelta;
      v.alpha *= Math.pow(0.94, frameDelta);
      if (v.alpha < 0.02) {
        verificationFlashes.splice(vf, 1);
      }
    }

    // -----------------------------------------------------------
    // PASS 1: Mouse Gravitational Probe Halo
    // -----------------------------------------------------------
    if (pointerEnergy > 0.015) {
      const haloRadius = 130 + pointerEnergy * 70;
      const mouseHalo = ctx.createRadialGradient(mouse.x, mouse.y, 0, mouse.x, mouse.y, haloRadius);
      const mHaloColor = dark ? '56, 189, 248' : '2, 132, 199';
      mouseHalo.addColorStop(0, `rgba(${mHaloColor}, ${0.070 * pointerEnergy})`);
      mouseHalo.addColorStop(0.5, `rgba(${mHaloColor}, ${0.022 * pointerEnergy})`);
      mouseHalo.addColorStop(1, `rgba(${mHaloColor}, 0)`);
      ctx.fillStyle = mouseHalo;
      ctx.fillRect(mouse.x - haloRadius, mouse.y - haloRadius, haloRadius * 2, haloRadius * 2);
    }

    // -----------------------------------------------------------
    // PASS 2: Background Stars with Einstein Lens Deflection
    // -----------------------------------------------------------
    const starBase = dark ? 'rgba(186, 230, 253, ' : 'rgba(14, 116, 144, ';
    for (let i = 0; i < stars.length; i++) {
      const s = stars[i];
      const starMotion = (0.08 + interactionEnergy * 0.30) * frameDelta;
      s.x += s.vx * starMotion;
      s.y += s.vy * starMotion - scrollVelocity * 0.12;
      s.z -= scrollVelocity * 0.20;

      if (s.x < -1350) s.x = 1350;
      if (s.x > 1350) s.x = -1350;
      if (s.y < -900) s.y = 900;
      if (s.y > 900) s.y = -900;
      if (s.z < 60) s.z = 1500;
      if (s.z > 1500) s.z = 60;

      const proj = projectStar(s.x, s.y, s.z);
      if (proj) {
        const dx = proj.x - bhX;
        const dy = proj.y - bhY;
        const dist = Math.hypot(dx, dy);

        // Shadow occlusion
        if (dist < rH * 0.98) continue;

        let sx = proj.x;
        let sy = proj.y;
        if (dist < rOut * 0.85) {
          const deflection = (rH * rH * 0.78) / (dist + 12);
          sx += (dx / dist) * deflection;
          sy += (dy / dist) * deflection;
        }

        const clearance = getTextClearance(sx, sy);
        if (clearance > 0.05) {
          const twinkle = 0.8 + 0.2 * Math.sin(time * s.twinkleSpeed * 10 + s.twinklePhase);
          ctx.beginPath();
          const starSize = Math.max(s.radius * proj.scale * 0.80, 0.45);
          ctx.arc(sx, sy, starSize, 0, Math.PI * 2);
          ctx.fillStyle = starBase + (s.alpha * twinkle * clearance * Math.min(proj.scale * 1.1, 1.0)) + ')';
          ctx.fill();
        }
      }
    }

    // -----------------------------------------------------------
    // PASS 3: Ambient Accretion Plasma Halo (Subtle & Atmospheric)
    // -----------------------------------------------------------
    const ambientGlowRadius = rOut * 0.95;
    const ambientGlow = ctx.createRadialGradient(bhX, bhY, rH * 0.7, bhX, bhY, ambientGlowRadius);
    if (dark) {
      ambientGlow.addColorStop(0, 'rgba(56, 189, 248, 0.085)');
      ambientGlow.addColorStop(0.35, 'rgba(30, 64, 175, 0.042)');
      ambientGlow.addColorStop(0.75, 'rgba(79, 70, 229, 0.018)');
      ambientGlow.addColorStop(1, 'rgba(8, 9, 12, 0)');
    } else {
      ambientGlow.addColorStop(0, 'rgba(2, 132, 199, 0.060)');
      ambientGlow.addColorStop(0.35, 'rgba(56, 189, 248, 0.028)');
      ambientGlow.addColorStop(0.8, 'rgba(147, 197, 253, 0.012)');
      ambientGlow.addColorStop(1, 'rgba(248, 250, 252, 0)');
    }
    ctx.fillStyle = ambientGlow;
    ctx.fillRect(bhX - ambientGlowRadius, bhY - ambientGlowRadius, ambientGlowRadius * 2, ambientGlowRadius * 2);

    // -----------------------------------------------------------
    // PASS 4: Interstellar Upper Relativistic Lensing Crown (Overhead Arch)
    // Multi-Layer Volumetric Plasma Arch with Doppler Color Grading
    // -----------------------------------------------------------
    function drawUpperLensingCrown() {
      ctx.save();
      const steps = 64;
      const crownRings = [
        { normR: 0.04, alpha: 0.42, width: 2.2, glowWidth: 14, glowAlpha: 0.09 },
        { normR: 0.28, alpha: 0.28, width: 1.5, glowWidth: 9,  glowAlpha: 0.06 },
        { normR: 0.60, alpha: 0.18, width: 1.0, glowWidth: 6,  glowAlpha: 0.03 }
      ];

      for (let cr = 0; cr < crownRings.length; cr++) {
        const ring = crownRings[cr];
        const rCurrent = rIsco + ring.normR * (rOut - rIsco);

        // Path generation
        ctx.beginPath();
        for (let i = 0; i <= steps; i++) {
          const theta = Math.PI + (i / steps) * Math.PI;
          const pt = projectRelativisticDiskPoint(rCurrent, theta, 0, true, false);
          if (i === 0) {
            ctx.moveTo(pt.x, pt.y);
          } else {
            ctx.lineTo(pt.x, pt.y);
          }
        }

        // Layer 1: Ambient Plasma Glow
        const glowGrad = ctx.createLinearGradient(bhX - rH * 2.2, bhY, bhX + rH * 2.2, bhY);
        if (dark) {
          glowGrad.addColorStop(0, `rgba(56, 189, 248, ${ring.glowAlpha * 1.6})`);
          glowGrad.addColorStop(0.4, `rgba(56, 189, 248, ${ring.glowAlpha})`);
          glowGrad.addColorStop(1, `rgba(99, 102, 241, ${ring.glowAlpha * 0.4})`);
        } else {
          glowGrad.addColorStop(0, `rgba(2, 132, 199, ${ring.glowAlpha * 1.4})`);
          glowGrad.addColorStop(0.4, `rgba(56, 189, 248, ${ring.glowAlpha})`);
          glowGrad.addColorStop(1, `rgba(79, 70, 229, ${ring.glowAlpha * 0.3})`);
        }
        ctx.strokeStyle = glowGrad;
        ctx.lineWidth = ring.glowWidth;
        ctx.stroke();

        // Layer 2: Core Incandescent Arch
        const coreGrad = ctx.createLinearGradient(bhX - rH * 2.2, bhY, bhX + rH * 2.2, bhY);
        if (dark) {
          coreGrad.addColorStop(0, `rgba(224, 242, 254, ${ring.alpha * 1.4})`);
          coreGrad.addColorStop(0.35, `rgba(56, 189, 248, ${ring.alpha * 1.15})`);
          coreGrad.addColorStop(0.75, `rgba(99, 102, 241, ${ring.alpha * 0.65})`);
          coreGrad.addColorStop(1, `rgba(67, 56, 202, ${ring.alpha * 0.28})`);
        } else {
          coreGrad.addColorStop(0, `rgba(2, 132, 199, ${ring.alpha * 1.2})`);
          coreGrad.addColorStop(0.4, `rgba(56, 189, 248, ${ring.alpha * 0.9})`);
          coreGrad.addColorStop(1, `rgba(79, 70, 229, ${ring.alpha * 0.25})`);
        }
        ctx.strokeStyle = coreGrad;
        ctx.lineWidth = ring.width;
        ctx.stroke();
      }
      ctx.restore();
    }

    // -----------------------------------------------------------
    // PASS 5: Keplerian Streamlines & Digital Bus Waveforms
    // Multi-Layer Volumetric Plasma Bands
    // -----------------------------------------------------------
    function drawStreamlines(isFrontPass) {
      ctx.save();
      const steps = 72;

      for (let s = 0; s < streamlines.length; s++) {
        const sl = streamlines[s];
        const rCurrent = rIsco + sl.normR * (rOut - rIsco);
        const keplerOmega = (0.0034 / Math.pow(0.35 + sl.normR * 0.65, 1.5)) * (1 + interactionEnergy * 0.6);
        const angleOffset = time * keplerOmega * (prefersReducedMotion ? 0 : 1);

        ctx.beginPath();
        let started = false;

        for (let step = 0; step <= steps; step++) {
          const theta = (step / steps) * Math.PI * 2 + angleOffset;
          const pt = projectRelativisticDiskPoint(rCurrent, theta, 0, false, false);

          if (pt.isFront !== isFrontPass) {
            started = false;
            continue;
          }

          if (!started) {
            ctx.moveTo(pt.x, pt.y);
            started = true;
          } else {
            ctx.lineTo(pt.x, pt.y);
          }
        }

        // Layer 1: Ambient Plasma Glow Band
        const baseAlpha = sl.opacity * (dark ? 1.0 : 0.85);
        ctx.strokeStyle = dark
          ? `rgba(56, 189, 248, ${baseAlpha * 0.22 * (0.85 + interactionEnergy * 0.3)})`
          : `rgba(2, 132, 199, ${baseAlpha * 0.18 * (0.90 + interactionEnergy * 0.3)})`;
        ctx.lineWidth = sl.width * 5.0;
        ctx.stroke();

        // Layer 2: Core Streamline
        ctx.strokeStyle = dark
          ? `rgba(56, 189, 248, ${baseAlpha * (0.85 + interactionEnergy * 0.3)})`
          : `rgba(2, 132, 199, ${baseAlpha * (0.90 + interactionEnergy * 0.3)})`;
        ctx.lineWidth = sl.width;
        ctx.stroke();

        // Front clock ticks along streamlines
        if (isFrontPass && sl.hasPulse) {
          const tickCount = 8;
          for (let t = 0; t < tickCount; t++) {
            const tickTheta = (t / tickCount) * Math.PI * 2 + angleOffset * 0.8;
            const pt = projectRelativisticDiskPoint(rCurrent, tickTheta, 0, false, false);
            if (pt.isFront) {
              const tickAlpha = (0.50 * pt.doppler * pt.clearance);
              ctx.beginPath();
              ctx.arc(pt.x, pt.y, 1.1, 0, Math.PI * 2);
              ctx.fillStyle = dark
                ? `rgba(186, 230, 253, ${tickAlpha})`
                : `rgba(2, 132, 199, ${tickAlpha * 0.9})`;
              ctx.fill();
            }
          }
        }
      }

      // Render Active Bus Waveform Packets (Simulating peripheral bitstream)
      if (isFrontPass) {
        for (let b = 0; b < busWavePackets.length; b++) {
          const pkt = busWavePackets[b];
          if (!prefersReducedMotion) {
            pkt.angle += pkt.speed * frameDelta * (1 + interactionEnergy * 0.5);
          }
          const sl = streamlines[pkt.streamlineIdx];
          const rCurrent = rIsco + sl.normR * (rOut - rIsco);

          const bitCount = pkt.bitPattern.length;
          ctx.beginPath();
          let waveStarted = false;

          for (let bit = 0; bit < bitCount; bit++) {
            const bitAngle = pkt.angle + (bit * 0.032);
            const bitVal = pkt.bitPattern[bit];
            const zPulse = bitVal ? 4.5 : 0;
            const pt = projectRelativisticDiskPoint(rCurrent, bitAngle, zPulse, false, false);

            if (!pt.isFront) continue;

            if (!waveStarted) {
              ctx.moveTo(pt.x, pt.y);
              waveStarted = true;
            } else {
              ctx.lineTo(pt.x, pt.y);
            }
          }

          if (waveStarted) {
            ctx.strokeStyle = dark ? 'rgba(56, 189, 248, 0.85)' : 'rgba(2, 132, 199, 0.80)';
            ctx.lineWidth = 1.5;
            ctx.stroke();

            const leadPt = projectRelativisticDiskPoint(rCurrent, pkt.angle + bitCount * 0.032, 4.5, false, false);
            if (leadPt.isFront) {
              ctx.beginPath();
              ctx.arc(leadPt.x, leadPt.y, 2.2, 0, Math.PI * 2);
              ctx.fillStyle = dark ? '#ffffff' : '#0284c7';
              ctx.shadowColor = dark ? '#38bdf8' : '#0284c7';
              ctx.shadowBlur = 6;
              ctx.fill();
              ctx.shadowBlur = 0;
            }
          }
        }
      }

      ctx.restore();
    }

    // -----------------------------------------------------------
    // PASS 6: Accretion Stardust Particles Simulation
    // -----------------------------------------------------------
    function drawParticles(isFrontPass) {
      const darkGlowRgb = '56, 189, 248';
      const lightGlowRgb = '2, 132, 199';

      for (let i = 0; i < PARTICLE_COUNT; i++) {
        const p = accretionParticles[i];
        const keplerOmega = (p.speedFactor / Math.pow(0.3 + p.normR * 0.7, 1.4)) * (1 + interactionEnergy * 0.8);

        if (!prefersReducedMotion) {
          p.theta += keplerOmega * frameDelta;
          p.normR += p.vRadial * frameDelta * (1 + interactionEnergy * 0.7);
          if (p.normR <= 0.05) {
            p.normR = 0.95 + Math.random() * 0.05;
            p.theta = Math.random() * Math.PI * 2;
          }
        }

        const rCurrent = rIsco + p.normR * (rOut - rIsco);
        const pt = projectRelativisticDiskPoint(rCurrent, p.theta, p.zDisp, false, false);

        if (pt.isFront !== isFrontPass) continue;

        const distanceFade = Math.sin(p.normR * Math.PI);
        const finalAlpha = Math.min(
          p.baseAlpha * pt.doppler * (0.65 + distanceFade * 0.35) * pt.clearance * (1 + interactionEnergy * 0.35),
          0.90
        );
        const particleSize = Math.max(p.size * (0.8 + pt.doppler * 0.25), 0.55);

        // Motion Blur Tail
        const tailAngle = p.theta + Math.PI * 0.5;
        const tailLength = Math.min(p.tailLen * keplerOmega * 280 * frameDelta * (1 + interactionEnergy * 0.5), 9.0);
        const tailEndX = pt.x - Math.cos(tailAngle) * tailLength * 0.85;
        const tailEndY = pt.y - Math.sin(tailAngle) * tailLength * 0.35;

        ctx.beginPath();
        ctx.moveTo(tailEndX, tailEndY);
        ctx.lineTo(pt.x, pt.y);
        ctx.strokeStyle = dark
          ? `rgba(${darkGlowRgb}, ${finalAlpha * 0.42})`
          : `rgba(${lightGlowRgb}, ${finalAlpha * 0.42})`;
        ctx.lineWidth = 0.75;
        ctx.stroke();

        // Particle Core
        ctx.beginPath();
        ctx.arc(pt.x, pt.y, particleSize, 0, Math.PI * 2);
        if (dark) {
          ctx.fillStyle = pt.doppler > 1.25
            ? `rgba(255, 255, 255, ${finalAlpha})`
            : (pt.doppler > 0.95 ? `rgba(186, 230, 253, ${finalAlpha})` : `rgba(129, 140, 248, ${finalAlpha * 0.70})`);
        } else {
          ctx.fillStyle = pt.doppler > 1.2
            ? `rgba(2, 132, 199, ${finalAlpha * 0.90})`
            : `rgba(14, 165, 233, ${finalAlpha * 0.78})`;
        }
        ctx.fill();
      }
    }

    // -----------------------------------------------------------
    // PASS 7: DriveForge Peripheral Hardware Infall Tokens
    // -----------------------------------------------------------
    function drawPeripheralTokens(isFrontPass) {
      ctx.save();
      ctx.font = '9px "Google Sans Code", "JetBrains Mono", monospace';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';

      for (let i = 0; i < peripheralTokens.length; i++) {
        const tok = peripheralTokens[i];
        const keplerOmega = (tok.speedFactor / Math.pow(0.35 + tok.normR * 0.65, 1.3)) * (1 + interactionEnergy * 0.6);

        if (!prefersReducedMotion) {
          tok.theta += keplerOmega * frameDelta;
          tok.normR += tok.vRadial * frameDelta * (1 + interactionEnergy * 0.7);

          // Infall to ISCO triggers verification flash
          if (tok.normR <= 0.08) {
            verificationFlashes.push({ x: bhX, y: bhY, r: rH * 1.1, alpha: 0.90 });
            tok.normR = 0.94 + Math.random() * 0.06;
            tok.theta = Math.random() * Math.PI * 2;
            tok.name = PERIPHERAL_NAMES[Math.floor(Math.random() * PERIPHERAL_NAMES.length)];
          }
        }

        const rCurrent = rIsco + tok.normR * (rOut - rIsco);
        const pt = projectRelativisticDiskPoint(rCurrent, tok.theta, 0, false, false);

        if (pt.isFront !== isFrontPass) continue;

        const badgeAlpha = tok.alpha * pt.clearance * (0.6 + pt.doppler * 0.4);
        const badgeColor = dark ? 'rgba(56, 189, 248, ' : 'rgba(2, 132, 199, ';

        ctx.fillStyle = dark ? 'rgba(8, 9, 14, 0.78)' : 'rgba(255, 255, 255, 0.88)';
        const textWidth = ctx.measureText(tok.name).width;
        ctx.fillRect(pt.x - textWidth / 2 - 3, pt.y - 6, textWidth + 6, 12);

        ctx.strokeStyle = badgeColor + (badgeAlpha * 0.7) + ')';
        ctx.lineWidth = 0.75;
        ctx.strokeRect(pt.x - textWidth / 2 - 3, pt.y - 6, textWidth + 6, 12);

        ctx.fillStyle = dark
          ? `rgba(224, 242, 254, ${badgeAlpha})`
          : `rgba(2, 132, 199, ${badgeAlpha})`;
        ctx.fillText(tok.name, pt.x, pt.y);
      }

      // Draw Verification Quenches
      for (let vf = 0; vf < verificationFlashes.length; vf++) {
        const v = verificationFlashes[vf];
        ctx.beginPath();
        ctx.arc(v.x, v.y, v.r, 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(16, 185, 129, ${v.alpha * 0.80})`;
        ctx.lineWidth = 1.4;
        ctx.stroke();
      }

      ctx.restore();
    }

    // -----------------------------------------------------------
    // PASS 8: Concentric Telemetry Geodesic HUD Rings
    // -----------------------------------------------------------
    function drawTelemetryHud() {
      ctx.save();
      const hudRings = [
        { r: rIsco, color: dark ? 'rgba(56, 189, 248, 0.28)' : 'rgba(2, 132, 199, 0.25)' },
        { r: rPhot, color: dark ? 'rgba(186, 230, 253, 0.30)' : 'rgba(14, 165, 233, 0.28)' }
      ];

      for (let h = 0; h < hudRings.length; h++) {
        const ring = hudRings[h];
        ctx.beginPath();
        const steps = 48;
        let started = false;

        for (let i = 0; i <= steps; i++) {
          const theta = (i / steps) * Math.PI * 2;
          const pt = projectRelativisticDiskPoint(ring.r, theta, 0, false, false);
          if (!pt.isFront) {
            started = false;
            continue;
          }
          if (!started) {
            ctx.moveTo(pt.x, pt.y);
            started = true;
          } else {
            ctx.lineTo(pt.x, pt.y);
          }
        }

        ctx.strokeStyle = ring.color;
        ctx.lineWidth = 0.65;
        ctx.setLineDash([3, 5]);
        ctx.stroke();
        ctx.setLineDash([]);
      }
      ctx.restore();
    }

    // -----------------------------------------------------------
    // PASS 9: Singularity Event Horizon Shadow & Razor-Sharp Photon Sphere
    // -----------------------------------------------------------
    function drawEventHorizon() {
      ctx.save();

      // Deep Cosmic Obsidian Shadow (Pure light trap, high text contrast)
      ctx.beginPath();
      ctx.arc(bhX, bhY, rH, 0, Math.PI * 2);
      if (dark) {
        const shadowGrad = ctx.createRadialGradient(bhX, bhY, 0, bhX, bhY, rH);
        shadowGrad.addColorStop(0, 'rgba(4, 5, 8, 0.90)');
        shadowGrad.addColorStop(0.78, 'rgba(6, 8, 12, 0.78)');
        shadowGrad.addColorStop(1, 'rgba(8, 9, 14, 0.45)');
        ctx.fillStyle = shadowGrad;
        ctx.fill();

        // Razor-Sharp Photon Ring Edge
        ctx.beginPath();
        ctx.arc(bhX, bhY, rH * 0.99, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.55)';
        ctx.lineWidth = 1.1;
        ctx.shadowColor = 'rgba(56, 189, 248, 0.55)';
        ctx.shadowBlur = 10;
        ctx.stroke();
      } else {
        const shadowGrad = ctx.createRadialGradient(bhX, bhY, 0, bhX, bhY, rH * 1.1);
        shadowGrad.addColorStop(0, 'rgba(255, 255, 255, 0.94)');
        shadowGrad.addColorStop(0.65, 'rgba(240, 249, 255, 0.48)');
        shadowGrad.addColorStop(0.95, 'rgba(56, 189, 248, 0.08)');
        shadowGrad.addColorStop(1, 'rgba(248, 250, 252, 0)');
        ctx.fillStyle = shadowGrad;
        ctx.fill();

        ctx.beginPath();
        ctx.arc(bhX, bhY, rH * 0.99, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(2, 132, 199, 0.35)';
        ctx.lineWidth = 0.90;
        ctx.stroke();
      }

      ctx.restore();
    }

    // -----------------------------------------------------------
    // PASS 10: Interactive Hardware Oscilloscope Probe Line
    // -----------------------------------------------------------
    function drawProbeInteraction() {
      if (pointerEnergy < 0.08 || !mouse.isHovering) return;
      const mdx = mouse.x - bhX;
      const mdy = mouse.y - bhY;
      const mouseDist = Math.hypot(mdx, mdy);

      if (mouseDist > rH * 0.9 && mouseDist < rOut * 1.15) {
        ctx.save();
        const targetR = Math.max(rIsco, Math.min(rOut, mouseDist));
        const targetTheta = Math.atan2(mdy, mdx);
        const contactPt = projectRelativisticDiskPoint(targetR, targetTheta, 0, false, false);

        // Thin laser probe line
        ctx.beginPath();
        ctx.moveTo(mouse.x, mouse.y);
        ctx.lineTo(contactPt.x, contactPt.y);
        ctx.strokeStyle = dark
          ? `rgba(56, 189, 248, ${0.35 * pointerEnergy})`
          : `rgba(2, 132, 199, ${0.30 * pointerEnergy})`;
        ctx.lineWidth = 0.8;
        ctx.setLineDash([2, 3]);
        ctx.stroke();
        ctx.setLineDash([]);

        // Contact reticle
        ctx.beginPath();
        ctx.arc(contactPt.x, contactPt.y, 2.8, 0, Math.PI * 2);
        ctx.strokeStyle = dark ? '#38bdf8' : '#0284c7';
        ctx.lineWidth = 1.0;
        ctx.stroke();

        // Micro telemetry tag
        ctx.font = '8px "Google Sans Code", monospace';
        ctx.fillStyle = dark ? 'rgba(56, 189, 248, 0.75)' : 'rgba(2, 132, 199, 0.80)';
        ctx.fillText(`PROBE: 3.3V // r:${Math.round(mouseDist)}px`, mouse.x + 12, mouse.y - 8);
        ctx.restore();
      }
    }

    // -----------------------------------------------------------
    // EXECUTION PIPELINE (Depth-Sorted Gravitational Layering)
    // -----------------------------------------------------------
    // 1. Rear Upper Lensing Crown (Overhead Arch)
    drawUpperLensingCrown();

    // 2. Rear Streamlines & Particles
    drawStreamlines(false);
    drawParticles(false);
    drawPeripheralTokens(false);

    // 3. Central Singularity & Event Horizon
    drawEventHorizon();

    // 4. Front Streamlines & Particles (Crossing in front)
    drawStreamlines(true);
    drawParticles(true);
    drawPeripheralTokens(true);

    // 5. Telemetry HUD Rings
    drawTelemetryHud();

    // 6. Interactive Oscilloscope Probe
    drawProbeInteraction();

    if (!prefersReducedMotion) {
      requestAnimationFrame(renderAntigravity);
    }
  }

  // -------------------------------------------------------------
  // 8. Event Listeners & Interactive Handlers
  // -------------------------------------------------------------
  window.addEventListener('resize', resizeCanvas, { passive: true });

  window.addEventListener('pointermove', (e) => {
    const now = performance.now();
    const elapsed = Math.max(now - mouse.lastActive, 8);
    const dist = Math.hypot(e.clientX - mouse.x, e.clientY - mouse.y);
    const speed = dist / elapsed;

    mouse.x = e.clientX;
    mouse.y = e.clientY;
    mouse.isHovering = true;
    mouse.lastActive = now;

    pointerEnergy = Math.min(1.0, Math.max(pointerEnergy, 0.22 + speed * 0.45));

    // Dynamic 3D Camera tilt with gentle spring physics
    const normX = (e.clientX / width) - 0.5;
    const normY = (e.clientY / height) - 0.22;
    targetCamRoll = normX * 0.10;
    targetCamPitch = normY * 0.15;
    targetCamYaw = normX * 0.08;
  }, { passive: true });

  window.addEventListener('pointerdown', (e) => {
    pointerEnergy = 1.0;
    addShockwave(e.clientX, e.clientY);
  }, { passive: true });

  document.documentElement.addEventListener('mouseleave', () => {
    mouse.isHovering = false;
    pointerEnergy *= 0.35;
    targetCamRoll = 0;
    targetCamPitch = 0;
    targetCamYaw = 0;
  });

  document.addEventListener('visibilitychange', () => {
    const wasVisible = pageVisible;
    pageVisible = !document.hidden;
    if (pageVisible && !wasVisible && !prefersReducedMotion) {
      lastFrameTime = performance.now();
      requestAnimationFrame(renderAntigravity);
    }
  });

  // -------------------------------------------------------------
  // 9. Public API Export
  // -------------------------------------------------------------
  const BlackHoleEngine = {
    canvas,
    ctx,
    blackHole,
    accretionParticles,
    resize: resizeCanvas,
    render: renderAntigravity,
    setMotionReduced(reduced) {
      prefersReducedMotion = reduced;
      if (prefersReducedMotion) {
        renderAntigravity();
      } else if (pageVisible) {
        lastFrameTime = performance.now();
        requestAnimationFrame(renderAntigravity);
      }
    },
    updateScroll(deltaY, curScrollY) {
      scrollY = curScrollY;
      scrollVelocity = deltaY;
      scrollEnergy = Math.min(1.0, Math.max(scrollEnergy, Math.abs(deltaY) / 50));
      targetCamPitch = Math.max(-0.25, Math.min(0.25, deltaY * 0.006 + (curScrollY * 0.00006)));
      targetCamRoll = (mouse.x / width - 0.5) * 0.08;
    },
    triggerShockwave(x, y) {
      addShockwave(x || blackHole.x, y || blackHole.y);
    }
  };

  // Global exports for tests, verification harnesses, and external modules
  window.canvas = canvas;
  window.blackHole = blackHole;
  window.accretionParticles = accretionParticles;
  window.renderAntigravity = renderAntigravity;
  window.BlackHoleEngine = BlackHoleEngine;

  // Initial Boot
  resizeCanvas();
  renderAntigravity();

})(window, document);
