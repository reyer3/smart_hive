# Testing Guide

## 1. Estrategia de Testing

### 1.1. Niveles de Testing
1. **Unit Testing**
   - Comportamiento individual de agentes
   - Funciones y utilidades
   - Componentes UI aislados

2. **Integration Testing**
   - Comunicación entre agentes
   - Flujos de trabajo completos
   - Interacción UI-Backend

3. **System Testing**
   - Comportamiento del enjambre completo
   - Escenarios end-to-end
   - Performance y carga

### 1.2. Herramientas
- **Unit Tests:** pytest, Jest
- **Integration:** pytest-asyncio, TestContainers
- **E2E:** Playwright
- **Mocking:** pytest-mock, jest-mock
- **Coverage:** pytest-cov, istanbul

## 2. Testing de Agentes

### 2.1. Unit Tests
```python
# test_backend_agent.py
class TestBackendAgent:
    @pytest.fixture
    def agent(self):
        return BackendAgent(domain="backend")

    async def test_process_task(self, agent):
        task = Task(
            type="CREATE_ENDPOINT",
            context={"path": "/api/users", "method": "GET"}
        )
        result = await agent.process(task)
        assert result.status == "SUCCESS"
        assert "endpoint_created" in result.data

    async def test_handoff(self, agent):
        task = Task(type="DATABASE_QUERY")
        result = await agent.process(task)
        assert result.status == "HANDOFF"
        assert result.target_agent == "database"
```

### 2.2. Integration Tests
```python
# test_agent_communication.py
class TestAgentCommunication:
    @pytest.fixture
    async def swarm(self):
        return await setup_test_swarm([
            BackendAgent(),
            DatabaseAgent(),
            QAAgent()
        ])

    async def test_task_delegation(self, swarm):
        task = ComplexTask(
            steps=[
                "create_endpoint",
                "setup_database",
                "run_tests"
            ]
        )
        result = await swarm.process_task(task)
        assert result.completed_steps == 3
        assert result.status == "SUCCESS"
```

## 3. Testing de UI

### 3.1. Component Tests
```typescript
// AgentWorkspace.test.tsx
describe('AgentWorkspace', () => {
    test('displays agent status', () => {
        const agent = mockAgent({
            status: 'processing',
            currentTask: 'Creating API endpoint'
        });
        
        const { getByText } = render(<AgentWorkspace agent={agent} />);
        expect(getByText('Creating API endpoint')).toBeInTheDocument();
    });

    test('handles task completion', async () => {
        const onComplete = jest.fn();
        const agent = mockAgent();
        
        const { getByRole } = render(
            <AgentWorkspace
                agent={agent}
                onTaskComplete={onComplete}
            />
        );
        
        await userEvent.click(getByRole('button', { name: 'Complete' }));
        expect(onComplete).toHaveBeenCalled();
    });
});
```

### 3.2. E2E Tests
```typescript
// agent-workflow.spec.ts
test('complete development workflow', async ({ page }) => {
    await page.goto('/workspace');
    
    // Iniciar nueva tarea
    await page.click('[data-testid="new-task"]');
    await page.fill('[data-testid="task-description"]', 
        'Create user registration API');
    
    // Verificar asignación de agentes
    await expect(page.locator('[data-testid="active-agents"]'))
        .toContainText(['BackendAgent', 'DatabaseAgent']);
    
    // Verificar completado
    await page.waitForSelector('[data-testid="task-complete"]');
    const files = await page.locator('[data-testid="generated-files"]')
        .allTextContents();
    expect(files).toContain('user.controller.ts');
});
```

## 4. Testing de Performance

### 4.1. Load Testing
```python
# test_swarm_performance.py
class TestSwarmPerformance:
    @pytest.mark.benchmark
    async def test_concurrent_tasks(self, swarm):
        tasks = [
            Task(type="CODE_REVIEW"),
            Task(type="API_DEVELOPMENT"),
            Task(type="DATABASE_OPTIMIZATION")
        ]
        
        start_time = time.time()
        results = await asyncio.gather(*[
            swarm.process_task(task)
            for task in tasks
        ])
        duration = time.time() - start_time
        
        assert duration < 5.0  # Max 5 segundos
        assert all(r.status == "SUCCESS" for r in results)
```

### 4.2. Memory Testing
```python
# test_memory_usage.py
class TestMemoryUsage:
    @pytest.mark.memory
    async def test_agent_memory_cleanup(self, agent):
        initial_memory = get_memory_usage()
        
        for _ in range(100):
            await agent.process_large_task()
            
        final_memory = get_memory_usage()
        diff = final_memory - initial_memory
        assert diff < 10_000_000  # Max 10MB de incremento
```

## 5. Mocking

### 5.1. Agent Mocks
```python
# conftest.py
@pytest.fixture
def mock_agent():
    class MockAgent:
        async def process(self, task):
            return Result(status="SUCCESS")
            
        async def handoff(self, task, target):
            return Result(status="HANDOFF")
    
    return MockAgent()

# test_orchestrator.py
async def test_orchestrator_delegation(mock_agent):
    orchestrator = OrchestratorAgent()
    orchestrator.register_agent("mock", mock_agent)
    
    result = await orchestrator.delegate_task(
        Task(type="TEST")
    )
    assert result.status == "SUCCESS"
```

### 5.2. External Services
```python
# test_external_services.py
class TestExternalServices:
    @pytest.fixture
    def mock_github(self):
        with aioresponses() as m:
            m.get(
                'https://api.github.com/repos/user/repo',
                payload={'id': 123}
            )
            yield m

    async def test_github_integration(self, mock_github, agent):
        result = await agent.fetch_repository_info(
            'user/repo'
        )
        assert result['id'] == 123
```

## 6. Cobertura y Calidad

### 6.1. Coverage Configuration
```ini
# pytest.ini
[pytest]
addopts = 
    --cov=smart_hive
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=90
```

### 6.2. Quality Checks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: poetry run pytest
        language: system
        types: [python]
        pass_filenames: false
        
      - id: type-check
        name: mypy
        entry: poetry run mypy
        language: system
        types: [python]
        pass_filenames: false
```

## 7. CI/CD Testing

### 7.1. GitHub Actions
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: |
          python -m pip install poetry
          poetry install
          
      - name: Run tests
        run: poetry run pytest
        
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

### 7.2. Test Environments
```python
# test_environments.py
class TestEnvironments:
    @pytest.mark.parametrize('env', ['dev', 'staging', 'prod'])
    async def test_environment_config(self, env):
        config = await load_config(env)
        assert config.database_url
        assert config.api_keys
        assert config.agent_configs
```

## 8. Debugging Tests

### 8.1. Logging Configuration
```python
# conftest.py
@pytest.fixture(autouse=True)
def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    yield
```

### 8.2. Debug Helpers
```python
class DebugHelpers:
    @staticmethod
    async def dump_agent_state(agent):
        return {
            'memory': agent.memory.usage(),
            'tasks': agent.task_queue.size(),
            'connections': agent.active_connections()
        }
    
    @staticmethod
    async def trace_task(task_id):
        return {
            'history': await get_task_history(task_id),
            'agents': await get_involved_agents(task_id),
            'duration': await get_task_duration(task_id)
        }