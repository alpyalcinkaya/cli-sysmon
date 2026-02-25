from dataclasses import dataclass, field


@dataclass
class MonitorConfig:
    refresh_interval: float = 1.0
    history_size: int = 20

    # (warn_threshold, crit_threshold) as percentages
    disk_thresholds: tuple[int, int] = (80, 95)
    memory_thresholds: tuple[int, int] = (70, 90)
    cpu_thresholds: tuple[int, int] = (70, 90)
    temp_thresholds: tuple[int, int] = (70, 90)

    # Update count thresholds
    update_thresholds: tuple[int, int] = (20, 100)

    # Network speed thresholds in MB/s
    network_thresholds: tuple[int, int] = (50, 100)
