import time
from pathlib import Path

from ..collector import MetricResult
from ..config import MonitorConfig

_STAT_PATH = Path("/proc/stat")


def _read_cpu_times() -> tuple[int, int]:
    line = _STAT_PATH.read_text().splitlines()[0]  # "cpu ..."
    fields = list(map(int, line.split()[1:]))
    idle = fields[3] + fields[4]  # idle + iowait
    total = sum(fields)
    return idle, total


class CpuCollector:
    def __init__(self, config: MonitorConfig | None = None):
        self._config = config or MonitorConfig()

    @property
    def name(self) -> str:
        return "cpu"

    @classmethod
    def available(cls) -> bool:
        return _STAT_PATH.exists()

    def collect(self) -> MetricResult:
        try:
            idle1, total1 = _read_cpu_times()
            time.sleep(0.1)
            idle2, total2 = _read_cpu_times()

            d_idle = idle2 - idle1
            d_total = total2 - total1
            pct = 100.0 * (1 - d_idle / d_total) if d_total else 0.0
            pct = round(pct, 1)

            warn, crit = self._config.cpu_thresholds
            color = "green" if pct < warn else "yellow" if pct < crit else "red"

            return MetricResult(
                label="CPU",
                value=f"{pct}%",
                icon="󰻠",
                color=color,
                percentage=pct,
                unit="%",
            )
        except Exception:
            return MetricResult(
                label="CPU", value="Error", icon="󰻠", color="red"
            )
