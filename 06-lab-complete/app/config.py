"""Production config — 12-Factor: tất cả từ environment variables."""
import os
import logging
from dataclasses import dataclass, field


@dataclass
class Settings:
    # Server
    host: str = field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.getenv("PORT", "8086")))
    environment: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")

    # App
    app_name: str = field(default_factory=lambda: os.getenv("APP_NAME", "Production AI Agent"))
    app_version: str = field(default_factory=lambda: os.getenv("APP_VERSION", "1.0.0"))

    # LLM
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    llm_model: str = field(default_factory=lambda: os.getenv("LLM_MODEL", "gpt-4o-mini"))

    # Security
    agent_api_key: str = field(default_factory=lambda: os.getenv("AGENT_API_KEY", "dev-key-change-me"))
    jwt_secret: str = field(default_factory=lambda: os.getenv("JWT_SECRET", "dev-jwt-secret"))
    allowed_origins: list = field(
        default_factory=lambda: os.getenv("ALLOWED_ORIGINS", "*").split(",")
    )
    ip_whitelist: list = field(
        default_factory=lambda: [
            ip.strip() for ip in os.getenv("IP_WHITELIST", "").split(",") if ip.strip()
        ]
    )

    # Rate limiting
    rate_limit_per_minute: int = field(
        default_factory=lambda: int(os.getenv("RATE_LIMIT_PER_MINUTE", "20"))
    )

    # Budget
    daily_budget_usd: float = field(
        default_factory=lambda: float(os.getenv("DAILY_BUDGET_USD", "5.0"))
    )

    # Storage
    redis_url: str = field(default_factory=lambda: os.getenv("REDIS_URL", ""))

    def validate(self):
        logger = logging.getLogger(__name__)
        
        if self.environment not in ("development", "staging", "production"):
            raise ValueError(f"ENVIRONMENT must be development/staging/production, got: {self.environment}")
        
        if self.environment == "production":
            if self.agent_api_key == "dev-key-change-me" or self.agent_api_key == "dev-key-change-me-in-production":
                raise ValueError("AGENT_API_KEY must be set in production!")
            if self.jwt_secret == "dev-jwt-secret" or self.jwt_secret == "dev-jwt-secret-change-in-production":
                raise ValueError("JWT_SECRET must be set in production!")
            if self.debug:
                raise ValueError("DEBUG must be false in production!")
            if "*" in self.allowed_origins:
                logger.warning("CORS allows all origins in production — consider restricting")
        
        if self.environment == "staging":
            if "dev-key" in self.agent_api_key:
                logger.warning("Using default API key in staging — change before production")
        
        if not self.openai_api_key:
            logger.warning("OPENAI_API_KEY not set — using mock LLM")
        
        if self.rate_limit_per_minute < 1:
            raise ValueError("RATE_LIMIT_PER_MINUTE must be >= 1")
        
        if self.daily_budget_usd <= 0:
            raise ValueError("DAILY_BUDGET_USD must be > 0")
        
        return self

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def use_mock_llm(self) -> bool:
        return not self.openai_api_key

    def to_safe_dict(self) -> dict:
        return {
            "host": self.host,
            "port": self.port,
            "environment": self.environment,
            "debug": self.debug,
            "app_name": self.app_name,
            "app_version": self.app_version,
            "llm_model": self.llm_model,
            "has_openai_key": bool(self.openai_api_key),
            "has_redis": bool(self.redis_url),
            "rate_limit_per_minute": self.rate_limit_per_minute,
            "daily_budget_usd": self.daily_budget_usd,
        }

settings = Settings().validate()
