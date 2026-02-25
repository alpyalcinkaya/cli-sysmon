import subprocess

from ..collector import MetricResult
from ..config import MonitorConfig


class UpdatesCollector:
    def __init__(self, config: MonitorConfig | None = None):
        self._config = config or MonitorConfig()

    @property
    def name(self) -> str:
        return "updates"

    @classmethod
    def available(cls) -> bool:
        try:
            subprocess.run(
                ["checkupdates"], capture_output=True, timeout=5
            )
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def collect(self) -> MetricResult:
        try:
            result = subprocess.run(
                ["checkupdates"], capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                count = len(result.stdout.splitlines())
            else:
                count = 0

            if count == 0:
                return MetricResult(
                    label="Updates",
                    value="Up to date",
                    icon="󰏔",
                    color="green",
                )

            warn, crit = self._config.update_thresholds
            color = "green" if count < warn else "yellow" if count < crit else "red"
            return MetricResult(
                label="Updates",
                value=f"{count} pending",
                icon="󰏔",
                color=color,
            )
        except Exception:
            return MetricResult(
                label="Updates", value="Error", icon="󰏔", color="red"
            )
