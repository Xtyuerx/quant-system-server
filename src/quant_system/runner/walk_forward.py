"""
Walk-Forward 分析

防止过拟合的关键工具：
- 在训练窗口优化参数
- 在测试窗口验证表现
- 滚动执行
"""
from dataclasses import dataclass
from typing import List, Dict, Any
from quant_system.backtest.engine import BacktestEngine
from quant_system.backtest.result import BacktestResult
from quant_system.strategy.base import Strategy
from quant_system.runner.param_scan import run_param_scan


@dataclass
class WalkForwardConfig:
    """Walk-Forward 配置"""
    train_window: int       # 训练窗口大小（天数）
    test_window: int        # 测试窗口大小（天数）
    step_size: int          # 滑动步长（天数）
    

@dataclass
class WalkForwardResult:
    """Walk-Forward 结果"""
    train_results: List[BacktestResult]  # 训练期结果
    test_results: List[BacktestResult]   # 测试期结果
    best_params_history: List[Dict]      # 每个周期的最优参数
    combined_equity_curve: List[float]   # 拼接的权益曲线
    
    @property
    def total_return(self) -> float:
        """总收益率"""
        if not self.combined_equity_curve:
            return 0.0
        return (self.combined_equity_curve[-1] / self.combined_equity_curve[0]) - 1
    
    @property
    def avg_train_performance(self) -> float:
        """平均训练期表现"""
        if not self.train_results:
            return 0.0
        return sum(r.total_return for r in self.train_results) / len(self.train_results)
    
    @property
    def avg_test_performance(self) -> float:
        """平均测试期表现"""
        if not self.test_results:
            return 0.0
        return sum(r.total_return for r in self.test_results) / len(self.test_results)
    
    @property
    def performance_decay(self) -> float:
        """性能衰减（训练期 vs 测试期）"""
        return self.avg_test_performance - self.avg_train_performance


def run_walk_forward_analysis(
    prices: List[float],
    strategy_cls: type[Strategy],
    param_grid: Dict[str, List[Any]],
    config: WalkForwardConfig,
    optimization_metric: str = "sharpe_ratio"
) -> WalkForwardResult:
    """
    运行 Walk-Forward 分析
    
    Args:
        prices: 价格序列
        strategy_cls: 策略类
        param_grid: 参数搜索空间
        config: Walk-Forward 配置
        optimization_metric: 优化目标指标
    
    Returns:
        Walk-Forward 结果
    
    Example:
        >>> config = WalkForwardConfig(
        ...     train_window=252,  # 1 年训练
        ...     test_window=63,    # 3 个月测试
        ...     step_size=63       # 每次前进 3 个月
        ... )
        >>> result = run_walk_forward_analysis(
        ...     prices=prices,
        ...     strategy_cls=SimpleMAStrategy,
        ...     param_grid={"window": [5, 10, 20, 50]},
        ...     config=config
        ... )
    """
    train_results = []
    test_results = []
    best_params_history = []
    combined_equity_curve = []
    
    current_position = 0
    total_length = len(prices)
    
    print(f"🔄 开始 Walk-Forward 分析...")
    print(f"   训练窗口: {config.train_window} 天")
    print(f"   测试窗口: {config.test_window} 天")
    print(f"   滑动步长: {config.step_size} 天")
    print()
    
    iteration = 0
    
    while current_position + config.train_window + config.test_window <= total_length:
        iteration += 1
        
        # 1️⃣ 训练期
        train_start = current_position
        train_end = current_position + config.train_window
        train_prices = prices[train_start:train_end]
        
        print(f"📊 第 {iteration} 轮:")
        print(f"   训练期: [{train_start}:{train_end}] ({len(train_prices)} 天)")
        
        # 在训练期优化参数
        train_scan = run_param_scan(
            symbol=f"Train_{iteration}",
            prices=train_prices,
            strategy_cls=strategy_cls,
            param_grid=param_grid
        )
        
        # 找到最优参数
        best_train_result = train_scan.sort_by(optimization_metric, descending=True).best(optimization_metric)
        best_params = best_train_result.params
        
        train_results.append(best_train_result)
        best_params_history.append(best_params)
        
        print(f"   最优参数: {best_params}")
        print(f"   训练期 {optimization_metric}: {getattr(best_train_result, optimization_metric):.3f}")
        
        # 2️⃣ 测试期
        test_start = train_end
        test_end = test_start + config.test_window
        test_prices = prices[test_start:test_end]
        
        print(f"   测试期: [{test_start}:{test_end}] ({len(test_prices)} 天)")
        
        # 用最优参数在测试期回测
        strategy = strategy_cls(**best_params)
        signals = strategy.generate_signals(test_prices)
        
        bt = BacktestEngine(
            symbol=f"Test_{iteration}",
            prices=test_prices,
            signals=signals,
        )
        test_result = bt.run()
        test_result.params = best_params
        
        test_results.append(test_result)
        
        print(f"   测试期 {optimization_metric}: {getattr(test_result, optimization_metric):.3f}")
        print(f"   性能衰减: {(getattr(test_result, optimization_metric) - getattr(best_train_result, optimization_metric)):.3f}")
        print()
        
        # 拼接权益曲线
        if not combined_equity_curve:
            combined_equity_curve.extend(test_result.equity_curve)
        else:
            # 归一化衔接
            scale_factor = combined_equity_curve[-1] / test_result.equity_curve[0]
            scaled_curve = [v * scale_factor for v in test_result.equity_curve]
            combined_equity_curve.extend(scaled_curve[1:])  # 跳过第一个点避免重复
        
        # 滑动窗口
        current_position += config.step_size
    
    print(f"✅ Walk-Forward 分析完成，共 {iteration} 轮")
    
    return WalkForwardResult(
        train_results=train_results,
        test_results=test_results,
        best_params_history=best_params_history,
        combined_equity_curve=combined_equity_curve
    )