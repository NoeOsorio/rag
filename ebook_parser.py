import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import os
import pathlib
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def epub_to_text(epub_path):
    try:
        book = epub.read_epub(epub_path)
        text = ""
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content().decode('utf-8'), 'html.parser')
                text += soup.get_text()
        return text
    except Exception as e:
        console.print(f"[red]Error procesando {epub_path}: {str(e)}[/red]")
        return None

def process_epub_files():
    # Crear directorio de salida si no existe
    output_dir = pathlib.Path("text_books")
    output_dir.mkdir(exist_ok=True)
    
    # Procesar cada archivo EPUB
    ebooks_dir = pathlib.Path("ebooks")
    epub_files = list(ebooks_dir.glob("*.epub"))
    
    if not epub_files:
        console.print("[yellow]No se encontraron archivos EPUB para procesar[/yellow]")
        return []
    
    failed_files = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Procesando archivos EPUB...", total=len(epub_files))
        
        for epub_file in epub_files:
            output_file = output_dir / f"{epub_file.stem}.txt"
            
            if output_file.exists():
                progress.print(f"[blue]⏭️  Saltando {epub_file.name} - ya convertido[/blue]")
                progress.advance(task)
                continue
                
            progress.print(f"[green]📖 Procesando {epub_file.name}...[/green]")
            text = epub_to_text(str(epub_file))
            
            if text:
                try:
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(text)
                    progress.print(f"[green]✓ {epub_file.name} convertido exitosamente[/green]")
                except Exception as e:
                    progress.print(f"[red]✗ Error guardando {epub_file.name}: {str(e)}[/red]")
                    failed_files.append(str(epub_file))
            else:
                failed_files.append(str(epub_file))
            
            progress.advance(task)
    
    return failed_files

if __name__ == "__main__":
    failed_files = process_epub_files()
    if failed_files:
        console.print("\n[yellow]⚠️  Algunos archivos no pudieron ser procesados:[/yellow]")
        for file in failed_files:
            console.print(f"[red]  - {file}[/red]")