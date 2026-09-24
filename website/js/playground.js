/**
 * DriveForge Web Landing Page - Interactive Simulator & Playground Module
 */

(function (window, document) {
  'use strict';

  // 1. Preset Configurations for Simulator
  const presets = {
    'CAN0': {
      pins: 'PD0 (RX), PD1 (TX)',
      clock: 'RCU_CAN0',
      irq: 'CAN0_RX0_IRQn',
      ref: 'drivers/drv_can1.c',
      strategy: 'adapt_existing_instance',
      testType: 'CAN 1Mbps Loopback, 100 frames'
    },
    'UART1': {
      pins: 'PA9 (TX), PA10 (RX)',
      clock: 'RCU_USART1',
      irq: 'USART1_IRQn',
      ref: 'drivers/drv_usart0.c',
      strategy: 'adapt_existing_instance',
      testType: 'UART 115200 DMA Echo Test'
    },
    'SPI2': {
      pins: 'PC10 (SCK), PC11 (MISO), PC12 (MOSI)',
      clock: 'RCU_SPI2',
      irq: 'SPI2_IRQn',
      ref: 'drivers/drv_spi.c',
      strategy: 'extend_existing_driver',
      testType: 'JEDEC ID 0xEF4018 Flash Read'
    },
    'I2C1': {
      pins: 'PB10 (SCL), PB11 (SDA)',
      clock: 'RCU_I2C1',
      irq: 'I2C1_EV_IRQn',
      ref: 'drivers/drv_soft_i2c.c',
      strategy: 'vendor_sdk_evidence',
      testType: 'AT24C02 EEPROM Write/Read 256B'
    },
    'ADC0': {
      pins: 'PA0 (CH0), PA1 (CH1)',
      clock: 'RCU_ADC0',
      irq: 'ADC0_1_IRQn',
      ref: 'drivers/drv_adc.c',
      strategy: 'adapt_existing_instance',
      testType: 'DMA Scan Mode 12-bit Linear Verification'
    }
  };

  function updatePreset() {
    const periphEl = document.getElementById('periph-select');
    if (!periphEl) return;
    const periph = periphEl.value;
    const preset = presets[periph] || presets['CAN0'];
    const pinInput = document.getElementById('pin-input');
    if (!pinInput) return;
    pinInput.value = preset.pins;
    pinInput.animate?.([
      { boxShadow: '0 0 0 0 rgba(56, 189, 248, 0)' },
      { boxShadow: '0 0 0 4px rgba(56, 189, 248, 0.18)' },
      { boxShadow: '0 0 0 0 rgba(56, 189, 248, 0)' }
    ], { duration: 520, easing: 'ease-out' });
  }

  // 2. Switch Tabs in Playground
  function switchTab(tabId) {
    ['tab-terminal', 'tab-manifest', 'tab-plan', 'tab-report'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.classList.add('hidden');
    });

    ['tab-btn-terminal', 'tab-btn-manifest', 'tab-btn-plan', 'tab-btn-report'].forEach(id => {
      const btn = document.getElementById(id);
      if (btn) {
        btn.setAttribute('aria-selected', 'false');
        btn.setAttribute('tabindex', '-1');
        btn.classList.remove('border-blue-600', 'dark:border-sky-400', 'text-blue-600', 'dark:text-sky-300');
        btn.classList.add('border-transparent', 'text-slate-500', 'dark:text-slate-400');
      }
    });

    const targetEl = document.getElementById(tabId);
    if (targetEl) {
      targetEl.classList.remove('hidden');
      targetEl.style.animation = 'none';
      void targetEl.offsetWidth;
      targetEl.style.animation = '';
    }

    const activeBtnId = tabId.replace('tab-', 'tab-btn-');
    const activeBtn = document.getElementById(activeBtnId);
    if (activeBtn) {
      activeBtn.setAttribute('aria-selected', 'true');
      activeBtn.setAttribute('tabindex', '0');
      activeBtn.classList.add('border-blue-600', 'dark:border-sky-400', 'text-blue-600', 'dark:text-sky-300');
      activeBtn.classList.remove('border-transparent', 'text-slate-500', 'dark:text-slate-400');
    }
  }

  // Tab keyboard accessibility
  const tabList = document.querySelector('[role="tablist"]');
  if (tabList) {
    tabList.addEventListener('keydown', event => {
      if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
      event.preventDefault();
      const tabs = [...document.querySelectorAll('[role="tab"]')];
      const currentIndex = tabs.indexOf(document.activeElement);
      let nextIndex = currentIndex;
      if (event.key === 'ArrowRight') nextIndex = (currentIndex + 1) % tabs.length;
      if (event.key === 'ArrowLeft') nextIndex = (currentIndex - 1 + tabs.length) % tabs.length;
      if (event.key === 'Home') nextIndex = 0;
      if (event.key === 'End') nextIndex = tabs.length - 1;
      const nextTab = tabs[nextIndex];
      switchTab(nextTab.getAttribute('aria-controls'));
      nextTab.focus();
    });
  }

  // 3. Simulator Runner
  let isRunning = false;
  function runSimulation() {
    if (isRunning) return;
    isRunning = true;

    const mcuEl = document.getElementById('mcu-select');
    const periphEl = document.getElementById('periph-select');
    const pinEl = document.getElementById('pin-input');
    if (!mcuEl || !periphEl || !pinEl) {
      isRunning = false;
      return;
    }

    const mcu = mcuEl.value;
    const periph = periphEl.value;
    const pins = pinEl.value;
    const preset = presets[periph] || presets['CAN0'];

    const runBtn = document.getElementById('run-btn');
    const runText = document.getElementById('run-text');
    const runIcon = document.getElementById('run-icon');
    const term = document.getElementById('terminal-content');
    const statusBadge = document.getElementById('sim-status-badge');

    if (runText) runText.textContent = '产品演示运行中...';
    if (runBtn) {
      runBtn.disabled = true;
      runBtn.setAttribute('aria-busy', 'true');
      runBtn.classList.add('opacity-80', 'cursor-not-allowed');
    }
    if (runIcon) runIcon.classList.add('animate-spin');

    const p1 = document.getElementById('step-1-pill');
    const p2 = document.getElementById('step-2-pill');
    const p3 = document.getElementById('step-3-pill');
    const p4 = document.getElementById('step-4-pill');

    if (p1) p1.className = 'flex items-center gap-2 text-blue-600 dark:text-sky-400';
    if (p2) p2.className = 'flex items-center gap-2 text-slate-400 dark:text-slate-500';
    if (p3) p3.className = 'flex items-center gap-2 text-slate-400 dark:text-slate-500';
    if (p4) p4.className = 'flex items-center gap-2 text-slate-400 dark:text-slate-500';

    switchTab('tab-terminal');
    if (term) {
      term.innerHTML = `<span class="text-amber-300 font-semibold">[PRODUCT DEMO] Preset data only; no command or hardware operation is executed.</span><br>`;
    }

    // Step 1: Scan & Intent
    setTimeout(() => {
      if (term) {
        term.innerHTML += `<span class="text-slate-300">→ [Intent] Identified Peripheral: <span class="text-white font-bold">${periph}</span>, MCU: <span class="text-white font-bold">${mcu}</span></span><br>`;
        term.innerHTML += `<span class="text-slate-300">→ [Demo Scan] Simulated workspace: 238 source files, build tool: SCons</span><br>`;
      }
      if (p2) p2.className = 'flex items-center gap-2 text-blue-600 dark:text-sky-400 font-medium';
      if (statusBadge) {
        statusBadge.textContent = 'GATING...';
        statusBadge.className = 'shrink-0 ml-4 px-2.5 py-1 rounded-full bg-blue-900/60 text-sky-300 border border-blue-500/40 text-[11px] font-semibold';
      }
    }, 700);

    // Step 2: Fact Gate
    setTimeout(() => {
      if (term) {
        term.innerHTML += `<span class="text-slate-300">→ [Fact Gate] Pins verified: <span class="text-emerald-400 font-semibold">${pins}</span> backed by board.h:42 (Confidence: HIGH)</span><br>`;
        term.innerHTML += `<span class="text-slate-300">→ [Fact Gate] Clock gate: <span class="text-emerald-400 font-semibold">${preset.clock}</span> confirmed via CMSIS RCU table</span><br>`;
        term.innerHTML += `<span class="text-amber-300">◇ Demo gate passed with preset facts; this is not project evidence.</span><br>`;
      }
      if (p3) p3.className = 'flex items-center gap-2 text-blue-600 dark:text-sky-400 font-medium';
      if (statusBadge) statusBadge.textContent = 'PLANNING...';
    }, 1500);

    // Step 3: Plan
    setTimeout(() => {
      if (term) {
        term.innerHTML += `<span class="text-slate-300">→ [Planner] Selected strategy: <span class="text-sky-300 font-semibold">${preset.strategy}</span></span><br>`;
        term.innerHTML += `<span class="text-slate-300">→ [Planner] Reusing reference file: <span class="text-amber-300">${preset.ref}</span></span><br>`;
        term.innerHTML += `<span class="text-sky-400">◇ Displaying sample manifest and plan; no files were generated.</span><br>`;
      }
      if (p4) p4.className = 'flex items-center gap-2 text-blue-600 dark:text-sky-400 font-medium';
      if (statusBadge) statusBadge.textContent = 'EXECUTING...';
    }, 2300);

    // Step 4: SCons Build & Flash & Test
    setTimeout(() => {
      if (term) {
        term.innerHTML += `<span class="text-slate-200">[simulated] $ scons -j8</span><br>`;
        term.innerHTML += `<span class="text-slate-300">◇ [Demo Build] Sample compilation result: PASS.</span><br>`;
        term.innerHTML += `<span class="text-slate-200">[simulated] $ JLinkExe -CommandFile flash.jlink</span><br>`;
        term.innerHTML += `<span class="text-slate-300">◇ [Demo Flash] No firmware was written to ${mcu}.</span><br>`;
        term.innerHTML += `<span class="text-slate-200">[simulated] $ python tools/hardware_test.py --target ${periph}</span><br>`;
        term.innerHTML += `<span class="text-slate-300">◇ [Demo Test] Sample scenario: ${preset.testType}.</span><br>`;
        term.innerHTML += `<span class="text-amber-300 font-semibold">★ Demo Status: SIMULATED_PASS (not VERIFIED)</span>`;
      }

      if (p4) p4.className = 'flex items-center gap-2 text-emerald-500 dark:text-emerald-400 font-bold';
      if (statusBadge) {
        statusBadge.textContent = 'SIMULATED PASS';
        statusBadge.className = 'shrink-0 ml-4 px-2.5 py-1 rounded-full bg-emerald-500/20 text-emerald-600 dark:text-emerald-300 border border-emerald-500/40 text-[11px] font-bold animate-pulse';
      }

      // Populate other tabs with formatted data
      const manifestEl = document.getElementById('manifest-content');
      if (manifestEl) {
        manifestEl.textContent = 
`target_peripheral: "${periph}"
mcu: "${mcu}"
os: "RT-Thread 5.1.0"
gating_status: "PASS"
facts:
  pins:
    value: "${pins}"
    confidence: "VERIFIED"
    source: "project:board.h"
    line: 42
  clock_gate:
    value: "${preset.clock}"
    confidence: "HIGH"
    source: "cmsis:rcu"
  irq:
    value: "${preset.irq}"
    confidence: "HIGH"
    source: "cmsis:nvic"`;
      }

      const planEl = document.getElementById('plan-content');
      if (planEl) {
        planEl.textContent =
`strategy: "${preset.strategy}"
reference_file: "${preset.ref}"
target_file: "drivers/drv_${periph.toLowerCase()}.c"
reuse_confidence: 0.96
steps:
  - id: "hardware_init"
    action: "Configure pins (${pins}) and enable clock ${preset.clock}"
  - id: "rt_device_register"
    action: "Register ${periph.toLowerCase()} to RT-Thread device framework"
acceptance_criteria:
  - "Build passes with scons"
  - "${preset.testType}"`;
      }

      const reportEl = document.getElementById('report-content');
      if (reportEl) {
        reportEl.textContent = JSON.stringify({
          simulated: true,
          status: "SIMULATED_PASS",
          note: "Product demo only. No commands or hardware operations were executed.",
          timestamp: new Date().toISOString(),
          target: { mcu: mcu, peripheral: periph },
          stages: {
            build: { command: "scons -j8", status: "PASS", duration_ms: 1840 },
            flash: { command: "JLinkExe -CommandFile flash.jlink", status: "PASS", duration_ms: 2150 },
            test: { command: `python tools/hardware_test.py --target ${periph}`, status: "PASS", passed_checks: 12 }
          }
        }, null, 2);
      }

      if (runText) runText.textContent = '重新运行产品演示';
      if (runBtn) {
        runBtn.disabled = false;
        runBtn.removeAttribute('aria-busy');
        runBtn.classList.remove('opacity-80', 'cursor-not-allowed');
      }
      if (runIcon) runIcon.classList.remove('animate-spin');
      isRunning = false;

      if (typeof window.showToast === 'function') {
        window.showToast(`${periph} 产品演示已完成（非真实验证）`);
      }
    }, 3400);
  }

  // Export to window
  window.presets = presets;
  window.updatePreset = updatePreset;
  window.switchTab = switchTab;
  window.runSimulation = runSimulation;

  window.Playground = {
    presets,
    updatePreset,
    switchTab,
    runSimulation
  };

  // Initial call
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', updatePreset);
  } else {
    updatePreset();
  }

})(window, document);
