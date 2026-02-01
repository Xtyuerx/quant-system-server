import argparse
import numpy as np

from quant_system.sentiment.market_sentiment import MarketSentimentModel
from quant_system.sentiment.ranking import rank_stocks


# ======================
# Fake data（现在阶段只做观测）
# 后面可替换为 AKShare / IB / Binance
# ======================

def fake_market_data():
    close = np.cumsum(np.random.normal(0.05, 1, 200)) + 100
    close = np.clip(close, 1, None)
    volume = np.random.randint(1_000_000, 3_000_000, 200)

    return {
        "close": close,
        "volume": volume
    }

def fake_stock_data(trend=0.0):
    close = np.cumsum(np.random.normal(trend, 1, 200)) + 50
    close = np.clip(close, 1, None)
    volume = np.random.randint(100_000, 500_000, 200)

    return {
        "close": close,
        "volume": volume
    }


# ======================
# CLI Commands
# ======================

def cmd_market():
    model = MarketSentimentModel()
    data = fake_market_data()
    result = model.run(data)

    print("\n=== Market Sentiment ===")
    print(f"Score : {result.score:.3f}")
    print(f"Level : {result.level}")
    print("Details:")
    for k, v in result.details.items():
        print(f"  {k:12s}: {v:.3f}")

    print("\nSlogan:")
    if result.level == "fear":
        print("👉 别人恐惧，我贪婪")
    elif result.level == "greed":
        print("👉 别人贪婪，我恐惧")
    else:
        print("👉 保持耐心，等待机会")


def cmd_rank(top_n: int):
    stock_data_map = {
        "AAPL": fake_stock_data(trend=0.2),
        "MSFT": fake_stock_data(trend=0.1),
        "META": fake_stock_data(trend=0.0),
        "TSLA": fake_stock_data(trend=-0.3),
        "NFLX": fake_stock_data(trend=-0.1),
    }

    ranking = rank_stocks(stock_data_map)

    print("\n=== Stock Sentiment Ranking ===")
    for i, (symbol, score) in enumerate(ranking[:top_n], 1):
        print(f"{i:02d}. {symbol:5s}  {score:.3f}")


# ======================
# Main
# ======================

def main():
    parser = argparse.ArgumentParser(
        description="Market Sentiment CLI"
    )

    subparsers = parser.add_subparsers(dest="command")

    # market
    subparsers.add_parser(
        "market",
        help="Show overall market sentiment"
    )

    # rank
    rank_parser = subparsers.add_parser(
        "rank",
        help="Rank stocks by sentiment"
    )
    rank_parser.add_argument(
        "--top",
        type=int,
        default=5,
        help="Top N stocks"
    )

    args = parser.parse_args()

    if args.command == "market":
        cmd_market()
    elif args.command == "rank":
        cmd_rank(args.top)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
