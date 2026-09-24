1: # DriveForge 官方落地页与仿真控制台 (Antigravity 科技风格)
2: 
3: 本项目为 **DriveForge**（证据链优先的嵌入式驱动自主工程智能体）的官方产品落地展示页与在线仿真交互控制台。视觉与动效参考 [Google Antigravity](https://antigravity.google/) 现代 Agentic 科技美学。
4: 
5: ---
6: 
7: ## 目录与工程架构
8: 
9: 本项目经过专业级前端工程化重构，遵循**关注点分离（Separation of Concerns）**与**零构建负担（Zero Build Step）**原则。既保持了双击或单命令即可本地极速运行的高便携性，又具备生产级独立部署、模块化解耦与高维护水准。
10: 
11: ```text
12: website/
13: ├── index.html                  # 语义化骨架入口（仅负责 SEO 元数据与 DOM 拓扑，精简纯净）
14: ├── css/
15: │   └── style.css               # 样式表（主题变量、高斯模糊玻璃拟态、流光进度、磁性光标、无障碍动效）
16: ├── js/
17: │   ├── tailwind-config.js      # Tailwind 扩展设计系统规范与调色板配置
18: │   ├── blackhole.js            # 3D 相对论引力透镜与吸积盘开普勒差动旋转 Canvas 物理引擎
19: │   ├── playground.js           # 芯片/外设交互式仿真控制台与数据流状态机（SCons/RTT/Manifest 生成）
20: │   ├── interactions.js         # UI 交互层（深浅主题切换/持久化、磁性光标、视差滚动、折叠菜单、Toast）
21: │   └── main.js                 # 应用主装配入口
22: ├── assets/
23: │   └── images/                 # 页面测试、验证截图与静态多媒体资产
24: ├── nginx.conf                  # 生产级高性能 Nginx 配置文件（Gzip/Brotli 压缩、长效缓存策略、安全响应头）
25: ├── Dockerfile                  # 基于 nginx:alpine 的极轻量容器镜像构建脚本（~10MB 镜像体积）
26: ├── docker-compose.yml          # Docker Compose 一键启动编排
27: ├── deploy.ps1                  # Windows PowerShell 一键同步/部署脚本（支持 PocketBase 与服务器）
28: ├── deploy.sh                   # Linux/macOS 自动化部署脚本
29: └── README.md                   # 本说明文档
30: ```
31: 
32: ---
33: 
34: ## 为什么进行工程化重构？（单文件 vs 模块化对比）
35: 
36: | 维度 | 原单文件 `index.html` 方案 | 当前工程化重构方案 |
37: | :--- | :--- | :--- |
38: | **PocketBase 部署** | 只能全量扔进 `pb_public`，127KB 混杂在一起，无法做分级缓存 | 资源规范解耦，PocketBase 可对 CSS/JS 设置长期静态缓存，HTML 秒级更新 |
39: | **服务器与 CDN 缓存** | 任何文案修改都会导致全量 127KB 失效重新传输 | 静态资源与页面骨架分离，利用浏览器强缓存节省 80%+ 带宽并秒开 |
40: | **代码可维护性** | 2347 行代码混杂，样式、业务模拟、黑洞物理动画纠缠，极易冲突 | 单一职责分工（样式、仿真、天体物理、UI 交互分离），结构清晰如艺术品 |
41: | **生产环境稳定性** | 内联过深，排查 Bug 和样式调试成本极高 | 模块生命周期清晰（`init`, `resize`, `render`），支持自动化 CDP 测试 |
42: | **容器化与自动化** | 缺少标准部署配置文件，需要运维手动编写 Nginx | 开箱即用提供 `Dockerfile`、`docker-compose`、`nginx.conf` 及一键同步脚本 |
43: 
44: ---
45: 
46: ## 本地预览与开发
47: 
48: ### 方式 1：使用 Python 内置简易 HTTP 服务器（推荐）
49: 在项目根目录或 `website` 目录下直接启动：
50: 
51: ```powershell
52: # 在 DriveForge 根目录下运行
53: python -m http.server 8080 --directory website
54: 
55: # 或在 website 目录下运行
56: .\deploy.ps1 -Target preview -Port 8080
57: ```
58: 浏览器打开 [http://localhost:8080](http://localhost:8080) 即可访问。
59: 
60: ### 方式 2：直接本地双击打开
所有引入均为标准的相对路径（`./css/style.css`, `./js/*.js`），直接使用 Chrome、Edge、Firefox 或 Safari 双击打开 `index.html` 即可正常浏览所有交互与 3D 效果。

---

## 生产环境部署指南

### 方案 1：部署到 PocketBase (推荐快速交付)

PocketBase 内置了极速的静态资源服务器，会自动将可执行文件同级目录下的 `pb_public` 文件夹映射到根路径 `/`。

#### 在 Windows 上部署：
```powershell
# 指定 PocketBase 所在目录，脚本会自动将最新资产过滤同步至 pb_public
.\deploy.ps1 -Target pocketbase -PocketBasePath "C:\Tools\pocketbase"
```

#### 在 Linux / macOS 上部署：
```bash
./deploy.sh pocketbase /opt/pocketbase
```

启动 PocketBase 后：
```bash
./pocketbase serve --http="0.0.0.0:8090"
```
落地页将直接在 `http://your-server-ip:8090/` 呈现，且享受零配置的完整静态支持！

---

### 方案 2：Docker / Docker Compose 容器化部署

本项目提供了极简的 `Dockerfile`（基于 Alpine Linux），无需任何构建工具，数十秒即可完成镜像打包：

```bash
# 启动容器（映射到宿主机 8080 端口）
docker compose up -d --build

# 访问页面
curl http://localhost:8080
```

---

### 方案 3：独立 Nginx / Caddy 服务器部署

将 `website/` 目录下的静态文件复制到服务器的 Web 根目录（如 `/var/www/driveforge`），并使用本项目自带的 `website/nginx.conf`：

```nginx
# 包含在您的 nginx.conf 或 conf.d 中
include /path/to/website/nginx.conf;
```
配置已自带：
- **Gzip 压缩**（压缩率达 70%+，首屏 LCP 极速）；
- **缓存分级**：HTML 入口 `no-cache`（更新即刻生效），CSS/JS 7 天带版本协商，静态图片 30 天强缓存；
- **安全响应头**（防点击劫持、MIME 嗅探防护等）。

---

## 页面核心技术特性

1. **3D 相对论黑洞引力吸积盘空间背景引擎 (`js/blackhole.js`)**：
   - 基于广义相对论引力透镜美学与开普勒差动旋转模型（Keplerian Differential Flow）；
   - 双向相对论引力透镜弯曲光环与超细高能光子环；
   - 相对论多普勒辐射增强（迎面旋向视线侧蓝移增亮，离去侧深邃柔光）；
   - 鼠标次级引力井扰动（鼠标悬停与移动形成优雅时空微涡流）；
   - 深浅双模式适配（深色黑曜石星际黑洞 / 浅色量子拓扑引力涡流）。

2. **在线交互式仿真控制台 (`js/playground.js`)**：
   - 动态切换芯片（GD32F470、STM32F407、GD32F450）与外设（CAN0、UART1、SPI2、I2C1、ADC0）；
   - 仿真 DriveForge 完整闭环：需求解析 → 硬件事实门禁校验 → 复用策略规划 → SCons 构建 → J-Link 烧录 → 实机 RTT 测试；
   - 动态输出 `hardware_manifest.yaml`、`driver_plan.yaml`、`verification_report.json`。

3. **精致微交互与无障碍动效体系 (`js/interactions.js`)**：
   - 无位移的邻近边缘高亮与克制微交互（Proximity Edge Illumination）；
   - 滚动速度耦合（Scroll Velocity Coupling）与视差倾角（Tilt）；
   - 原生 Light / Dark 主题一键切换（状态持久化于 `localStorage`）；
   - 减弱动效开关（Motion Reduction Toggle）与无障碍 ARIA 支持；
   - 触摸设备按压水波纹（Ripple）与轻量 Toast 通知反馈。

---

## 自动化测试与质量保障

项目配备了基于 Chrome/Edge CDP（Chrome DevTools Protocol）的无头浏览器端到端测试套件：

```powershell
# 运行自动化端到端测试
python tools/verify_website.py
```
测试流程包括：
- 启动 Headless 浏览器环境加载落地页；
- 验证深色模式渲染与视口截图；
- 自动化模拟鼠标微扰与粒子物理场计算；
- 模拟切换浅色模式并捕获渲染结果；
- 检查控制台报错（确保 **0 Errors, 0 Exceptions**）；
- 验证 Canvas 动态运行指标（宽度、高度、粒子存活数、黑洞视界半径）。
