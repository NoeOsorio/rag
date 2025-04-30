# Proyecto de Aprendizaje: Agentes de IA y RAG

Este proyecto es una implementación educativa para aprender sobre Agentes de IA y RAG (Retrieval-Augmented Generation). El objetivo es demostrar cómo se pueden combinar diferentes componentes para crear un sistema de IA que pueda procesar y responder preguntas sobre documentos específicos.

## Componentes del Proyecto

1. **gpt.py**: Implementa la interacción básica con la API de OpenAI para generar respuestas.
2. **file_manager.py**: Maneja la carga y procesamiento de documentos de texto.
3. **embeddings.py**: Implementa la generación de embeddings para búsqueda semántica.

## Requisitos para Ejecutar el Proyecto

1. **Python 3.8+**
2. **Dependencias**:
   - openai
   - python-dotenv
   - langchain

3. **Configuración**:
   - Crear un archivo `.env` en el directorio raíz con tu API key de OpenAI:
     ```
     OPENAI_API_KEY=tu_api_key_aquí
     ```

4. **Instalación de Dependencias**:
   ```bash
   pip install openai python-dotenv langchain
   ```

## Estructura del Proyecto

- `gpt.py`: Maneja la comunicación con la API de OpenAI
- `file_manager.py`: Gestiona la carga y procesamiento de documentos
- `embeddings.py`: Implementa la generación de embeddings para búsqueda semántica
- `file.txt`: Documento de ejemplo para pruebas

## Uso

1. Asegúrate de tener todas las dependencias instaladas
2. Configura tu archivo `.env` con tu API key de OpenAI
3. Ejecuta los scripts según sea necesario

## Notas de Aprendizaje

Este proyecto está diseñado para:
- Entender cómo funcionan los embeddings en el contexto de RAG
- Aprender a manejar documentos y extraer información relevante
- Implementar búsqueda semántica
- Integrar diferentes componentes de un sistema de IA

## Próximos Pasos

- Implementar un sistema de búsqueda semántica más robusto
- Agregar soporte para diferentes tipos de documentos
- Mejorar el sistema de recuperación de información
- Implementar un frontend para interacción más amigable 