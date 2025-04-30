# Importaciones necesarias para el agente RAG
from langchain_openai import OpenAIEmbeddings  # Para generar embeddings usando OpenAI
from langchain.text_splitter import CharacterTextSplitter  # Para dividir documentos en chunks
from langchain_chroma import Chroma  # Para almacenar y buscar embeddings
from langchain_openai import ChatOpenAI  # Para el modelo de chat de OpenAI
from langchain.chains import RetrievalQA  # Para crear la cadena de QA
from file_manager import load_documents  # Para cargar documentos
from dotenv import load_dotenv  # Para cargar variables de entorno
import os  # Para manejar variables de entorno

def init_vector_store(docs, embedding, db_path="db"):
    """
    Inicializa o carga un vector store existente usando ChromaDB.
    
    Args:
        docs (list): Lista de documentos a indexar
        embedding: Función de embedding a usar
        db_path (str): Ruta donde se almacenará/recuperará el vector store
        
    Returns:
        Chroma: Instancia del vector store
    """
    from pathlib import Path
    # Si el vector store ya existe, lo carga
    if Path(db_path).exists():
        print("Loading existing vector store...")
        return Chroma(persist_directory=db_path, embedding_function=embedding)
    # Si no existe, crea uno nuevo con los documentos
    else:
        print("Creating new vector store and adding documents...")
        return Chroma.from_documents(docs, embedding, persist_directory=db_path)

def create_qa_chain(vector_store, model_name="gpt-4o-mini", temperature=0):
    """
    Crea una cadena de QA que combina el modelo de chat con el vector store.
    
    Args:
        vector_store: Vector store con los documentos indexados
        model_name (str): Nombre del modelo a usar
        temperature (float): Temperatura para la generación (0 = más determinista)
        
    Returns:
        RetrievalQA: Cadena de QA configurada
    """
    # Inicializa el modelo de chat
    llm = ChatOpenAI(model=model_name, temperature=temperature)
    # Crea un retriever a partir del vector store
    retriever = vector_store.as_retriever()
    # Crea y retorna la cadena de QA
    return RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)

def main():
    """
    Función principal que ejecuta el agente RAG.
    Carga documentos, crea embeddings, inicializa el vector store
    y permite hacer preguntas interactivamente.
    """
    # Carga los documentos
    documents = load_documents("file.txt")
    if not documents:
        print("No documents found")
        return
    
    # Divide los documentos en chunks más pequeños
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(documents)

    # Inicializa el generador de embeddings
    embeddings = OpenAIEmbeddings()
    # Crea o carga el vector store
    vector_store = init_vector_store(chunks, embeddings)
    # Crea la cadena de QA
    qa = create_qa_chain(vector_store)

    # Loop interactivo para hacer preguntas
    while True:
        query = input("Enter a query (or 'exit' to quit): ")
        if query.lower() == "exit":
            break
        # Obtiene y muestra la respuesta
        response = qa.invoke({"query": query})
        print(response)

if __name__ == "__main__":
    # Carga las variables de entorno
    load_dotenv()
    # Configura la API key de OpenAI
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
    # Ejecuta la función principal
    main()
