from pathlib import Path

from ..collector import MetricResult
from ..config import MonitorConfig

_THERMAL_BASE = Path("/sys/class/thermal")


class TemperatureCollector:
    def __init__(self, config: MonitorConfig | None = None):
        self._config = config or MonitorConfig()

    @property
    def name(self) -> str:
        return "temperature"

    @classmethod
    def available(cls) -> bool:
        return any(_THERMAL_BASE.glob("thermal_zone*/temp"))

    def collect(self) -> MetricResult:
        try:
            temps: list[float] = []
            for zone in sorted(_THERMAL_BASE.glob("thermal_zone*")):
                temp_file = zone / "temp"
                if temp_file.exists():
                    raw = temp_file.read_text().strip()
                    temps.append(int(raw) / 1000.0)

            if not temps:
                return MetricResult(
                    label="Temp", value="N/A", icon="󰔏", color="dim"
                )

            max_temp = max(temps)
            warn, crit = self._config.temp_thresholds
            color = "green" if max_temp < warn else "yellow" if max_temp < crit else "red"

            return MetricResult(
                label="Temp",
                value=f"{max_temp:.0f}°C",
                icon="󰔏",
                color=color,
                percentage=min(max_temp, 100.0),
                unit="°C",
            )
        except Exception:
            return MetricResult(
                label="Temp", value="Error", icon="󰔏", color="red"
            )
