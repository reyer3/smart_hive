"""
Configuración global para tests
"""

import os
import sys
import pytest

# Agregar directorio de mocks al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "mocks"))

# Patch llama_agents
import llama_agents
