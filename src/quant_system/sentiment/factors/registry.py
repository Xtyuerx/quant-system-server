from dataclasses import dataclass
from typing import List


@dataclass
class FactorEntry:
    factor: object
    weight: float = 1.0
    enabled: bool = True


class FactorRegistry:
    def __init__(self):
        self._factors: List[FactorEntry] = []

    def register(self, factor, weight: float = 1.0, enabled: bool = True):
        if not hasattr(factor, "compute"):
            raise TypeError("Factor must implement compute(data)")

        if not hasattr(factor, "name"):
            raise TypeError("Factor must have a name attribute")

        self._factors.append(
            FactorEntry(
                factor=factor,
                weight=weight,
                enabled=enabled
            )
        )

    def active_factors(self) -> List[FactorEntry]:
        return [f for f in self._factors if f.enabled]
