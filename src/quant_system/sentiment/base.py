from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict


@dataclass
class SentimentResult:
    score: float              # -1 ~ +1
    level: str                # fear / neutral / greed
    details: Dict[str, float] # 各因子得分


class BaseSentimentModel(ABC):

    @abstractmethod
    def compute(self, data) -> SentimentResult:
        pass


def score_to_level(score: float) -> str:
    if score <= -0.3:
        return "fear"
    elif score >= 0.3:
        return "greed"
    else:
        return "neutral"
