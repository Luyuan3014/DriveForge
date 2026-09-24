/**
 * DriveForge Web Landing Page - UI Interactions & Accessibility Module
 * Handles Themes, Motion, Proximity Feedback, Scroll Parallax, Navigation & Toast
 */

(function (window, document) {
  'use strict';

  // ----------------------------------------------------
  // 1. Theme Management (Light / Dark)
  // ----------------------------------------------------
  function isDarkMode() {
    return document.documentElement.classList.contains('dark');
  }

  function updateThemeControl() {
    const button = document.getElementById('theme-toggle');
    if (!button) return;
    const isDark = isDarkMode();
    button.setAttribute('aria-label', isDark ? '切换至浅色模式' : '切换至深色模式');
    button.title = button.getAttribute('aria-label');
    button.setAttribute('aria-pressed', String(isDark));
  }

  function applyTheme(theme, options = {}) {
    const html = document.documentElement;
    const nextTheme = theme === 'light' ? 'light' : 'dark';
    const previousTheme = isDarkMode() ? 'dark' : 'light';

    html.classList.toggle('dark', nextTheme === 'dark');
    html.classList.toggle('light', nextTheme === 'light');
    html.dataset.theme = nextTheme;
    html.style.colorScheme = nextTheme;

    if (options.persist) {
      try { localStorage.setItem('driveforge-theme', nextTheme); } catch (_) {}
    }

    updateThemeControl();

    if (options.announce && previousTheme !== nextTheme) {
      showToast(nextTheme === 'dark' ? '已切换至深色模式' : '已切换至浅色模式');
    }
  }

  function initTheme() {
    let savedTheme = null;
    try {
      const params = new URLSearchParams(location.search);
      savedTheme = params.get('theme') || localStorage.getItem('driveforge-theme');
    } catch (_) {}
    const prefersLight = window.matchMedia('(prefers-color-scheme: light)').matches;
    const initialTheme = savedTheme === 'light' || (!savedTheme && prefersLight) ? 'light' : 'dark';
    applyTheme(initialTheme);
  }

  function toggleTheme() {
    applyTheme(isDarkMode() ? 'light' : 'dark', { persist: true, announce: true });
  }

  // ----------------------------------------------------
  // 2. Motion Reduction & Control
  // ----------------------------------------------------
  let prefersReducedMotion = document.documentElement.classList.contains('motion-reduced');

  function updateMotionControl() {
    const button = document.getElementById('motion-toggle');
    if (!button) return;
    const label = prefersReducedMotion ? '恢复页面动效' : '暂停页面动效';
    button.setAttribute('aria-label', label);
    button.setAttribute('aria-pressed', String(prefersReducedMotion));
    button.title = label;
    document.getElementById('motion-on-icon')?.classList.toggle('hidden', prefersReducedMotion);
    document.getElementById('motion-off-icon')?.classList.toggle('hidden', !prefersReducedMotion);
  }

  function toggleMotion() {
    prefersReducedMotion = !prefersReducedMotion;
    document.documentElement.classList.toggle('motion-reduced', prefersReducedMotion);
    clearProximityTarget();
    try { localStorage.setItem('driveforge-motion', prefersReducedMotion ? 'reduced' : 'full'); } catch (_) {}
    updateMotionControl();

    if (window.BlackHoleEngine) {
      window.BlackHoleEngine.setMotionReduced(prefersReducedMotion);
    }
    showToast(prefersReducedMotion ? '页面动效已暂停' : '3D 动效与滚动视差已恢复');
  }

  // ----------------------------------------------------
  // 3. Toast Notification
  // ----------------------------------------------------
  let toastTimer;
  function showToast(message) {
    const toast = document.getElementById('interaction-toast');
    const toastText = document.getElementById('interaction-toast-text');
    if (!toast || !toastText) return;
    toastText.textContent = message;
    toast.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove('show'), 1800);
  }

  // ----------------------------------------------------
  // 4. Clipboard Helper
  // ----------------------------------------------------
  function copyCommand(text) {
    const copy = navigator.clipboard?.writeText
      ? navigator.clipboard.writeText(text)
      : Promise.reject(new Error('Clipboard API unavailable'));
    copy.then(() => {
      const badge = document.getElementById('copy-badge');
      if (badge) {
        badge.style.opacity = '1';
        setTimeout(() => { badge.style.opacity = '0'; }, 1600);
      }
      showToast('命令已复制到剪贴板');
    }).catch(() => showToast('复制失败，请手动选择命令'));
  }

  // ----------------------------------------------------
  // 5. Proximity-aware edge illumination
  // ----------------------------------------------------
  const finePointerQuery = window.matchMedia('(pointer: fine)');
  const proximitySelector = '.edge-target, button, select, input';
  const PROXIMITY_DISTANCE = 28;
  let proximityTarget = null;
  let proximityFrame = 0;
  let pointerPosition = { x: 0, y: 0 };

  function clearProximityTarget() {
    proximityTarget?.classList.remove('edge-proximity');
    proximityTarget = null;
  }

  function distanceToRect(x, y, rect) {
    const dx = Math.max(rect.left - x, 0, x - rect.right);
    const dy = Math.max(rect.top - y, 0, y - rect.bottom);
    return Math.hypot(dx, dy);
  }

  function updateProximityTarget() {
    proximityFrame = 0;
    if (prefersReducedMotion || document.hidden) {
      clearProximityTarget();
      return;
    }

    const directTarget = document.elementFromPoint(pointerPosition.x, pointerPosition.y)?.closest(proximitySelector);
    let nextTarget = directTarget || null;
    let nearestDistance = directTarget ? 0 : PROXIMITY_DISTANCE;
    let nearestArea = directTarget ? directTarget.getBoundingClientRect().width * directTarget.getBoundingClientRect().height : Infinity;

    if (!directTarget) {
      document.querySelectorAll(proximitySelector).forEach((element) => {
        if (element.disabled || element.getAttribute('aria-hidden') === 'true') return;
        const rect = element.getBoundingClientRect();
        if (!rect.width || !rect.height || rect.bottom < -PROXIMITY_DISTANCE || rect.top > window.innerHeight + PROXIMITY_DISTANCE) return;
        const distance = distanceToRect(pointerPosition.x, pointerPosition.y, rect);
        const area = rect.width * rect.height;
        if (distance < nearestDistance || (distance === nearestDistance && area < nearestArea)) {
          nearestDistance = distance;
          nearestArea = area;
          nextTarget = element;
        }
      });
    }

    if (nextTarget !== proximityTarget) {
      clearProximityTarget();
      proximityTarget = nextTarget;
      proximityTarget?.classList.add('edge-proximity');
    }

  }

  window.addEventListener('pointermove', (event) => {
    pointerPosition.x = event.clientX;
    pointerPosition.y = event.clientY;
    if (!proximityFrame) proximityFrame = requestAnimationFrame(updateProximityTarget);
  }, { passive: true });

  document.documentElement.addEventListener('mouseleave', clearProximityTarget);
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) clearProximityTarget();
  });

  // ----------------------------------------------------
  // 6. Scroll Effects, Hero Parallax & Navigation Sync
  // ----------------------------------------------------
  let scrollY = window.scrollY;
  let lastScrollY = window.scrollY;
  let scrollTicking = false;

  function updateHeroParallax() {
    const track = document.getElementById('hero-scroll-track');
    const intro = document.getElementById('hero-intro');
    const hint = document.getElementById('hero-scroll-hint');
    const stageContainer = document.getElementById('hero-stage-container');
    const heroConsole = document.getElementById('hero-console');
    const sat1 = document.getElementById('satellite-1');
    const sat2 = document.getElementById('satellite-2');
    const sat3 = document.getElementById('satellite-3');
    const expandedPanel = document.getElementById('hero-expanded-panel');

    if (!track || !heroConsole) return;

    const isWidescreen = window.innerWidth >= 1280;
    const isDesktop = window.innerWidth >= 1024;

    if (prefersReducedMotion) {
      if (intro) { intro.style.transform = ''; intro.style.opacity = '1'; intro.style.pointerEvents = 'auto'; }
      if (stageContainer) stageContainer.style.transform = '';
      heroConsole.style.transform = '';
      if (sat1) { sat1.style.transform = ''; sat1.style.opacity = '1'; sat1.style.pointerEvents = 'auto'; }
      if (sat2) { sat2.style.transform = ''; sat2.style.opacity = '1'; sat2.style.pointerEvents = 'auto'; }
      if (sat3) { sat3.style.transform = ''; sat3.style.opacity = '1'; sat3.style.pointerEvents = 'auto'; }
      if (expandedPanel) expandedPanel.style.opacity = '1';
      return;
    }

    // Tablet & Mobile natural scroll reveal (< 1024px)
    if (!isDesktop) {
      const mobScroll = window.scrollY;
      const mobReveal = Math.min(Math.max((mobScroll - 30) / 160, 0), 1);
      const mobEase = 1 - Math.pow(1 - mobReveal, 3);
      [sat1, sat2, sat3].forEach(sat => {
        if (!sat) return;
        sat.style.opacity = String(mobEase);
        sat.style.transform = `translate3d(0, ${(1 - mobEase) * 16}px, 0)`;
        sat.style.pointerEvents = mobEase > 0.8 ? 'auto' : 'none';
      });
      if (intro) { intro.style.transform = ''; intro.style.opacity = '1'; intro.style.pointerEvents = 'auto'; }
      if (stageContainer) stageContainer.style.transform = '';
      heroConsole.style.transform = '';
      if (expandedPanel) expandedPanel.style.opacity = '1';
      return;
    }

    const rect = track.getBoundingClientRect();
    const scrollableDistance = rect.height - window.innerHeight;
    if (scrollableDistance <= 0) return;

    const progress = Math.min(Math.max(-rect.top / scrollableDistance, 0), 1);
    const ease = 1 - Math.pow(1 - progress, 3); // easeOutCubic

    // 1. Intro header lift & fade out as user scrolls
    if (intro) {
      const introY = -ease * 100;
      const introOpacity = Math.max(1 - progress * 2.5, 0);
      intro.style.transform = `translate3d(0, ${introY}px, 0)`;
      intro.style.opacity = String(introOpacity);
      intro.style.pointerEvents = progress > 0.35 ? 'none' : 'auto';
    }

    if (hint) {
      hint.style.opacity = String(Math.max(1 - progress * 3.5, 0));
    }

    // 2. Stage container lifts smoothly so card is centered in viewport (Attio-style)
    if (stageContainer) {
      const introHeight = intro ? intro.offsetHeight : 340;
      const stageLift = Math.min(introHeight + 20, 260);
      const stageY = -ease * stageLift;
      stageContainer.style.transform = `translate3d(0, ${stageY}px, 0)`;
    }

    // 3. Central Main Card expansion & 3D perspective flattening
    // At scroll=0: 6deg tilt and scale 0.93 (teaser state)
    // As user scrolls: flattens to 0deg and scales smoothly to 1.0 (full majesty)
    const cardProgress = Math.min(progress / 0.72, 1);
    const cardEase = 1 - Math.pow(1 - cardProgress, 3);
    const scale = 0.93 + cardEase * 0.07;
    const rotateX = (1 - cardEase) * 6;
    heroConsole.style.transform = `perspective(1200px) rotateX(${rotateX}deg) scale(${scale})`;

    // 4. SATELLITE CARDS: ATTIO-STYLE SCROLL EMERGENCE
    // At scroll = 0: opacity = 0, tucked behind console edges (Zero distraction)
    // Progress 0.06 -> 0.58: smoothly emerge outward and pop into orbit!
    // Progress >= 0.58: opacity = 1.0, scale = 1.0, fully interactive
    const REVEAL_START = 0.06;
    const REVEAL_END = 0.58;
    const reveal = Math.min(Math.max((progress - REVEAL_START) / (REVEAL_END - REVEAL_START), 0), 1);
    const satEase = 1 - Math.pow(1 - reveal, 3); // easeOutCubic

    const satOpacity = satEase;
    const satScale = 0.76 + satEase * 0.24;
    const isInteractive = satEase > 0.82;

    if (isWidescreen) {
      // Sat 1: Top-Left Wing (Fact Gate)
      if (sat1) {
        const s1X = (1 - satEase) * 35;
        const s1Y = (1 - satEase) * 14;
        const s1Rot = (1 - satEase) * 2.5;
        sat1.style.opacity = String(satOpacity);
        sat1.style.transform = `translate3d(${s1X}px, ${s1Y}px, 0) scale(${satScale}) rotate(${s1Rot}deg)`;
        sat1.style.pointerEvents = isInteractive ? 'auto' : 'none';
      }

      // Sat 2: Bottom-Left Wing (Reuse Strategy)
      if (sat2) {
        const s2X = (1 - satEase) * 35;
        const s2Y = -(1 - satEase) * 14;
        const s2Rot = -(1 - satEase) * 2.5;
        sat2.style.opacity = String(satOpacity);
        sat2.style.transform = `translate3d(${s2X}px, ${s2Y}px, 0) scale(${satScale}) rotate(${s2Rot}deg)`;
        sat2.style.pointerEvents = isInteractive ? 'auto' : 'none';
      }

      // Sat 3: Right Wing (HIL Telemetry)
      if (sat3) {
        const s3X = -(1 - satEase) * 35;
        const s3Y = (1 - satEase) * 12;
        const s3Rot = -(1 - satEase) * 2.0;
        sat3.style.opacity = String(satOpacity);
        sat3.style.transform = `translate3d(${s3X}px, ${s3Y}px, 0) scale(${satScale}) rotate(${s3Rot}deg)`;
        sat3.style.pointerEvents = isInteractive ? 'auto' : 'none';
      }
    } else {
      // Tablet / Compact Desktop (< 1280px): Docked 3-card deck above console
      const dockY = (1 - satEase) * 18;
      [sat1, sat2, sat3].forEach(sat => {
        if (!sat) return;
        sat.style.opacity = String(satOpacity);
        sat.style.transform = `translate3d(0, ${dockY}px, 0) scale(${satScale})`;
        sat.style.pointerEvents = isInteractive ? 'auto' : 'none';
      });
    }

    // 5. Right Expanded Panel is ALWAYS visible with crisp telemetry
    if (expandedPanel) {
      expandedPanel.style.opacity = '1';
    }
  }

  function updateScrollEffects() {
    scrollY = window.scrollY;
    const deltaY = scrollY - lastScrollY;
    lastScrollY = scrollY;

    if (window.BlackHoleEngine) {
      window.BlackHoleEngine.updateScroll(deltaY, scrollY);
    }

    updateHeroParallax();

    const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
    const progress = maxScroll > 0 ? Math.min(1, scrollY / maxScroll) : 0;
    const scrollProgressEl = document.getElementById('scroll-progress');
    if (scrollProgressEl) {
      scrollProgressEl.style.transform = `scaleX(${progress})`;
    }

    const header = document.getElementById('main-header');
    if (header) {
      if (scrollY > 30) header.classList.add('shadow-md');
      else header.classList.remove('shadow-md');
    }

    const orb1 = document.getElementById('ambient-orb-1');
    const orb2 = document.getElementById('ambient-orb-2');
    if (!prefersReducedMotion) {
      if (orb1) orb1.style.transform = `translate(-50%, ${scrollY * 0.06}px)`;
      if (orb2) orb2.style.transform = `translate(0, ${-scrollY * 0.05}px)`;
    }

    document.getElementById('back-to-top')?.classList.toggle('visible', scrollY > 720);
    scrollTicking = false;
  }

  window.addEventListener('scroll', () => {
    if (!scrollTicking) {
      scrollTicking = true;
      requestAnimationFrame(updateScrollEffects);
    }
  }, { passive: true });

  window.addEventListener('resize', () => {
    requestAnimationFrame(updateHeroParallax);
  }, { passive: true });

  // ----------------------------------------------------
  // 7. Active Navigation Link Sync
  // ----------------------------------------------------
  const navLinks = [...document.querySelectorAll('.nav-link')];
  const sectionTargets = [...document.querySelectorAll('#hero-section, #principles, #features, #playground, #quickstart, #matrix')];
  let navTicking = false;

  function updateActiveNavigation() {
    const activationLine = window.innerHeight * 0.32 + 64;
    let activeSection = sectionTargets[0];
    sectionTargets.forEach(section => {
      if (section.getBoundingClientRect().top <= activationLine) activeSection = section;
    });
    if (!activeSection) return;
    const sectionId = activeSection.id === 'hero-section' ? 'workflow' : activeSection.id;
    navLinks.forEach(link => {
      const active = link.getAttribute('href') === `#${sectionId}`;
      if (active) link.setAttribute('aria-current', 'true');
      else link.removeAttribute('aria-current');
    });
    navTicking = false;
  }

  window.addEventListener('scroll', () => {
    if (!navTicking) {
      navTicking = true;
      requestAnimationFrame(updateActiveNavigation);
    }
  }, { passive: true });

  // ----------------------------------------------------
  // 8. Mobile Menu Navigation
  // ----------------------------------------------------
  const mobileMenuButton = document.getElementById('mobile-menu-button');
  const mobileMenu = document.getElementById('mobile-menu');

  function setMobileMenu(open) {
    if (!mobileMenu || !mobileMenuButton) return;
    mobileMenu.classList.toggle('open', open);
    mobileMenu.setAttribute('aria-hidden', String(!open));
    mobileMenu.inert = !open;
    mobileMenuButton.setAttribute('aria-expanded', String(open));
    mobileMenuButton.setAttribute('aria-label', open ? '关闭页面导航' : '打开页面导航');
  }

  if (mobileMenuButton && mobileMenu) {
    mobileMenuButton.addEventListener('click', () => setMobileMenu(mobileMenuButton.getAttribute('aria-expanded') !== 'true'));
    mobileMenu.querySelectorAll('a').forEach(link => link.addEventListener('click', () => setMobileMenu(false)));
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape') setMobileMenu(false);
    });
  }

  // ----------------------------------------------------
  // 9. Micro-interactions: Card Spotlight, 3D Hero Console & Ripple
  // ----------------------------------------------------
  function initMicroInteractions() {
    // Scroll Reveal
    const revealElements = [...document.querySelectorAll('.reveal')];
    revealElements.forEach((el, index) => el.style.setProperty('--reveal-delay', `${(index % 4) * 65}ms`));
    const revealObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('active');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

    revealElements.forEach(el => {
      if (prefersReducedMotion) el.classList.add('active');
      else revealObserver.observe(el);
    });

    // 3D Tilt on Hero Console Inner (Pointer Interaction)
    const heroConsole = document.getElementById('hero-console');
    const heroConsoleInner = document.getElementById('hero-console-inner');
    if (heroConsole && heroConsoleInner && finePointerQuery.matches && !prefersReducedMotion) {
      heroConsole.addEventListener('pointermove', (e) => {
        const rect = heroConsole.getBoundingClientRect();
        const dx = (e.clientX - rect.left) / rect.width - 0.5;
        const dy = (e.clientY - rect.top) / rect.height - 0.5;
        heroConsoleInner.style.transform = `perspective(1000px) rotateX(${-dy * 4.5}deg) rotateY(${dx * 5.5}deg)`;
        heroConsoleInner.style.transition = 'transform 80ms linear';
      });
      heroConsole.addEventListener('mouseleave', () => {
        heroConsoleInner.style.transform = '';
        heroConsoleInner.style.transition = 'transform 480ms var(--ease-out-expo)';
      });
    }

    // Satellite Linking Micro-interaction: highlights matching pipeline step nodes
    document.querySelectorAll('.satellite-card').forEach(sat => {
      const stepIdx = sat.getAttribute('data-target-step');
      if (!stepIdx) return;
      const targetNode = document.getElementById(`pipe-step-${stepIdx}`);
      if (!targetNode) return;

      sat.addEventListener('mouseenter', () => {
        targetNode.classList.add('pipeline-node-active');
      });
      sat.addEventListener('mouseleave', () => {
        targetNode.classList.remove('pipeline-node-active');
      });
    });

    // Pointer-aware card lighting
    document.querySelectorAll('.glass-card-hover').forEach(card => {
      card.addEventListener('pointermove', (event) => {
        const rect = card.getBoundingClientRect();
        card.style.setProperty('--spot-x', `${event.clientX - rect.left}px`);
        card.style.setProperty('--spot-y', `${event.clientY - rect.top}px`);
      }, { passive: true });
    });

    // Ripple click effect
    document.querySelectorAll('button, a[class*="rounded-full"], a[class*="rounded-xl"]').forEach(el => {
      el.classList.add('pressable');
      el.addEventListener('pointerdown', event => {
        if (prefersReducedMotion) return;
        const rect = el.getBoundingClientRect();
        const ripple = document.createElement('span');
        const size = Math.max(rect.width, rect.height) * 1.8;
        ripple.className = 'ripple';
        ripple.style.width = ripple.style.height = `${size}px`;
        ripple.style.left = `${event.clientX - rect.left}px`;
        ripple.style.top = `${event.clientY - rect.top}px`;
        el.appendChild(ripple);
        ripple.addEventListener('animationend', () => ripple.remove(), { once: true });
      });
    });

    // Back to top
    document.getElementById('back-to-top')?.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: prefersReducedMotion ? 'auto' : 'smooth' });
    });

    // Motion toggle button
    document.getElementById('motion-toggle')?.addEventListener('click', toggleMotion);

    // Theme toggle button
    document.getElementById('theme-toggle')?.addEventListener('click', toggleTheme);
  }

  // Export interface
  window.initTheme = initTheme;
  window.toggleTheme = toggleTheme;
  window.isDarkMode = isDarkMode;
  window.toggleMotion = toggleMotion;
  window.updateMotionControl = updateMotionControl;
  window.showToast = showToast;
  window.copyCommand = copyCommand;

  // Initialize
  initTheme();
  updateMotionControl();
  updateScrollEffects();
  updateActiveNavigation();

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMicroInteractions);
  } else {
    initMicroInteractions();
  }

})(window, document);
