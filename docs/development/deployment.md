# Deployment Guide

## 1. Arquitectura de Deployment

### 1.1. Componentes
```plaintext
SmartHive Deployment
├── Agent Swarm
│   ├── OrchestratorAgent
│   ├── BackendAgent
│   ├── FrontendAgent
│   ├── DatabaseAgent
│   ├── QAAgent
│   └── DevOpsAgent
├── Infrastructure
│   ├── API Gateway
│   ├── Load Balancer
│   ├── Message Queue
│   └── Monitoring
└── Storage
    ├── PostgreSQL
    ├── Redis
    └── Object Storage
```

### 1.2. Tecnologías
- **Containerization:** Docker
- **Orchestration:** Kubernetes
- **CI/CD:** GitHub Actions
- **Monitoring:** Prometheus + Grafana
- **Logging:** ELK Stack

## 2. Configuración de Contenedores

### 2.1. Base Image
```dockerfile
# Dockerfile.agent
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copiar archivos del proyecto
COPY pyproject.toml poetry.lock ./
COPY src/ ./src/

# Instalar dependencias
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Script de inicio
COPY scripts/start-agent.sh ./
RUN chmod +x start-agent.sh

ENTRYPOINT ["./start-agent.sh"]
```

### 2.2. Agent-Specific Images
```dockerfile
# Dockerfile.backend-agent
FROM smarthive/base-agent:latest

ENV AGENT_TYPE=backend
ENV AGENT_CONFIG=/etc/smarthive/backend-config.yaml

COPY configs/backend-config.yaml /etc/smarthive/

CMD ["backend"]
```

## 3. Kubernetes Configuration

### 3.1. Agent Deployment
```yaml
# agent-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend-agent
  template:
    metadata:
      labels:
        app: backend-agent
    spec:
      containers:
      - name: backend-agent
        image: smarthive/backend-agent:latest
        env:
        - name: ORCHESTRATOR_URL
          value: "http://orchestrator-service:8000"
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis-credentials
              key: url
        resources:
          requests:
            memory: "256Mi"
            cpu: "200m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### 3.2. Service Configuration
```yaml
# agent-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-agent-service
spec:
  selector:
    app: backend-agent
  ports:
  - port: 8080
    targetPort: 8080
  type: ClusterIP
```

## 4. Monitoreo y Logging

### 4.1. Prometheus Configuration
```yaml
# prometheus-config.yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'agent-metrics'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        regex: .*agent.*
        action: keep
```

### 4.2. Grafana Dashboard
```json
{
  "dashboard": {
    "panels": [
      {
        "title": "Agent Memory Usage",
        "type": "graph",
        "datasource": "Prometheus",
        "targets": [
          {
            "expr": "agent_memory_usage_bytes",
            "legendFormat": "{{agent_type}}"
          }
        ]
      },
      {
        "title": "Task Processing Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(tasks_processed_total[5m])",
            "legendFormat": "{{agent_type}}"
          }
        ]
      }
    ]
  }
}
```

## 5. Escalamiento

### 5.1. Horizontal Pod Autoscaling
```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-agent-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend-agent
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### 5.2. Vertical Pod Autoscaling
```yaml
# vpa.yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: backend-agent-vpa
spec:
  targetRef:
    apiVersion: "apps/v1"
    kind: Deployment
    name: backend-agent
  updatePolicy:
    updateMode: "Auto"
```

## 6. Backup y Recuperación

### 6.1. Backup Configuration
```yaml
# backup-cronjob.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: agent-state-backup
spec:
  schedule: "0 */6 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: smarthive/backup-tool:latest
            env:
            - name: BACKUP_PATH
              value: "/backups"
            - name: S3_BUCKET
              value: "smarthive-backups"
          restartPolicy: OnFailure
```

### 6.2. Recovery Procedure
```bash
#!/bin/bash
# restore-agent-state.sh

# Detener agentes
kubectl scale deployment --all --replicas=0 -n smarthive

# Restaurar datos
kubectl exec -it backup-restore -- ./restore.sh \
    --backup-id="latest" \
    --target-namespace="smarthive"

# Reiniciar agentes
kubectl scale deployment --all --replicas=1 -n smarthive
```

## 7. CI/CD Pipeline

### 7.1. Build y Test
```yaml
# .github/workflows/build.yml
name: Build and Test
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build Agent Images
        run: |
          docker-compose build
          
      - name: Run Tests
        run: |
          docker-compose run tests
          
      - name: Push Images
        if: github.ref == 'refs/heads/main'
        run: |
          docker-compose push
```

### 7.2. Deployment
```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]
    
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Configure kubectl
        uses: azure/k8s-set-context@v1
        with:
          kubeconfig: ${{ secrets.KUBE_CONFIG }}
          
      - name: Deploy to Kubernetes
        run: |
          kubectl apply -f k8s/
          kubectl rollout status deployment/backend-agent
```

## 8. Mantenimiento

### 8.1. Health Checks
```yaml
# health-check-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: health-check-config
data:
  config.yaml: |
    endpoints:
      - name: backend-agent
        url: http://backend-agent-service:8080/health
        interval: 30s
        timeout: 5s
      - name: orchestrator
        url: http://orchestrator-service:8000/health
        interval: 15s
        timeout: 3s
```

### 8.2. Actualización de Agentes
```bash
#!/bin/bash
# update-agents.sh

# Actualizar imágenes
docker-compose pull

# Actualizar deployments
kubectl set image deployment/backend-agent \
    backend-agent=smarthive/backend-agent:latest

# Verificar rollout
kubectl rollout status deployment/backend-agent