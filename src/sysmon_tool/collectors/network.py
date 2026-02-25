import time
from pathlib import Path

from ..collector import MetricResult
from ..config import MonitorConfig

_NET_DEV = Path("/proc/net/dev")


def _read_bytes() -> tuple[int, int]:
    """Return (total_rx_bytes, total_tx_bytes) across all non-lo interfaces."""
    rx_total = 0
    tx_total = 0
    for line in _NET_DEV.read_text().splitlines()[2:]:
        iface, _, data = line.partition(":")
        if iface.strip() == "lo":
            continue
        fields = data.split()
        rx_total += int(fields[0])
        tx_total += int(fields[8])
    return rx_total, tx_total


def _human_speed(bps: float) -> str:
    if bps >= 1_000_000:
        return f"{bps / 1_000_000:.1f} MB/s"
    if bps >= 1_000:
        return f"{bps / 1_000:.1f} KB/s"
    return f"{bps:.0f} B/s"


class NetworkCollector:
    def __init__(self, config: MonitorConfig | None = None):
        self._config = config or MonitorConfig()
        self._prev: tuple[int, int, float] | None = None  # rx, tx, timestamp

    @property
    def name(self) -> str:
        return "network"

    @classmethod
    def available(cls) -> bool:
        return _NET_DEV.exists()

    def collect(self) -> MetricResult:
        try:
            rx, tx = _read_bytes()
            now = time.monotonic()

            if self._prev is None:
                self._prev = (rx, tx, now)
                return MetricResult(
                    label="Network",
                    value="measuring...",
                    icon="󰛳",
                    color="dim",
                )

            prev_rx, prev_tx, prev_t = self._prev
            dt = now - prev_t
            if dt <= 0:
                dt = 1.0

            rx_speed = (rx - prev_rx) / dt
            tx_speed = (tx - prev_tx) / dt
            self._prev = (rx, tx, now)

            return MetricResult(
                label="Network",
                value=f"↓ {_human_speed(rx_speed)}  ↑ {_human_speed(tx_speed)}",
                icon="󰛳",
                color="cyan",
            )
        except Exception:
            return MetricResult(
                label="Network", value="Error", icon="󰛳", color="red"
            )
