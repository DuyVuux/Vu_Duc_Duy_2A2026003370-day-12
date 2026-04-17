import time
import logging
from dataclasses import dataclass, field
from fastapi import HTTPException
from app.config import settings

logger = logging.getLogger(__name__)

PRICE_PER_1K_INPUT_TOKENS = 0.00015
PRICE_PER_1K_OUTPUT_TOKENS = 0.0006


@dataclass
class UsageRecord:
    input_tokens: int = 0
    output_tokens: int = 0
    request_count: int = 0
    day: str = field(default_factory=lambda: time.strftime("%Y-%m-%d"))

    @property
    def total_cost_usd(self) -> float:
        input_cost = (self.input_tokens / 1000) * PRICE_PER_1K_INPUT_TOKENS
        output_cost = (self.output_tokens / 1000) * PRICE_PER_1K_OUTPUT_TOKENS
        return round(input_cost + output_cost, 6)


class CostGuard:
    def __init__(self, daily_budget_usd: float = 5.0):
        self.daily_budget_usd = daily_budget_usd
        self._daily_cost = 0.0
        self._cost_reset_day = time.strftime("%Y-%m-%d")

    def check_and_record(self, input_tokens: int, output_tokens: int):
        today = time.strftime("%Y-%m-%d")
        if today != self._cost_reset_day:
            self._daily_cost = 0.0
            self._cost_reset_day = today
        if self._daily_cost >= self.daily_budget_usd:
            raise HTTPException(503, "Daily budget exhausted. Try tomorrow.")
        cost = (input_tokens / 1000) * PRICE_PER_1K_INPUT_TOKENS + \
               (output_tokens / 1000) * PRICE_PER_1K_OUTPUT_TOKENS
        self._daily_cost += cost

    @property
    def daily_cost(self) -> float:
        return self._daily_cost


cost_guard = CostGuard(daily_budget_usd=settings.daily_budget_usd)
