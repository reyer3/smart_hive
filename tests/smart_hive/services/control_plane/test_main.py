"""
Tests for SmartHive Control Plane
"""

import pytest
from fastapi.testclient import TestClient

from smart_hive.services.control_plane.main import (
    SmartHiveOrchestrator,
    app,
    orchestrator,
    set_orchestrator
)

@pytest.fixture
def client(request):
    """Create a test client."""
    app.dependency_overrides = {}
    request.cls.app = app
    return TestClient(app)

@pytest.fixture(autouse=True)
async def clean_state():
    """Clean up state before and after each test."""
    global orchestrator
    if orchestrator:
        await orchestrator.reset()
    set_orchestrator(None)
    yield
    if orchestrator:
        await orchestrator.reset()
    set_orchestrator(None)

@pytest.mark.asyncio
class TestControlPlane:
    """Test control plane endpoints."""

    async def test_create_agent(self, client):
        """Test agent creation."""
        orchestrator = await SmartHiveOrchestrator.create()
        set_orchestrator(orchestrator)
        response = client.post(
            "/agents/create",
            json={
                "name": "test_agent",
                "agent_type": "backend",
                "requirements": {"cpu": 1, "memory": 512}
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["agent_id"] == "backend_test_agent"
        assert data["status"] == "created"

    async def test_create_agent_invalid_type(self, client):
        """Test agent creation with invalid type."""
        orchestrator = await SmartHiveOrchestrator.create()
        set_orchestrator(orchestrator)
        response = client.post(
            "/agents/create",
            json={
                "name": "test_agent",
                "agent_type": "invalid",
                "requirements": {"cpu": 1, "memory": 512}
            }
        )
        assert response.status_code == 422

    async def test_create_agent_invalid_name(self, client):
        """Test agent creation with invalid name."""
        orchestrator = await SmartHiveOrchestrator.create()
        set_orchestrator(orchestrator)
        response = client.post(
            "/agents/create",
            json={
                "name": "test@agent",
                "agent_type": "backend",
                "requirements": {"cpu": 1, "memory": 512}
            }
        )
        assert response.status_code == 422

    async def test_destroy_agent(self, client):
        """Test agent destruction."""
        orchestrator = await SmartHiveOrchestrator.create()
        set_orchestrator(orchestrator)
        # Create agent first
        response = client.post(
            "/agents/create",
            json={
                "name": "test_agent",
                "agent_type": "backend",
                "requirements": {"cpu": 1, "memory": 512}
            }
        )
        assert response.status_code == 200
        agent_id = response.json()["agent_id"]

        # Destroy agent
        response = client.delete(f"/agents/{agent_id}")
        assert response.status_code == 200

        # Verify agent is gone
        response = client.get(f"/agents/{agent_id}")
        assert response.status_code == 404

    async def test_destroy_nonexistent_agent(self, client):
        """Test destroying a nonexistent agent."""
        orchestrator = await SmartHiveOrchestrator.create()
        set_orchestrator(orchestrator)
        response = client.delete("/agents/nonexistent")
        assert response.status_code == 404

    async def test_get_agent(self, client):
        """Test getting agent details."""
        orchestrator = await SmartHiveOrchestrator.create()
        set_orchestrator(orchestrator)
        # Create agent first
        response = client.post(
            "/agents/create",
            json={
                "name": "test_agent",
                "agent_type": "backend",
                "requirements": {"cpu": 1, "memory": 512}
            }
        )
        assert response.status_code == 200
        agent_id = response.json()["agent_id"]

        # Get agent details
        response = client.get(f"/agents/{agent_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["agent_id"] == agent_id
        assert data["status"] == "running"

    async def test_get_nonexistent_agent(self, client):
        """Test getting a nonexistent agent."""
        orchestrator = await SmartHiveOrchestrator.create()
        set_orchestrator(orchestrator)
        response = client.get("/agents/nonexistent")
        assert response.status_code == 404

    async def test_list_agents(self, client):
        """Test listing all agents."""
        orchestrator = await SmartHiveOrchestrator.create()
        set_orchestrator(orchestrator)
        # Create a few agents
        agents = [
            {"name": "agent1", "agent_type": "backend"},
            {"name": "agent2", "agent_type": "backend"}
        ]
        created_agents = []
        for agent in agents:
            response = client.post("/agents/create", json=agent)
            assert response.status_code == 200
            created_agents.append(response.json()["agent_id"])

        # List agents
        response = client.get("/agents")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == len(agents)
        for agent in data:
            assert agent["agent_id"] in created_agents
