from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import json
import os
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def infer_metadata_with_gpt(file_path: str) -> dict:
    # Verificar que el archivo existe
    if not os.path.exists(file_path):
        console.print(f"[red]Error: El archivo {file_path} no existe[/red]")
        return {"title": None, "author": None, "topic": None}

    # Leer los primeros 1000 caracteres del archivo
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read(1000)
    except Exception as e:
        console.print(f"[red]Error al leer el archivo: {str(e)}[/red]")
        return {"title": None, "author": None, "topic": None}

    # Crear el prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Eres un asistente experto en análisis de libros. Tu tarea es extraer metadatos del texto proporcionado."),
        ("human", """Analiza el siguiente fragmento de texto y extrae:
        1. Título del libro (si está presente)
        2. Autor (si es posible identificarlo)
        3. Tema general del texto
        
        Devuelve la información en formato JSON con las siguientes claves:
        - title: título del libro
        - author: autor del libro
        - topic: tema general
        
        Fragmento de texto:
        {text}
        """)
    ])

    # Inicializar el modelo
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    
    # Crear la cadena de procesamiento
    chain = prompt | llm

    try:
        # Ejecutar la cadena
        response = chain.invoke({"text": text})
        
        # Intentar parsear la respuesta como JSON
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            console.print(f"[red]Error al parsear el JSON: {response.content}[/red]")
            return {"title": None, "author": None, "topic": None}
            
    except Exception as e:
        console.print(f"[red]Error al procesar con GPT: {str(e)}[/red]")
        return {"title": None, "author": None, "topic": None}

def process_all_books():
    # Crear directorio para metadata si no existe
    metadata_dir = "metadata"
    os.makedirs(metadata_dir, exist_ok=True)
    
    # Procesar cada archivo de texto
    text_books_dir = "text_books"
    txt_files = [f for f in os.listdir(text_books_dir) if f.endswith(".txt")]
    
    if not txt_files:
        console.print("[yellow]No se encontraron archivos de texto para analizar[/yellow]")
        return []
    
    failed_files = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Analizando libros...", total=len(txt_files))
        
        for txt_file in txt_files:
            metadata_file = os.path.join(metadata_dir, f"{os.path.splitext(txt_file)[0]}_metadata.json")
            
            if os.path.exists(metadata_file):
                progress.print(f"[blue]⏭️  Saltando {txt_file} - metadata ya extraída[/blue]")
                progress.advance(task)
                continue
                
            file_path = os.path.join(text_books_dir, txt_file)
            progress.print(f"[green]📚 Analizando {txt_file}...[/green]")
            
            metadata = infer_metadata_with_gpt(file_path)
            
            if metadata["title"] or metadata["author"] or metadata["topic"]:
                try:
                    with open(metadata_file, "w", encoding="utf-8") as f:
                        json.dump(metadata, f, ensure_ascii=False, indent=2)
                    progress.print(f"[green]✓ Metadata extraída exitosamente para {txt_file}[/green]")
                except Exception as e:
                    progress.print(f"[red]✗ Error guardando metadata de {txt_file}: {str(e)}[/red]")
                    failed_files.append(file_path)
            else:
                progress.print(f"[red]✗ No se pudo extraer metadata de {txt_file}[/red]")
                failed_files.append(file_path)
            
            progress.advance(task)
    
    return failed_files

if __name__ == "__main__":
    failed_files = process_all_books()
    if failed_files:
        console.print("\n[yellow]⚠️  Algunos archivos no pudieron ser procesados:[/yellow]")
        for file in failed_files:
            console.print(f"[red]  - {file}[/red]")
    
    