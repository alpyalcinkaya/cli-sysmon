import subprocess
import time

from .updater import PackageUpdater 

from rich.live import Live
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.columns import Columns

class SystemMonitor:
    def __init__(self):
        self.console = Console()
        self.updater = PackageUpdater() 

    def get_disk_usage(self):
        """Fetches disk usage and returns a status dict."""
        try:
            result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True, check=True)
            usage_line = result.stdout.splitlines()[1].split()
            usage_pct = int(usage_line[4].replace('%', ''))
            
            color = "green" if usage_pct < 80 else "yellow" if usage_pct < 95 else "red"
            return {"label": "Disk", "value": f"{usage_pct}%", "color": color}

        except Exception:
            return {"label": "Disk", "value": "Error", "color": "red"}

    def get_memory_usage(self):
        """Fetches memory usage and returns a status dict."""
        try:
            result = subprocess.run(['free', '-m'], capture_output=True, text=True)
            mem_info = result.stdout.splitlines()[1].split()
            total, available = int(mem_info[1]), int(mem_info[6])
            usage_pct = 100 * (1 - (available / total))
            
            color = "green" if usage_pct < 70 else "yellow" if usage_pct < 90 else "red"
            return {"label": "Memory", "value": f"{usage_pct:.1f}%", "color": color}

        except Exception:
            return {"label": "Memory", "value": "Error", "color": "red"}

    def generate_dashboard(self):
        """Generates the UI components without printing them yet."""
        disk = self.get_disk_usage()
        mem = self.get_memory_usage()
        updates = self.updater.get_status()

        disk_panel = Panel(f"[bold {disk['color']}]{disk['value']}[/]", title="Disk")
        mem_panel = Panel(f"[bold {mem['color']}]{mem['value']}[/]", title="Memory")
        update_panel = Panel(f"[bold {updates['color']}]{updates['message']}[/]", title="Updates")

        return Columns([disk_panel, mem_panel, update_panel])

    def run_live(self):
        """Starts the live updating dashboard."""
        with Live(self.generate_dashboard(), console=self.console, refresh_per_second=1) as live:
            try:
                while True:
                    time.sleep(1)
                    # Update the 'Live' display with a fresh dashboard
                    live.update(self.generate_dashboard())
            except KeyboardInterrupt:
                # Handle Ctrl+C gracefully
                self.console.print("\n[bold yellow]Exiting Monitor...[/]")


def main():
    """Entry point for the CLI tool."""
    monitor = SystemMonitor()
    monitor.run_live()

if __name__ == "__main__":
    main()
