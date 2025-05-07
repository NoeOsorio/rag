# Conversor de EPUB a Texto

Esta herramienta convierte archivos EPUB a formato de texto plano, manteniendo el contenido textual del libro mientras elimina el formato HTML y otros elementos de presentación.

## Características

- Procesa múltiples archivos EPUB en lote
- Manejo automático de errores
- Evita reprocesar archivos ya convertidos
- Preserva la codificación UTF-8
- Proceso eficiente de recursos

## Requisitos

```bash
pip install ebooklib beautifulsoup4
```

## Estructura de Directorios

```
.
├── ebooks/           # Directorio con los archivos EPUB originales
├── text_books/       # Directorio donde se guardan los archivos de texto convertidos
├── ebook_parser.py   # Script principal
└── docs/            # Documentación
```

## Uso

1. Coloca tus archivos EPUB en el directorio `ebooks/`
2. Ejecuta el script:
   ```bash
   python ebook_parser.py
   ```
3. Los archivos de texto convertidos se guardarán en `text_books/`

## Funcionamiento

El script realiza las siguientes operaciones:

1. Verifica la existencia del directorio `text_books/` y lo crea si es necesario
2. Busca todos los archivos `.epub` en el directorio `ebooks/`
3. Para cada archivo EPUB:
   - Verifica si ya existe una versión convertida
   - Si no existe, procesa el archivo y extrae el texto
   - Guarda el resultado en un archivo `.txt` con el mismo nombre base
   - Muestra mensajes de progreso y errores si ocurren

## Manejo de Errores

El script incluye manejo de errores para:
- Problemas de lectura de archivos EPUB
- Errores de codificación
- Problemas al guardar archivos de texto
- Archivos corruptos o mal formateados

## Notas

- Los archivos ya convertidos se saltan automáticamente
- El proceso es no destructivo: los archivos EPUB originales no se modifican
- Se mantiene la codificación UTF-8 para preservar caracteres especiales 