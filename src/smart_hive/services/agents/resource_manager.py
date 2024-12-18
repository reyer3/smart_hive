"""
Resource Manager Agent

This agent is responsible for managing system resources and ensuring optimal resource allocation
across all agents in the system.
"""

from typing import Dict, Any, Optional
from llama_agents import AgentConfig, AgentMetrics
from .base_agent import SmartHiveAgent

class ResourceManagerAgent(SmartHiveAgent):
    """
    Agent responsible for managing system resources.
    
    Capabilities:
    - Monitor system-wide resource usage
    - Allocate resources to agents
    - Enforce resource limits
    - Optimize resource distribution
    """

    def __init__(self, name: str = "resource_manager", config: Optional[AgentConfig] = None):
        """Initialize the resource manager agent."""
        super().__init__(
            name=name,
            agent_type="resource_manager",
            config=config
        )
        self.resource_allocations: Dict[str, Dict[str, float]] = {}
        self.system_metrics = AgentMetrics()

    async def initialize(self) -> None:
        """Initialize resource monitoring."""
        await super().initialize()
        # Initialize system metrics collection
        await self.system_metrics.initialize()

    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process resource-related messages.
        
        Supported actions:
        - allocate_resources: Allocate resources to an agent
        - release_resources: Release resources from an agent
        - get_usage: Get current resource usage
        - check_availability: Check resource availability
        """
        action = message.get("action")
        
        if action == "allocate_resources":
            return await self._handle_allocation(message)
        elif action == "release_resources":
            return await self._handle_release(message)
        elif action == "get_usage":
            return await self._handle_get_usage(message)
        elif action == "check_availability":
            return await self._handle_check_availability(message)
        
        return {
            "status": "error",
            "message": f"Unknown action: {action}"
        }

    async def _handle_allocation(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resource allocation requests."""
        agent_id = message.get("agent_id")
        requested_resources = message.get("resources", {})
        
        # Check if resources are available
        if not await self._check_resource_availability(requested_resources):
            return {
                "status": "error",
                "message": "Insufficient resources available"
            }
        
        # Allocate resources
        self.resource_allocations[agent_id] = requested_resources
        await self.system_metrics.record_allocation(agent_id, requested_resources)
        
        return {
            "status": "success",
            "message": "Resources allocated",
            "allocated": requested_resources
        }

    async def _handle_release(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resource release requests."""
        agent_id = message.get("agent_id")
        
        if agent_id not in self.resource_allocations:
            return {
                "status": "error",
                "message": "No resources allocated to agent"
            }
        
        released = self.resource_allocations.pop(agent_id)
        await self.system_metrics.record_release(agent_id, released)
        
        return {
            "status": "success",
            "message": "Resources released",
            "released": released
        }

    async def _handle_get_usage(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resource usage queries."""
        agent_id = message.get("agent_id")
        
        if agent_id:
            usage = self.resource_allocations.get(agent_id, {})
            return {
                "status": "success",
                "agent_id": agent_id,
                "usage": usage
            }
        
        # Return system-wide usage
        return {
            "status": "success",
            "system_usage": self.resource_allocations,
            "metrics": await self.system_metrics.get_current()
        }

    async def _handle_check_availability(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resource availability checks."""
        requested = message.get("resources", {})
        available = await self._check_resource_availability(requested)
        
        return {
            "status": "success",
            "available": available,
            "current_usage": await self.system_metrics.get_current()
        }

    async def _check_resource_availability(self, requested: Dict[str, float]) -> bool:
        """
        Check if requested resources are available.
        
        Args:
            requested: Dictionary of requested resources
            
        Returns:
            bool: True if resources are available
        """
        current_metrics = await self.system_metrics.get_current()
        
        # Check each resource type
        for resource, amount in requested.items():
            used = sum(alloc.get(resource, 0) for alloc in self.resource_allocations.values())
            capacity = current_metrics.get(f"total_{resource}", float('inf'))
            
            if used + amount > capacity:
                return False
        
        return True

    async def cleanup(self) -> None:
        """Cleanup resource manager."""
        # Release all allocations
        self.resource_allocations.clear()
        await self.system_metrics.cleanup()
        await super().cleanup()
