from .cpu import CpuCollector
from .disk import DiskCollector
from .memory import MemoryCollector
from .network import NetworkCollector
from .temperature import TemperatureCollector
from .updates import UpdatesCollector

ALL_COLLECTORS = [
    DiskCollector,
    MemoryCollector,
    CpuCollector,
    NetworkCollector,
    TemperatureCollector,
    UpdatesCollector,
]
