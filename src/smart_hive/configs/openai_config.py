"""
Configuration module for OpenAI settings.
"""

import os
from typing import Optional

from pydantic import BaseModel, Field


class OpenAIConfig(BaseModel):
    """Configuration for OpenAI API."""
    api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key. If not provided, will try to get from OPENAI_API_KEY env var."
    )
    model: str = Field(
        default="gpt-4-1106-preview",
        description="OpenAI model to use for LLM evaluations."
    )
    temperature: float = Field(
        default=0.0,
        description="Temperature for model responses. Lower values are more deterministic.",
        ge=0.0,
        le=2.0
    )

    @classmethod
    def from_env(cls) -> "OpenAIConfig":
        """Create config from environment variables."""
        return cls(
            api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("OPENAI_MODEL", "gpt-4-1106-preview"),
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.0"))
        )

    def validate_api_key(self) -> bool:
        """Check if API key is configured."""
        return bool(self.api_key)
