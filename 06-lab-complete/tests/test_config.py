import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest


def test_settings_default_values():
    os.environ.pop("ENVIRONMENT", None)
    os.environ.pop("AGENT_API_KEY", None)
    from app.config import Settings
    s = Settings()
    assert s.host == "0.0.0.0"
    assert s.port == 8086
    assert s.environment == "development"


def test_settings_production_validation_fails():
    os.environ["ENVIRONMENT"] = "production"
    os.environ["AGENT_API_KEY"] = "dev-key-change-me"
    from app.config import Settings
    with pytest.raises(ValueError, match="AGENT_API_KEY"):
        Settings().validate()
    os.environ.pop("ENVIRONMENT", None)
    os.environ.pop("AGENT_API_KEY", None)


def test_settings_development_passes():
    os.environ["ENVIRONMENT"] = "development"
    from app.config import Settings
    s = Settings().validate()
    assert s.environment == "development"
    os.environ.pop("ENVIRONMENT", None)
