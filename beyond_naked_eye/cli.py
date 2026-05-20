from __future__ import annotations

import asyncio
from collections import deque
from datetime import datetime
from typing import Optional
from pathlib import Path

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from beyond_naked_eye.agents.orchestrator import MultiAgentOrchestrator
from beyond_naked_eye.analysis.assistant import summarize_findings
from beyond_naked_eye.config import SETTINGS
from beyond_naked_eye.diagnostics.system_diagnostics import get_device_info, get_network_status, get_system_status, run_diagnostics
from beyond_naked_eye.engine import ScanEngine
from beyond_naked_eye.modules.intake_analysis import analyze_archive, analyze_executable, analyze_file, analyze_image, analyze_source, analyze_url, export_analysis_bundle
from beyond_naked_eye.exporters import export_session
from beyond_naked_eye.graph.relationship import build_relationship_ascii
from beyond_naked_eye.models import InvestigationSession
from beyond_naked_eye.storage import SessionStore
from beyond_naked_eye.themes.retro_crt import get_default_theme
from beyond_naked_eye.ui.crt_effects import rasterize_text, scanline_block, terminal_flicker

THEME = get_default_theme()
console = Console(theme=THEME.rich_theme())


def _boot_logo() -> str:
    return """  ____  _   _ _____ \\  |
 | __ )| \\ | | ____|\\ |
 |  _ \\|  \\| |  _| |\\|
 | |_) | |\\  | |___|  |
 |____/|_| \\_|_____|_|_|
 BEYOND THE NAKED EYE :: ARCHIVE NODE"""



async def _startup_sequence() -> None:
    steps = [
        "SYSTEM DIAGNOSTICS ............ OK",
        "LOADING CRT THEME ENGINE ...... OK",
        "MOUNTING EVIDENCE ARCHIVE ...... OK",
        "VERIFYING MODULE CHECKSUMS ..... OK",
        "INITIALIZING TACTICAL PANELS ... OK",
        "ATTACHING TERMINAL I/O ......... OK",
    ]
    console.clear()
    console.print(Panel(rasterize_text(_boot_logo()), title="BOOT", border_style="crt.border", style="on black"))
    for step in steps:
        console.print(f"[crt.fg]{terminal_flicker(step)}[/crt.fg]")
        console.print(f"[crt.dim]{scanline_block(48, 1)}[/crt.dim]")
        await asyncio.sleep(0.08)
    console.print(f"[crt.warn]NOTICE:[/crt.warn] {SETTINGS.ethical_warning}")


def _findings_table(findings, filter_term: str = "") -> Table:
    table = Table(title="ACTIVE INVESTIGATION FEED", style="crt.fg", border_style="crt.border", box=None)
    table.add_column("CAT", style="crt.dim")
    table.add_column("TITLE")
    table.add_column("VALUE")
    table.add_column("CONF", justify="right")
    for f in findings:
        hay = f"{f.category} {f.title} {f.value}".lower()
        if filter_term and filter_term.lower() not in hay:
            continue
        table.add_row(f.category[:10], f.title[:20], str(f.value)[:54], f"{f.confidence:.2f}")
    return table


def _timeline_panel(session: InvestigationSession) -> Panel:
    recent = session.timeline[-8:]
    rows = []
    for event in recent:
        mark = "!" if event.get("event") in {"tag"} else "-"
        rows.append(f"{mark} {event.get('event', 'event')}: {str(event)[:72]}")
    return Panel("\n".join(rows) or "- timeline empty", title="TIMELINE RECONSTRUCTION", border_style="crt.border")


async def repl() -> None:
    await _startup_sequence()
    engine, orchestrator, store = ScanEngine(), MultiAgentOrchestrator(), SessionStore()
    current: Optional[InvestigationSession] = InvestigationSession("default")
    logs: deque[str] = deque(maxlen=18)
    filter_term = ""
    diagnostics_summary = "NO DIAGNOSTICS RECORDED"
    intake_summary = "ANALYSIS INTAKE CENTER: IDLE"

    while True:
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")
        layout = Layout(name="root")
        layout.split_column(Layout(name="top", ratio=4), Layout(name="bottom", ratio=1))
        layout["top"].split_row(Layout(name="left", ratio=3), Layout(name="right", ratio=2))
        layout["left"].split_column(
            Layout(Panel(_findings_table(current.findings, filter_term), title=f"CASE FILE :: {current.name}", border_style="crt.border"), ratio=3),
            Layout(_timeline_panel(current), ratio=2),
        )
        relation = build_relationship_ascii(current.findings)
        graph_panel = Panel(rasterize_text(relation), title="RELATIONSHIP GRAPH", border_style="crt.border")
        diag_text = f"UTC: {now}\n{get_system_status()}\n{get_network_status()}\n\n{diagnostics_summary}"
        logs_panel = Panel("\n".join(logs) or "- no logs", title="TERMINAL LOG STREAM", border_style="crt.border")
        intake_panel = Panel(intake_summary, title="ANALYSIS INTAKE CENTER", border_style="crt.border")
        layout["right"].split_column(graph_panel, Panel(diag_text, title="TACTICAL DIAGNOSTICS", border_style="crt.border"), intake_panel, logs_panel)
        layout["bottom"].update(Panel(Text(scanline_block(140, 2), style="crt.dim"), title="SIGNAL NOISE / CRT SCANLINES", border_style="crt.border"))

        with Live(layout, console=console, refresh_per_second=8, transient=True):
            raw = console.input("[crt.prompt]archive@node:/ $ [/crt.prompt]").strip()

        if raw in {"quit", "exit"}:
            break
        if raw == "help":
            console.print("scan <type> <value> | agentscan <type> <value> | analyze url <url> | analyze file <path> | analyze image <path> | analyze executable <path> | analyze source <path> | analyze archive <path> | analyze export <out.json> | system status | network status | device info | diagnostics run [--lan] | monitor <type> <value> | note <text> | tag <value> | filter <term> | save <name> | load <name> | export <name> <json|txt|csv|html> | graph <name> | clear")
            continue
        if raw == "clear":
            console.clear()
            await _startup_sequence()
            continue

        parts = raw.split()
        if not parts:
            continue
        try:
            cmd = parts[0]
            if cmd == "scan" and len(parts) >= 3:
                t, v = parts[1], " ".join(parts[2:])
                found = await engine.scan(t, v)
                current.add_findings(found, raw)
                logs.appendleft(f"[{now}] scan::{t} -> {len(found)} records")
            elif cmd == "agentscan" and len(parts) >= 3:
                t, v = parts[1], " ".join(parts[2:])
                results = await orchestrator.run(t, v)
                for r in results:
                    current.add_findings(r.findings, f"{r.agent} completed")
                logs.appendleft(f"[{now}] multi-agent complete ({len(results)})")
            elif cmd == "analyze" and len(parts) >= 3:
                sub = parts[1]
                target = " ".join(parts[2:])
                if sub == "url":
                    entries = analyze_url(target)
                elif sub == "file":
                    entries = analyze_file(target)
                elif sub == "image":
                    entries = analyze_image(target)
                elif sub == "executable":
                    entries = analyze_executable(target)
                elif sub == "source":
                    entries = analyze_source(target)
                elif sub == "archive":
                    entries = analyze_archive(target)
                elif sub == "export":
                    export_analysis_bundle(Path(target), current.findings)
                    logs.appendleft(f"[{now}] analysis bundle exported -> {target}")
                    intake_summary = "ANALYSIS INTAKE CENTER: bundle exported"
                    continue
                else:
                    raise ValueError(f"Unsupported analyze target: {sub}")
                current.add_findings(entries, f"analyze {sub}")
                intake_summary = f"ANALYSIS INTAKE CENTER: {sub} analyzed ({len(entries)} findings)"
                logs.appendleft(f"[{now}] analyze::{sub} -> {len(entries)} findings")
            elif cmd == "monitor" and len(parts) >= 3:
                logs.appendleft(f"[{now}] monitor armed for {' '.join(parts[1:])}")
            elif cmd == "note":
                current.timeline.append({"event": "note", "text": " ".join(parts[1:])})
            elif cmd == "tag" and len(parts) >= 2:
                current.timeline.append({"event": "tag", "value": parts[1]})
            elif cmd == "filter":
                filter_term = " ".join(parts[1:])
            elif cmd == "save" and len(parts) == 2:
                current.name = parts[1]
                store.save(current)
                logs.appendleft(f"[{now}] session saved")
            elif cmd == "load" and len(parts) == 2:
                current = store.load(parts[1])
                logs.appendleft(f"[{now}] session loaded")
            elif cmd == "export" and len(parts) == 3:
                export_session(current, parts[2])
                logs.appendleft(f"[{now}] exported::{parts[2]}")
            elif cmd == "graph":
                console.print(Panel(rasterize_text(build_relationship_ascii(current.findings)), title="TACTICAL GRAPH MAP", border_style="crt.border"))
                console.print(Panel(summarize_findings(current.findings), title="ANALYST SUMMARY", border_style="crt.border"))
            elif cmd == "system" and len(parts) >= 2 and parts[1] == "status":
                logs.appendleft(f"[{now}] {get_system_status()}")
            elif cmd == "network" and len(parts) >= 2 and parts[1] == "status":
                logs.appendleft(f"[{now}] {get_network_status()}")
            elif cmd == "device" and len(parts) >= 2 and parts[1] == "info":
                logs.appendleft(f"[{now}] {get_device_info(False)}")
            elif cmd == "diagnostics" and len(parts) >= 2 and parts[1] == "run":
                payload = run_diagnostics(enable_lan_discovery=("--lan" in parts))
                diagnostics_summary = payload["summary"]
                logs.appendleft(f"[{now}] diagnostics complete")
            else:
                logs.appendleft(f"[{now}] unknown command")
        except Exception as exc:
            logs.appendleft(f"[{now}] error: {exc}")


def main() -> None:
    asyncio.run(repl())
