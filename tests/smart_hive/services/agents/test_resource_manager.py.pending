"""
Tests for ResourceManager
"""

import pytest
import sys
import os

# Mock imports
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../"))
from mocks.llama_agents import AgentService

from smart_hive.services.agents.resource_manager import ResourceManager

@pytest.fixture
def resource_manager():
    """Fixture para crear una instancia de ResourceManager."""
    return ResourceManager()

@pytest.mark.asyncio
async def test_resource_allocation(resource_manager):
    """Verificar asignación básica de recursos."""
    agent_id = "test_agent_1"
    requirements = {"cpu": 2, "memory": 1024}
    
    # Verificar asignación exitosa
    success = await resource_manager.allocate_resources(agent_id, requirements)
    assert success, "La asignación de recursos debe ser exitosa"
    
    # Verificar que los recursos fueron asignados correctamente
    status = await resource_manager.get_resource_status(agent_id)
    assert status is not None, "El estado de recursos debe existir"
    assert status["cpu"] == requirements["cpu"], "CPU asignada incorrectamente"
    assert status["memory"] == requirements["memory"], "Memoria asignada incorrectamente"
    assert status["status"] == "allocated", "Estado incorrecto"

@pytest.mark.asyncio
async def test_resource_deallocation(resource_manager):
    """Verificar liberación de recursos."""
    agent_id = "test_agent_2"
    requirements = {"cpu": 1, "memory": 512}
    
    # Asignar recursos
    await resource_manager.allocate_resources(agent_id, requirements)
    
    # Verificar liberación exitosa
    success = await resource_manager.deallocate_resources(agent_id)
    assert success, "La liberación de recursos debe ser exitosa"
    
    # Verificar que los recursos fueron liberados
    status = await resource_manager.get_resource_status(agent_id)
    assert status is None, "No debería haber recursos asignados después de liberar"

@pytest.mark.asyncio
async def test_duplicate_allocation(resource_manager):
    """Verificar que no se pueden asignar recursos dos veces al mismo agente."""
    agent_id = "test_agent_3"
    requirements = {"cpu": 1, "memory": 512}
    
    # Primera asignación
    success1 = await resource_manager.allocate_resources(agent_id, requirements)
    assert success1, "Primera asignación debe ser exitosa"
    
    # Segunda asignación debe fallar
    success2 = await resource_manager.allocate_resources(agent_id, requirements)
    assert not success2, "Segunda asignación debe fallar"

@pytest.mark.asyncio
async def test_default_requirements(resource_manager):
    """Verificar que se usan requerimientos por defecto cuando no se especifican."""
    agent_id = "test_agent_4"
    
    # Asignar sin requerimientos específicos
    success = await resource_manager.allocate_resources(agent_id, {})
    assert success, "La asignación con valores por defecto debe ser exitosa"
    
    # Verificar valores por defecto
    status = await resource_manager.get_resource_status(agent_id)
    assert status["cpu"] == 1, "CPU por defecto debe ser 1"
    assert status["memory"] == 512, "Memoria por defecto debe ser 512"
