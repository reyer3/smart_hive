# ADR 001: Selección del Framework de Agentes

## Estado
Propuesto

## Contexto
Necesitamos seleccionar un framework para implementar el sistema multi-agente de SmartHive. Las opciones consideradas son:

1. **LangChain**
   - Framework maduro y bien establecido
   - Gran comunidad y documentación
   - Abstracción de múltiples LLMs
   - Herramientas para memoria y cadenas de razonamiento

2. **LlamaIndex (llama-agents)**
   - Arquitectura orientada a microservicios
   - Control plane centralizado
   - Monitoreo en tiempo real
   - Comunicación estandarizada vía API
   - Lanzamiento previsto: Junio 2024

3. **OpenAI Swarm**
   - Ligero y minimalista
   - Enfocado en orquestación de agentes
   - Basado en handoffs
   - Experimental y educacional
   - Acoplado a OpenAI

4. **CrewAI**
   - Enfocado en colaboración entre agentes
   - Roles y especialización
   - Más nuevo pero con conceptos interesantes

## Decisión
Proponemos usar **llama-agents** de LlamaIndex como framework principal por las siguientes razones:

1. **Arquitectura Orientada a Servicios**
   - Cada agente puede ser un microservicio independiente
   - Facilita el escalado y mantenimiento
   - Mejor aislamiento y resiliencia

2. **Control y Monitoreo**
   - Control plane centralizado para orquestación
   - Herramientas de monitoreo incluidas
   - Mejor observabilidad del sistema

3. **Flexibilidad**
   - Soporte para múltiples LLMs
   - Comunicación estandarizada
   - Patrones de orquestación flexibles

4. **Producción-Ready**
   - Diseñado para sistemas en producción
   - Escalabilidad incorporada
   - Gestión de recursos integrada

## Consecuencias

### Positivas
1. Arquitectura más robusta y escalable
2. Mejor monitoreo y observabilidad
3. Facilidad para cambiar entre diferentes LLMs
4. Mejor preparado para producción

### Negativas
1. Framework nuevo (alpha) con posibles cambios
2. Menor comunidad inicial
3. Documentación en desarrollo
4. Lanzamiento previsto para mediados de 2024

### Riesgos
1. Posibles cambios en la API antes del lanzamiento final
2. Necesidad de actualizar código con nuevas versiones
3. Bugs iniciales por ser versión alpha

## Alternativas Consideradas

### LangChain
- **Pros**: Maduro, gran comunidad, bien documentado
- **Contras**: Menos enfocado en sistemas multi-agente

### OpenAI Swarm
- **Pros**: Simple, fácil de entender
- **Contras**: Experimental, acoplado a OpenAI

### CrewAI
- **Pros**: Buenos conceptos de colaboración
- **Contras**: Menos maduro, menos funcionalidades

## Referencias
- [Anuncio de llama-agents](https://blog.llamaindex.ai/introducing-llama-agents-a-powerful-framework-for-building-production-multi-agent-ai-systems-3d13d952419c)
- [OpenAI Swarm](https://github.com/openai/swarm)
- [LangChain](https://www.langchain.com/)
- [CrewAI](https://www.crewai.io/)
