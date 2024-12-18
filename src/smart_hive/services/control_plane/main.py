"""
Control Plane Service

This module implements the central control plane for SmartHive using llama-agents.
"""

import re
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, ValidationError, validator
from llama_agents import (
    AgentService,
    ControlPlaneServer,
    SimpleMessageQueue,
    AgentOrchestrator,
)
from llama_index.llms.openai import OpenAI

from smart_hive.configs.agent_configs import AGENT_CONFIGS, AGENT_VALIDATION
from smart_hive.services.agents.resource_manager import ResourceManager
from smart_hive.services.control_plane.state_manager import StateManager

class AgentRequest(BaseModel):
    """Request model for agent operations with validation."""
    name: str
    agent_type: str
    requirements: Optional[Dict] = None

    @validator("name")
    def validate_name(cls, v):
        if not re.match(AGENT_VALIDATION["name_pattern"], v):
            raise ValueError("Name must contain only letters, numbers, underscores, and hyphens")
        return v

    @validator("agent_type")
    def validate_agent_type(cls, v):
        if v not in AGENT_CONFIGS:
            raise ValueError(f"Invalid agent type. Must be one of: {list(AGENT_CONFIGS.keys())}")
        return v

    class Config:
        schema_extra = {
            "example": {
                "name": "worker_1",
                "agent_type": "backend",
                "requirements": {"cpu": 1, "memory": 512}
            }
        }

class AgentResponse(BaseModel):
    """Response model for agent operations."""
    agent_id: str
    status: str
    resources: Optional[Dict] = None
    error: Optional[str] = None

# Initialize components
app = FastAPI(title="SmartHive Control Plane")
message_queue = SimpleMessageQueue()
resource_manager = ResourceManager()
state_manager = StateManager()

class SmartHiveOrchestrator(AgentOrchestrator):
    """Custom orchestrator with enhanced error handling and state management."""
    
    def __init__(self):
        super().__init__(llm=OpenAI())
        self.resource_manager = resource_manager
        self.state_manager = state_manager
        self._agents: Dict[str, Dict] = {}
        self._initialize_from_state()

    def _initialize_from_state(self):
        """Initialize agents from saved state."""
        saved_states = state_manager.list_states()
        for agent_id, state in saved_states.items():
            self._agents[agent_id] = state

    async def create_agent(self, name: str, agent_type: str, requirements: Optional[Dict] = None) -> str:
        """Create a new agent with resource allocation and state persistence."""
        try:
            # Create base agent
            agent_id = f"{agent_type}_{name}"
            if agent_id in self._agents:
                raise ValueError(f"Agent {agent_id} already exists")

            # Check instance limits
            agent_count = sum(1 for a in self._agents.values() if a["type"] == agent_type)
            max_instances = AGENT_VALIDATION["max_instances"].get(
                agent_type,
                AGENT_VALIDATION["max_instances"]["default"]
            )
            if agent_count >= max_instances:
                raise ValueError(f"Maximum number of {agent_type} instances ({max_instances}) reached")

            # Allocate resources
            if not await resource_manager.allocate_resources(agent_id, requirements or {}):
                raise ValueError(f"Failed to allocate resources for agent {agent_id}")

            # Initialize agent
            agent = AgentService(
                description=AGENT_CONFIGS[agent_type]["description"],
                service_name=name
            )
            
            # Save state
            agent_state = {
                "agent": agent,
                "status": "running",
                "type": agent_type,
                "resources": await resource_manager.get_resource_status(agent_id)
            }
            self._agents[agent_id] = agent_state
            await state_manager.save_state(agent_id, agent_state)
            
            return agent_id
            
        except Exception as e:
            # Cleanup on failure
            if agent_id in self._agents:
                await self.destroy_agent(agent_id)
            raise e

    async def destroy_agent(self, agent_id: str) -> bool:
        """Destroy an agent with complete cleanup."""
        if agent_id not in self._agents:
            return False

        try:
            # Get agent info for cleanup
            agent_info = self._agents[agent_id]
            
            # Cleanup message queue
            await message_queue.remove_subscriber(agent_id)
            
            # Cleanup resources
            await resource_manager.deallocate_resources(agent_id)
            
            # Cleanup state
            await state_manager.delete_state(agent_id)
            
            # Remove from memory
            del self._agents[agent_id]
            
            return True
            
        except Exception as e:
            # Log error but don't re-raise
            print(f"Error during agent cleanup: {str(e)}")
            return False

    async def get_agent(self, agent_id: str) -> Optional[Dict]:
        """Get agent details including resource status."""
        if agent_id not in self._agents:
            return None
            
        agent_info = self._agents[agent_id].copy()
        agent_info["resources"] = await resource_manager.get_resource_status(agent_id)
        return agent_info

    async def list_agents(self) -> List[Dict]:
        """List all agents and their status."""
        agents = []
        for agent_id, info in self._agents.items():
            agent_info = info.copy()
            agent_info["resources"] = await resource_manager.get_resource_status(agent_id)
            agents.append({"agent_id": agent_id, **agent_info})
        return agents

# Initialize orchestrator
orchestrator = SmartHiveOrchestrator()
control_plane = ControlPlaneServer(
    message_queue=message_queue,
    orchestrator=orchestrator,
)

@app.post("/agents", response_model=AgentResponse)
async def create_agent(request: AgentRequest):
    """Create a new agent with validation."""
    try:
        agent_id = await orchestrator.create_agent(
            name=request.name,
            agent_type=request.agent_type,
            requirements=request.requirements
        )
        agent = await orchestrator.get_agent(agent_id)
        return AgentResponse(
            agent_id=agent_id,
            status=agent["status"],
            resources=agent["resources"]
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create agent: {str(e)}"
        )

@app.delete("/agents/{agent_id}", response_model=AgentResponse)
async def destroy_agent(agent_id: str):
    """Destroy an agent with cleanup."""
    try:
        agent = await orchestrator.get_agent(agent_id)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found"
            )
            
        if await orchestrator.destroy_agent(agent_id):
            return AgentResponse(
                agent_id=agent_id,
                status="destroyed"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to destroy agent {agent_id}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    """Get agent details."""
    agent = await orchestrator.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    return AgentResponse(
        agent_id=agent_id,
        status=agent["status"],
        resources=agent["resources"]
    )

@app.get("/agents", response_model=List[AgentResponse])
async def list_agents():
    """List all agents."""
    agents = await orchestrator.list_agents()
    return [
        AgentResponse(
            agent_id=agent["agent_id"],
            status=agent["status"],
            resources=agent["resources"]
        )
        for agent in agents
    ]

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Control plane is operational"}
