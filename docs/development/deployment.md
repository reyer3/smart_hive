# Deployment Guide

## 1. Arquitectura de Deployment

### 1.1. Componentes
```plaintext
SmartHive Deployment
├── Control Plane
│   ├── Message Queue
│   ├── Orchestrator
│   └── Monitor
├── Agent Services
│   ├── ResourceManager
│   ├── TaskCoordinator
│   ├── ErrorHandler
│   ├── Backend
│   ├── Frontend
│   └── QA
├── Infrastructure
│   ├── API Gateway
│   ├── Load Balancer
│   └── Service Discovery
└── Storage
    ├── Vector Store
    ├── Document Store
    └── Message Store
```

### 1.2. Tecnologías
- **Framework:** llama-agents
- **Containerization:** Docker
- **Orchestration:** Kubernetes
- **CI/CD:** GitHub Actions
- **Monitoring:** llama-agents monitor + Prometheus + Grafana
- **Logging:** ELK Stack

## 2. Configuración de Servicios

### 2.1. Control Plane
```python
# control_plane.py
from llama_agents import ControlPlaneServer, AgentOrchestrator, SimpleMessageQueue
from llama_index.llms.openai import OpenAI

def setup_control_plane():
    message_queue = SimpleMessageQueue()
    control_plane = ControlPlaneServer(
        message_queue=message_queue,
        orchestrator=AgentOrchestrator(llm=OpenAI())
    )
    return control_plane, message_queue
```

### 2.2. Agent Service
```python
# agent_service.py
from llama_agents import AgentService
from llama_index.core.agent import FunctionCallingAgentWorker

def create_agent_service(name: str, description: str, tools: list):
    worker = FunctionCallingAgentWorker.from_tools(tools, llm=OpenAI())
    agent = worker.as_agent()
    
    return AgentService(
        agent=agent,
        message_queue=message_queue,
        description=description,
        service_name=name
    )
```

## 3. Containerización

### 3.1. Base Image
```dockerfile
# Dockerfile.base
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copiar código
COPY smart_hive/ ./smart_hive/
```

### 3.2. Service Images
```dockerfile
# Dockerfile.control-plane
FROM smarthive/base:latest

ENV SERVICE_TYPE=control-plane
EXPOSE 8000

CMD ["python", "-m", "smart_hive.services.control_plane"]

# Dockerfile.agent-service
FROM smarthive/base:latest

ARG SERVICE_NAME
ENV SERVICE_NAME=${SERVICE_NAME}
EXPOSE 8080

CMD ["python", "-m", "smart_hive.services.agent_service"]
```

## 4. Kubernetes Configuration

### 4.1. Control Plane Deployment
```yaml
# control-plane-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: control-plane
spec:
  replicas: 1
  selector:
    matchLabels:
      app: control-plane
  template:
    metadata:
      labels:
        app: control-plane
    spec:
      containers:
      - name: control-plane
        image: smarthive/control-plane:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: llm-secrets
              key: openai-api-key
```

### 4.2. Agent Service Deployment
```yaml
# agent-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${SERVICE_NAME}
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ${SERVICE_NAME}
  template:
    metadata:
      labels:
        app: ${SERVICE_NAME}
    spec:
      containers:
      - name: ${SERVICE_NAME}
        image: smarthive/agent-service:latest
        ports:
        - containerPort: 8080
        env:
        - name: SERVICE_NAME
          value: ${SERVICE_NAME}
        - name: CONTROL_PLANE_URL
          value: http://control-plane:8000
```

## 5. Monitoreo

### 5.1. llama-agents Monitor
```bash
# Iniciar monitor
llama-agents monitor --control-plane-url http://localhost:8000
```

### 5.2. Prometheus Metrics
```yaml
# prometheus-config.yaml
scrape_configs:
  - job_name: 'smart-hive'
    static_configs:
      - targets: ['control-plane:8000']
    metrics_path: '/metrics'
```

## 6. Deployment Scripts

### 6.1. Deploy All Services
```bash
#!/bin/bash
# deploy.sh

# Deploy Control Plane
kubectl apply -f k8s/control-plane/

# Deploy Agent Services
for service in resource-manager task-coordinator error-handler backend frontend qa; do
    envsubst < k8s/templates/agent-service.yaml | kubectl apply -f -
done

# Deploy Monitoring
kubectl apply -f k8s/monitoring/
```

### 6.2. Scale Services
```bash
#!/bin/bash
# scale.sh

# Scale specific service
kubectl scale deployment ${SERVICE_NAME} --replicas=${REPLICAS}

# Auto-scaling
kubectl apply -f k8s/templates/hpa.yaml
```

## 7. CI/CD Pipeline

### 7.1. GitHub Actions Workflow
```yaml
# .github/workflows/deploy.yml
name: Deploy SmartHive

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build Images
        run: |
          docker build -t smarthive/base -f Dockerfile.base .
          docker build -t smarthive/control-plane -f Dockerfile.control-plane .
          for service in resource-manager task-coordinator error-handler backend frontend qa; do
            docker build -t smarthive/agent-service:${service} \
              --build-arg SERVICE_NAME=${service} \
              -f Dockerfile.agent-service .
          done
      
      - name: Deploy to K8s
        run: ./scripts/deploy.sh
```

### 7.2. Rollback Procedure
```bash
#!/bin/bash
# rollback.sh

# Rollback to previous version
kubectl rollout undo deployment/${SERVICE_NAME}

# Verify rollback
kubectl rollout status deployment/${SERVICE_NAME}