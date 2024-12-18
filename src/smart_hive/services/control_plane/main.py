"""
Control Plane Service

This module implements the central control plane for SmartHive using llama-agents.
"""

from fastapi import FastAPI, HTTPException
from llama_agents import (
    AgentService,
    ControlPlaneServer,
    SimpleMessageQueue,
    AgentOrchestrator,
)
from llama_index.llms.openai import OpenAI
from pydantic import BaseModel
from typing import Dict, List, Optional

from smart_hive.services.meta.archive import AgentArchive
from smart_hive.services.meta.prompt_engineer import PromptEngineer

app = FastAPI(title="SmartHive Control Plane")

class SmartHiveOrchestrator(AgentOrchestrator):
    """
    Custom orchestrator that integrates ADAS capabilities with llama-agents.
    """
    def __init__(self, llm=None):
        super().__init__(llm=llm or OpenAI())
        self.archive = AgentArchive()
        self.prompt_engineer = PromptEngineer()

    async def route_task(self, task, context=None):
        """
        Route tasks using ADAS insights and prompt engineering.
        """
        # Apply prompt engineering techniques
        enhanced_task = self.prompt_engineer.rag_enhance(
            task,
            context or {}
        )
        
        # Get historical patterns from archive
        patterns = self.archive.get_patterns(task)
        
        # Use Chain-of-Thought for routing
        reasoning = self.prompt_engineer.chain_of_thought(
            enhanced_task,
            {"patterns": patterns}
        )
        
        return await super().route_task(enhanced_task)

# Initialize components
message_queue = SimpleMessageQueue()
orchestrator = SmartHiveOrchestrator()
control_plane = ControlPlaneServer(
    message_queue=message_queue,
    orchestrator=orchestrator,
)

class AgentRequest(BaseModel):
    """Request model for agent operations."""
    name: str
    agent_type: str
    config: Optional[Dict] = None

@app.post("/agents")
async def create_agent(request: AgentRequest):
    """Create a new agent."""
    try:
        config = AgentService(**request.config) if request.config else AgentService()
        agent = await control_plane.create_agent(
            name=request.name,
            agent_type=request.agent_type,
            config=config
        )
        return {"agent_id": agent.id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/agents")
async def list_agents():
    """List all registered agents."""
    agents = await control_plane.list_agents()
    return {"agents": agents}

@app.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get agent details."""
    agent = await control_plane.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@app.post("/agents/{agent_id}/start")
async def start_agent(agent_id: str):
    """Start an agent."""
    try:
        await control_plane.start_agent(agent_id)
        return {"status": "started"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/agents/{agent_id}/stop")
async def stop_agent(agent_id: str):
    """Stop an agent."""
    try:
        await control_plane.stop_agent(agent_id)
        return {"status": "stopped"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
