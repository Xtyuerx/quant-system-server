import pytest
import time
from datetime import datetime
from quant_system.data.live_feed import (
    BarData, CSVReplayFeed, HistoricalSimulator
)

class TestBarData:
    """测试BarData数据结构"""
    
    def test_bar_data_creation(self):
        """测试创建BarData"""
        bar = BarData(
            symbol="TEST",
            timestamp=datetime.now(),
            open=100.0,
            high=105.0,
            low=98.0,
            close=102.0,
            volume=1000000
        )
        
        assert bar.symbol == "TEST"
        assert bar.open == 100.0
        assert bar.high == 105.0
        assert bar.low == 98.0
        assert bar.close == 102.0
        assert bar.volume == 1000000


class TestHistoricalSimulator:
    """测试历史模拟器"""
    
    def test_simulator_basic(self):
        """测试基本回放功能"""
        prices = [100, 101, 102, 103, 104]
        simulator = HistoricalSimulator(prices, symbol="TEST", speed=100.0)
        
        received_bars = []
        
        def callback(bar: BarData):
            received_bars.append(bar)
        
        simulator.on_bar(callback)
        simulator.start()
        
        # 等待回放完成
        time.sleep(1)
        simulator.stop()
        
        # 验证
        assert len(received_bars) == 5
        assert received_bars[0].close == 100
        assert received_bars[-1].close == 104
    
    def test_simulator_speed(self):
        """测试回放速度"""
        prices = [100] * 10
        simulator = HistoricalSimulator(prices, symbol="TEST", speed=10.0)
        
        start_time = time.time()
        simulator.start()
        time.sleep(1.5)  # 10条数据 / 10倍速 = 1秒
        simulator.stop()
        elapsed = time.time() - start_time
        
        assert elapsed < 2.0  # 应该在2秒内完成


class TestCSVReplayFeed:
    """测试CSV回放器"""
    
    def test_csv_replay_basic(self, tmp_path):
        """测试CSV回放基本功能"""
        # 创建临时CSV
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(
            "date,open,high,low,close,volume\n"
            "2024-01-01,100,105,98,102,1000000\n"
            "2024-01-02,102,108,101,106,1200000\n"
        )
        
        feed = CSVReplayFeed(str(csv_file), symbol="TEST", speed=100.0)
        
        received_bars = []
        feed.on_bar(lambda bar: received_bars.append(bar))
        feed.start()
        
        time.sleep(0.5)
        feed.stop()
        
        assert len(received_bars) == 2
        assert received_bars[0].open == 100
        assert received_bars[1].close == 106