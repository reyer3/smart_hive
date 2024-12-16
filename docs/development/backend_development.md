# Guía de Desarrollo Backend para SmartHive

Esta guía describe cómo desarrollar y mantener la lógica del backend dentro del ecosistema **SmartHive**, incluyendo la configuración inicial, patrones de diseño, y mejores prácticas.

---

## 1. Configuración Inicial

### 1.1. Entorno de Desarrollo

1. **Requisitos:**
   - Python 3.12+
   - Framework seleccionado: FastAPI o Flask (opcional para tareas RESTful).
   - Gestor de dependencias: Poetry.

2. **Instalación de Dependencias:**
   Ejecuta el siguiente comando para instalar las dependencias definidas en `pyproject.toml`:
   ```bash
   poetry install
   ```

3. **Configuración del Entorno:**
   - Crea un archivo `.env` en la raíz del proyecto con las variables necesarias (por ejemplo, base de datos, claves API).
   - Ejemplo:
     ```env
     DATABASE_URL=postgresql://user:password@localhost/smarthive
     SECRET_KEY=tu_clave_secreta
     DEBUG=True
     ```

4. **Ejecución del Servidor de Desarrollo:**
   Si utilizas FastAPI:
   ```bash
   poetry run uvicorn src.smart_hive.main:app --reload
   ```

---

## 2. Organización del Código

### 2.1. Estructura del Backend

El backend sigue una estructura modular basada en DDD (Domain-Driven Design):

```plaintext
src/smart_hive/
├── configs/         # Configuración global
│   ├── agents/      # Agentes especializados
│   ├── data/        # Variables y esquemas compartidos
│   └── tools/       # Herramientas de soporte
├── main.py          # Punto de entrada principal
├── models/          # Definición de modelos y entidades
├── repositories/    # Gestión de persistencia y bases de datos
├── services/        # Lógica de negocio
└── api/             # Endpoints y controladores
```

### 2.2. Ejemplo de Organización

- **models/property.py**:
  ```python
  from pydantic import BaseModel

  class Property(BaseModel):
      id: int
      title: str
      description: str
      price: float
      available: bool
  ```

- **repositories/property_repository.py**:
  ```python
  from typing import List
  from models.property import Property

  class PropertyRepository:
      def get_all(self) -> List[Property]:
          # Implementar lógica para recuperar propiedades
          pass

      def get_by_id(self, property_id: int) -> Property:
          # Implementar lógica para recuperar una propiedad por ID
          pass
  ```

- **services/property_service.py**:
  ```python
  from repositories.property_repository import PropertyRepository

  class PropertyService:
      def __init__(self):
          self.repository = PropertyRepository()

      def list_properties(self):
          return self.repository.get_all()
  ```

- **api/property_controller.py**:
  ```python
  from fastapi import APIRouter
  from services.property_service import PropertyService

  router = APIRouter()
  service = PropertyService()

  @router.get("/properties")
  def list_properties():
      return service.list_properties()
  ```

---

## 3. Patrones de Diseño

### 3.1. Domain-Driven Design (DDD)
Organiza el código en dominios independientes para garantizar escalabilidad y mantenibilidad.

- **Agregados:** Clases principales que representan objetos de negocio.
- **Entidades:** Objetos con una identidad única.
- **Objetos de Valor:** Representan conceptos sin identidad única.

### 3.2. Separación de Responsabilidades
- **Repositorios:** Se encargan de acceder a la base de datos.
- **Servicios:** Implementan la lógica de negocio.
- **Controladores:** Manejan las solicitudes HTTP y delegan a los servicios.

---

## 4. Buenas Prácticas

1. **Validación de Datos:**
   - Usa Pydantic para validar los datos de entrada y salida.
2. **Pruebas Automatizadas:**
   - Implementa pruebas unitarias con Pytest para servicios y repositorios.
3. **Logs y Monitoreo:**
   - Configura un sistema de logs para registrar errores y eventos importantes.
4. **Gestión de Errores:**
   - Maneja errores utilizando excepciones personalizadas.
   ```python
   class PropertyNotFoundError(Exception):
       def __init__(self, property_id):
           self.message = f"Property with ID {property_id} not found"
           super().__init__(self.message)
   ```

---

## 5. Próximos Pasos

1. Crear endpoints adicionales para CRUD de propiedades.
2. Implementar autenticación y autorización.
3. Configurar integración con otros agentes (FrontendAgent, QAAgent).

---

Esta guía será actualizada conforme se desarrollen nuevas funcionalidades en el backend de **SmartHive**.

