import csv
from pathlib import Path
from typing import List


def load_prices_from_csv(filename: str) -> List[float]:
    prices: List[float] = []

    current_dir = Path(__file__).parent
    filepath = current_dir / filename

    with filepath.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        if "price" not in reader.fieldnames:
            raise ValueError(f"CSV 文件缺少 price 列，实际列: {reader.fieldnames}")

        for row in reader:
            raw_price = row["price"]

            try:
                prices.append(float(raw_price))
            except ValueError:
                raise ValueError(f"非法 price 值: {raw_price}")

    return prices
