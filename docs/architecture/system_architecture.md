# Documentación del Proyecto SmartHive

El proyecto **SmartHive** es un ecosistema de agentes multiuso diseñado para automatizar y optimizar tareas relacionadas con el desarrollo y mantenimiento de software en el contexto de una agencia inmobiliaria. Esta documentación proporciona una guía para entender y trabajar con su arquitectura y componentes.

---

## 1. Arquitectura del Sistema

El sistema se organiza siguiendo una arquitectura orientada a microservicios utilizando el framework llama-agents. Las carpetas principales incluyen:

### 1.1. Estructura General
```plaintext
.
├── README.md
├── pyproject.toml
├── smart_hive
│   ├── services
│   │   ├── resource_manager
│   │   ├── task_coordinator
│   │   ├── error_handler
│   │   ├── backend
│   │   ├── frontend
│   │   └── qa
│   ├── core
│   │   ├── control_plane
│   │   ├── message_queue
│   │   └── monitor
│   ├── config
│   │   ├── agents
│   │   └── services
│   └── main.py
├── docs
│   ├── architecture
│   ├── development
│   ├── roadmap
│   └── workflows
└── tests
```

### 1.2. Descripción de Carpetas

- **services/**: Servicios independientes, cada uno con su propia lógica y responsabilidades
- **core/**: Componentes centrales del sistema (control plane, message queue)
- **config/**: Configuraciones para agentes y servicios
- **docs/**: Documentación estructurada del sistema
- **tests/**: Pruebas unitarias y de integración

### 1.3. Arquitectura de Microservicios

La arquitectura está diseñada como un conjunto de servicios independientes que se comunican a través de un message queue centralizado:

#### Control Plane
```python
from llama_agents import ControlPlaneServer, AgentOrchestrator

control_plane = ControlPlaneServer(
    message_queue=message_queue,
    orchestrator=AgentOrchestrator(llm=OpenAI())
)
```

#### Servicios Base
- **ResourceManagerService**: Gestión de recursos computacionales
- **TaskCoordinatorService**: Coordinación de tareas
- **ErrorHandlerService**: Manejo de errores y recuperación

#### Servicios Especializados
- **BackendService**: Desarrollo backend
- **FrontendService**: Desarrollo frontend
- **QAService**: Testing y calidad

---

## 2. Comunicación entre Servicios

### 2.1. Message Queue
```python
from llama_agents import SimpleMessageQueue

message_queue = SimpleMessageQueue()
```

### 2.2. API Interfaces
- REST APIs para comunicación síncrona
- Webhooks para eventos asíncronos
- GraphQL para consultas complejas

---

## 3. Monitoreo y Observabilidad

### 3.1. Monitor CLI
```bash
llama-agents monitor --control-plane-url http://localhost:8000
```

### 3.2. Métricas y Alertas
- Latencia de procesamiento
- Uso de recursos
- Tasa de éxito/error
- Transferencias entre agentes

---

## 4. Despliegue y Escalabilidad

### 4.1. Despliegue de Servicios
```python
from llama_agents import ServerLauncher

launcher = ServerLauncher(
    [service1, service2],
    control_plane,
    message_queue
)
```

### 4.2. Estrategias de Escalado
- Escalado horizontal de servicios
- Balanceo de carga
- Auto-scaling basado en carga

---

## 5. Seguridad

### 5.1. Autenticación y Autorización
- Autenticación de servicios
- Control de acceso basado en roles
- Auditoría de acciones

### 5.2. Comunicación Segura
- TLS para todas las comunicaciones
- Cifrado de datos sensibles
- Validación de mensajes
