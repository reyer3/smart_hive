"""
Demo script to test SmartHive Control Plane functionality in a real scenario.
"""

import asyncio
import logging
from fastapi import FastAPI
from fastapi.testclient import TestClient

from smart_hive.services.control_plane.main import (
    SmartHiveOrchestrator,
    AgentRequest,
    set_orchestrator,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Run a demo of the control plane functionality."""
    # Initialize FastAPI app and components
    app = FastAPI()
    orchestrator = SmartHiveOrchestrator()
    set_orchestrator(orchestrator)
    
    try:
        # Create an agent
        logger.info("Creating agent...")
        agent_request = AgentRequest(
            name="demo_agent",
            agent_type="backend",
            requirements={"cpu": 1, "memory": 512}
        )
        agent_id = await orchestrator.create_agent(agent_request)
        logger.info(f"Agent created with ID: {agent_id}")

        # Get agent status
        logger.info("\nGetting agent status...")
        agent = await orchestrator.get_agent(agent_id)
        logger.info(f"Agent status: {agent}")

        # List all agents
        logger.info("\nListing all agents...")
        agents = await orchestrator.list_agents()
        logger.info(f"Agents list: {agents}")

        # Destroy the agent
        logger.info("\nDestroying agent...")
        await orchestrator.destroy_agent(agent_id)
        logger.info("Agent destroyed successfully")

        # Verify agent is gone
        logger.info("\nVerifying agent is gone...")
        agents = await orchestrator.list_agents()
        assert len(agents) == 0, f"Expected no agents, but found: {agents}"
        logger.info("No agents found, as expected")

    except Exception as e:
        logger.error(f"Demo failed: {e}")
        raise
    else:
        logger.info("\nDemo completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
