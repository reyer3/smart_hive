"""
Tests for SmartHive Control Plane
"""

import pytest
from fastapi.testclient import TestClient

from smart_hive.services.control_plane.main import (
    SmartHiveOrchestrator,
    app,
    initialize_components
)

@pytest.fixture
async def orchestrator():
    """Create a test orchestrator."""
    return await SmartHiveOrchestrator.create()

@pytest.fixture
def client(request):
    """Create a test client."""
    app.dependency_overrides = {}
    request.cls.app = app
    return TestClient(app)

@pytest.mark.usefixtures("client")
class TestControlPlane:
    """Test control plane endpoints."""

    async def test_create_agent(self, client):
        """Test agent creation."""
        await initialize_components()
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
        assert data["resources"] == {"cpu": 1, "memory": 512}

    async def test_create_agent_invalid_type(self, client):
        """Test agent creation with invalid type."""
        await initialize_components()
        response = client.post(
            "/agents/create",
            json={
                "name": "test_agent",
                "agent_type": "invalid",
                "requirements": {"cpu": 1, "memory": 512}
            }
        )
        assert response.status_code == 400
        assert "Invalid agent type" in response.json()["detail"]

    async def test_create_agent_invalid_name(self, client):
        """Test agent creation with invalid name."""
        await initialize_components()
        response = client.post(
            "/agents/create",
            json={
                "name": "test@agent",
                "agent_type": "backend",
                "requirements": {"cpu": 1, "memory": 512}
            }
        )
        assert response.status_code == 400
        assert "Name must contain only letters" in response.json()["detail"]

    async def test_destroy_agent(self, client):
        """Test agent destruction."""
        await initialize_components()
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
        assert response.json()["status"] == "destroyed"

    async def test_destroy_nonexistent_agent(self, client):
        """Test destroying a nonexistent agent."""
        await initialize_components()
        response = client.delete("/agents/nonexistent")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    async def test_get_agent(self, client):
        """Test getting agent details."""
        await initialize_components()
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
        assert data["resources"] == {"cpu": 1, "memory": 512}

    async def test_get_nonexistent_agent(self, client):
        """Test getting a nonexistent agent."""
        await initialize_components()
        response = client.get("/agents/nonexistent")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    async def test_list_agents(self, client):
        """Test listing all agents."""
        await initialize_components()
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
            assert agent["status"] == "running"
