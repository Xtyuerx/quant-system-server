from quant_system.data.price_feed import load_prices_from_csv
from quant_system.strategy.buy_and_hold import BuyAndHoldStrategy
from quant_system.backtest.multi_backtest import MultiBacktest
from quant_system.analysis.visualization import plot_advanced_backtest
from quant_system.analysis.performance import total_return, max_drawdown
from quant_system.analysis.multi_visualization import plot_multi_strategy_comparison

def main():
    print("Quant System Started 🚀")

    # 1️⃣ 多标的价格数据
    price_data = {
        "AAPL": load_prices_from_csv("AAPL.csv"),
        "MSFT": load_prices_from_csv("MSFT.csv")
    }

    # 2️⃣ 多策略实例
    strategies = {
        "BuyAndHold": BuyAndHoldStrategy(),
        # 可以在这里继续添加策略
    }

    # 3️⃣ 初始化多策略回测
    multi_bt = MultiBacktest(price_data=price_data, strategies=strategies, initial_cash=100_000)

    # 4️⃣ 运行回测
    results = multi_bt.run()

    # 5️⃣ 输出回测结果 + 可视化
    for symbol, strat_results in results.items():
        for strat_name, backtest in strat_results.items():
            print(f"\n=== {symbol} - {strat_name} ===")
            print("Final equity:", backtest.equity_curve[-1])
            tr = total_return(backtest.equity_curve)
            mdd = max_drawdown(backtest.equity_curve)
            print(f"Total Return: {tr:.2%}")
            print(f"Max Drawdown: {mdd:.2%}")

            # 高级可视化
            plot_advanced_backtest(
                prices=price_data[symbol],
                equity_curve=backtest.equity_curve,
                trades=backtest.trades,
                title=f"{symbol}-{strat_name}",
                save_path=f"{symbol}_{strat_name}_backtest.png"
            )

            plot_multi_strategy_comparison(
                price_data=price_data,
                backtest_results=results,
                title="Multi-Strategy Multi-Asset Equity Curve",
                save_path="multi_strategy_comparison.png"
            )

if __name__ == "__main__":
    main()
