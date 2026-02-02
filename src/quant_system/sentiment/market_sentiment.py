import numpy as np
from collections import Counter
from quant_system.backtest.signal import Signal, SignalType
from typing import List


class MarketSentiment:
    """
    基于动量 + 波动率的市场情绪模型
    """

    def __init__(
        self,
        momentum_window: int = 10,
        volatility_window: int = 10,
        long_threshold: float = 0.005,
        short_threshold: float = -0.005,
        ma_window: int = 5,
    ):
        self.momentum_window = momentum_window
        self.volatility_window = volatility_window
        self.long_threshold = long_threshold
        self.short_threshold = short_threshold
        self.ma_window = ma_window

    # 动量
    def _momentum(self, prices: np.ndarray) -> np.ndarray:
        momentum = np.zeros(len(prices))
        for i in range(self.momentum_window, len(prices)):
            momentum[i] = prices[i] / prices[i - self.momentum_window] - 1
        return momentum

    # 波动率
    def _volatility(self, prices: np.ndarray) -> np.ndarray:
        returns = np.diff(prices) / prices[:-1]
        vol = np.zeros(len(prices))
        for i in range(self.volatility_window, len(prices)):
            vol[i] = np.std(returns[i - self.volatility_window : i])
        return vol
    
    # 情绪值
    def calculate_sentiment(self, prices: list[float]) -> list[float]:
        """
        使用对数收益率作为情绪值
        """
        sentiment = [0.0]

        for i in range(1, len(prices)):
            prev = prices[i - 1]
            curr = prices[i]

            if prev == 0:
                sentiment.append(0.0)
                continue

            ret = (curr - prev) / prev
            sentiment.append(ret)

        return sentiment
    
    # 情绪均线
    def moving_average(self, values: list[float], window: int) -> list[float]:
        ma = []
        for i in range(len(values)):
            if i < window - 1:
                ma.append(0.0)
            else:
                ma.append(sum(values[i - window + 1:i + 1]) / window)
        return ma

    # 生成信号
    def generate_signals(self, prices: List[float]) -> List[Signal]:
        sentiment = self.calculate_sentiment(prices)
        # 情绪均线
        sentiment_ma = self.moving_average(sentiment, self.ma_window)

        signals: list[Signal] = []

        for score in sentiment_ma:
            if score > self.long_threshold:
                signals.append(Signal(SignalType.BUY))
            elif score < self.short_threshold:
                signals.append(Signal(SignalType.SELL))
            else:
                signals.append(Signal(SignalType.HOLD))

        # 🔍 调试用：看信号分布
        print("Signal stats:", Counter(s.type for s in signals))

        return signals
