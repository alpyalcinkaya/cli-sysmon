from __future__ import annotations

import platform
import subprocess
from datetime import datetime

from rich.bar import Bar
from rich.columns import Columns
from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .collector import MetricResult

SPARK_CHARS = "▁▂▃▅▇"


def _sparkline(values: list[float], width: int = 20) -> str:
    if not values:
        return ""
    lo = min(values)
    hi = max(values)
    span = hi - lo if hi != lo else 1.0
    return "".join(
        SPARK_CHARS[min(int((v - lo) / span * (len(SPARK_CHARS) - 1)), len(SPARK_CHARS) - 1)]
        for v in values[-width:]
    )


def _color_gradient(pct: float, warn: int = 70, crit: int = 90) -> str:
    if pct < warn:
        return "green"
    if pct < crit:
        return "yellow"
    return "red"


def _get_uptime() -> str:
    try:
        with open("/proc/uptime") as f:
            secs = float(f.read().split()[0])
        hours = int(secs // 3600)
        mins = int((secs % 3600) // 60)
        if hours > 0:
            return f"{hours}h {mins}m"
        return f"{mins}m"
    except Exception:
        return "N/A"


def _get_kernel() -> str:
    return platform.release()


def _get_hostname() -> str:
    return platform.node()


def _build_header() -> Panel:
    info = Text()
    info.append("  ", style="bold cyan")
    info.append(_get_hostname(), style="bold white")
    info.append("  |  ", style="dim")
    info.append("  ", style="bold blue")
    info.append(_get_kernel(), style="white")
    info.append("  |  ", style="dim")
    info.append("󰥔  ", style="bold green")
    info.append(_get_uptime(), style="white")
    return Panel(info, style="blue", title="[bold]System Monitor[/]", title_align="center")


def _build_metric_panel(
    metric: MetricResult,
    history: list[float] | None = None,
) -> Panel:
    content = Table.grid(padding=(0, 1))
    content.add_column(justify="left", min_width=22)
    content.add_column(justify="right", min_width=12)

    value_text = Text(metric.value, style=f"bold {metric.color}")

    if metric.percentage is not None:
        bar = Bar(size=100.0, begin=0, end=metric.percentage, color=metric.color)
        pct_text = Text(f" {metric.percentage:.0f}%", style=f"bold {metric.color}")
        bar_row = Table.grid(padding=0)
        bar_row.add_column(ratio=1)
        bar_row.add_column(justify="right", min_width=5)
        bar_row.add_row(bar, pct_text)
        content.add_row(bar_row, value_text)
    else:
        content.add_row(value_text, Text(""))

    if history:
        spark = _sparkline(history)
        content.add_row(
            Text(spark, style=f"{metric.color}"),
            Text(""),
        )

    title = f"{metric.icon}  {metric.label}"
    return Panel(content, title=f"[bold]{title}[/]", title_align="left", border_style="dim")


def _build_footer(interval: float) -> Panel:
    now = datetime.now().strftime("%H:%M:%S")
    footer = Text()
    footer.append(f"  Refreshing every {interval:.0f}s", style="dim")
    footer.append("  |  ", style="dim")
    footer.append(f"  {now}", style="dim")
    return Panel(footer, style="dim", height=3)


def render(
    metrics: list[MetricResult],
    history: dict[str, list[float]],
    interval: float = 1.0,
) -> RenderableType:
    layout = Table.grid(padding=0)
    layout.add_column(ratio=1)

    # Header
    layout.add_row(_build_header())

    # Metric panels in a 2-column grid
    pairs: list[list[Panel]] = []
    row: list[Panel] = []
    for m in metrics:
        panel = _build_metric_panel(m, history.get(m.label.lower()))
        row.append(panel)
        if len(row) == 2:
            pairs.append(row)
            row = []
    if row:
        pairs.append(row)

    for pair in pairs:
        grid = Table.grid(padding=(0, 1))
        grid.add_column(ratio=1)
        grid.add_column(ratio=1)
        if len(pair) == 2:
            grid.add_row(pair[0], pair[1])
        else:
            grid.add_row(pair[0], Text(""))
        layout.add_row(grid)

    # Footer
    layout.add_row(_build_footer(interval))

    return layout
