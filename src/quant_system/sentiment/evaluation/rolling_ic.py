# quant_system/sentiment/evaluation/rolling_ic.py
import pandas as pd
from quant_system.sentiment.evaluation.ic import ICEvaluator


class RollingICEvaluator:
  """
  滚动 IC 计算
  """

  def __init__(self, window: int = 20):
    self.window = window

  def compute(
    self,
    factor_df: pd.DataFrame,
    return_df: pd.DataFrame,
  ) -> pd.Series:
    """
    factor_df / return_df:
    index = date
    columns = symbol
    """
    ic_list = []

    for end in range(self.window, len(factor_df)):
      start = end - self.window

      factor_slice = factor_df.iloc[start:end]
      return_slice = return_df.iloc[start:end]

      ics = []
      for t in range(len(factor_slice)):
        ic = ICEvaluator.calc_ic(
          factor_slice.iloc[t],
          return_slice.iloc[t],
        )
        ics.append(ic)

      # 忽略 NaN
      valid_ics = [ic for ic in ics if not pd.isna(ic)]
      if valid_ics:
        ic_list.append(sum(valid_ics) / len(valid_ics))
      else:
        ic_list.append(0.0)

    return pd.Series(ic_list, index=factor_df.index[self.window:])
