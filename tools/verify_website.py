import subprocess
import time
import json
import os
import sys
import urllib.request
import websocket
import base64

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
BROWSER_PATH = EDGE_PATH if os.path.exists(EDGE_PATH) else CHROME_PATH

PORT = 9333
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
HTML_PATH = os.path.join(PROJECT_ROOT, "website", "index.html")
URL = f"file:///{HTML_PATH.replace(os.sep, '/')}"
OUT_DIR = os.path.join(PROJECT_ROOT, "website", "assets", "images")
os.makedirs(OUT_DIR, exist_ok=True)

print(f"Using browser: {BROWSER_PATH} on port {PORT}")

import tempfile
temp_dir = tempfile.mkdtemp()

# Launch headless browser with CDP
proc = subprocess.Popen([
    BROWSER_PATH,
    "--headless=new",
    f"--remote-debugging-port={PORT}",
    "--remote-debugging-address=127.0.0.1",
    "--remote-allow-origins=*",
    f"--user-data-dir={temp_dir}",
    "--window-size=1440,900",
    "--disable-gpu",
    "--no-sandbox",
    "--disable-extensions",
    "--disable-dev-shm-usage",
    URL
])

try:
    ws_url = None
    for _ in range(20):
        time.sleep(0.5)
        try:
            req = urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/list")
            targets = json.loads(req.read().decode())
            # Find the specific target for our index.html page
            page_target = next((t for t in targets if t.get("type") == "page" and "index.html" in t.get("url", "")), None)
            if not page_target:
                page_target = next((t for t in targets if t.get("type") == "page"), None)
            if page_target:
                ws_url = page_target["webSocketDebuggerUrl"]
                print(f"Target page found: {page_target.get('url')}")
                break
        except Exception:
            pass

    if not ws_url:
        raise RuntimeError("Failed to connect to CDP endpoint")
    print(f"Connected to CDP: {ws_url}")

    ws = websocket.create_connection(ws_url)

    msg_id = 1
    console_errors = []

    def send_cmd(method, params=None):
        global msg_id
        msg_id += 1
        payload = {"id": msg_id, "method": method, "params": params or {}}
        ws.send(json.dumps(payload))
        while True:
            res = json.loads(ws.recv())
            if res.get("method") == "Runtime.consoleAPICalled":
                msg_type = res.get("params", {}).get("type")
                args = res.get("params", {}).get("args", [])
                text = " ".join(str(a.get("value", "")) for a in args)
                print(f"[Browser Console {msg_type}]: {text}")
                if msg_type in ("error", "warning"):
                    console_errors.append(f"{msg_type}: {text}")
            elif res.get("method") == "Runtime.exceptionThrown":
                desc = res.get("params", {}).get("exceptionDetails", {}).get("text", "")
                print(f"[Browser Exception]: {desc}")
                console_errors.append(f"exception: {desc}")
            if res.get("id") == payload["id"]:
                return res.get("result", {})

    # Enable console and page
    send_cmd("Page.enable")
    send_cmd("Runtime.enable")

    # Wait for initial render of black hole and reveal animations
    time.sleep(2.2)
    send_cmd("Runtime.evaluate", {
        "expression": "document.querySelectorAll('.reveal').forEach(el => el.classList.add('active'));"
    })
    time.sleep(0.4)

    # Helper function to set viewport
    def set_viewport(width, height, is_mobile=False):
        send_cmd("Emulation.setDeviceMetricsOverride", {
            "width": width,
            "height": height,
            "deviceScaleFactor": 1,
            "mobile": is_mobile
        })
        time.sleep(0.4)

    # 1. 1440x900 (Standard Desktop / Laptop)
    print("Testing 1440x900: Initial state (Scroll = 0, Attio Single Card)...")
    set_viewport(1440, 900)
    send_cmd("Runtime.evaluate", {"expression": "window.scrollTo(0, 0); window.dispatchEvent(new Event('scroll'));"})
    time.sleep(0.5)
    
    # Check satellite opacity at scroll = 0
    sat_opacity = send_cmd("Runtime.evaluate", {
        "expression": "({ s1: window.getComputedStyle(document.getElementById('satellite-1')).opacity, s2: window.getComputedStyle(document.getElementById('satellite-2')).opacity, s3: window.getComputedStyle(document.getElementById('satellite-3')).opacity })",
        "returnByValue": True
    }).get("value", {})
    print(f"1440 Initial Satellite Opacities: {sat_opacity}")

    res = send_cmd("Page.captureScreenshot", {"format": "png"})
    d1440_init_png = os.path.join(OUT_DIR, "verify_1440_initial_single.png")
    with open(d1440_init_png, "wb") as f:
        f.write(base64.b64decode(res["data"]))
    print(f"Saved: {d1440_init_png}")

    print("Testing 1440x900: Scrolled state (Scroll = 480, Attio Flanking Emerged)...")
    send_cmd("Runtime.evaluate", {"expression": "window.scrollTo(0, 480); window.dispatchEvent(new Event('scroll'));"})
    time.sleep(0.6)
    sat_opacity_scrolled = send_cmd("Runtime.evaluate", {
        "expression": "({ s1: window.getComputedStyle(document.getElementById('satellite-1')).opacity, s2: window.getComputedStyle(document.getElementById('satellite-2')).opacity, s3: window.getComputedStyle(document.getElementById('satellite-3')).opacity })",
        "returnByValue": True
    }).get("value", {})
    print(f"1440 Scrolled Satellite Opacities: {sat_opacity_scrolled}")

    res = send_cmd("Page.captureScreenshot", {"format": "png"})
    d1440_scrolled_png = os.path.join(OUT_DIR, "verify_1440_scrolled_emerged.png")
    with open(d1440_scrolled_png, "wb") as f:
        f.write(base64.b64decode(res["data"]))
    print(f"Saved: {d1440_scrolled_png}")

    # 2. 1600x900 (Widescreen 2K/1080p Desktop)
    print("Testing 1600x900: Initial state (Scroll = 0)...")
    set_viewport(1600, 900)
    send_cmd("Runtime.evaluate", {"expression": "window.scrollTo(0, 0); window.dispatchEvent(new Event('scroll'));"})
    time.sleep(0.5)
    res = send_cmd("Page.captureScreenshot", {"format": "png"})
    d1600_init_png = os.path.join(OUT_DIR, "verify_1600_initial_single.png")
    with open(d1600_init_png, "wb") as f:
        f.write(base64.b64decode(res["data"]))
    print(f"Saved: {d1600_init_png}")

    print("Testing 1600x900: Scrolled state (Scroll = 480)...")
    send_cmd("Runtime.evaluate", {"expression": "window.scrollTo(0, 480); window.dispatchEvent(new Event('scroll'));"})
    time.sleep(0.6)
    res = send_cmd("Page.captureScreenshot", {"format": "png"})
    d1600_scrolled_png = os.path.join(OUT_DIR, "verify_1600_scrolled_emerged.png")
    with open(d1600_scrolled_png, "wb") as f:
        f.write(base64.b64decode(res["data"]))
    print(f"Saved: {d1600_scrolled_png}")

    # 3. 1024x768 (Tablet Landscape)
    print("Testing 1024x768 Tablet...")
    set_viewport(1024, 768)
    send_cmd("Runtime.evaluate", {"expression": "window.scrollTo(0, 0); window.dispatchEvent(new Event('scroll'));"})
    time.sleep(0.5)
    res = send_cmd("Page.captureScreenshot", {"format": "png"})
    t1024_init_png = os.path.join(OUT_DIR, "verify_1024_initial.png")
    with open(t1024_init_png, "wb") as f:
        f.write(base64.b64decode(res["data"]))
    print(f"Saved: {t1024_init_png}")

    send_cmd("Runtime.evaluate", {"expression": "window.scrollTo(0, 320); window.dispatchEvent(new Event('scroll'));"})
    time.sleep(0.5)
    res = send_cmd("Page.captureScreenshot", {"format": "png"})
    t1024_scrolled_png = os.path.join(OUT_DIR, "verify_1024_scrolled.png")
    with open(t1024_scrolled_png, "wb") as f:
        f.write(base64.b64decode(res["data"]))
    print(f"Saved: {t1024_scrolled_png}")

    # 4. 390x844 (Mobile Portrait)
    print("Testing 390x844 Mobile...")
    set_viewport(390, 844, is_mobile=True)
    send_cmd("Runtime.evaluate", {"expression": "window.scrollTo(0, 0); window.dispatchEvent(new Event('scroll'));"})
    time.sleep(0.5)
    res = send_cmd("Page.captureScreenshot", {"format": "png"})
    m390_init_png = os.path.join(OUT_DIR, "verify_390_initial.png")
    with open(m390_init_png, "wb") as f:
        f.write(base64.b64decode(res["data"]))
    print(f"Saved: {m390_init_png}")

    send_cmd("Runtime.evaluate", {"expression": "window.scrollTo(0, 300); window.dispatchEvent(new Event('scroll'));"})
    time.sleep(0.5)
    res = send_cmd("Page.captureScreenshot", {"format": "png"})
    m390_scrolled_png = os.path.join(OUT_DIR, "verify_390_scrolled.png")
    with open(m390_scrolled_png, "wb") as f:
        f.write(base64.b64decode(res["data"]))
    print(f"Saved: {m390_scrolled_png}")

    # Reset back to 1440x900
    set_viewport(1440, 900)

    # 4. Check if animation is continuously running without throwing errors
    eval_res = send_cmd("Runtime.evaluate", {
        "expression": "({ canvasWidth: window.canvas ? window.canvas.width : 0, canvasHeight: window.canvas ? window.canvas.height : 0, particleCount: window.accretionParticles ? window.accretionParticles.length : 0, blackHoleR: window.blackHole ? window.blackHole.rHorizon : 0 })",
        "returnByValue": True
    })
    res_val = eval_res.get("result", {}).get("value") or eval_res.get("value", {})
    print(f"Canvas Runtime State: {json.dumps(res_val)}")

    # Switch to Dark Mode
    send_cmd("Runtime.evaluate", {
        "expression": "if (!document.documentElement.classList.contains('dark')) document.getElementById('theme-toggle').click(); window.scrollTo(0, 0); window.dispatchEvent(new Event('scroll'));"
    })
    time.sleep(0.6)

    # Capture Dark Mode Initial Hero (Scroll = 0)
    print("Testing Dark Mode Initial (Scroll = 0)...")
    res = send_cmd("Page.captureScreenshot", {"format": "png"})
    d_dark_init_png = os.path.join(OUT_DIR, "verify_dark_hero_initial.png")
    with open(d_dark_init_png, "wb") as f:
        f.write(base64.b64decode(res["data"]))
    print(f"Saved: {d_dark_init_png}")

    # Capture Dark Mode Scrolled Hero
    print("Testing Dark Mode Scrolled (Scroll = 480)...")
    send_cmd("Runtime.evaluate", {"expression": "window.scrollTo(0, 480); window.dispatchEvent(new Event('scroll'));"})
    time.sleep(0.6)
    res = send_cmd("Page.captureScreenshot", {"format": "png"})
    d_dark_png = os.path.join(OUT_DIR, "verify_dark_hero_scrolled.png")
    with open(d_dark_png, "wb") as f:
        f.write(base64.b64decode(res["data"]))
    print(f"Saved: {d_dark_png}")

    # Test Mouse Interaction & Shockwave
    print("Testing Mouse Interaction & Gravitational Shockwave...")
    # Simulate mouse movement across the accretion disk
    for mx in range(350, 750, 50):
        send_cmd("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": mx, "y": 210})
        time.sleep(0.04)
    time.sleep(0.1)
    # Simulate click to trigger shockwave
    send_cmd("Input.dispatchMouseEvent", {"type": "mousePressed", "x": 620, "y": 210, "button": "left", "clickCount": 1})
    send_cmd("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": 620, "y": 210, "button": "left", "clickCount": 1})
    time.sleep(0.3)
    res = send_cmd("Page.captureScreenshot", {"format": "png"})
    d_mouse_png = os.path.join(OUT_DIR, "verify_mouse_interaction.png")
    with open(d_mouse_png, "wb") as f:
        f.write(base64.b64decode(res["data"]))
    print(f"Saved: {d_mouse_png}")

    # Jump to Step 6 in Dark Mode to verify full closed-loop visual
    print("Testing Step 6 HIL in Dark Mode...")
    send_cmd("Runtime.evaluate", {"expression": "window.HeroOrchestrator.jumpToStep(6);"})
    time.sleep(1.8)
    res = send_cmd("Page.captureScreenshot", {"format": "png"})
    d_step6_dark_png = os.path.join(OUT_DIR, "verify_dark_hero_step6.png")
    with open(d_step6_dark_png, "wb") as f:
        f.write(base64.b64decode(res["data"]))
    print(f"Saved: {d_step6_dark_png}")

    print("=== Verification Summary ===")
    print(f"Console errors count: {len(console_errors)}")
    if console_errors:
        for err in console_errors:
            print(f"  - {err}")
    else:
        print("  [SUCCESS] ZERO console errors or exceptions detected!")

    ws.close()

finally:
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except Exception:
        proc.kill()
