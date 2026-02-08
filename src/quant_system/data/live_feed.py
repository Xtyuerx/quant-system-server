from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional, Callable, List
import time
import threading

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


class AKShareDataFeed(LiveDataFeed):
    """
    AKShare数据源（免费、推荐）
    
    特点：
    - 完全免费
    - 支持A股实时行情
    - 无需token
    
    使用示例：
        feed = AKShareDataFeed(interval=60)  # 每60秒更新
        feed.subscribe(['000001', '600519'])
        feed.on_bar(my_callback)
        feed.start()
    """
    
    def __init__(self, interval: int = 60):
        """
        Args:
            interval: 更新间隔（秒），默认60秒
        """
        self.interval = interval
        self.symbols: List[str] = []
        self._bar_callbacks: List[Callable] = []
        self._tick_callbacks: List[Callable] = []
        self._is_running = False
        self._thread: Optional[threading.Thread] = None
    
    def subscribe(self, symbols: list[str]):
        """订阅股票代码（6位数字，如 '000001', '600519'）"""
        self.symbols = symbols
        print(f"📡 订阅股票: {', '.join(symbols)}")
    
    def on_bar(self, callback: Callable[[BarData], None]):
        """注册K线回调函数"""
        self._bar_callbacks.append(callback)
    
    def on_tick(self, callback: Callable[[TickData], None]):
        """注册Tick回调函数"""
        self._tick_callbacks.append(callback)
    
    def start(self):
        """启动数据流（后台线程）"""
        if self._is_running:
            print("⚠️ 数据流已在运行")
            return
        
        self._is_running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        print("🚀 AKShare数据流已启动")
    
    def stop(self):
        """停止数据流"""
        self._is_running = False
        if self._thread:
            self._thread.join(timeout=5)
        print("⏹️ AKShare数据流已停止")
    
    def _run_loop(self):
        """数据获取循环"""
        while self._is_running:
            try:
                self._fetch_and_broadcast()
            except Exception as e:
                print(f"❌ 数据获取失败: {e}")
            
            time.sleep(self.interval)
    
    def _fetch_and_broadcast(self):
        """获取并广播数据"""
        try:
            import akshare as ak
        except ImportError:
            print("❌ 请安装 akshare: pip install akshare")
            self.stop()
            return
        
        for symbol in self.symbols:
            try:
                # 获取实时行情
                df = ak.stock_zh_a_spot_em()
                
                # 查找对应股票
                stock_data = df[df['代码'] == symbol]
                
                if stock_data.empty:
                    print(f"⚠️ 未找到股票 {symbol}")
                    continue
                
                row = stock_data.iloc[0]
                
                # 构造BarData
                bar = BarData(
                    symbol=symbol,
                    timestamp=datetime.now(),
                    open=float(row['今开']),
                    high=float(row['最高']),
                    low=float(row['最低']),
                    close=float(row['最新价']),
                    volume=float(row['成交量'])
                )
                
                # 广播给所有回调
                for callback in self._bar_callbacks:
                    callback(bar)
                
            except Exception as e:
                print(f"❌ 获取 {symbol} 行情失败: {e}")


class HistoricalSimulator(LiveDataFeed):
    """
    历史数据模拟器（用于测试）
    
    用历史数据模拟实时数据流，方便测试策略
    """
    
    def __init__(self, prices: list[float], symbol: str = "TEST", speed: float = 1.0):
        """
        Args:
            prices: 历史价格序列
            symbol: 股票代码
            speed: 播放速度（1.0=正常，2.0=2倍速）
        """
        self.prices = prices
        self.symbol = symbol
        self.speed = speed
        
        self._bar_callbacks: List[Callable] = []
        self._is_running = False
        self._thread: Optional[threading.Thread] = None
    
    def subscribe(self, symbols: list[str]):
        """模拟器忽略订阅"""
        pass
    
    def on_bar(self, callback: Callable[[BarData], None]):
        self._bar_callbacks.append(callback)
    
    def on_tick(self, callback: Callable[[TickData], None]):
        pass
    
    def start(self):
        """启动历史回放"""
        self._is_running = True
        self._thread = threading.Thread(target=self._replay, daemon=True)
        self._thread.start()
        print(f"🎬 历史数据回放已启动 (共 {len(self.prices)} 条)")
    
    def stop(self):
        self._is_running = False
        if self._thread:
            self._thread.join(timeout=5)
        print("⏹️ 历史回放已停止")
    
    def _replay(self):
        """回放历史数据"""
        start_time = datetime.now()
        
        for i, price in enumerate(self.prices):
            if not self._is_running:
                break
            
            # 模拟OHLC（简化处理）
            bar = BarData(
                symbol=self.symbol,
                timestamp=start_time + timedelta(days=i),
                open=price * 0.995,
                high=price * 1.01,
                low=price * 0.99,
                close=price,
                volume=1000000
            )
            
            for callback in self._bar_callbacks:
                callback(bar)
            
            # 控制速度
            time.sleep(1.0 / self.speed)


class TushareDataFeed(LiveDataFeed):
    """Tushare数据源（需要token）"""
    
    def __init__(self, token: str, interval: int = 60):
        try:
            import tushare as ts
            self.pro = ts.pro_api(token)
        except ImportError:
            raise ImportError("请安装 tushare: pip install tushare")
        
        self.interval = interval
        self.symbols: List[str] = []
        self._bar_callbacks: List[Callable] = []
        self._is_running = False
        self._thread: Optional[threading.Thread] = None
    
    def subscribe(self, symbols: list[str]):
        """订阅股票代码（Tushare格式，如 '000001.SZ'）"""
        self.symbols = symbols
    
    def on_bar(self, callback):
        self._bar_callbacks.append(callback)
    
    def on_tick(self, callback):
        pass
    
    def start(self):
        self._is_running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        print("🚀 Tushare数据流已启动")
    
    def stop(self):
        self._is_running = False
        if self._thread:
            self._thread.join(timeout=5)
        print("⏹️ Tushare数据流已停止")
    
    def _run_loop(self):
        while self._is_running:
            try:
                self._fetch_and_broadcast()
            except Exception as e:
                print(f"❌ 数据获取失败: {e}")
            
            time.sleep(self.interval)
    
    def _fetch_and_broadcast(self):
        for symbol in self.symbols:
            try:
                # 获取最新日线数据
                today = datetime.now().strftime('%Y%m%d')
                df = self.pro.daily(ts_code=symbol, start_date=today, end_date=today)
                
                if df.empty:
                    continue
                
                row = df.iloc[0]
                bar = BarData(
                    symbol=symbol,
                    timestamp=datetime.now(),
                    open=float(row['open']),
                    high=float(row['high']),
                    low=float(row['low']),
                    close=float(row['close']),
                    volume=float(row['vol'])
                )
                
                for callback in self._bar_callbacks:
                    callback(bar)
                
            except Exception as e:
                print(f"❌ 获取 {symbol} 行情失败: {e}")
                
class CSVReplayFeed(LiveDataFeed):
    """
    CSV文件回放数据源（最稳定，推荐用于开发测试）
    
    特点：
    - 完全离线，无需网络
    - 支持完整OHLCV数据
    - 可控回放速度
    - 适合策略开发和测试
    
    使用示例：
        feed = CSVReplayFeed(
            csv_path="data/AAPL.csv",
            symbol="AAPL",
            speed=10.0  # 10倍速
        )
        feed.on_bar(callback)
        feed.start()
    """
    
    def __init__(self, csv_path: str, symbol: str, speed: float = 1.0, loop: bool = False):
        """
        Args:
            csv_path: CSV文件路径
            symbol: 股票代码
            speed: 回放速度倍数（1.0=实时，10.0=10倍速）
            loop: 是否循环播放
        """
        self.csv_path = csv_path
        self.symbol = symbol
        self.speed = speed
        self.loop = loop
        
        self._bar_callbacks: List[Callable] = []
        self._is_running = False
        self._thread: Optional[threading.Thread] = None
        self._bars: List[BarData] = []
        
        # 加载数据
        self._load_data()
    
    def _load_data(self):
        """加载CSV数据"""
        try:
            import pandas as pd
            from pathlib import Path
            
            # 支持相对路径
            if not Path(self.csv_path).is_absolute():
                base_path = Path(__file__).parent
                csv_path = base_path / self.csv_path
            else:
                csv_path = Path(self.csv_path)
            
            if not csv_path.exists():
                raise FileNotFoundError(f"CSV文件不存在: {csv_path}")
            
            df = pd.read_csv(csv_path)
            
            # 尝试不同的列名组合
            column_mapping = {
                'date': ['date', 'Date', 'datetime', 'timestamp'],
                'open': ['open', 'Open', 'price'],
                'high': ['high', 'High', 'price'],
                'low': ['low', 'Low', 'price'],
                'close': ['close', 'Close', 'price'],
                'volume': ['volume', 'Volume', 'vol']
            }
            
            # 找到实际列名
            actual_columns = {}
            for key, possible_names in column_mapping.items():
                for name in possible_names:
                    if name in df.columns:
                        actual_columns[key] = name
                        break
                if key not in actual_columns and key != 'date':
                    # 如果没有找到且不是date，使用默认值
                    actual_columns[key] = possible_names[0]
            
            # 解析日期
            if 'date' in actual_columns:
                df['parsed_date'] = pd.to_datetime(df[actual_columns['date']])
            else:
                # 如果没有日期列，生成日期
                df['parsed_date'] = pd.date_range(
                    start=datetime.now() - timedelta(days=len(df)),
                    periods=len(df),
                    freq='D'
                )
            
            # 构造BarData列表
            for _, row in df.iterrows():
                try:
                    bar = BarData(
                        symbol=self.symbol,
                        timestamp=row['parsed_date'],
                        open=float(row.get(actual_columns.get('open', 'open'), 0)),
                        high=float(row.get(actual_columns.get('high', 'high'), 0)),
                        low=float(row.get(actual_columns.get('low', 'low'), 0)),
                        close=float(row.get(actual_columns.get('close', 'close'), 0)),
                        volume=float(row.get(actual_columns.get('volume', 'volume'), 1000000))
                    )
                    self._bars.append(bar)
                except Exception as e:
                    print(f"⚠️ 跳过无效数据行: {e}")
                    continue
            
            print(f"✅ 加载了 {len(self._bars)} 条历史数据 from {csv_path}")
            
            if len(self._bars) == 0:
                raise ValueError("没有有效的数据")
            
        except Exception as e:
            print(f"❌ 加载CSV失败: {e}")
            # 降级：使用简单的price_feed
            try:
                from .price_feed import load_prices_from_csv
                prices = load_prices_from_csv(Path(self.csv_path).name)
                
                self._bars = []
                base_time = datetime.now() - timedelta(days=len(prices))
                for i, price in enumerate(prices):
                    bar = BarData(
                        symbol=self.symbol,
                        timestamp=base_time + timedelta(days=i),
                        open=price * 0.995,
                        high=price * 1.01,
                        low=price * 0.99,
                        close=price,
                        volume=1000000
                    )
                    self._bars.append(bar)
                
                print(f"✅ 使用降级方案加载了 {len(self._bars)} 条数据")
            except Exception as e2:
                print(f"❌ 降级方案也失败: {e2}")
                raise
    
    def subscribe(self, symbols: list[str]):
        """CSV回放器忽略订阅"""
        pass
    
    def on_bar(self, callback: Callable[[BarData], None]):
        self._bar_callbacks.append(callback)
    
    def on_tick(self, callback):
        pass
    
    def start(self):
        """启动回放"""
        if not self._bars:
            print("❌ 没有数据可以回放")
            return
        
        self._is_running = True
        self._thread = threading.Thread(target=self._replay, daemon=True)
        self._thread.start()
        print(f"🎬 CSV回放已启动: {len(self._bars)} 条数据, {self.speed}x 速度")
    
    def stop(self):
        """停止回放"""
        self._is_running = False
        if self._thread:
            self._thread.join(timeout=5)
        print("⏹️ CSV回放已停止")
    
    def _replay(self):
        """回放数据"""
        while True:
            for i, bar in enumerate(self._bars):
                if not self._is_running:
                    return
                
                # 显示进度
                if i % 10 == 0:
                    progress = (i + 1) / len(self._bars) * 100
                    print(f"📊 回放进度: {i+1}/{len(self._bars)} ({progress:.1f}%)")
                
                # 广播数据
                for callback in self._bar_callbacks:
                    try:
                        callback(bar)
                    except Exception as e:
                        print(f"❌ 回调函数错误: {e}")
                
                # 控制速度
                time.sleep(1.0 / self.speed)
            
            # 是否循环
            if not self.loop:
                print("✅ 回放完成")
                self._is_running = False
                break
            else:
                print("🔄 循环回放...")


class ImprovedAKShareFeed(LiveDataFeed):
    """
    改进版AKShare数据源（带重试和降级）
    
    改进：
    - 自动清除代理
    - 重试机制
    - 数据验证
    - 错误处理
    """
    
    def __init__(self, interval: int = 60, max_retries: int = 3):
        """
        Args:
            interval: 更新间隔（秒）
            max_retries: 最大重试次数
        """
        self.interval = interval
        self.max_retries = max_retries
        self.symbols: List[str] = []
        self._bar_callbacks: List[Callable] = []
        self._tick_callbacks: List[Callable] = []
        self._is_running = False
        self._thread: Optional[threading.Thread] = None
        
        # 统计
        self.success_count = 0
        self.fail_count = 0
    
    def subscribe(self, symbols: list[str]):
        self.symbols = symbols
        print(f"📡 订阅股票: {', '.join(symbols)}")
    
    def on_bar(self, callback: Callable[[BarData], None]):
        self._bar_callbacks.append(callback)
    
    def on_tick(self, callback: Callable[[TickData], None]):
        self._tick_callbacks.append(callback)
    
    def start(self):
        if self._is_running:
            print("⚠️ 数据流已在运行")
            return
        
        self._is_running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        print("🚀 改进版AKShare数据流已启动")
    
    def stop(self):
        self._is_running = False
        if self._thread:
            self._thread.join(timeout=5)
        print(f"⏹️ AKShare数据流已停止 (成功: {self.success_count}, 失败: {self.fail_count})")
    
    def _run_loop(self):
        while self._is_running:
            try:
                self._fetch_and_broadcast()
            except Exception as e:
                print(f"❌ 数据获取失败: {e}")
                self.fail_count += 1
            
            time.sleep(self.interval)
    
    def _fetch_and_broadcast(self):
        """获取并广播数据（带重试）"""
        try:
            import akshare as ak
            import os
            
            # 清除代理（解决连接问题）
            proxies_to_clear = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
            for proxy in proxies_to_clear:
                os.environ.pop(proxy, None)
            
        except ImportError:
            print("❌ 请安装 akshare: pip install akshare")
            self.stop()
            return
        
        for symbol in self.symbols:
            retry_count = 0
            success = False
            
            while retry_count < self.max_retries and not success:
                try:
                    # 获取实时行情
                    df = ak.stock_zh_a_spot_em()
                    
                    # 查找对应股票
                    stock_data = df[df['代码'] == symbol]
                    
                    if stock_data.empty:
                        print(f"⚠️ 未找到股票 {symbol}")
                        break
                    
                    row = stock_data.iloc[0]
                    
                    # 数据验证
                    def safe_float(value, default=0.0):
                        try:
                            return float(value) if value and str(value).strip() != '-' else default
                        except:
                            return default
                    
                    # 构造BarData
                    bar = BarData(
                        symbol=symbol,
                        timestamp=datetime.now(),
                        open=safe_float(row.get('今开'), row.get('最新价', 0)),
                        high=safe_float(row.get('最高'), row.get('最新价', 0)),
                        low=safe_float(row.get('最低'), row.get('最新价', 0)),
                        close=safe_float(row.get('最新价'), 0),
                        volume=safe_float(row.get('成交量'), 0)
                    )
                    
                    # 验证数据合理性
                    if bar.close <= 0:
                        print(f"⚠️ 无效价格数据: {symbol}")
                        break
                    
                    # 广播给所有回调
                    for callback in self._bar_callbacks:
                        callback(bar)
                    
                    success = True
                    self.success_count += 1
                    
                except Exception as e:
                    retry_count += 1
                    if retry_count >= self.max_retries:
                        print(f"❌ 获取 {symbol} 失败 (已重试{self.max_retries}次): {str(e)[:100]}")
                        self.fail_count += 1
                    else:
                        print(f"⚠️ 重试 {retry_count}/{self.max_retries}... ({symbol})")
                        time.sleep(2)


class MultiSourceDataFeed(LiveDataFeed):
    """
    多数据源降级策略
    
    自动切换：AKShare → Tushare → CSV
    保证数据供应的稳定性
    """
    
    def __init__(
        self,
        primary_feed: LiveDataFeed,
        fallback_feeds: List[LiveDataFeed],
        switch_threshold: int = 3
    ):
        """
        Args:
            primary_feed: 主数据源
            fallback_feeds: 备用数据源列表
            switch_threshold: 连续失败多少次后切换
        """
        self.primary_feed = primary_feed
        self.fallback_feeds = fallback_feeds
        self.switch_threshold = switch_threshold
        
        self.current_feed = primary_feed
        self.fail_count = 0
        self.feed_index = -1  # -1表示使用primary
    
    def subscribe(self, symbols: list[str]):
        self.current_feed.subscribe(symbols)
    
    def on_bar(self, callback: Callable[[BarData], None]):
        # 包装回调，监控失败
        def wrapped_callback(bar: BarData):
            try:
                callback(bar)
                self.fail_count = 0  # 成功则重置
            except Exception as e:
                self.fail_count += 1
                print(f"⚠️ 数据异常 ({self.fail_count}/{self.switch_threshold})")
                
                if self.fail_count >= self.switch_threshold:
                    self._switch_feed()
                raise e
        
        self.current_feed.on_bar(wrapped_callback)
    
    def on_tick(self, callback):
        self.current_feed.on_tick(callback)
    
    def start(self):
        print(f"🌐 多源数据流启动 (主: {type(self.current_feed).__name__})")
        self.current_feed.start()
    
    def stop(self):
        self.current_feed.stop()
    
    def _switch_feed(self):
        """切换到备用数据源"""
        print(f"🔄 切换数据源...")
        
        self.current_feed.stop()
        
        if self.feed_index < len(self.fallback_feeds) - 1:
            self.feed_index += 1
            self.current_feed = self.fallback_feeds[self.feed_index]
            print(f"✅ 切换到: {type(self.current_feed).__name__}")
            self.current_feed.start()
            self.fail_count = 0
        else:
            print("❌ 所有数据源均不可用!")