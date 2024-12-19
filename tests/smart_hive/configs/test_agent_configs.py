"""
Tests for agent configurations
"""

import pytest
from smart_hive.configs.agent_configs import AGENT_CONFIGS, AGENT_VALIDATION

def test_agent_configs_structure():
    """Verificar que todas las configuraciones de agentes tienen la estructura correcta."""
    required_keys = {"name", "description", "requirements"}
    
    for agent_type, config in AGENT_CONFIGS.items():
        assert isinstance(config, dict), f"Config para {agent_type} debe ser un diccionario"
        assert all(key in config for key in required_keys), \
            f"Config para {agent_type} debe tener todas las claves requeridas: {required_keys}"

def test_resource_requirements():
    """Verificar que los requerimientos de recursos son válidos."""
    for agent_type, config in AGENT_CONFIGS.items():
        requirements = config["requirements"]
        assert isinstance(requirements, dict), \
            f"Requirements para {agent_type} debe ser un diccionario"
        assert "cpu" in requirements, f"Requirements para {agent_type} debe especificar CPU"
        assert "memory" in requirements, f"Requirements para {agent_type} debe especificar memoria"
        assert requirements["cpu"] > 0, f"CPU para {agent_type} debe ser positivo"
        assert requirements["memory"] > 0, f"Memoria para {agent_type} debe ser positiva"

def test_validation_rules():
    """Verificar reglas de validación."""
    assert "name_pattern" in AGENT_VALIDATION, "Debe existir patrón de validación de nombres"
    assert "max_instances" in AGENT_VALIDATION, "Debe existir límite de instancias"
    assert "default" in AGENT_VALIDATION["max_instances"], "Debe existir límite por defecto"
    assert AGENT_VALIDATION["max_instances"]["default"] > 0, "Límite por defecto debe ser positivo"
