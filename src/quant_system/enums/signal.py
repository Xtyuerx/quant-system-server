from quant_system.backtest.signal import SignalType

def sentiment_to_signal(sentiment: float) -> SignalType:
    if sentiment > 0.3:
        return SignalType.BUY
    elif sentiment < -0.3:
        return SignalType.EXIT
    else:
        return SignalType.HOLD