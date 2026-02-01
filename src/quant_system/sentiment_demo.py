import numpy as np

from sentiment.market_sentiment import MarketSentimentModel
from sentiment.ranking import rank_stocks


def fake_market_data():
    """
    模拟指数行情（比如 SP500 / 沪深300）
    """
    close = np.cumsum(np.random.normal(0.1, 1, 200)) + 100
    volume = np.random.randint(1_000_000, 3_000_000, 200)

    return {
        "close": close,
        "volume": volume
    }


def fake_stock_data(trend=0.0):
    """
    模拟单只股票行情
    trend > 0 偏多
    trend < 0 偏空
    """
    close = np.cumsum(np.random.normal(trend, 1, 200)) + 50
    volume = np.random.randint(100_000, 500_000, 200)

    return {
        "close": close,
        "volume": volume
    }


def main():
    # ===== 1️⃣ 市场情绪 =====
    market_model = MarketSentimentModel()
    market_data = fake_market_data()

    market_sentiment = market_model.compute(market_data)

    print("=== Market Sentiment ===")
    print(f"Score : {market_sentiment.score:.3f}")
    print(f"Level : {market_sentiment.level}")
    print(f"Details: {market_sentiment.details}")
    print()

    # ===== 2️⃣ 个股情绪排序 =====
    stock_data_map = {
        "AAPL": fake_stock_data(trend=0.2),
        "MSFT": fake_stock_data(trend=0.1),
        "TSLA": fake_stock_data(trend=-0.3),
        "META": fake_stock_data(trend=0.0),
    }

    ranking = rank_stocks(stock_data_map)

    print("=== Stock Sentiment Ranking ===")
    for symbol, score in ranking:
        print(f"{symbol:5s}  {score:.3f}")


if __name__ == "__main__":
    main()
