from typing import List
from quant_system.enums.signal import Signal


class SimpleBacktest:
    def __init__(
        self,
        prices: List[float],
        signals: List[Signal],
        initial_cash: float = 100_000,
    ):
        self.prices = prices
        self.signals = signals
        self.initial_cash = initial_cash

        self.cash = initial_cash
        self.position = 0.0
        self.equity_curve = []

    def run(self, max_drawdown_limit: float = -0.1):
        peak_equity = self.initial_cash

        for i, price in enumerate(self.prices):
            signal = self.signals[i]

            # === 正常交易逻辑 ===
            if signal == Signal.LONG and self.position == 0:
                self.position = self.cash / price
                self.cash = 0.0

            elif signal == Signal.FLAT and self.position > 0:
                self.cash = self.position * price
                self.position = 0.0

            equity = self.cash + self.position * price
            self.equity_curve.append(equity)

            # === 风控：最大回撤止损 ===
            if equity > peak_equity:
                peak_equity = equity

            drawdown = (equity / peak_equity) - 1
            if drawdown <= max_drawdown_limit and self.position > 0:
                # 强制平仓
                self.cash = self.position * price
                self.position = 0.0

        return self.equity_curve
