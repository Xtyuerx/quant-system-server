from abc import ABC, abstractmethod
from quant_system.sentiment.factors.registry import FactorRegistry
from quant_system.sentiment.base import SentimentResult


class SentimentModel(ABC):
    def __init__(self, registry: FactorRegistry):
        self.registry = registry

    def run(self, data: dict) -> SentimentResult:
        scores = {}
        weighted_sum = 0.0
        weight_sum = 0.0

        for entry in self.registry.active_factors():
            raw = entry.factor.compute(data)
            scores[entry.factor.name] = raw
            weighted_sum += raw * entry.weight
            weight_sum += entry.weight

        final_score = weighted_sum / weight_sum if weight_sum > 0 else 0.0

        return SentimentResult(
            score=final_score,
            level=self.score_to_level(final_score),
            details=scores,
        )

    @abstractmethod
    def score_to_level(self, score: float) -> str:
        ...
