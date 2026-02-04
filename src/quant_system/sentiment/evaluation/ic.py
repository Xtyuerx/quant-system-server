import pandas as pd


class ICEvaluator:
  """
  计算单期 IC（Spearman Rank Correlation）
  """

  @staticmethod
  def calc_ic(
    factor: pd.Series,
    future_return: pd.Series,
  ) -> float:
    """
    factor: t 时刻因子值
    future_return: t+1 或 t+n 收益
    """
    df = pd.concat([factor, future_return], axis=1).dropna()
    if len(df) < 2:
      return 0.0

    if df.iloc[:, 0].nunique() < 1:
      return 0.0
    if df.iloc[:, 1].nunique() < 1:
      return 0.0

    # Spearman = rank 后 Pearson
    ic = df.iloc[:, 0].rank().corr(df.iloc[:, 1].rank())
    return float(ic)

  def compute_decayed_ic(
    self,
    factor_values: pd.Series,
    price_series: pd.Series,
    window: int = 20,
    half_life: int = 10,
  ) -> float:
    """
    计算衰减 IC
    """
    # ✅ 在方法内部导入，避免循环依赖
    from quant_system.sentiment.evaluation.rolling_ic import RollingICEvaluator
    from quant_system.sentiment.evaluation.decay import ICDecayEvaluator
    
    # 1️⃣ 计算未来收益
    returns = price_series.pct_change().shift(-1)
    
    # 2️⃣ 转换为 DataFrame 格式
    factor_df = pd.DataFrame({"stock": factor_values})
    return_df = pd.DataFrame({"stock": returns})
    
    # 3️⃣ 滚动计算 IC
    rolling_evaluator = RollingICEvaluator(window=window)
    ic_series = rolling_evaluator.compute(factor_df, return_df)
    
    if len(ic_series) == 0:
      return 0.0
    
    # 4️⃣ 时间衰减
    decayed_ic = ICDecayEvaluator.apply_exponential_decay(
      ic_series, 
      half_life=half_life
    )
    
    return decayed_ic