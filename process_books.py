import os
import json
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.panel import Panel
from rich import print as rprint
import chromadb
from chromadb.config import Settings
from ebook_parser import process_epub_files
from infer_metadata_ai import process_all_books

console = Console()

def ensure_directories():
    """Asegura que todos los directorios necesarios existan"""
    directories = {
        "ebooks": "📚 Directorio para archivos EPUB originales",
        "text_books": "📝 Directorio para archivos de texto convertidos",
        "metadata": "📋 Directorio para archivos de metadata",
        "books_db": "💾 Directorio para la base de datos vectorial"
    }
    
    console.print("\n[bold cyan]🔍 Verificando estructura de directorios...[/bold cyan]")
    
    for dir_name, description in directories.items():
        dir_path = Path(dir_name)
        if not dir_path.exists():
            console.print(f"[yellow]Creando directorio: {dir_name}[/yellow]")
            dir_path.mkdir(exist_ok=True)
            console.print(f"[green]✓ {description} creado[/green]")
        else:
            console.print(f"[blue]✓ {description} ya existe[/blue]")
    
    # Verificar si hay archivos EPUB para procesar
    epub_files = list(Path("ebooks").glob("*.epub"))
    if not epub_files:
        console.print("\n[red]⚠️  No se encontraron archivos EPUB en el directorio 'ebooks/'[/red]")
        console.print("[yellow]Por favor, coloca tus archivos EPUB en el directorio 'ebooks/' y vuelve a ejecutar el script[/yellow]")
        return False
    
    console.print(f"\n[green]✓ Se encontraron {len(epub_files)} archivos EPUB para procesar[/green]")
    return True

def setup_chroma_db():
    """Inicializa la base de datos Chroma"""
    console.print("\n[bold cyan]📚 Inicializando base de datos vectorial...[/bold cyan]")
    
    # Asegurarse de que el directorio existe
    db_dir = Path("books_db")
    db_dir.mkdir(exist_ok=True)
    
    # Inicializar el cliente con persistencia
    client = chromadb.PersistentClient(path=str(db_dir))
    
    # Crear o obtener la colección
    try:
        collection = client.get_collection("books")
        console.print("[blue]✓ Colección 'books' encontrada[/blue]")
    except:
        collection = client.create_collection(
            name="books",
            metadata={"hnsw:space": "cosine"}
        )
        console.print("[green]✓ Nueva colección 'books' creada[/green]")
    
    return collection

def load_existing_books(collection):
    """Carga los libros existentes en la base de datos"""
    try:
        # Obtener todos los documentos
        result = collection.get()
        if result and "ids" in result and result["ids"]:
            console.print(f"[blue]📚 Se encontraron {len(result['ids'])} libros en la base de datos[/blue]")
            return set(result["ids"])
        else:
            console.print("[yellow]ℹ️  No se encontraron libros en la base de datos[/yellow]")
            return set()
    except Exception as e:
        console.print(f"[yellow]⚠️  Error al cargar libros existentes: {str(e)}[/yellow]")
        return set()

def process_books():
    """Proceso principal de orquestación"""
    console.print(Panel.fit(
        "[bold green]📚 Sistema de Procesamiento de Libros[/bold green]\n"
        "Este script procesará tus libros EPUB, extraerá su metadata\n"
        "y los almacenará en una base de datos vectorial.",
        title="Inicio del Proceso"
    ))

    # Verificar y crear directorios necesarios
    if not ensure_directories():
        return

    # Paso 1: Convertir EPUBs a texto
    console.print("\n[bold cyan]1️⃣  Fase de Conversión[/bold cyan]")
    failed_epubs = process_epub_files()
    
    # Paso 2: Extraer metadata
    console.print("\n[bold cyan]2️⃣  Fase de Extracción de Metadata[/bold cyan]")
    failed_metadata = process_all_books()
    
    # Paso 3: Cargar en ChromaDB
    console.print("\n[bold cyan]3️⃣  Fase de Carga en Base de Datos[/bold cyan]")
    collection = setup_chroma_db()
    existing_books = load_existing_books(collection)
    
    # Procesar archivos de texto y metadata
    text_books_dir = Path("text_books")
    metadata_dir = Path("metadata")
    failed_db = []
    skipped_files = []
    processed_files = []
    
    txt_files = list(text_books_dir.glob("*.txt"))
    if not txt_files:
        console.print("[yellow]No se encontraron archivos para procesar[/yellow]")
        return
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Verificando libros en la base de datos...", total=len(txt_files))
        
        for txt_file in txt_files:
            book_id = txt_file.stem
            
            # Verificar si el libro ya está en la base de datos
            if book_id in existing_books:
                skipped_files.append(txt_file.name)
                progress.print(f"[blue]⏭️  Saltando {txt_file.name} - ya en base de datos[/blue]")
                progress.advance(task)
                continue
            
            metadata_file = metadata_dir / f"{txt_file.stem}_metadata.json"
            
            try:
                # Leer el texto y la metadata
                with open(txt_file, "r", encoding="utf-8") as f:
                    text = f.read()
                
                if metadata_file.exists():
                    with open(metadata_file, "r", encoding="utf-8") as f:
                        metadata = json.load(f)
                else:
                    metadata = {"title": None, "author": None, "topic": None}
                
                # Verificar nuevamente antes de agregar (por si acaso)
                if book_id in existing_books:
                    skipped_files.append(txt_file.name)
                    progress.print(f"[blue]⏭️  Saltando {txt_file.name} - ya en base de datos[/blue]")
                    progress.advance(task)
                    continue
                
                # Agregar a la base de datos
                collection.add(
                    documents=[text],
                    metadatas=[{
                        "id": book_id,
                        "title": metadata.get("title", "Sin título"),
                        "author": metadata.get("author", "Autor desconocido"),
                        "topic": metadata.get("topic", "Sin tema")
                    }],
                    ids=[book_id]
                )
                
                processed_files.append(txt_file.name)
                progress.print(f"[green]✓ {txt_file.name} agregado a la base de datos[/green]")
            except Exception as e:
                progress.print(f"[red]✗ Error cargando {txt_file.name}: {str(e)}[/red]")
                failed_db.append(str(txt_file))
            
            progress.advance(task)
    
    # Resumen final
    console.print("\n[bold cyan]📊 Resumen del Proceso[/bold cyan]")
    
    if skipped_files:
        console.print("\n[blue]📋 Archivos ya existentes en la base de datos:[/blue]")
        for file in skipped_files:
            console.print(f"[blue]  - {file}[/blue]")
    
    if processed_files:
        console.print("\n[green]✨ Archivos nuevos agregados a la base de datos:[/green]")
        for file in processed_files:
            console.print(f"[green]  - {file}[/green]")
    
    if failed_epubs:
        console.print("\n[yellow]⚠️  Archivos EPUB que no pudieron ser convertidos:[/yellow]")
        for file in failed_epubs:
            console.print(f"[red]  - {file}[/red]")
    
    if failed_metadata:
        console.print("\n[yellow]⚠️  Archivos que no pudieron ser analizados:[/yellow]")
        for file in failed_metadata:
            console.print(f"[red]  - {file}[/red]")
    
    if failed_db:
        console.print("\n[yellow]⚠️  Archivos que no pudieron ser cargados en la base de datos:[/yellow]")
        for file in failed_db:
            console.print(f"[red]  - {file}[/red]")
    
    if not (failed_epubs or failed_metadata or failed_db):
        if not processed_files:
            console.print("\n[blue]ℹ️  No se encontraron nuevos archivos para procesar[/blue]")
        else:
            console.print("\n[green]✨ ¡Proceso completado exitosamente![/green]")
    
    console.print("\n[bold]Base de datos guardada en:[/bold] books_db/")

if __name__ == "__main__":
    process_books() 