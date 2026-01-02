from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # 🔐 Multiple OpenRouter keys
    openrouter_api_keys: List[str]

    # 🧠 Supabase
    supabase_url: str
    supabase_key: str

    # 🤖 Models
    medium_model: str = "meta-llama/llama-4-scout"
    strong_model: str = "meta-llama/llama-4-scout"
    format_model: str = "meta-llama/llama-4-scout"

    # ⚙️ App config
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"    
    
    # 🎯 Thresholds
    confidence_threshold: float = 0.85
    max_cost_per_xray: float = 0.10

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
    }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

