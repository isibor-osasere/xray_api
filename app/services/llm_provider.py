"""LLM provider integration with OpenRouter"""

import itertools
from typing import Literal

from langchain_openai import ChatOpenAI

from app.config import get_settings

settings = get_settings()


class LLMProvider:
    """Manages LLM model access with OpenRouter"""

    def __init__(self):
        self.base_url = "https://openrouter.ai/api/v1"

        # 🔁 cycle through multiple API keys
        if not settings.openrouter_api_keys:
            raise ValueError("No OpenRouter API keys configured")

        self._api_key_cycle = itertools.cycle(settings.openrouter_api_keys)

    def _get_api_key(self) -> str:
        """Return the next API key (round-robin)"""
        return next(self._api_key_cycle)

    def get_model(
        self,
        model_type: Literal["haiku", "sonnet", "triage"],
    ) -> ChatOpenAI:
        """Get LLM model instance"""

        model_map = {
            "medium": settings.medium_model,
            "strong": settings.strong_model,
            "format": settings.format_model,
        }

        model_name = model_map[model_type]

        return ChatOpenAI(
            model=model_name,
            openai_api_key=self._get_api_key(),  # ✅ rotated key
            openai_api_base=self.base_url,
            temperature=0.1,
            max_tokens=2000,
        )
    

    @property
    def medium(self) -> ChatOpenAI:
        """Haiku model"""
        return self.get_model("medium")

    @property
    def strong(self) -> ChatOpenAI:
        """Sonnet model"""
        return self.get_model("strong")

    @property
    def format(self) -> ChatOpenAI:
        """Triage model"""
        return self.get_model("format")


# 🌍 Global singleton
llm_provider = LLMProvider()
