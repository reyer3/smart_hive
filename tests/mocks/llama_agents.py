"""
Mock de llama-agents para tests
"""

class AgentService:
    """Mock de AgentService."""
    def __init__(self, description=None, service_name=None, llm=None):
        self.description = description
        self.service_name = service_name
        self.llm = llm

class ControlPlaneServer:
    """Mock de ControlPlaneServer."""
    def __init__(self, message_queue=None, agent_orchestrator=None):
        self.message_queue = message_queue
        self.agent_orchestrator = agent_orchestrator

class SimpleMessageQueue:
    """Mock de SimpleMessageQueue."""
    async def remove_subscriber(self, subscriber_id):
        return True

class AgentOrchestrator:
    """Mock de AgentOrchestrator."""
    def __init__(self, llm=None):
        self.llm = llm
        self._agents = {}
