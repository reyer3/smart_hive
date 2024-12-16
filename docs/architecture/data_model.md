# Modelo de Datos

## 1. Entidades Core

### 1.1. Agent
```python
class Agent:
    id: UUID
    type: AgentType
    name: str
    domain: str
    capabilities: List[Capability]
    status: AgentStatus
    created_at: datetime
    updated_at: datetime
```

### 1.2. Task
```python
class Task:
    id: UUID
    type: TaskType
    priority: int
    status: TaskStatus
    creator_id: UUID
    assigned_agent_id: UUID
    parent_task_id: Optional[UUID]
    context: Dict
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
```

### 1.3. Interaction
```python
class Interaction:
    id: UUID
    user_id: UUID
    agent_id: UUID
    type: InteractionType
    content: Dict
    context: Dict
    feedback: Optional[Feedback]
    created_at: datetime
```

## 2. Modelos de Aprendizaje

### 2.1. UserPreference
```python
class UserPreference:
    id: UUID
    user_id: UUID
    category: PreferenceCategory
    key: str
    value: Any
    confidence: float
    last_updated: datetime
```

### 2.2. Pattern
```python
class Pattern:
    id: UUID
    type: PatternType
    context: Dict
    frequency: int
    confidence: float
    created_at: datetime
    updated_at: datetime
```

### 2.3. Feedback
```python
class Feedback:
    id: UUID
    interaction_id: UUID
    type: FeedbackType
    rating: int
    comments: Optional[str]
    created_at: datetime
```

## 3. Comunicación

### 3.1. Message
```python
class Message:
    id: UUID
    sender_id: UUID
    receiver_id: UUID
    type: MessageType
    content: Dict
    priority: int
    status: MessageStatus
    created_at: datetime
    delivered_at: Optional[datetime]
```

### 3.2. Event
```python
class Event:
    id: UUID
    type: EventType
    source_id: UUID
    data: Dict
    created_at: datetime
```

## 4. Estado y Contexto

### 4.1. AgentState
```python
class AgentState:
    id: UUID
    agent_id: UUID
    memory_usage: int
    task_queue_size: int
    active_tasks: List[UUID]
    last_heartbeat: datetime
```

### 4.2. Context
```python
class Context:
    id: UUID
    type: ContextType
    scope: ContextScope
    data: Dict
    created_at: datetime
    expires_at: Optional[datetime]
```

## 5. Configuración

### 5.1. AgentConfig
```python
class AgentConfig:
    id: UUID
    agent_id: UUID
    settings: Dict
    plugins: List[str]
    version: str
    updated_at: datetime
```

### 5.2. SystemConfig
```python
class SystemConfig:
    id: UUID
    key: str
    value: Any
    environment: str
    updated_at: datetime
```

## 6. Monitoreo

### 6.1. Metric
```python
class Metric:
    id: UUID
    type: MetricType
    source_id: UUID
    value: float
    timestamp: datetime
```

### 6.2. Log
```python
class Log:
    id: UUID
    level: LogLevel
    source_id: UUID
    message: str
    context: Dict
    timestamp: datetime
```

## 7. Seguridad

### 7.1. Permission
```python
class Permission:
    id: UUID
    name: str
    description: str
    scope: str
    created_at: datetime
```

### 7.2. Role
```python
class Role:
    id: UUID
    name: str
    permissions: List[UUID]
    created_at: datetime
```

## 8. Relaciones

### 8.1. Principales Relaciones
- Agent -> Tasks (1:N)
- Task -> Subtasks (1:N)
- User -> Preferences (1:N)
- Agent -> State (1:1)
- Message -> Events (1:N)

### 8.2. Índices Recomendados
1. Agent Queries
   - agent_id + status
   - domain + capabilities
   
2. Task Queries
   - status + priority
   - assigned_agent_id + status
   
3. Interaction Queries
   - user_id + created_at
   - agent_id + type

## 9. Consideraciones de Escalabilidad

### 9.1. Particionamiento
- Logs por fecha
- Métricas por agente
- Mensajes por timestamp

### 9.2. Caché
- Preferencias de usuario
- Estado de agentes
- Configuraciones activas