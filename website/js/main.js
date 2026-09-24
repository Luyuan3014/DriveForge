/**
 * DriveForge Web Landing Page - Main Application Entrypoint
 */

(function () {
  'use strict';

  function initApp() {
    console.info('[DriveForge] Web Landing Page initialized successfully.');
    console.info('[DriveForge] Architecture: Decoupled Vanilla ES6+, CSS3 & Tailwind Design System.');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
  } else {
    initApp();
  }
})();
