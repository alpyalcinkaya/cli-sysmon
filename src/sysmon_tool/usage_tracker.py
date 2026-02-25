from collections import deque


class UsageTracker:
    def __init__(self, max_size: int = 20):
        self._max_size = max_size
        self._data: dict[str, deque[float]] = {}

    def record(self, name: str, value: float) -> None:
        if name not in self._data:
            self._data[name] = deque(maxlen=self._max_size)
        self._data[name].append(value)

    def get_history(self, name: str) -> list[float]:
        if name in self._data:
            return list(self._data[name])
        return []

    def all_history(self) -> dict[str, list[float]]:
        return {k: list(v) for k, v in self._data.items()}
