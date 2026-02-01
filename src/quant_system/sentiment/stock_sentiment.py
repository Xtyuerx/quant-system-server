from quant_system.sentiment.base import SentimentResult, score_to_level
from quant_system.sentiment.registry import FactorRegistry


class StockSentimentModel:
    """
    个股级情绪模型
    """

    def __init__(self, registry: FactorRegistry | None = None):
        self.registry = registry or FactorRegistry()

    def run(self, data) -> SentimentResult:
        """
        对单只股票计算情绪分数
        """
        scores = {}
        weighted_sum = 0.0
        weight_total = 0.0

        # 关键点：scope = "stock"
        factors = self.registry.get_factors("stock")

        for factor in factors:
            score = factor.compute(data)
            scores[factor.name] = score

            weighted_sum += score * factor.weight
            weight_total += factor.weight

        final_score = weighted_sum / weight_total if weight_total > 0 else 0.0

        return SentimentResult(
            score=final_score,
            level=score_to_level(final_score),
            details=scores,
        )
