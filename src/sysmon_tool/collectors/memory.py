import subprocess

from ..collector import MetricResult
from ..config import MonitorConfig


class MemoryCollector:
    def __init__(self, config: MonitorConfig | None = None):
        self._config = config or MonitorConfig()

    @property
    def name(self) -> str:
        return "memory"

    @classmethod
    def available(cls) -> bool:
        try:
            subprocess.run(["free", "-m"], capture_output=True, check=True)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False

    def collect(self) -> MetricResult:
        try:
            result = subprocess.run(
                ["free", "-m"], capture_output=True, text=True, check=True
            )
            parts = result.stdout.splitlines()[1].split()
            total = int(parts[1])
            available = int(parts[6])
            used = total - available
            pct = 100.0 * (1 - available / total)

            warn, crit = self._config.memory_thresholds
            color = "green" if pct < warn else "yellow" if pct < crit else "red"

            return MetricResult(
                label="Memory",
                value=f"{used}M / {total}M",
                icon="󰍛",
                color=color,
                percentage=round(pct, 1),
                unit="%",
            )
        except Exception:
            return MetricResult(
                label="Memory", value="Error", icon="󰍛", color="red"
            )
