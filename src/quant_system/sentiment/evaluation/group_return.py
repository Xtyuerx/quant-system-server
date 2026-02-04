import numpy as np
from quant_system.sentiment.evaluation.base import FactorEvaluator


class GroupReturnEvaluator(FactorEvaluator):
  def __init__(self, groups: int = 5):
    self.groups = groups

  def evaluate(self, factor_values, forward_returns):
    group_returns = [[] for _ in range(self.groups)]

    for fv, fr in zip(factor_values, forward_returns):
      ranked = sorted(fv.items(), key=lambda x: x[1])
      n = len(ranked)
      if n < self.groups:
        continue

      size = n // self.groups

      for i in range(self.groups):
        bucket = ranked[i * size:(i + 1) * size]
        rets = [fr[s] for s, _ in bucket if s in fr]
        if rets:
          group_returns[i].append(sum(rets) / len(rets))

    return {
      f"group_{i}_mean": float(np.mean(group_returns[i]))
      for i in range(self.groups)
    }
