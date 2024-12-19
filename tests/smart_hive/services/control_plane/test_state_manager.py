"""
Tests for StateManager
"""

import pytest
import tempfile
from pathlib import Path
import sys
import os

# Mock imports
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../"))
from mocks.llama_agents import AgentService

from smart_hive.services.control_plane.state_manager import StateManager

@pytest.fixture
def temp_state_dir():
    """Fixture para crear un directorio temporal para estados."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname

@pytest.fixture
def state_manager(temp_state_dir):
    """Fixture para crear una instancia de StateManager con directorio temporal."""
    return StateManager(state_dir=temp_state_dir)

@pytest.mark.asyncio
async def test_save_and_load_state(state_manager):
    """Verificar guardado y carga de estado."""
    agent_id = "test_agent_1"
    test_state = {
        "status": "running",
        "type": "worker",
        "resources": {"cpu": 1, "memory": 512}
    }
    
    # Guardar estado
    success = await state_manager.save_state(agent_id, test_state)
    assert success, "El guardado de estado debe ser exitoso"
    
    # Cargar estado
    loaded_state = await state_manager.load_state(agent_id)
    assert loaded_state == test_state, "El estado cargado debe ser igual al guardado"

@pytest.mark.asyncio
async def test_delete_state(state_manager):
    """Verificar eliminación de estado."""
    agent_id = "test_agent_2"
    test_state = {"status": "running"}
    
    # Guardar y luego eliminar estado
    await state_manager.save_state(agent_id, test_state)
    success = await state_manager.delete_state(agent_id)
    assert success, "La eliminación de estado debe ser exitosa"
    
    # Verificar que el estado fue eliminado
    loaded_state = await state_manager.load_state(agent_id)
    assert loaded_state is None, "No debe existir estado después de eliminarlo"

@pytest.mark.asyncio
async def test_list_states(state_manager):
    """Verificar listado de estados."""
    test_states = {
        "agent1": {"status": "running"},
        "agent2": {"status": "stopped"},
        "agent3": {"status": "paused"}
    }
    
    # Guardar varios estados
    for agent_id, state in test_states.items():
        await state_manager.save_state(agent_id, state)
    
    # Listar estados
    states = await state_manager.list_states()
    assert len(states) == len(test_states), "Debe listar todos los estados guardados"
    for agent_id, state in test_states.items():
        assert agent_id in states, f"Debe existir estado para {agent_id}"
        assert states[agent_id] == state, f"Estado incorrecto para {agent_id}"

@pytest.mark.asyncio
async def test_state_persistence(temp_state_dir):
    """Verificar que los estados persisten entre instancias."""
    agent_id = "test_agent_3"
    test_state = {"status": "running"}
    
    # Guardar estado con primera instancia
    manager1 = StateManager(state_dir=temp_state_dir)
    await manager1.save_state(agent_id, test_state)
    
    # Cargar estado con segunda instancia
    manager2 = StateManager(state_dir=temp_state_dir)
    loaded_state = await manager2.load_state(agent_id)
    assert loaded_state == test_state, "El estado debe persistir entre instancias"
