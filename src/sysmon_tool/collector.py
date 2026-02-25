from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass
class MetricResult:
    label: str
    value: str
    icon: str
    color: str
    percentage: float | None = None
    unit: str = ""


@runtime_checkable
class Collector(Protocol):
    @property
    def name(self) -> str: ...

    def collect(self) -> MetricResult: ...

    @classmethod
    def available(cls) -> bool: ...
