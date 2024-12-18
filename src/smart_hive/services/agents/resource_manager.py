"""
Resource Manager Service

Basic resource management for agents using llama-agents framework.
"""

from typing import Dict, Optional
from llama_agents import AgentService
from llama_index.llms.openai import OpenAI

from smart_hive.configs.agent_configs import AGENT_CONFIGS

class ResourceManager(AgentService):
    """
    Basic resource manager for agent lifecycle management.
    """
    
    def __init__(self):
        config = AGENT_CONFIGS["resource_manager"]
        super().__init__(
            description=config["description"],
            service_name=config["name"],
            llm=OpenAI()
        )
        self.resource_allocations: Dict[str, Dict] = {}

    async def allocate_resources(self, agent_id: str, requirements: Dict):
        """Allocate resources to an agent."""
        if agent_id in self.resource_allocations:
            return False
            
        # Use default requirements from config if not specified
        agent_type = agent_id.split("_")[0]
        default_requirements = AGENT_CONFIGS.get(agent_type, {}).get("requirements", {})
        final_requirements = {**default_requirements, **requirements}
            
        self.resource_allocations[agent_id] = {
            "cpu": final_requirements.get("cpu", 1),
            "memory": final_requirements.get("memory", 512),
            "status": "allocated"
        }
        return True

    async def deallocate_resources(self, agent_id: str):
        """Clean up resources when an agent is destroyed."""
        if agent_id not in self.resource_allocations:
            return False
            
        del self.resource_allocations[agent_id]
        return True

    async def get_resource_status(self, agent_id: str) -> Optional[Dict]:
        """Get current resource allocation for an agent."""
        return self.resource_allocations.get(agent_id)
