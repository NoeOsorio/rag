import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import os
import pathlib

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
        print(f"Error procesando {epub_path}: {str(e)}")
        return None

def process_epub_files():
    # Crear directorio de salida si no existe
    output_dir = pathlib.Path("text_books")
    output_dir.mkdir(exist_ok=True)
    
    # Procesar cada archivo EPUB
    ebooks_dir = pathlib.Path("ebooks")
    for epub_file in ebooks_dir.glob("*.epub"):
        # Crear nombre del archivo de salida
        output_file = output_dir / f"{epub_file.stem}.txt"
        
        # Saltar si el archivo ya existe
        if output_file.exists():
            print(f"Saltando {epub_file.name} - ya convertido")
            continue
            
        print(f"Procesando {epub_file.name}...")
        text = epub_to_text(str(epub_file))
        
        if text:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(text)
                print(f"✓ {epub_file.name} convertido exitosamente")
            except Exception as e:
                print(f"Error guardando {epub_file.name}: {str(e)}")

if __name__ == "__main__":
    process_epub_files()