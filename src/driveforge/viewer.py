from __future__ import annotations

import json
from html import escape
from pathlib import Path
from typing import Any
from urllib.parse import quote

from .utils import load_json


def _display(value: Any) -> str:
    if value is None or value == "":
        return "—"
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _rows(items: list[tuple[Any, ...]]) -> str:
    return "".join(
        "<tr>" + "".join(f"<td>{escape(_display(cell))}</td>" for cell in row) + "</tr>"
        for row in items
    ) or '<tr><td colspan="5" class="empty">暂无数据</td></tr>'


def _list(items: list[Any]) -> str:
    return "".join(f"<li>{escape(_display(item))}</li>" for item in items) or "<li>无</li>"


def generate_report_page(artifact_dir: Path) -> tuple[Path, str]:
    artifact_dir = artifact_dir.resolve()
    state_path = artifact_dir / "state.json"
    if not state_path.is_file():
        raise ValueError(
            f"No plan/run state found in {artifact_dir}. Run 'driveforge plan' or 'driveforge run' first."
        )

    state = load_json(state_path)
    manifest = state.get("manifest") if isinstance(state.get("manifest"), dict) else {}
    plan = state.get("plan") if isinstance(state.get("plan"), dict) else {}
    report_path = artifact_dir / "verification_report.json"
    report = load_json(report_path) if report_path.is_file() else {}
    status = str(report.get("status") or plan.get("status") or manifest.get("status") or "UNKNOWN")

    facts = manifest.get("facts") if isinstance(manifest.get("facts"), dict) else {}
    fact_rows: list[tuple[Any, ...]] = []
    for key, item in facts.items():
        fact = item if isinstance(item, dict) else {}
        evidence = fact.get("evidence") if isinstance(fact.get("evidence"), list) else []
        locations = []
        for entry in evidence:
            if not isinstance(entry, dict):
                continue
            location = str(entry.get("path") or "")
            if entry.get("line") is not None:
                location += f":{entry['line']}"
            if location:
                locations.append(location)
        fact_rows.append(
            (key, fact.get("value"), fact.get("confidence"), fact.get("source"), ", ".join(locations))
        )

    phases = report.get("phases") if isinstance(report.get("phases"), list) else []
    phase_rows = [
        (
            item.get("phase"),
            item.get("status"),
            item.get("attempt"),
            item.get("duration_seconds"),
            item.get("log"),
        )
        for item in phases
        if isinstance(item, dict)
    ]
    steps = plan.get("steps") if isinstance(plan.get("steps"), list) else []
    step_rows = [
        (item.get("id"), item.get("phase"), item.get("status"), item.get("action"), item.get("acceptance"))
        for item in steps
        if isinstance(item, dict)
    ]
    blockers = manifest.get("blockers") if isinstance(manifest.get("blockers"), list) else []
    warnings = manifest.get("warnings") if isinstance(manifest.get("warnings"), list) else []
    risks = plan.get("risks") if isinstance(plan.get("risks"), list) else []
    modified = report.get("modified_files") if isinstance(report.get("modified_files"), list) else []
    reference = plan.get("reference") if isinstance(plan.get("reference"), dict) else {}
    reference_label = " · ".join(
        str(reference[key]) for key in ("instance", "file") if reference.get(key)
    ) or "—"
    logs = sorted((artifact_dir / "logs").glob("*.log")) if (artifact_dir / "logs").is_dir() else []
    log_links = "".join(
        f'<li><a href="logs/{quote(path.name)}">{escape(path.name)}</a></li>' for path in logs
    ) or "<li>无</li>"
    status_class = status.lower() if status in {"PLANNED", "BUILD_PASS", "FLASH_PASS", "VERIFIED", "FAIL", "BLOCKED"} else "unknown"
    raw_state = escape(json.dumps(state, ensure_ascii=False, indent=2))
    raw_report = escape(json.dumps(report, ensure_ascii=False, indent=2)) if report else "尚未生成 Verification Report。"

    page = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>DriveForge · {escape(status)}</title>
  <style>
    :root {{ color-scheme: light dark; font-family: system-ui, sans-serif; background:#0b1220; color:#e5e7eb; }}
    body {{ margin:0; }} main {{ max-width:1180px; margin:auto; padding:32px 20px 64px; }}
    header,.card {{ background:#111827; border:1px solid #263244; border-radius:14px; padding:20px; }}
    header {{ display:flex; justify-content:space-between; gap:20px; align-items:flex-start; }}
    h1,h2 {{ margin:0 0 12px; }} h1 {{ font-size:24px; }} h2 {{ font-size:17px; }}
    .muted,.empty {{ color:#94a3b8; }} .notice {{ margin:16px 0; color:#fbbf24; }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr)); gap:14px; margin:14px 0; }}
    .value {{ overflow-wrap:anywhere; }} .badge {{ padding:7px 11px; border-radius:999px; font-weight:700; background:#334155; }}
    .verified,.build_pass,.flash_pass {{ background:#14532d; color:#bbf7d0; }} .fail,.blocked {{ background:#7f1d1d; color:#fecaca; }}
    table {{ width:100%; border-collapse:collapse; font-size:14px; }} th,td {{ text-align:left; padding:10px; border-bottom:1px solid #263244; vertical-align:top; overflow-wrap:anywhere; }}
    th {{ color:#93c5fd; }} th:nth-child(-n+3),td:nth-child(-n+3) {{ white-space:nowrap; }} ul {{ margin:0; padding-left:20px; }} a {{ color:#7dd3fc; }}
    details {{ margin-top:14px; }} summary {{ cursor:pointer; color:#93c5fd; }} pre {{ white-space:pre-wrap; overflow-wrap:anywhere; font-size:12px; }}
    @media (max-width:650px) {{ header {{ display:block; }} .badge {{ display:inline-block; margin-top:12px; }} table {{ display:block; overflow:auto; }} }}
  </style>
</head>
<body><main>
  <header>
    <div><h1>DriveForge 只读执行报告</h1><div class="muted value">{escape(_display(manifest.get('project')))}</div></div>
    <span class="badge {status_class}">{escape(status)}</span>
  </header>
  <p class="notice">此页面只展示本地真实产物，不执行构建、烧录或硬件测试。状态以 Verification Report 为准。</p>
  <section class="grid">
    <div class="card"><h2>需求</h2><div class="value">{escape(_display(plan.get('request') or manifest.get('request')))}</div></div>
    <div class="card"><h2>目标</h2><div class="value">{escape(_display(plan.get('target')))}</div></div>
    <div class="card"><h2>策略</h2><div class="value">{escape(_display(plan.get('strategy')))}</div></div>
    <div class="card"><h2>复用参考</h2><div class="value">{escape(reference_label)}</div></div>
    <div class="card"><h2>生成时间</h2><div class="value">{escape(_display(report.get('generated_at') or plan.get('generated_at')))}</div></div>
  </section>
  <section class="card"><h2>阶段结果</h2><table><thead><tr><th>阶段</th><th>状态</th><th>尝试</th><th>耗时（秒）</th><th>日志</th></tr></thead><tbody>{_rows(phase_rows)}</tbody></table></section>
  <section class="card" style="margin-top:14px"><h2>驱动规划</h2><table><thead><tr><th>步骤</th><th>阶段</th><th>状态</th><th>操作</th><th>验收条件</th></tr></thead><tbody>{_rows(step_rows)}</tbody></table></section>
  <section class="card" style="margin-top:14px"><h2>硬件事实与证据</h2><table><thead><tr><th>事实</th><th>值</th><th>置信度</th><th>来源</th><th>证据位置</th></tr></thead><tbody>{_rows(fact_rows)}</tbody></table></section>
  <section class="grid">
    <div class="card"><h2>阻塞项</h2><ul>{_list(blockers)}</ul></div>
    <div class="card"><h2>警告</h2><ul>{_list(warnings)}</ul></div>
    <div class="card"><h2>风险</h2><ul>{_list(risks)}</ul></div>
    <div class="card"><h2>修改文件</h2><ul>{_list(modified)}</ul></div>
    <div class="card"><h2>原始日志</h2><ul>{log_links}</ul></div>
  </section>
  <section class="card"><h2>原始产物</h2><details><summary>state.json</summary><pre>{raw_state}</pre></details><details><summary>verification_report.json</summary><pre>{raw_report}</pre></details></section>
</main></body></html>
"""
    page_path = artifact_dir / "report.html"
    page_path.write_text(page, encoding="utf-8")
    return page_path, status
