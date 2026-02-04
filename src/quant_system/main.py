import random
from quant_system.data.price_feed import load_columns_from_csv
from quant_system.sentiment.engine.sentiment_engine import SentimentEngine

def load_data(csv_path: str):
    data = load_columns_from_csv(csv_path, ["close", "sentiment"])
    return data["close"], data["sentiment"]

def main():
    prices, sentiment = load_data("AAPL.csv")

    engine = SentimentEngine(
        factor_window=3,
        ic_window=5,
    )

    signal = engine.compute_signal(
        price_series=prices,
        sentiment_series=sentiment,
    )

    print("Sentiment Signal:", signal)

if __name__ == "__main__":
    main()
