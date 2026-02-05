"""
验证 P0/P1 功能的测试脚本
"""
from quant_system.data.price_feed import load_prices_from_csv
from quant_system.strategy.simple_ma import SimpleMAStrategy
from quant_system.backtest.engine import BacktestEngine
from quant_system.backtest.cost_model import CostModel, NoCostModel
from quant_system.visualization.backtest_report import plot_backtest_report


def test_enhanced_metrics():
    """测试增强指标"""
    print("=" * 60)
    print("测试 1: 增强指标计算")
    print("=" * 60)
    
    # 加载数据
    prices = load_prices_from_csv("AAPL.csv")
    
    # 生成信号
    strategy = SimpleMAStrategy(window=5)
    signals = strategy.generate_signals(prices)
    
    # 运行回测
    bt = BacktestEngine(
        prices=prices,
        signals=signals,
        symbol="AAPL",
        initial_cash=100_000,
    )
    result = bt.run()
    
    # 输出所有指标
    print("\n📊 回测结果：")
    print(f"总收益率: {result.total_return:.2%}")
    print(f"年化收益率: {result.annual_return:.2%}")
    print(f"最大回撤: {result.max_drawdown:.2%}")
    print(f"夏普比率: {result.sharpe_ratio:.2f}")
    print(f"年化波动率: {result.annual_volatility:.2%}")
    print(f"交易次数: {result.num_trades}")
    print(f"胜率: {result.win_rate:.1%}")
    print(f"平均单笔收益: {result.avg_trade_return:.2%}")
    print(f"盈亏比: {result.profit_factor:.2f}")
    
    return result


def test_cost_model():
    """测试成本模型"""
    print("\n" + "=" * 60)
    print("测试 2: 交易成本影响")
    print("=" * 60)
    
    prices = load_prices_from_csv("AAPL.csv")
    strategy = SimpleMAStrategy(window=5)
    signals = strategy.generate_signals(prices)
    
    # 无成本回测
    bt_no_cost = BacktestEngine(
        prices=prices,
        signals=signals,
        symbol="AAPL",
        cost_model=NoCostModel()
    )
    result_no_cost = bt_no_cost.run()
    
    # 有成本回测（默认万三）
    bt_with_cost = BacktestEngine(
        prices=prices,
        signals=signals,
        symbol="AAPL",
        cost_model=CostModel()
    )
    result_with_cost = bt_with_cost.run()
    
    # 对比结果
    print("\n💰 成本影响分析：")
    print(f"{'指标':<20} {'无成本':<15} {'含成本':<15} {'差异':<15}")
    print("-" * 65)
    
    print(f"{'总收益率':<20} {result_no_cost.total_return:>12.2%} {result_with_cost.total_return:>12.2%} {(result_no_cost.total_return - result_with_cost.total_return):>12.2%}")
    print(f"{'最终资金':<20} ${result_no_cost.final_equity:>11,.0f} ${result_with_cost.final_equity:>11,.0f} ${(result_no_cost.final_equity - result_with_cost.final_equity):>11,.0f}")
    print(f"{'夏普比率':<20} {result_no_cost.sharpe_ratio:>12.2f} {result_with_cost.sharpe_ratio:>12.2f} {(result_no_cost.sharpe_ratio - result_with_cost.sharpe_ratio):>12.2f}")
    
    cost_impact = result_no_cost.final_equity - result_with_cost.final_equity
    print(f"\n⚠️  交易成本总计: ${cost_impact:,.2f}")
    print(f"⚠️  成本占初始资金比例: {cost_impact / 100_000:.2%}")
    
    return result_no_cost, result_with_cost


def test_visualization(result):
    """测试可视化"""
    print("\n" + "=" * 60)
    print("测试 3: 综合可视化报告")
    print("=" * 60)
    
    print("\n📈 生成可视化报告...")
    plot_backtest_report(result, save_path="backtest_report.png")
    print("✅ 报告已生成并保存")


def main():
    """主函数入口（供 Poetry 脚本调用）"""
    # 执行所有测试
    print("🚀 开始测试 P0/P1 功能...\n")
    
    # 测试 1: 增强指标
    result = test_enhanced_metrics()
    
    # 测试 2: 成本模型
    result_no_cost, result_with_cost = test_cost_model()
    
    # 测试 3: 可视化
    test_visualization(result_with_cost)
    
    print("\n" + "=" * 60)
    print("✅ 所有测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()