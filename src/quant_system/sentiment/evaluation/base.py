from abc import ABC, abstractmethod
from typing import Dict, List


class FactorEvaluator(ABC):
  @abstractmethod
  def evaluate(
    self,
    factor_values: List[Dict[str, float]],
    forward_returns: List[Dict[str, float]],
  ) -> dict:
    """
    factor_values[t]: {symbol: factor}
    forward_returns[t]: {symbol: return}
    """
    ...
