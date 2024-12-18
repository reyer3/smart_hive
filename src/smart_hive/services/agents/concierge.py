"""
Concierge Agent Service

This module implements the concierge agent that handles user interactions.
"""

from llama_agents import AgentService
from llama_index.llms.openai import OpenAI

from smart_hive.services.meta.prompt_engineer import PromptEngineer

class ConciergeAgent(AgentService):
    """
    Main interaction agent that handles user requests and coordinates with other agents.
    """
    
    def __init__(self, name="concierge"):
        super().__init__(
            description="Main user interaction agent",
            service_name=name,
            llm=OpenAI()
        )
        self.prompt_engineer = PromptEngineer()

    async def process_message(self, message):
        """Process incoming user messages."""
        # Apply prompt engineering
        enhanced_message = self.prompt_engineer.rag_enhance(
            message.content,
            message.context
        )
        
        # Use Chain-of-Thought for understanding
        understanding = self.prompt_engineer.chain_of_thought(
            enhanced_message,
            message.context
        )
        
        return {
            "type": "response",
            "content": understanding.conclusion,
            "next_steps": understanding.steps
        }
