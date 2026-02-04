def ic_to_weight(
    ic_score: float,
    scale: float = 0.05,
    max_weight: float = 1.0
) -> float:
    """
    将 IC 分数映射为 [-max_weight, max_weight] 的因子权重
    """
    if ic_score is None or abs(ic_score) < 1e-4:
        return 0.0

    weight = ic_score / scale
    weight = max(min(weight, 1.0), -1.0)

    return weight * max_weight
