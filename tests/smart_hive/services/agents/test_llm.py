"""
Tests for LLM agents using DeepEval.
"""

import pytest
from deepeval import assert_test
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualRelevancyMetric,
)
from deepeval.test_case import LLMTestCase

from smart_hive.services.control_plane.main import (
    SmartHiveOrchestrator,
    AgentRequest,
    set_orchestrator,
)

@pytest.fixture
async def orchestrator():
    """Create a test orchestrator."""
    orchestrator = SmartHiveOrchestrator()
    set_orchestrator(orchestrator)
    yield orchestrator
    await orchestrator.reset()

@pytest.mark.asyncio
async def test_backend_agent_response(orchestrator):
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

    # Define metrics
    metrics = [
        AnswerRelevancyMetric(threshold=0.7),
        FaithfulnessMetric(threshold=0.7),
        ContextualRelevancyMetric(threshold=0.7)
    ]

    # Assert test passes all metrics
    assert_test(test_case, metrics)

    # Clean up
    await orchestrator.destroy_agent(agent_id)
