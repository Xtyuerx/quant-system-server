from typing import Dict, List, Tuple

from quant_system.sentiment.stock_sentiment import StockSentimentModel


def rank_stocks(
    stock_data_map: Dict[str, dict],
) -> List[Tuple[str, float]]:
    """
    根据情绪分数对股票进行排序

    :param stock_data_map:
        {
            "AAPL": {"close": ..., "volume": ...},
            "MSFT": {"close": ..., "volume": ...},
        }

    :return:
        [
            ("AAPL", 0.72),
            ("MSFT", 0.31),
            ...
        ]
    """
    model = StockSentimentModel()
    results = []

    for symbol, data in stock_data_map.items():
        result = model.run(data)
        results.append((symbol, result.score))

    # 情绪分数从高到低排序
    results.sort(key=lambda x: x[1], reverse=True)

    return results
