import csv
import pandas as pd
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

def load_series_from_csv(
    filename: str,
    column: str = "price",
) -> List[float]:
    values: List[float] = []

    current_dir = Path(__file__).parent
    filepath = current_dir / filename

    with filepath.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        if column not in reader.fieldnames:
            raise ValueError(
                f"CSV 文件缺少 {column} 列，实际列: {reader.fieldnames}"
            )

        for row in reader:
            raw = row[column]
            try:
                values.append(float(raw))
            except ValueError:
                raise ValueError(f"非法 {column} 值: {raw}")

    return values

def load_columns_from_csv(
    filename: str,
    columns: List[str],
) -> dict[str, pd.Series]:  # ✅ 改为返回 pd.Series
    data = {col: [] for col in columns}

    current_dir = Path(__file__).parent
    filepath = current_dir / filename

    with filepath.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        missing = [c for c in columns if c not in reader.fieldnames]
        if missing:
            raise ValueError(f"CSV 缺少列: {missing}")

        for row in reader:
            for col in columns:
                try:
                    data[col].append(float(row[col]))
                except ValueError:
                    raise ValueError(f"非法 {col} 值: {row[col]}")

    # ✅ 转换为 pd.Series
    return {col: pd.Series(values) for col, values in data.items()}