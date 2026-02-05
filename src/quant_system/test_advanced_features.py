"""
测试 P3 进阶功能
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from quant_system.data.price_feed import load_prices_from_csv
from quant_system.strategy.simple_ma import SimpleMAStrategy
from quant_system.strategy.dual_ma import DualMAStrategy
from quant_system.backtest.engine import BacktestEngine
from quant_system.backtest.cost_model import CostModel
from quant_system.backtest.risk_control import ConservativeRiskControl, AggressiveRiskControl
from quant_system.backtest.slippage import FixedSlippage
from quant_system.runner.param_scan import run_param_scan
from quant_system.runner.walk_forward import run_walk_forward_analysis, WalkForwardConfig
from quant_system.visualization.param_heatmap import plot_param_heatmap
from quant_system.visualization.backtest_report import plot_backtest_report


def test_integrated_features():
    """测试集成后的完整功能"""
    print("=" * 60)
    print("测试：集成风控 + 滑点 + 成本")
    print("=" * 60)
    
    prices = load_prices_from_csv("AAPL.csv")
    strategy = SimpleMAStrategy(window=5)
    signals = strategy.generate_signals(prices)
    
    # 场景 1：无约束
    bt_basic = BacktestEngine(
        prices=prices,
        signals=signals,
        symbol="Basic"
    ).run()
    
    # 场景 2：完整约束
    bt_full = BacktestEngine(
        prices=prices,
        signals=signals,
        symbol="Full Constraints",
        cost_model=CostModel(),
        slippage_model=FixedSlippage(slippage_bps=5),
        risk_control=ConservativeRiskControl()
    ).run()
    
    print(f"\n📊 对比结果:")
    print(f"{'场景':<20} {'收益率':<12} {'夏普':<10} {'交易次数'}")
    print("-" * 60)
    print(f"{'无约束':<20} {bt_basic.total_return:>10.2%} {bt_basic.sharpe_ratio:>8.2f} {bt_basic.num_trades:>8}")
    print(f"{'完整约束':<20} {bt_full.total_return:>10.2%} {bt_full.sharpe_ratio:>8.2f} {bt_full.num_trades:>8}")
    
    print("\n✅ 集成功能测试完成")
    return bt_full


def test_param_heatmap():
    """测试参数热力图（双参数）"""
    print("\n" + "=" * 60)
    print("测试：参数热力图（双均线策略）")
    print("=" * 60)
    
    prices = load_prices_from_csv("AAPL.csv")
    
    results = run_param_scan(
        symbol="AAPL",
        prices=prices,
        strategy_cls=DualMAStrategy,
        param_grid={
            "fast_window": [3, 5, 10],
            "slow_window": [15, 20, 30],
            "threshold": [0.0, 0.01]
        }
    )
    
    print(f"\n✅ 参数扫描完成，共 {len(results.results)} 组结果")
    
    # 绘制热力图
    try:
        plot_param_heatmap(
            results,
            x_param="fast_window",
            y_param="slow_window",
            metric="sharpe_ratio",
            save_path="param_heatmap.png"
        )
    except Exception as e:
        print(f"⚠️ 热力图生成失败: {e}")


def test_walk_forward():
    """测试 Walk-Forward 分析"""
    print("\n" + "=" * 60)
    print("测试：Walk-Forward 分析")
    print("=" * 60)
    
    prices = load_prices_from_csv("AAPL.csv")
    
    if len(prices) < 100:
        print("⚠️ 数据点不足，跳过 Walk-Forward 测试")
        return
    
    config = WalkForwardConfig(
        train_window=50,   # 50 天训练
        test_window=20,    # 20 天测试
        step_size=20       # 每次前进 20 天
    )
    
    result = run_walk_forward_analysis(
        prices=prices,
        strategy_cls=SimpleMAStrategy,
        param_grid={"window": [3, 5, 10, 20]},
        config=config,
        optimization_metric="sharpe_ratio"
    )
    
    print(f"\n📊 Walk-Forward 结果:")
    print(f"平均训练期表现: {result.avg_train_performance:.2%}")
    print(f"平均测试期表现: {result.avg_test_performance:.2%}")
    print(f"性能衰减: {result.performance_decay:.2%}")
    print(f"总收益率: {result.total_return:.2%}")
    
    print("\n✅ Walk-Forward 分析完成")


def main():
    """主函数"""
    print("🚀 测试 P3 进阶功能（完整版）...\n")
    
    # 测试 1：集成功能
    result = test_integrated_features()
    
    # 测试 2：参数热力图
    test_param_heatmap()
    
    # 测试 3：Walk-Forward
    test_walk_forward()
    
    # 生成最终报告
    print("\n" + "=" * 60)
    print("生成可视化报告")
    print("=" * 60)
    plot_backtest_report(result, save_path="advanced_report.png")
    
    print("\n" + "=" * 60)
    print("✅ 所有 P3 测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()