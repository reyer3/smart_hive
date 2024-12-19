"""
State Manager Service

Basic state persistence for agents using llama-agents framework.
"""

from typing import Dict, Optional
from llama_agents import AgentService
from llama_index.llms.openai import OpenAI

from smart_hive.configs.agent_configs import AGENT_CONFIGS

class StateManager(AgentService):
    """
    Basic state manager for agent state persistence.
    """
    
    def __init__(self):
        config = AGENT_CONFIGS["resource_manager"]
        super().__init__(
            description=config["description"],
            service_name=config["name"],
            llm=OpenAI()
        )
        self.states: Dict[str, Dict] = {}

    async def save_state(self, agent_id: str, state: Dict):
        """Save agent state."""
        self.states[agent_id] = state
        return True

    async def load_state(self, agent_id: str) -> Optional[Dict]:
        """Load agent state."""
        return self.states.get(agent_id)

    async def delete_state(self, agent_id: str):
        """Delete agent state."""
        if agent_id in self.states:
            del self.states[agent_id]
            return True
        return False

    async def list_states(self) -> Dict[str, Dict]:
        """List all agent states."""
        return self.states

    async def clear(self):
        """Clear all states."""
        self.states = {}
