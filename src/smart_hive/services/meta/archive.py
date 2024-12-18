"""
Agent Archive Module

This module implements the agent archive system for storing and retrieving successful agent
configurations and patterns, following the ADAS approach.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import json

class AgentMetrics(BaseModel):
    """Metrics for evaluating agent performance."""
    accuracy: float = 0.0
    response_time: float = 0.0
    resource_usage: float = 0.0
    code_quality: Optional[float] = None
    custom_metrics: Dict[str, float] = {}

class AgentConfiguration(BaseModel):
    """Configuration and performance record for an agent."""
    agent_type: str
    configuration: Dict[str, Any]
    metrics: AgentMetrics
    timestamp: datetime = datetime.utcnow()
    version: str
    tags: List[str] = []

class AgentArchive:
    """
    Stores and manages successful agent configurations.
    
    Features:
    - Storage of successful configurations
    - Pattern recognition
    - Configuration retrieval
    - Performance tracking
    """

    def __init__(self, storage_path: str = "data/agent_archive.json"):
        """Initialize the archive."""
        self.storage_path = storage_path
        self.configurations: Dict[str, List[AgentConfiguration]] = {}
        self._load_archive()

    def store(self, config: AgentConfiguration) -> None:
        """
        Store a successful configuration.
        
        Args:
            config: The configuration to store
        """
        if config.agent_type not in self.configurations:
            self.configurations[config.agent_type] = []
        
        self.configurations[config.agent_type].append(config)
        self._save_archive()

    def retrieve(
        self,
        agent_type: str,
        min_metrics: Optional[AgentMetrics] = None,
        tags: Optional[List[str]] = None
    ) -> List[AgentConfiguration]:
        """
        Retrieve configurations matching criteria.
        
        Args:
            agent_type: Type of agent to retrieve configs for
            min_metrics: Minimum required metrics
            tags: Required tags
            
        Returns:
            List[AgentConfiguration]: Matching configurations
        """
        if agent_type not in self.configurations:
            return []

        configs = self.configurations[agent_type]
        
        if min_metrics:
            configs = [
                c for c in configs
                if self._meets_metrics(c.metrics, min_metrics)
            ]
        
        if tags:
            configs = [
                c for c in configs
                if all(tag in c.tags for tag in tags)
            ]
        
        return sorted(
            configs,
            key=lambda x: self._calculate_score(x.metrics),
            reverse=True
        )

    def get_patterns(self, agent_type: str) -> Dict[str, Any]:
        """
        Extract common patterns from successful configurations.
        
        Args:
            agent_type: Type of agent to analyze
            
        Returns:
            Dict[str, Any]: Common patterns found
        """
        if agent_type not in self.configurations:
            return {}

        configs = self.configurations[agent_type]
        if not configs:
            return {}

        patterns = {
            "common_config": self._extract_common_config(configs),
            "performance_trends": self._analyze_performance(configs),
            "successful_patterns": self._identify_patterns(configs)
        }

        return patterns

    def _meets_metrics(self, actual: AgentMetrics, minimum: AgentMetrics) -> bool:
        """Check if metrics meet minimum requirements."""
        return (
            actual.accuracy >= minimum.accuracy and
            actual.response_time <= minimum.response_time and
            actual.resource_usage <= minimum.resource_usage and
            (minimum.code_quality is None or
             actual.code_quality is not None and
             actual.code_quality >= minimum.code_quality)
        )

    def _calculate_score(self, metrics: AgentMetrics) -> float:
        """Calculate an overall score for metrics."""
        # Customize weights based on importance
        weights = {
            "accuracy": 0.4,
            "response_time": 0.3,
            "resource_usage": 0.2,
            "code_quality": 0.1
        }

        score = (
            metrics.accuracy * weights["accuracy"] +
            (1 / (1 + metrics.response_time)) * weights["response_time"] +
            (1 / (1 + metrics.resource_usage)) * weights["resource_usage"]
        )

        if metrics.code_quality is not None:
            score += metrics.code_quality * weights["code_quality"]

        return score

    def _extract_common_config(
        self,
        configs: List[AgentConfiguration]
    ) -> Dict[str, Any]:
        """Extract common configuration patterns."""
        if not configs:
            return {}

        common = {}
        first = configs[0].configuration
        
        for key in first:
            values = [c.configuration.get(key) for c in configs]
            if all(v == values[0] for v in values):
                common[key] = values[0]

        return common

    def _analyze_performance(
        self,
        configs: List[AgentConfiguration]
    ) -> Dict[str, Any]:
        """Analyze performance trends."""
        if not configs:
            return {}

        trends = {
            "accuracy": {
                "avg": sum(c.metrics.accuracy for c in configs) / len(configs),
                "max": max(c.metrics.accuracy for c in configs),
                "min": min(c.metrics.accuracy for c in configs)
            },
            "response_time": {
                "avg": sum(c.metrics.response_time for c in configs) / len(configs),
                "best": min(c.metrics.response_time for c in configs)
            }
        }

        return trends

    def _identify_patterns(
        self,
        configs: List[AgentConfiguration]
    ) -> Dict[str, Any]:
        """Identify successful patterns in configurations."""
        if not configs:
            return {}

        # Sort by score
        scored_configs = [
            (c, self._calculate_score(c.metrics))
            for c in configs
        ]
        scored_configs.sort(key=lambda x: x[1], reverse=True)

        # Get top performing configurations
        top_configs = scored_configs[:min(3, len(scored_configs))]
        
        patterns = {
            "top_performers": [
                {
                    "config": c.configuration,
                    "score": score,
                    "metrics": c.metrics.dict()
                }
                for c, score in top_configs
            ]
        }

        return patterns

    def _load_archive(self) -> None:
        """Load archive from storage."""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                self.configurations = {
                    agent_type: [
                        AgentConfiguration(**config)
                        for config in configs
                    ]
                    for agent_type, configs in data.items()
                }
        except (FileNotFoundError, json.JSONDecodeError):
            self.configurations = {}

    def _save_archive(self) -> None:
        """Save archive to storage."""
        data = {
            agent_type: [
                config.dict()
                for config in configs
            ]
            for agent_type, configs in self.configurations.items()
        }
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
