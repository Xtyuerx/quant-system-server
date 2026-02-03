from typing import Dict, List
from quant_system.sentiment.factor.base import Factor
from quant_system.backtest.result import BacktestResult


class FactorBacktestRunner:
  def __init__(
    self,
    prices: Dict[str, List[float]],
    factor: Factor,
    initial_cash: float = 100_000,
  ):
    self.prices = prices
    self.factor = factor
    self.initial_cash = initial_cash

  def run(self) -> BacktestResult:
    equity = self.initial_cash
    equity_curve = [equity]

    symbols = list(self.prices.keys())
    T = len(next(iter(self.prices.values())))

    for t in range(1, T - 1):
      factor_values = self.factor.compute(self.prices, t)
      if not factor_values:
        equity_curve.append(equity)
        continue

      ranked = sorted(
        factor_values.items(),
        key=lambda x: x[1],
        reverse=True
      )

      top_n = max(1, len(ranked) // 2)
      longs = [s for s, _ in ranked[:top_n]]

      returns = []
      for s in longs:
        p0 = self.prices[s][t]
        p1 = self.prices[s][t + 1]
        returns.append(p1 / p0 - 1)

      if returns:
        equity *= (1 + sum(returns) / len(returns))

      equity_curve.append(equity)

    return BacktestResult(
      symbol="FACTOR_PORTFOLIO",
      initial_cash=self.initial_cash,
      final_equity=equity_curve[-1],
      equity_curve=equity_curve,
      params={
        "factor": self.factor.__class__.__name__,
      },
    )
