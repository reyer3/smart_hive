"""
State Manager Service

Handles persistence and recovery of agent states.
"""

import json
import os
from typing import Dict, Optional
from pathlib import Path

class StateManager:
    """Manages persistent state for agents."""
    
    def __init__(self, state_dir: Optional[str] = None):
        self.state_dir = Path(state_dir or "/tmp/smart_hive/states")
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_state_file(self, agent_id: str) -> Path:
        """Get the state file path for an agent."""
        return self.state_dir / f"{agent_id}.json"
        
    async def save_state(self, agent_id: str, state: Dict) -> bool:
        """Save agent state to disk."""
        try:
            state_file = self._get_state_file(agent_id)
            with state_file.open('w') as f:
                json.dump(state, f)
            return True
        except Exception:
            return False
            
    async def load_state(self, agent_id: str) -> Optional[Dict]:
        """Load agent state from disk."""
        try:
            state_file = self._get_state_file(agent_id)
            if not state_file.exists():
                return None
            with state_file.open('r') as f:
                return json.load(f)
        except Exception:
            return None
            
    async def delete_state(self, agent_id: str) -> bool:
        """Delete agent state from disk."""
        try:
            state_file = self._get_state_file(agent_id)
            if state_file.exists():
                state_file.unlink()
            return True
        except Exception:
            return False
            
    async def list_states(self) -> Dict[str, Dict]:
        """List all saved agent states."""
        states = {}
        for state_file in self.state_dir.glob("*.json"):
            agent_id = state_file.stem
            state = await self.load_state(agent_id)
            if state:
                states[agent_id] = state
        return states
