"""
Agent Configurations

Centralized configuration for all agent types in SmartHive.
"""

AGENT_CONFIGS = {
    "resource_manager": {
        "name": "resource_manager",
        "description": "Resource allocation and management service",
        "requirements": {
            "cpu": 1,
            "memory": 512
        }
    },
    "backend": {
        "name": "backend",
        "description": "Backend development and maintenance agent",
        "requirements": {
            "cpu": 2,
            "memory": 1024
        }
    },
    "database": {
        "name": "database",
        "description": "Database management and optimization agent",
        "requirements": {
            "cpu": 2,
            "memory": 1024,
            "storage": 5120
        }
    },
    "devops": {
        "name": "devops",
        "description": "Infrastructure and deployment agent",
        "requirements": {
            "cpu": 2,
            "memory": 1024
        }
    },
    "frontend": {
        "name": "frontend",
        "description": "Frontend development and UI/UX agent",
        "requirements": {
            "cpu": 1,
            "memory": 512
        }
    },
    "qa": {
        "name": "qa",
        "description": "Quality assurance and testing agent",
        "requirements": {
            "cpu": 1,
            "memory": 512
        }
    }
}

# Validation rules for agent creation
AGENT_VALIDATION = {
    "name_pattern": r"^[a-zA-Z0-9_-]+$",
    "max_instances": {
        "resource_manager": 1,  # Only one resource manager allowed
        "default": 5           # Default max instances per type
    },
    "required_fields": ["name", "agent_type"]
}
