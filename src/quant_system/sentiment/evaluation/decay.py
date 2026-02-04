# quant_system/sentiment/evaluation/decay.py
import numpy as np
import pandas as pd


class ICDecayEvaluator:
  """
  对 Rolling IC 做时间衰减
  """

  @staticmethod
  def apply_exponential_decay(
    ic_series: pd.Series,
    half_life: int = 10,
  ) -> float:
    """
    half_life: 半衰期
    """
    n = len(ic_series)
    if n == 0:
      return 0.0

    weights = np.exp(-np.log(2) * np.arange(n)[::-1] / half_life)
    weights /= weights.sum()

    return float((ic_series.values * weights).sum())
