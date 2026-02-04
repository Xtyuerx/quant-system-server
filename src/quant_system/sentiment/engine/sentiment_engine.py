from quant_system.sentiment.factors.ma import MASentimentFactor
from quant_system.sentiment.evaluation.ic import ICEvaluator
from quant_system.sentiment.evaluation.ic_weight import ic_to_weight


class SentimentEngine:
  def __init__(self, factor_window=5, ic_window=20):
    self.factor_window = factor_window
    self.ic_window = ic_window
    self.evaluator = ICEvaluator()  # ✅ 无参构造，和你现有实现一致

  def compute_signal(self, price_series, sentiment_series):
    """
    返回一个可以直接用于主线策略的情绪 signal
    """

    # 1️⃣ 计算情绪因子
    factor = MASentimentFactor(window=self.factor_window)
    factor_values = factor.compute(sentiment_series)
    latest_factor_value = factor_values.iloc[-1]

    # 2️⃣ 计算衰减 IC（E11-3 的成果）
    decayed_ic = self.evaluator.compute_decayed_ic(
      factor_values=factor_values,
      price_series=price_series,
      window=self.ic_window
    )

    # 3️⃣ IC → 权重
    weight = ic_to_weight(decayed_ic)

    # 4️⃣ 主线最终信号
    final_signal = latest_factor_value * weight

    return final_signal
