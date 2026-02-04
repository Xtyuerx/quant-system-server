# quant_system/sentiment/factor/ma.py

import pandas as pd
from quant_system.sentiment.factors.base import BaseFactor


class MASentimentFactor(BaseFactor):
  """
  MA-based sentiment factor

  factor_t = (price_t - MA_t) / MA_t
  """

  def __init__(self, window: int):
    self.window = window
    self.name = f"ma_sentiment_{window}"

  def compute(self, prices: pd.Series) -> pd.Series:
    """
    prices: pd.Series indexed by time
    return: pd.Series (factor values)
    """
    ma = prices.rolling(self.window).mean()
    factor = (prices - ma) / ma
    return factor
