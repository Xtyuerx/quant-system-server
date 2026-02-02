class BacktestEngine:
    def __init__(
        self,
        prices: list[float],
        signals: list,
        symbol: str,
        initial_cash: float = 100_000,
    ):
        self.prices = prices
        self.signals = signals
        self.symbol = symbol

        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.position = 0.0  # 持有股数（必须是 float）

    def run(self) -> list[float]:
        """
        E6：执行回测，返回资金曲线（equity_curve）
        """
        equity_curve: list[float] = []

        for i, price in enumerate(self.prices):
            signal = self.signals[i]

            # 买入：全仓
            if signal.name == "BUY" and self.position == 0:
                self.position = self.cash / price
                self.cash = 0.0

            # 卖出：清仓
            elif signal.name == "SELL" and self.position > 0:
                self.cash = self.position * price
                self.position = 0.0

            # 当前总资产
            equity = self.cash + self.position * price
            equity_curve.append(equity)

        return equity_curve
