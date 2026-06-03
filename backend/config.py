from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Literal

class Settings(BaseSettings):
    # App
    APP_NAME: str = "CodeSentinel"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    # LLM Configuration
    LLM_PROVIDER: Literal["openai", "gemini", "codelama", "deepseek"] = "gemini"
    OPENAI_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # Model Selection
    OPENAI_MODEL: str = "gpt-4-turbo"
    GEMINI_MODEL: str = "gemini-1.5-pro"  # Better for code understanding
    CODELAMA_MODEL: str = "codellama-34b"  # Open-source, specialized for code
    DEEPSEEK_MODEL: str = "deepseek-coder"

    # Static Analysis
    MAX_CODE_SIZE_MB: int = 10
    SUPPORTED_LANGUAGES: list[str] = ["python", "javascript", "java", "go", "cpp"]

    # Analysis Settings
    ENABLE_STATIC_ANALYSIS: bool = True
    ENABLE_SECURITY_SCAN: bool = True
    ENABLE_COMPLEXITY_ANALYSIS: bool = True
    ENABLE_DUPLICATE_DETECTION: bool = True
    ENABLE_LLM_REVIEW: bool = True

    # Issue Severity Thresholds
    SECURITY_SEVERITY_THRESHOLD: Literal["low", "medium", "high", "critical"] = "low"
    CODE_QUALITY_MIN_SCORE: float = 0.0  # Include all quality issues

    # Database
    DATABASE_URL: str = "postgresql://codesentinel:codesentinel@localhost:5432/codesentinel"
    REDIS_URL: str = "redis://localhost:6379"

    # GitHub Integration
    GITHUB_APP_ID: str = ""
    GITHUB_PRIVATE_KEY: str = ""
    GITHUB_WEBHOOK_SECRET: str = ""

    # Report Generation
    GENERATE_PDF_REPORTS: bool = True
    INCLUDE_SUGGESTED_FIXES: bool = True

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
