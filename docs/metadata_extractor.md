# Extractor de Metadata de Libros

Esta herramienta analiza archivos de texto de libros y extrae automáticamente su metadata (título, autor y tema) utilizando GPT-4.

## Características

- Extrae metadata usando GPT-4
- Procesa múltiples archivos en lote
- Manejo automático de errores
- Evita reprocesar archivos ya analizados
- Guarda la metadata en formato JSON

## Requisitos

```bash
pip install langchain-openai
```

## Estructura de Directorios

```
.
├── text_books/       # Directorio con los archivos de texto a analizar
├── metadata/         # Directorio donde se guardan los archivos JSON con la metadata
├── infer_metadata_ai.py  # Script principal
└── docs/            # Documentación
```

## Uso

1. Asegúrate de tener configurada tu API key de OpenAI:
   ```bash
   export OPENAI_API_KEY='tu-api-key'
   ```
2. Ejecuta el script:
   ```bash
   python infer_metadata_ai.py
   ```
3. Los archivos JSON con la metadata se guardarán en `metadata/`

## Funcionamiento

El script realiza las siguientes operaciones:

1. Verifica la existencia del directorio `metadata/` y lo crea si es necesario
2. Busca todos los archivos `.txt` en el directorio `text_books/`
3. Para cada archivo de texto:
   - Verifica si ya existe un archivo de metadata correspondiente
   - Si no existe, analiza los primeros 1000 caracteres del texto
   - Utiliza GPT-4 para extraer título, autor y tema
   - Guarda la metadata en un archivo JSON
   - Muestra mensajes de progreso y errores si ocurren

## Formato de Metadata

Los archivos JSON de metadata tienen la siguiente estructura:
```json
{
  "title": "Título del libro",
  "author": "Nombre del autor",
  "topic": "Tema general del libro"
}
```

## Manejo de Errores

El script incluye manejo de errores para:
- Problemas de lectura de archivos
- Errores en la API de OpenAI
- Problemas al parsear respuestas JSON
- Problemas al guardar archivos JSON

## Notas

- Los archivos ya analizados se saltan automáticamente
- El proceso es no destructivo: los archivos originales no se modifican
- Se requiere una API key válida de OpenAI
- El análisis se realiza sobre los primeros 1000 caracteres del texto 