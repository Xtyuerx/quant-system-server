from quant_system.strategy.signal import SignalType
from quant_system.backtest.result import BacktestResult

class BacktestEngine:
    def __init__(self, prices, signals, symbol, initial_cash=100_000):
        self.prices = prices
        self.signals = signals
        self.symbol = symbol
        self.initial_cash = initial_cash

        self.cash = initial_cash
        self.position = 0.0
        self.equity_curve = []

    def _calc_max_drawdown(self, equity_curve):
        peak = equity_curve[0]
        max_dd = 0.0
        for equity in equity_curve:
            peak = max(peak, equity)
            dd = (equity - peak) / peak
            max_dd = min(max_dd, dd)
        return max_dd

    # 👇 就是它
    def run(self):
        for price, signal in zip(self.prices, self.signals):

            if signal == SignalType.BUY and self.position == 0:
                self.position = self.cash / price
                self.cash = 0.0

            elif signal == SignalType.SELL and self.position > 0:
                self.cash = self.position * price
                self.position = 0.0

            equity = self.cash + self.position * price
            self.equity_curve.append(equity)

        final_equity = self.equity_curve[-1]
        total_return = final_equity / self.initial_cash - 1
        max_dd = self._calc_max_drawdown(self.equity_curve)

        return BacktestResult(
            symbol=self.symbol,
            initial_cash=self.initial_cash,
            final_equity=final_equity,
            equity_curve=self.equity_curve,
        )
