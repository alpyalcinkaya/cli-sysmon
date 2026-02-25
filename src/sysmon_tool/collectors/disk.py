import subprocess

from ..collector import MetricResult
from ..config import MonitorConfig


class DiskCollector:
    def __init__(self, config: MonitorConfig | None = None):
        self._config = config or MonitorConfig()

    @property
    def name(self) -> str:
        return "disk"

    @classmethod
    def available(cls) -> bool:
        try:
            subprocess.run(["df", "-h", "/"], capture_output=True, check=True)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False

    def collect(self) -> MetricResult:
        try:
            result = subprocess.run(
                ["df", "-h", "/"], capture_output=True, text=True, check=True
            )
            parts = result.stdout.splitlines()[1].split()
            pct = int(parts[4].replace("%", ""))
            used, total = parts[2], parts[1]

            warn, crit = self._config.disk_thresholds
            color = "green" if pct < warn else "yellow" if pct < crit else "red"

            return MetricResult(
                label="Disk",
                value=f"{used} / {total}",
                icon="󰋊",
                color=color,
                percentage=float(pct),
                unit="%",
            )
        except Exception:
            return MetricResult(
                label="Disk", value="Error", icon="󰋊", color="red"
            )
