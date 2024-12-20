# Testing LLM Agents

SmartHive utiliza [DeepEval](https://github.com/confident-ai/deepeval) para probar la calidad de las respuestas de los agentes LLM. Este documento explica cómo configurar y ejecutar los tests de LLM.

## Configuración

### 1. Requisitos
- OpenAI API Key
- Python 3.12+
- Poetry

### 2. Variables de Entorno
Copia el archivo `.env.example` a `.env` y configura las variables:

```bash
cp .env.example .env
```

Edita `.env` con tus credenciales:
```bash
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4-1106-preview  # o el modelo que prefieras
OPENAI_TEMPERATURE=0.0           # 0.0 para respuestas más deterministas
```

### 3. Instalación
```bash
# Instalar dependencias
poetry install

# Activar entorno virtual
poetry shell
```

## Ejecutando Tests

### Tests Unitarios
Los tests unitarios no requieren credenciales de OpenAI:
```bash
pytest tests/smart_hive/configs/test_openai_config.py -v
```

### Tests de LLM
Los tests de LLM requieren una API key de OpenAI:
```bash
# Ejecutar todos los tests de LLM
pytest tests/smart_hive/services/agents/test_llm.py -v

# Ejecutar un test específico
pytest tests/smart_hive/services/agents/test_llm.py::test_backend_agent_response -v
```

Los tests se saltarán automáticamente si no hay una API key configurada.

## Métricas de Evaluación

DeepEval proporciona varias métricas para evaluar las respuestas de los LLM:

### 1. Answer Relevancy (threshold=0.7)
Evalúa qué tan relevante es la respuesta a la pregunta del usuario.

### 2. Faithfulness (threshold=0.7)
Verifica que la respuesta sea fiel al contexto proporcionado y no contenga información falsa.

### 3. Contextual Relevancy (threshold=0.7)
Evalúa qué tan relevante es el contexto proporcionado para la pregunta.

## Añadiendo Nuevos Tests

Para añadir un nuevo test de LLM:

1. Crea un nuevo método de test con el fixture `openai_config`:
```python
@pytest.mark.asyncio
async def test_my_llm_feature(openai_config: OpenAIConfig):
    # Configura el test case
    test_case = LLMTestCase(
        input="pregunta",
        actual_output="respuesta",
        retrieval_context=["contexto relevante"]
    )

    # Configura las métricas
    metrics = [
        AnswerRelevancyMetric(
            threshold=0.7,
            openai_api_key=openai_config.api_key,
            model=openai_config.model,
            temperature=openai_config.temperature
        )
    ]

    # Ejecuta el test
    assert_test(test_case, metrics)
```

2. Ejecuta el test:
```bash
pytest path/to/test_file.py::test_my_llm_feature -v
```

## Mejores Prácticas

1. **Contexto Relevante**: Proporciona contexto específico y relevante para cada test.
2. **Thresholds**: Ajusta los thresholds según la criticidad del test.
3. **Determinismo**: Usa `temperature=0.0` para tests más deterministas.
4. **API Keys**: Nunca comitees API keys al repositorio.
5. **Tests Aislados**: Cada test debe ser independiente y limpiar sus recursos.
