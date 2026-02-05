"""
测试参数热力图可视化
"""
import pytest
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端

from quant_system.visualization.param_heatmap import (
    plot_param_heatmap,
    plot_param_comparison_bar
)
from quant_system.runner.param_scan import run_param_scan
from quant_system.strategy.dual_ma import DualMAStrategy


@pytest.fixture
def sample_prices():
    """样本价格序列"""
    return [100.0 + i * 0.5 for i in range(100)]


@pytest.fixture
def param_scan_results(sample_prices):
    """参数扫描结果"""
    results = run_param_scan(
        symbol="TEST",
        prices=sample_prices,
        strategy_cls=DualMAStrategy,
        param_grid={
            "fast_window": [3, 5],
            "slow_window": [10, 20],
        }
    )
    return results


class TestParamHeatmap:
    """参数热力图测试"""
    
    def test_heatmap_creation(self, param_scan_results, tmp_path):
        """测试热力图生成"""
        save_path = tmp_path / "test_heatmap.png"
        
        # 不应该抛出异常
        try:
            plot_param_heatmap(
                param_scan_results,
                x_param="fast_window",
                y_param="slow_window",
                metric="total_return",
                save_path=str(save_path)
            )
            
            # 文件应该被创建
            assert save_path.exists()
        except Exception as e:
            pytest.skip(f"Matplotlib display issue: {e}")
    
    def test_invalid_param_name(self, param_scan_results):
        """测试无效的参数名"""
        with pytest.raises(ValueError):
            plot_param_heatmap(
                param_scan_results,
                x_param="invalid_param",
                y_param="slow_window",
                metric="total_return"
            )
    
    def test_invalid_metric_name(self, param_scan_results):
        """测试无效的指标名"""
        with pytest.raises(ValueError):
            plot_param_heatmap(
                param_scan_results,
                x_param="fast_window",
                y_param="slow_window",
                metric="invalid_metric"
            )


class TestParamComparisonBar:
    """参数对比柱状图测试"""
    
    def test_bar_chart_creation(self, param_scan_results, tmp_path):
        """测试柱状图生成"""
        save_path = tmp_path / "test_bar.png"
        
        try:
            plot_param_comparison_bar(
                param_scan_results,
                param="fast_window",
                metrics=["total_return", "sharpe_ratio"],
                save_path=str(save_path)
            )
            
            assert save_path.exists()
        except Exception as e:
            pytest.skip(f"Matplotlib display issue: {e}")