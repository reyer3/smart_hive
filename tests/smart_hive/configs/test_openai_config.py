"""
Tests for OpenAI configuration.
"""

import os
from unittest.mock import patch

import pytest
from smart_hive.configs.openai_config import OpenAIConfig


def test_openai_config_defaults():
    """Test default values for OpenAI config."""
    config = OpenAIConfig()
    assert config.api_key is None
    assert config.model == "gpt-4-1106-preview"
    assert config.temperature == 0.0


def test_openai_config_from_env():
    """Test loading config from environment variables."""
    with patch.dict(os.environ, {
        "OPENAI_API_KEY": "test-key",
        "OPENAI_MODEL": "gpt-4",
        "OPENAI_TEMPERATURE": "0.5"
    }):
        config = OpenAIConfig.from_env()
        assert config.api_key == "test-key"
        assert config.model == "gpt-4"
        assert config.temperature == 0.5


def test_openai_config_validation():
    """Test API key validation."""
    config = OpenAIConfig()
    assert not config.validate_api_key()

    config.api_key = "test-key"
    assert config.validate_api_key()


def test_openai_config_temperature_validation():
    """Test temperature validation."""
    with pytest.raises(ValueError):
        OpenAIConfig(temperature=-0.1)
    
    with pytest.raises(ValueError):
        OpenAIConfig(temperature=2.1)
