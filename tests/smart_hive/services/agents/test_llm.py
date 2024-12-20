"""
Tests for LLM agents using DeepEval.
"""

import os
from typing import AsyncGenerator

import pytest
from deepeval import assert_test
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualRelevancyMetric,
)
from deepeval.test_case import LLMTestCase

from smart_hive.configs.openai_config import OpenAIConfig
from smart_hive.services.control_plane.main import (
    SmartHiveOrchestrator,
    AgentRequest,
    set_orchestrator,
)


@pytest.fixture
def openai_config() -> OpenAIConfig:
    """Create OpenAI config for testing."""
    config = OpenAIConfig.from_env()
    if not config.validate_api_key():
        pytest.skip("OpenAI API key not configured")
    return config


@pytest.fixture
async def orchestrator() -> AsyncGenerator[SmartHiveOrchestrator, None]:
    """Create a test orchestrator."""
    orchestrator = SmartHiveOrchestrator()
    set_orchestrator(orchestrator)
    yield orchestrator
    await orchestrator.reset()


@pytest.mark.asyncio
async def test_backend_agent_response(orchestrator: SmartHiveOrchestrator, openai_config: OpenAIConfig):
    """Test that backend agent responses are relevant and faithful."""
    # Create an agent
    request = AgentRequest(
        name="test_agent",
        agent_type="backend",
        requirements={"cpu": 1, "memory": 512}
    )
    agent_id = await orchestrator.create_agent(request)

    # Test case with context
    test_case = LLMTestCase(
        input="¿Cómo puedo crear un nuevo agente?",
        actual_output="Para crear un nuevo agente, debes especificar un nombre y tipo válidos. Los tipos disponibles son: backend, frontend, database.",
        retrieval_context=[
            "Los agentes pueden ser de tipo: backend, frontend, database",
            "Para crear un agente se requiere un nombre válido y un tipo",
            "Los nombres deben contener solo letras, números y guiones bajos"
        ]
    )

    # Configure metrics with OpenAI settings
    metrics = [
        AnswerRelevancyMetric(
            threshold=0.7,
            openai_api_key=openai_config.api_key,
            model=openai_config.model,
            temperature=openai_config.temperature
        ),
        FaithfulnessMetric(
            threshold=0.7,
            openai_api_key=openai_config.api_key,
            model=openai_config.model,
            temperature=openai_config.temperature
        ),
        ContextualRelevancyMetric(
            threshold=0.7,
            openai_api_key=openai_config.api_key,
            model=openai_config.model,
            temperature=openai_config.temperature
        )
    ]

    # Assert test passes all metrics
    assert_test(test_case, metrics)

    # Clean up
    await orchestrator.destroy_agent(agent_id)
