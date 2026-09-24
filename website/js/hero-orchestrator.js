/**
 * DriveForge Web Landing Page - Hero Orchestrator & Autonomous Closed-Loop Simulation
 * ===================================================================================
 * 
 * 核心设计目标：
 * 1. 完整展示 "需求扫描 -> 硬件事实门禁 -> 复用优先策略 -> 代码实施 -> 构建 SCons -> 烧录 & RTT实测" 的自主闭环。
 * 2. 日志流式/打字输出，高科技终端动效，实时遥测指标联动。
 * 3. 极高可扩展性：主卡片的所有项目信息、硬件参数、步骤定义、终端日志、遥测指标均抽离至下方的 DriveForgeHeroConfig，
 *    后续无论是切换芯片 (STM32, ESP32, GD32)、外设 (CAN, SPI, UART, I2C)、构建系统还是验证模式，均可直接修改配置对象完成！
 */

(function (window, document) {
  'use strict';

  // =========================================================================
  // 1. 驱动智能体首页主卡片配置对象 (DriveForgeHeroConfig)
  //    开发者或项目后续维护者仅需修改此处的字段即可自定义整个闭环流程！
  // =========================================================================
  window.DriveForgeHeroConfig = {
    // 项目基础信息与硬件规格
    project: {
      name: "GD32F470ZIT6 [CAN0]",
      title: "DriveForge Orchestrator · GD32F470ZIT6 [CAN0]",
      targetBsp: "./bsp/gd32f470",
      rtos: "RT-Thread 5.1.0",
      mcuCore: "Cortex-M4 240MHz",
      busPeripheral: "APB1 @ 45MHz",
      probe: "J-Link SWD (4000kHz)",
      rxPin: "PD0 (CAN0_RX)",
      txPin: "PD1 (CAN0_TX)",
      evidenceFile: "board.h:42",
      clockGate: "RCU_CAN0",
      reuseSource: "drv_can1.c",
      reuseTarget: "drv_can.c",
      reuseStrategy: "adapt_existing_instance",
      similarityScore: "95.2%",
      diffStats: "+38 / -4 lines",
      buildDuration: "3.21s (零告警)",
      flashDelta: "+2.4KB Flash, +380B RAM",
      loopbackRate: "1 Mbps Loopback",
      loopbackTotal: 100
    },

    // 调度与动画控制参数
    settings: {
      autoLoop: true,             // 是否持续无缝循环闭环流程
      pauseOnHover: true,         // 鼠标悬停在控制台卡片时自动暂停，移开后恢复
      stepDuration: 3200,         // 每个步骤的基础持续时间 (毫秒)
      cycleEndDelay: 3800,        // 第 6 步验收完成后，保持全面通过状态的驻留时间 (毫秒)
      streamLineDelay: 260        // 每行日志输出的节奏间隔 (毫秒)
    },

    // 闭环流水线 6 大步骤详细定义
    steps: [
      {
        index: 1,
        id: "scan",
        title: "需求扫描",
        phaseName: "[1/6] 需求解析与工作区扫描",
        statusBadge: "SCANNING",
        statusClass: "text-sky-400 bg-sky-500/15 border-sky-500/30",
        satelliteHighlight: null,
        logs: [
          { type: "header", text: "# Step 1: Workspace scanning & hardware fact gating" },
          { type: "cmd", text: "$ driveforge plan ./bsp/gd32f470 --request \"适配 CAN0 驱动\" --rx-pin PD0 --tx-pin PD1" },
          { type: "info", text: "→ [Scan] 检测到工程环境: RT-Thread 5.1.0, SCons 4.5.2, GCC 10.3.1" },
          { type: "info", text: "→ [Scan] 目标 MCU 识别: GD32F470ZIT6 (ARM Cortex-M4 @ 240MHz)" },
          { type: "cyan", text: "→ [Scan] 提取硬件声明: RX=PD0, TX=PD1, 外设=CAN0, 目标总线=APB1" }
        ],
        telemetry: {
          phase: "工作区分析中",
          status: "PARSING_AST",
          statusColor: "text-sky-400",
          loopbackState: "IDLE · 等待驱动生成",
          loopbackProgress: 0,
          mcu: "Cortex-M4 240MHz",
          bus: "APB1 @ 45MHz",
          build: "等待构建...",
          flash: "--"
        }
      },
      {
        index: 2,
        id: "fact",
        title: "硬件事实门禁",
        phaseName: "[2/6] 硬件事实门禁确定性校验",
        statusBadge: "FACT_CHECK",
        statusClass: "text-blue-400 bg-blue-500/15 border-blue-500/30",
        satelliteHighlight: "satellite-1", // 联动硬件事实卫星卡片
        logs: [
          { type: "header", text: "# Step 2: Invariant check - Evidence-first Pin & Clock gating" },
          { type: "info", text: "🔍 [Fact Gate] 正在从工程源码语法树溯源引脚与时钟物理事实..." },
          { type: "green", text: "✓ [Fact Gate] 引脚 PD0 (CAN0_RX), PD1 (CAN0_TX) 由 board.h:42 语法树溯源确证 (VERIFIED)" },
          { type: "green", text: "✓ [Fact Gate] 外设时钟门控 RCU_CAN0 在 CMSIS 头文件 gd32f4xx_rcu.h 中确证存在" },
          { type: "purple", text: "✓ [Fact Gate] 中断向量 CAN0_TX_IRQn / CAN0_RX0_IRQn 校验有效 · 零臆造门禁通过" }
        ],
        telemetry: {
          phase: "硬件事实门禁",
          status: "FACTS_VERIFIED",
          statusColor: "text-emerald-400",
          loopbackState: "PIN / RCU 门禁通过",
          loopbackProgress: 12,
          mcu: "Cortex-M4 240MHz",
          bus: "RCU_CAN0 (APB1)",
          build: "待编译",
          flash: "--"
        }
      },
      {
        index: 3,
        id: "reuse",
        title: "复用优先策略",
        phaseName: "[3/6] 驱动资产复用规划",
        statusBadge: "REUSE_PLAN",
        statusClass: "text-amber-400 bg-amber-500/15 border-amber-500/30",
        satelliteHighlight: "satellite-2", // 联动复用规划卫星卡片
        logs: [
          { type: "header", text: "# Step 3: Reuse-first strategy selection & AST pattern match" },
          { type: "info", text: "🧩 [Planner] 扫描当前 BSP 既有驱动库: drivers/drv_can1.c (模式相似度: 95.2%)" },
          { type: "amber", text: "→ [Planner] 选定最优方案: adapt_existing_instance (极简侵入策略)" },
          { type: "info", text: "→ [Planner] 复用 CAN1 FIFO 环形缓冲区、波特率计算器及中断回调骨架" },
          { type: "green", text: "✓ [Planner] 差异预算评估: 预计新增 38 行，精简 4 行 · 贴合原有编码规范" }
        ],
        telemetry: {
          phase: "复用策略规划",
          status: "REUSE_OPTIMIZED",
          statusColor: "text-amber-300",
          loopbackState: "复用 drv_can1 骨架",
          loopbackProgress: 28,
          mcu: "Cortex-M4 240MHz",
          bus: "CAN0 / CAN1 对齐",
          build: "准备实施",
          flash: "--"
        }
      },
      {
        index: 4,
        id: "codegen",
        title: "代码实施",
        phaseName: "[4/6] 确定性代码生成与补丁集成",
        statusBadge: "SYNTHESIS",
        statusClass: "text-indigo-400 bg-indigo-500/15 border-indigo-500/30",
        satelliteHighlight: null,
        logs: [
          { type: "header", text: "# Step 4: Deterministic driver implementation & SConscript patch" },
          { type: "info", text: "🛠 [Codegen] 正在按 RT-Thread 设备驱动框架确定性生成 drivers/drv_can.c..." },
          { type: "cyan", text: "→ [Codegen] 注册核心操作集: rt_hw_can_init(), gd32_can_configure(), gd32_can_sendmsg()" },
          { type: "cyan", text: "→ [Codegen] 绑定 RT-Thread 标准设备: \"can0\" (RT_Device_Class_CAN)" },
          { type: "green", text: "✓ [Codegen] 生成完成: drivers/drv_can.c (+38 行) · SConscript 增量补丁 (+2 行)" }
        ],
        telemetry: {
          phase: "驱动代码就绪",
          status: "PATCH_APPLIED",
          statusColor: "text-indigo-300",
          loopbackState: "设备 \"can0\" 已注册",
          loopbackProgress: 50,
          mcu: "Cortex-M4 240MHz",
          bus: "APB1 @ 45MHz",
          build: "准备构建 SCons",
          flash: "+2.4KB Flash"
        }
      },
      {
        index: 5,
        id: "build",
        title: "构建 SCons",
        phaseName: "[5/6] 确定性构建系统编译验证",
        statusBadge: "SCONS_BUILD",
        statusClass: "text-emerald-400 bg-emerald-500/15 border-emerald-500/30",
        satelliteHighlight: null,
        logs: [
          { type: "header", text: "# Step 5: SCons compiler invocation & static verification" },
          { type: "cmd", text: "$ scons -j8 --target=rtthread.elf" },
          { type: "info", text: "CC drivers/drv_can.o (arm-none-eabi-gcc -mcpu=cortex-m4 -mthumb -O2)" },
          { type: "info", text: "LINK rtthread.elf (text: 245,612 bytes, data: 2,140 bytes, bss: 8,432 bytes)" },
          { type: "green", text: "✓ [Build] SCons 构建完全通过: 0 错误, 0 警告 (耗时: 3.21s, 目标: rtthread.elf)" }
        ],
        telemetry: {
          phase: "SCons 编译通过",
          status: "BUILD_SUCCESS",
          statusColor: "text-emerald-400",
          loopbackState: "固件 ELF 已就绪",
          loopbackProgress: 75,
          mcu: "Cortex-M4 240MHz",
          bus: "APB1 @ 45MHz",
          build: "3.21s (0 告警)",
          flash: "+2.4KB Flash"
        }
      },
      {
        index: 6,
        id: "verify",
        title: "烧录 & RTT实测",
        phaseName: "[6/6] 实机闭环烧录与物理总线回环实测",
        statusBadge: "HIL_VERIFIED",
        statusClass: "text-emerald-400 bg-emerald-500/20 border-emerald-500/40",
        satelliteHighlight: "satellite-3", // 联动实机验证遥测卫星卡片
        logs: [
          { type: "header", text: "# Step 6: Target flash via SWD probe & physical loopback telemetry" },
          { type: "cmd", text: "$ driveforge verify --probe jlink --execute-flash --loopback-test" },
          { type: "info", text: "⚡ [Flash] J-Link SWD @ 4000kHz: 成功烧录 256KB 至 0x08000000 (校验 100%)" },
          { type: "info", text: "📡 [RTT HIL] 启动物理总线硬件在环回环: CAN0_TX(PD1) → 回环线 → CAN0_RX(PD0)" },
          { type: "green", text: "✓ [RTT HIL] 实测回环帧数: 100/100 帧全数通过 · 0 丢包 · CRC 校验正确 (延迟 0.12ms)" },
          { type: "emerald-glow", text: "🏆 [Closed-Loop] 物理总线实测闭环通过！生成代码已通过真实硬件工程检验！" }
        ],
        telemetry: {
          phase: "实机验证通过",
          status: "100 / 100 PASS",
          statusColor: "text-emerald-400",
          loopbackState: "100/100 帧 (0 Loss)",
          loopbackProgress: 100,
          mcu: "Cortex-M4 240MHz",
          bus: "APB1 @ 45MHz",
          build: "3.21s (0 告警)",
          flash: "+2.4KB Flash"
        }
      }
    ]
  };

  // =========================================================================
  // 2. 闭环调度引擎 (HeroOrchestrator)
  // =========================================================================
  const HeroOrchestrator = {
    config: window.DriveForgeHeroConfig,
    currentStepIndex: 1,
    isPlaying: true,
    isPausedByHover: false,
    stepTimer: null,
    logTimeouts: [],
    cycleCount: 1,

    // DOM 元素缓存
    elements: {
      console: null,
      terminal: null,
      projectTitle: null,
      globalStatusBadge: null,
      globalStatusText: null,
      rtosVersion: null,
      telemetryPhase: null,
      telemetryStatus: null,
      loopbackTrack: null,
      loopbackLabel: null,
      metricMcu: null,
      metricBus: null,
      metricBuild: null,
      metricFlash: null,
      stepNodes: [],
      stepLines: [],
      satellites: []
    },

    init() {
      this.cacheElements();
      if (!this.elements.console || !this.elements.terminal) {
        console.warn('[HeroOrchestrator] Console or Terminal elements not found.');
        return;
      }

      this.bindEvents();
      this.syncProjectInfo();
      this.startCycle(1);
      console.info('[HeroOrchestrator] Autonomous Closed-Loop Engine started.');
    },

    cacheElements() {
      const e = this.elements;
      e.console = document.getElementById('hero-console');
      e.terminal = document.getElementById('hero-terminal-stream');
      e.projectTitle = document.getElementById('hero-project-title');
      e.globalStatusBadge = document.getElementById('hero-global-status-badge');
      e.globalStatusText = document.getElementById('hero-global-status-text');
      e.rtosVersion = document.getElementById('hero-rtos-version');
      e.telemetryPhase = document.getElementById('hero-telemetry-phase');
      e.telemetryStatus = document.getElementById('hero-telemetry-status');
      e.loopbackTrack = document.getElementById('hero-loopback-track');
      e.loopbackLabel = document.getElementById('hero-loopback-label');
      e.metricMcu = document.getElementById('hero-metric-mcu');
      e.metricBus = document.getElementById('hero-metric-bus');
      e.metricBuild = document.getElementById('hero-metric-build');
      e.metricFlash = document.getElementById('hero-metric-flash');

      e.stepNodes = [];
      for (let i = 1; i <= 6; i++) {
        const node = document.getElementById(`pipe-step-${i}`);
        if (node) e.stepNodes.push(node);
      }

      e.stepLines = [];
      for (let i = 1; i <= 5; i++) {
        const line = document.getElementById(`step-line-${i}`);
        if (line) e.stepLines.push(line);
      }

      e.satellites = [
        document.getElementById('satellite-1'),
        document.getElementById('satellite-2'),
        document.getElementById('satellite-3')
      ].filter(Boolean);
    },

    bindEvents() {
      const e = this.elements;

      // 1. 鼠标悬停暂停机制 (方便用户细读日志和指标)
      if (this.config.settings.pauseOnHover && e.console) {
        e.console.addEventListener('mouseenter', () => {
          this.isPausedByHover = true;
          if (e.globalStatusText && this.isPlaying) {
            e.globalStatusText.textContent = 'PAUSED';
          }
        });
        e.console.addEventListener('mouseleave', () => {
          this.isPausedByHover = false;
          if (e.globalStatusText && this.isPlaying) {
            e.globalStatusText.textContent = this.currentStepIndex === 6 ? 'VERIFIED' : 'RUNNING';
          }
        });
      }

      // 2. 流水线步骤节点点击交互 (允许用户自由切换与复现任意步骤)
      e.stepNodes.forEach((node, index) => {
        const stepNum = index + 1;
        node.style.cursor = 'pointer';
        node.setAttribute('role', 'button');
        node.setAttribute('tabindex', '0');
        node.setAttribute('aria-label', `跳转至步骤 ${stepNum}: ${this.config.steps[index]?.title || ''}`);
        node.addEventListener('click', (ev) => {
          ev.preventDefault();
          this.jumpToStep(stepNum);
        });
        node.addEventListener('keydown', (ev) => {
          if (ev.key === 'Enter' || ev.key === ' ') {
            ev.preventDefault();
            this.jumpToStep(stepNum);
          }
        });
      });

      // 3. 卫星卡片联动点击 (点击卫星卡片跳转对应步骤)
      e.satellites.forEach(sat => {
        const targetStep = sat.getAttribute('data-target-step');
        if (targetStep) {
          sat.addEventListener('click', (ev) => {
            const stepNum = parseInt(targetStep, 10);
            if (!isNaN(stepNum)) {
              this.jumpToStep(stepNum);
            }
          });
        }
      });
    },

    syncProjectInfo() {
      const p = this.config.project;
      const e = this.elements;
      if (e.projectTitle && p.title) e.projectTitle.textContent = p.title;
      if (e.rtosVersion && p.rtos) e.rtosVersion.textContent = p.rtos;
      if (e.metricMcu && p.mcuCore) e.metricMcu.textContent = p.mcuCore;
      if (e.metricBus && p.busPeripheral) e.metricBus.textContent = p.busPeripheral;
    },

    clearTimeouts() {
      clearTimeout(this.stepTimer);
      this.stepTimer = null;
      this.logTimeouts.forEach(t => clearTimeout(t));
      this.logTimeouts = [];
    },

    startCycle(startStep = 1) {
      this.clearTimeouts();
      this.currentStepIndex = startStep;
      if (startStep === 1) {
        this.clearTerminal();
      }
      this.executeStep(startStep);
    },

    jumpToStep(stepIndex) {
      this.clearTimeouts();
      this.currentStepIndex = stepIndex;
      this.clearTerminal();

      // 先快速渲染之前步骤的简明结果
      for (let i = 1; i < stepIndex; i++) {
        const prevStep = this.config.steps[i - 1];
        if (prevStep) {
          this.appendHistoricalStepLog(prevStep);
        }
      }

      this.executeStep(stepIndex);
    },

    clearTerminal() {
      const t = this.elements.terminal;
      if (t) {
        t.innerHTML = '';
      }
    },

    appendHistoricalStepLog(step) {
      const t = this.elements.terminal;
      if (!t) return;
      const wrap = document.createElement('div');
      wrap.className = 'space-y-1 opacity-70 mb-2 border-b border-white/[0.04] pb-1.5';
      step.logs.forEach(log => {
        const line = this.createLogLineElement(log);
        wrap.appendChild(line);
      });
      t.appendChild(wrap);
    },

    executeStep(stepNum) {
      const stepConfig = this.config.steps[stepNum - 1];
      if (!stepConfig) return;

      this.updatePipelineTrack(stepNum);
      this.updateTelemetry(stepConfig);
      this.highlightSatellite(stepConfig.satelliteHighlight);
      this.renderStepLogs(stepConfig, () => {
        // 当该步骤日志全部输出完毕后，计划下一步骤
        this.scheduleNextStep(stepNum);
      });
    },

    updatePipelineTrack(activeStep) {
      const e = this.elements;
      e.stepNodes.forEach((node, idx) => {
        const stepNum = idx + 1;
        const circle = node.querySelector('.pipe-node-badge') || node.querySelector('div:first-child');
        const text = node.querySelector('span:last-child');

        if (stepNum < activeStep) {
          // 已完成步骤
          node.className = 'pipe-step-node flex items-center gap-2 text-emerald-600 dark:text-emerald-400 transition-all duration-300';
          if (circle) {
            circle.className = 'pipe-node-badge w-6 h-6 rounded-full bg-emerald-500/15 dark:bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 border border-emerald-400/50 flex items-center justify-center font-bold text-[10px] shadow-sm';
            circle.innerHTML = '✓';
          }
        } else if (stepNum === activeStep) {
          // 当前激活步骤
          node.className = 'pipe-step-node flex items-center gap-2 text-sky-600 dark:text-sky-300 font-semibold transition-all duration-300 scale-105';
          if (circle) {
            circle.className = 'pipe-node-badge w-6 h-6 rounded-full bg-sky-500/25 dark:bg-sky-400/25 text-sky-600 dark:text-sky-300 border border-sky-400/90 flex items-center justify-center font-bold text-[10px] shadow-[0_0_12px_rgba(56,189,248,0.7)] animate-pulse';
            circle.textContent = String(stepNum);
          }
        } else {
          // 未激活待执行步骤
          node.className = 'pipe-step-node flex items-center gap-2 text-slate-400 dark:text-slate-500 transition-all duration-300 opacity-60';
          if (circle) {
            circle.className = 'pipe-node-badge w-6 h-6 rounded-full bg-slate-200 dark:bg-slate-800 text-slate-500 dark:text-slate-400 border border-slate-300 dark:border-slate-700 flex items-center justify-center font-bold text-[10px]';
            circle.textContent = String(stepNum);
          }
        }
      });

      // 更新连接线颜色
      e.stepLines.forEach((line, idx) => {
        const lineNum = idx + 1;
        if (lineNum < activeStep) {
          line.className = 'pipe-step-line w-6 h-[1.5px] bg-emerald-500/60 dark:bg-emerald-400/60 transition-all duration-300';
        } else if (lineNum === activeStep) {
          line.className = 'pipe-step-line w-6 h-[1.5px] bg-gradient-to-r from-emerald-500 via-sky-400 to-slate-400 transition-all duration-300';
        } else {
          line.className = 'pipe-step-line w-6 h-[1px] bg-slate-300 dark:bg-slate-800 transition-all duration-300';
        }
      });

      // 顶部全局状态
      if (e.globalStatusText) {
        e.globalStatusText.textContent = activeStep === 6 ? 'VERIFIED' : 'RUNNING';
      }
    },

    updateTelemetry(step) {
      const t = step.telemetry;
      const e = this.elements;
      if (!t) return;

      if (e.telemetryPhase) e.telemetryPhase.textContent = step.phaseName;
      if (e.telemetryStatus) {
        e.telemetryStatus.textContent = t.status;
        e.telemetryStatus.className = `font-semibold font-mono ${t.statusColor || 'text-emerald-400'}`;
      }
      if (e.loopbackLabel) e.loopbackLabel.textContent = t.loopbackState;
      if (e.loopbackTrack) {
        const bar = e.loopbackTrack.querySelector('.loopback-bar-pulse') || e.loopbackTrack.firstElementChild;
        if (bar) {
          bar.style.width = `${Math.max(t.loopbackProgress, 6)}%`;
        }
      }
      if (e.metricBuild && t.build) e.metricBuild.textContent = t.build;
      if (e.metricFlash && t.flash) e.metricFlash.textContent = t.flash;
      if (e.metricMcu && t.mcu) e.metricMcu.textContent = t.mcu;
      if (e.metricBus && t.bus) e.metricBus.textContent = t.bus;
    },

    highlightSatellite(satId) {
      this.elements.satellites.forEach(sat => {
        if (!sat) return;
        if (sat.id === satId) {
          sat.classList.add('satellite-active-glow');
        } else {
          sat.classList.remove('satellite-active-glow');
        }
      });
    },

    createLogLineElement(log) {
      const line = document.createElement('div');
      line.className = 'terminal-line leading-relaxed';

      switch (log.type) {
        case 'header':
          line.className += ' text-slate-400 pt-1 font-semibold';
          line.innerHTML = `<span class="text-sky-400"># </span>${escapeHtml(log.text.replace(/^#\s*/, ''))}`;
          break;
        case 'cmd':
          line.className += ' text-slate-100 font-bold';
          line.innerHTML = `<span class="text-emerald-400 mr-1.5">$</span>${escapeHtml(log.text.replace(/^\$\s*/, ''))}`;
          break;
        case 'info':
          line.className += ' text-slate-300';
          line.innerHTML = escapeHtml(log.text);
          break;
        case 'green':
          line.className += ' text-emerald-400 font-medium';
          line.innerHTML = escapeHtml(log.text);
          break;
        case 'cyan':
          line.className += ' text-sky-300';
          line.innerHTML = escapeHtml(log.text);
          break;
        case 'amber':
          line.className += ' text-amber-300';
          line.innerHTML = escapeHtml(log.text);
          break;
        case 'purple':
          line.className += ' text-purple-300';
          line.innerHTML = escapeHtml(log.text);
          break;
        case 'emerald-glow':
          line.className += ' text-emerald-300 font-bold py-1 bg-emerald-500/10 px-2 rounded border border-emerald-500/20';
          line.innerHTML = escapeHtml(log.text);
          break;
        default:
          line.className += ' text-slate-300';
          line.innerHTML = escapeHtml(log.text);
      }

      return line;
    },

    renderStepLogs(step, onComplete) {
      const t = this.elements.terminal;
      if (!t) return;

      const cursor = this.ensureCursor();
      let lineIndex = 0;

      const pushLine = () => {
        if (lineIndex >= step.logs.length) {
          if (onComplete) onComplete();
          return;
        }

        const log = step.logs[lineIndex];
        const el = this.createLogLineElement(log);
        if (cursor && cursor.parentNode === t) {
          t.insertBefore(el, cursor);
        } else {
          t.appendChild(el);
        }

        // 丝滑自动滚屏保持最新日志在可视范围内
        t.scrollTop = t.scrollHeight;
        lineIndex++;

        const timeout = setTimeout(pushLine, this.config.settings.streamLineDelay);
        this.logTimeouts.push(timeout);
      };

      pushLine();
    },

    ensureCursor() {
      const t = this.elements.terminal;
      if (!t) return null;
      let cursor = document.getElementById('hero-terminal-cursor');
      if (!cursor) {
        cursor = document.createElement('div');
        cursor.id = 'hero-terminal-cursor';
        cursor.className = 'inline-flex items-center gap-1.5 text-sky-400 pt-0.5 text-[11px]';
        cursor.innerHTML = '<span class="w-1.5 h-3.5 bg-sky-400 animate-pulse inline-block"></span><span class="text-slate-500 font-mono text-[10px]">autonomous stream</span>';
        t.appendChild(cursor);
      }
      return cursor;
    },

    scheduleNextStep(currentStepNum) {
      const nextStepNum = currentStepNum + 1;

      const waitAndAdvance = () => {
        if (this.isPausedByHover) {
          // 悬停期间保持轮询等待恢复
          this.stepTimer = setTimeout(waitAndAdvance, 400);
          return;
        }

        if (nextStepNum <= 6) {
          this.currentStepIndex = nextStepNum;
          this.executeStep(nextStepNum);
        } else {
          // 全部 6 步已完成！
          this.onCycleComplete();
        }
      };

      this.stepTimer = setTimeout(waitAndAdvance, this.config.settings.stepDuration);
    },

    onCycleComplete() {
      const e = this.elements;
      const t = e.terminal;

      // 终端底部展示验收产物总结
      if (t) {
        const summary = document.createElement('div');
        summary.className = 'mt-3 pt-2.5 border-t border-slate-800 dark:border-white/[0.08] text-sky-400 font-semibold flex flex-wrap items-center gap-2 animate-fadeIn';
        summary.innerHTML = `
          <span class="flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>Verified Artifacts:</span>
          </span>
          <span class="text-slate-300 font-normal text-[11px] font-mono">
            hardware_manifest.yaml, driver_plan.yaml, verification_report.json
          </span>
        `;
        const cursor = document.getElementById('hero-terminal-cursor');
        if (cursor && cursor.parentNode === t) {
          t.insertBefore(summary, cursor);
        } else {
          t.appendChild(summary);
        }
        t.scrollTop = t.scrollHeight;
      }

      if (e.globalStatusText) {
        e.globalStatusText.textContent = 'ALL VERIFIED';
      }

      // 如果开启了自动循环，驻留 cycleEndDelay 后开启下一轮
      if (this.config.settings.autoLoop) {
        const loopNext = () => {
          if (this.isPausedByHover) {
            this.stepTimer = setTimeout(loopNext, 500);
            return;
          }
          this.cycleCount++;
          // 平滑淡入下一轮循环
          this.startCycle(1);
        };
        this.stepTimer = setTimeout(loopNext, this.config.settings.cycleEndDelay);
      }
    }
  };

  function escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // 挂载到全局，供外界按需控制或调试
  window.HeroOrchestrator = HeroOrchestrator;

  // 页面就绪后自动启动
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => HeroOrchestrator.init());
  } else {
    HeroOrchestrator.init();
  }

})(window, document);
