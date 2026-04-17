import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import time
from fastapi import HTTPException
from app.rate_limiter import RateLimiter

def test_rate_limiter_allows_requests():
    rl = RateLimiter(max_requests=5, window_seconds=60)
    user_id = "test_user_1"
    
    # Should allow 5 requests
    for _ in range(5):
        result = rl.check(user_id)
        assert result["limit"] == 5
        assert result["remaining"] >= 0

def test_rate_limiter_blocks_excess_requests():
    rl = RateLimiter(max_requests=2, window_seconds=60)
    user_id = "test_user_2"
    
    rl.check(user_id)
    rl.check(user_id)
    
    with pytest.raises(HTTPException) as exc:
        rl.check(user_id)
    
    assert exc.value.status_code == 429
    assert exc.value.detail.startswith("Rate limit exceeded")

def test_rate_limiter_window_slide():
    # Set window to 1 second for fast testing
    rl = RateLimiter(max_requests=1, window_seconds=1)
    user_id = "test_user_3"
    
    rl.check(user_id)
    
    with pytest.raises(HTTPException):
        rl.check(user_id)
        
    time.sleep(1.1)  # Wait for window to slide
    
    # After window slides, it should allow again
    result = rl.check(user_id)
    assert result["limit"] == 1
