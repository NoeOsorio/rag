# Procesador de Libros (process_books.py)

## Descripción
Este script es una herramienta de orquestación que automatiza el proceso completo de conversión de libros EPUB a una base de datos vectorial. El proceso incluye la conversión de EPUB a texto, la extracción de metadata usando IA, y el almacenamiento en una base de datos vectorial ChromaDB para búsquedas semánticas.

## Características Principales
- Conversión automática de archivos EPUB a texto
- Extracción de metadata usando GPT-4
- Almacenamiento en base de datos vectorial ChromaDB
- Sistema de logging detallado con indicadores de progreso
- Manejo de errores robusto
- Prevención de duplicados
- Interfaz visual con Rich

## Estructura de Directorios
El script utiliza y crea automáticamente la siguiente estructura de directorios:
```
.
├── ebooks/           # Directorio para archivos EPUB originales
├── text_books/       # Directorio para archivos de texto convertidos
├── metadata/         # Directorio para archivos de metadata
└── books_db/         # Directorio para la base de datos vectorial
```

## Requisitos
- Python 3.8+
- Dependencias:
  - chromadb
  - rich
  - langchain
  - langchain_openai
  - ebooklib
  - beautifulsoup4

## Uso
1. Coloca tus archivos EPUB en el directorio `ebooks/`
2. Ejecuta el script:
```bash
python process_books.py
```

## Proceso de Ejecución
El script ejecuta tres fases principales:

### 1. Fase de Conversión
- Convierte archivos EPUB a texto plano
- Guarda los archivos de texto en `text_books/`
- Salta archivos ya convertidos

### 2. Fase de Extracción de Metadata
- Analiza los primeros 1000 caracteres de cada libro
- Extrae título, autor y tema usando GPT-4
- Guarda la metadata en archivos JSON en `metadata/`
- Salta archivos ya analizados

### 3. Fase de Carga en Base de Datos
- Inicializa o conecta a la base de datos ChromaDB
- Verifica libros existentes
- Carga nuevos libros en la base de datos
- Salta libros ya existentes

## Manejo de Errores
El script incluye manejo de errores para:
- Archivos EPUB corruptos o ilegibles
- Fallos en la extracción de metadata
- Errores de conexión con la base de datos
- Problemas de permisos de archivos

## Salida
El script proporciona:
- Indicadores de progreso en tiempo real
- Mensajes de estado detallados
- Resumen final del proceso
- Lista de archivos procesados y errores

## Base de Datos
- Utiliza ChromaDB como base de datos vectorial
- Almacena el texto completo de cada libro
- Incluye metadata (título, autor, tema)
- Persiste los datos entre ejecuciones
- Usa similitud coseno para búsquedas

## Notas Importantes
- La base de datos se mantiene entre ejecuciones
- Los archivos ya procesados se saltan automáticamente
- Se requiere una clave de API de OpenAI para la extracción de metadata
- El proceso puede ser lento para libros grandes

## Ejemplo de Uso
```python
from process_books import process_books

# Ejecutar el proceso completo
process_books()
```

## Mantenimiento
- La base de datos se guarda en `books_db/`
- Los archivos intermedios se mantienen para referencia
- Se pueden eliminar los archivos intermedios sin afectar la base de datos

## Limitaciones
- Requiere conexión a internet para la extracción de metadata
- El tamaño de la base de datos crece con cada libro
- La extracción de metadata tiene un costo asociado con OpenAI

## Contribución
Para contribuir al proyecto:
1. Fork el repositorio
2. Crea una rama para tu feature
3. Envía un pull request

## Licencia
[Especificar la licencia del proyecto] 