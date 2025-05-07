from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import json
import os

def infer_metadata_with_gpt(file_path: str) -> dict:
    # Verificar que el archivo existe
    if not os.path.exists(file_path):
        print(f"Error: El archivo {file_path} no existe")
        return {"title": None, "author": None, "topic": None}

    # Leer los primeros 1000 caracteres del archivo
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read(1000)
    except Exception as e:
        print(f"Error al leer el archivo: {str(e)}")
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
            print(f"Error al parsear el JSON: {response.content}")
            return {"title": None, "author": None, "topic": None}
            
    except Exception as e:
        print(f"Error al procesar con GPT: {str(e)}")
        return {"title": None, "author": None, "topic": None}

def process_all_books():
    # Crear directorio para metadata si no existe
    metadata_dir = "metadata"
    os.makedirs(metadata_dir, exist_ok=True)
    
    # Procesar cada archivo de texto
    text_books_dir = "text_books"
    for txt_file in os.listdir(text_books_dir):
        if txt_file.endswith(".txt"):
            # Crear nombre del archivo de metadata
            metadata_file = os.path.join(metadata_dir, f"{os.path.splitext(txt_file)[0]}_metadata.json")
            
            # Saltar si el archivo de metadata ya existe
            if os.path.exists(metadata_file):
                print(f"Saltando {txt_file} - metadata ya extraída")
                continue
                
            file_path = os.path.join(text_books_dir, txt_file)
            print(f"\nProcesando {txt_file}...")
            
            # Extraer metadata
            metadata = infer_metadata_with_gpt(file_path)
            
            # Guardar metadata en archivo JSON
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            print(f"Metadata guardada en {metadata_file}")

if __name__ == "__main__":
    process_all_books()
    
    