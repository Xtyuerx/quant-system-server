import csv
from pathlib import Path
from typing import List, Tuple


def load_prices_from_csv(filename: str) -> Tuple[List[str], List[float]]:
    dates: List[str] = []
    prices: List[float] = []

    current_dir = Path(__file__).parent
    filepath = current_dir / filename

    with filepath.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            dates.append(row["date"])
            prices.append(float(row["price"]))

    return dates, prices
