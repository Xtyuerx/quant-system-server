from typing import List, Dict
from quant_system.backtest.simple_backtest import SimpleBacktest
from quant_system.strategy.base_strategy import BaseStrategy

class MultiBacktest:
    """
    多策略、多标的回测框架
    """
    def __init__(self, price_data: Dict[str, List[float]],  # symbol -> price list
                 strategies: Dict[str, BaseStrategy],       # strategy_name -> strategy instance
                 initial_cash: float = 100_000,
                 max_drawdown_limit: float = -0.1):
        self.price_data = price_data
        self.strategies = strategies
        self.initial_cash = initial_cash
        self.max_drawdown_limit = max_drawdown_limit

        # 回测结果存储
        self.results = {}  # symbol -> strategy_name -> SimpleBacktest instance

    def run(self):
        for symbol, prices in self.price_data.items():
            self.results[symbol] = {}
            for strategy_name, strategy in self.strategies.items():
                signals = strategy.generate_signals(prices)
                backtest = SimpleBacktest(prices, signals, initial_cash=self.initial_cash)
                backtest.run(max_drawdown_limit=self.max_drawdown_limit)
                self.results[symbol][strategy_name] = backtest
        return self.results
