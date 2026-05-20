from __future__ import annotations

import asyncio
from collections import deque
from typing import Optional

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table

from beyond_naked_eye.agents.orchestrator import MultiAgentOrchestrator
from beyond_naked_eye.analysis.assistant import summarize_findings
from beyond_naked_eye.diagnostics.system_diagnostics import get_device_info, get_network_status, get_system_status, run_diagnostics
from beyond_naked_eye.graph.relationship import build_relationship_ascii
from beyond_naked_eye.config import SETTINGS
from beyond_naked_eye.engine import ScanEngine
from beyond_naked_eye.exporters import export_session
from beyond_naked_eye.models import InvestigationSession
from beyond_naked_eye.storage import SessionStore

console = Console()


def _banner() -> None:
    console.print("[bold cyan]BEYOND THE NAKED EYE[/bold cyan]\n[magenta]Public Intelligence Correlation Framework[/magenta]\n[i]Eyes see less than data.[/i]")


async def _startup_animation() -> None:
    _banner()
    console.print(f"[yellow]Ethical Notice:[/yellow] {SETTINGS.ethical_warning}")
    with Progress() as progress:
        t = progress.add_task("[cyan]System diagnostics & module init...", total=100)
        for _ in range(20):
            await asyncio.sleep(0.03)
            progress.update(t, advance=5)


def _findings_table(findings, filter_term: str = "") -> Table:
    table = Table(title="Live Findings", style="cyan")
    table.add_column("Category"); table.add_column("Title"); table.add_column("Value"); table.add_column("Conf")
    for f in findings:
        if filter_term and filter_term.lower() not in f"{f.category} {f.title} {f.value}".lower():
            continue
        table.add_row(f.category, f.title, str(f.value)[:80], f"{f.confidence:.2f}")
    return table


async def repl() -> None:
    await _startup_animation()
    engine, orchestrator, store = ScanEngine(), MultiAgentOrchestrator(), SessionStore()
    current: Optional[InvestigationSession] = InvestigationSession("default")
    logs: deque[str] = deque(maxlen=10)
    filter_term = ""
    diagnostics_summary = "No diagnostics run yet."

    while True:
        layout = Layout()
        system_panel = Panel(str(get_system_status()), title="System Health Panel", border_style="green")
        network_panel = Panel(str(get_network_status()), title="Network Status Panel", border_style="cyan")
        diag_panel = Panel(diagnostics_summary, title="Diagnostic Summary Panel", border_style="magenta")
        layout.split_column(
            Layout(Panel(_findings_table(current.findings, filter_term), title=f"Investigation: {current.name}"), ratio=3),
            Layout(Panel("\n".join(logs) or "No logs", title="Real-time logs"), ratio=1),
            Layout(system_panel, ratio=1),
            Layout(network_panel, ratio=1),
            Layout(diag_panel, ratio=1),
        )
        with Live(layout, console=console, refresh_per_second=12, transient=True):
            raw = console.input("[bold magenta]bne> [/bold magenta]").strip()
        if raw in {"quit", "exit"}:
            break
        if raw == "help":
            console.print("scan <type> <value> | agentscan <type> <value> | system status | network status | device info | diagnostics run [--lan] | monitor <type> <value> | note <text> | tag <value> | filter <term> | save <name> | load <name> | export <name> <json|txt|csv|html> | graph <name> | clear")
            continue
        if raw == "clear":
            console.clear(); _banner(); continue
        parts = raw.split()
        if not parts:
            continue
        try:
            cmd = parts[0]
            if cmd == "scan" and len(parts) >= 3:
                t, v = parts[1], " ".join(parts[2:])
                found = await engine.scan(t, v)
                current.add_findings(found, raw); logs.appendleft(f"scan complete {t}: {len(found)}")
            elif cmd == "agentscan" and len(parts) >= 3:
                t, v = parts[1], " ".join(parts[2:])
                results = await orchestrator.run(t, v)
                for r in results:
                    current.add_findings(r.findings, f"{r.agent} completed")
                logs.appendleft(f"multi-agent completed: {len(results)} agents")
            elif cmd == "monitor" and len(parts) >= 3:
                logs.appendleft(f"monitoring enabled for {' '.join(parts[1:])} (webhook/email adapters configurable)")
            elif cmd == "note":
                current.timeline.append({"event": "note", "text": " ".join(parts[1:])})
            elif cmd == "tag" and len(parts) >= 2:
                current.timeline.append({"event": "tag", "value": parts[1]})
            elif cmd == "filter":
                filter_term = " ".join(parts[1:])
            elif cmd == "save" and len(parts) == 2:
                current.name = parts[1]; store.save(current); logs.appendleft("session saved")
            elif cmd == "load" and len(parts) == 2:
                current = store.load(parts[1]); logs.appendleft("session loaded")
            elif cmd == "export" and len(parts) == 3:
                export_session(current, parts[2]); logs.appendleft(f"exported {parts[2]}")
            elif cmd == "graph":
                console.print(Panel(build_relationship_ascii(current.findings), title="ASCII Relationship Graph"))
                console.print(Panel(summarize_findings(current.findings), title="Graph Summary"))
            elif cmd == "system" and len(parts) >= 2 and parts[1] == "status":
                logs.appendleft(str(get_system_status()))
            elif cmd == "network" and len(parts) >= 2 and parts[1] == "status":
                logs.appendleft(str(get_network_status()))
            elif cmd == "device" and len(parts) >= 2 and parts[1] == "info":
                logs.appendleft(str(get_device_info(False)))
            elif cmd == "diagnostics" and len(parts) >= 2 and parts[1] == "run":
                payload = run_diagnostics(enable_lan_discovery=("--lan" in parts))
                diagnostics_summary = payload["summary"]
                logs.appendleft("diagnostics completed")
            else:
                logs.appendleft("unknown command")
        except Exception as exc:
            logs.appendleft(f"error: {exc}")


def main() -> None:
    asyncio.run(repl())
