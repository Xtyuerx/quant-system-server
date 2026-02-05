from abc import ABC, abstractmethod
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Callable

@dataclass
class BarData:
    """K线数据"""
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

@dataclass  
class TickData:
    """Tick级数据"""
    symbol: str
    timestamp: datetime
    last_price: float
    bid_price: float
    ask_price: float
    bid_volume: int
    ask_volume: int
    volume: int

class LiveDataFeed(ABC):
    """实时数据源基类"""
    
    @abstractmethod
    def subscribe(self, symbols: list[str]):
        """订阅行情"""
        pass
    
    @abstractmethod
    def on_bar(self, callback: Callable[[BarData], None]):
        """K线回调"""
        pass
    
    @abstractmethod
    def on_tick(self, callback: Callable[[TickData], None]):
        """Tick回调"""
        pass
    
    @abstractmethod
    def start(self):
        """启动数据流"""
        pass
    
    @abstractmethod
    def stop(self):
        """停止数据流"""
        pass


class TushareDataFeed(LiveDataFeed):
    """Tushare数据源（适合A股）"""
    
    def __init__(self, token: str):
        import tushare as ts
        self.pro = ts.pro_api(token)
        self.symbols = []
        self._callbacks = []
    
    def subscribe(self, symbols: list[str]):
        self.symbols = symbols
    
    def on_bar(self, callback):
        self._callbacks.append(callback)
    
    def start(self):
        """轮询模式获取实时数据"""
        import time
        while True:
            for symbol in self.symbols:
                # 获取最新数据
                df = self.pro.daily(ts_code=symbol, 
                                   start_date='20240101')
                if not df.empty:
                    bar = BarData(
                        symbol=symbol,
                        timestamp=datetime.now(),
                        open=df.iloc[-1]['open'],
                        high=df.iloc[-1]['high'],
                        low=df.iloc[-1]['low'],
                        close=df.iloc[-1]['close'],
                        volume=df.iloc[-1]['vol']
                    )
                    for callback in self._callbacks:
                        callback(bar)
            
            time.sleep(60)  # 每分钟更新


class AKShareDataFeed(LiveDataFeed):
    """AKShare数据源（免费）"""
    pass


class AlpacaDataFeed(LiveDataFeed):
    """Alpaca数据源（美股）"""
    pass