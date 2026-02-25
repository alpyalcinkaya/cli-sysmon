import time

from rich.console import Console
from rich.live import Live

from .collectors import ALL_COLLECTORS
from .config import MonitorConfig
from .display import render
from .usage_tracker import UsageTracker


def main() -> None:
    config = MonitorConfig()
    console = Console()
    tracker = UsageTracker(max_size=config.history_size)

    # Auto-discover available collectors
    active = []
    for cls in ALL_COLLECTORS:
        try:
            if cls.available():
                active.append(cls(config))
        except Exception:
            pass

    if not active:
        console.print("[bold red]No collectors available.[/]")
        return

    console.print(f"[dim]Starting with {len(active)} collectors...[/]")

    with Live(console=console, refresh_per_second=2, screen=False) as live:
        try:
            while True:
                metrics = []
                for collector in active:
                    result = collector.collect()
                    metrics.append(result)
                    if result.percentage is not None:
                        tracker.record(result.label.lower(), result.percentage)

                dashboard = render(metrics, tracker.all_history(), config.refresh_interval)
                live.update(dashboard)
                time.sleep(config.refresh_interval)
        except KeyboardInterrupt:
            pass

    console.print("\n[bold yellow]Exiting Monitor...[/]")


if __name__ == "__main__":
    main()
