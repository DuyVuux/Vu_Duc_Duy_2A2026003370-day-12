import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import time
from fastapi import HTTPException
from app.cost_guard import CostGuard, UsageRecord, PRICE_PER_1K_INPUT_TOKENS, PRICE_PER_1K_OUTPUT_TOKENS

def test_usage_record_cost_calculation():
    record = UsageRecord(input_tokens=1000, output_tokens=1000)
    expected_cost = PRICE_PER_1K_INPUT_TOKENS + PRICE_PER_1K_OUTPUT_TOKENS
    assert record.total_cost_usd == round(expected_cost, 6)

def test_cost_guard_allows_within_budget():
    cg = CostGuard(daily_budget_usd=0.1)
    # Using small numbers so cost remains low
    cg.check_and_record(input_tokens=100, output_tokens=100)
    assert cg.daily_cost > 0.0

def test_cost_guard_blocks_budget_exceeded():
    cg = CostGuard(daily_budget_usd=0.0001)
    
    # This should exhaust the budget
    with pytest.raises(HTTPException) as exc:
        cg.check_and_record(input_tokens=1000, output_tokens=1000)
        cg.check_and_record(input_tokens=1000, output_tokens=1000)
    
    assert exc.value.status_code == 503
    assert exc.value.detail == "Daily budget exhausted. Try tomorrow."
    
def test_cost_guard_day_reset(monkeypatch):
    cg = CostGuard(daily_budget_usd=5.0)
    
    # First record some cost today
    cg.check_and_record(input_tokens=10000, output_tokens=10000)
    assert cg.daily_cost > 0.0
    
    # Mock time.strftime to return tomorrow
    original_strftime = time.strftime
    def mock_strftime(fmt="%Y-%m-%d"):
        if fmt == "%Y-%m-%d":
            return "2099-01-01"
        return original_strftime(fmt)
    
    monkeypatch.setattr(time, "strftime", mock_strftime)
    
    # Record cost on new day, daily cost should reset
    cg.check_and_record(input_tokens=10, output_tokens=10)
    
    cost_for_10_tokens = (10 / 1000) * PRICE_PER_1K_INPUT_TOKENS + (10 / 1000) * PRICE_PER_1K_OUTPUT_TOKENS
    assert cg.daily_cost == cost_for_10_tokens
