from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.agents import Tool, initialize_agent
from langchain.agents.agent_types import AgentType
from langchain.chains import RetrievalQA
from langchain_chroma import Chroma
from langchain.memory import ConversationBufferMemory
from langchain.tools import BaseTool
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import Optional, Type, Any
from pydantic import BaseModel, Field, PrivateAttr
import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
import os
from dotenv import load_dotenv
import chromadb

from config import setup_openai_api

console = Console()
def load_books_vectorstore():
    """Carga la base de datos vectorial de libros"""
    try:
        db_path = Path("books_db")
        if not db_path.exists() or not any(db_path.iterdir()):
            console.print("[red]❌ No se encontró o está vacío el directorio 'books_db/'. Asegúrate de haber ejecutado primero process_books.py[/red]")
            return None

        console.print("[cyan]Cargando embeddings y base de datos...[/cyan]")

        vectorstore = Chroma(
            persist_directory=str(db_path),
            collection_name="books",
            embedding_function=OpenAIEmbeddings(model="text-embedding-3-small", dimensions=384)
        )

        results = vectorstore.get()
        if not results or not results.get("metadatas"):
            console.print("[red]❌ No se encontraron documentos en la base de datos. Asegúrate de haber ejecutado primero process_books.py[/red]")
            return None

        console.print(f"[green]✓ Base de datos cargada correctamente[/green]")
        console.print(f"[cyan]Libros encontrados: {len(results['metadatas'])}[/cyan]")
        for metadata in results["metadatas"]:
            console.print(f"  • {metadata.get('title', 'Sin título')} - {metadata.get('author', 'Autor desconocido')}")

        return vectorstore
    except Exception as e:
        console.print(f"[red]❌ Error al cargar la base de datos: {str(e)}[/red]")
        return None

def create_search_tool(vectorstore):
    """Crea la herramienta de búsqueda en libros"""
    from langchain.chains import RetrievalQA
    from difflib import get_close_matches

    # Obtener lista de títulos y sus book_id
    results = vectorstore.get()
    book_index = {}
    for meta in results.get("metadatas", []):
        book_id = meta.get("book_id")
        title = meta.get("title", "").lower()
        if book_id and title:
            book_index[title] = book_id

    def search_books(query: str) -> str:
        try:
            # Detectar si se menciona un título
            matched_title = get_close_matches(query.lower(), list(book_index.keys()), n=1)
            filtro = {}

            if matched_title:
                filtro["book_id"] = book_index[matched_title[0]]

            retriever = vectorstore.as_retriever(
                search_kwargs={
                    "k": 6,
                    "filter": filtro if filtro else None
                }
            )

            llm = ChatOpenAI(model="gpt-4", temperature=0)

            chain = RetrievalQA.from_chain_type(
                llm=llm,
                retriever=retriever,
                return_source_documents=True,
                chain_type="map_reduce"
            )

            result = chain.invoke({"query": query})
            answer = result["result"]
            sources = result.get("source_documents", [])

            output = f"📘 Respuesta: {answer}\n\n📚 Fuentes:\n"
            for doc in sources:
                meta = doc.metadata
                if doc.page_content.strip():
                    output += f"- {meta.get('title', 'Sin título')} de {meta.get('author', 'Autor desconocido')} (tema: {meta.get('topic', 'Sin tema')})\n"

            return output
        except Exception as e:
            return f"Error al buscar en los libros: {str(e)}"

    return Tool(
        name="BuscarEnLibros",
        description="Usa esta herramienta para buscar información específica en el contenido de los libros. Útil para encontrar citas, conceptos, personajes o temas específicos.",
        func=search_books
    )

def create_metadata_tool(vectorstore):
    """Crea la herramienta de metadata de libros"""
    def get_metadata(query: str) -> str:
        try:
            # Obtener todos los documentos únicos (por book_id)
            results = vectorstore.get()
            if not results or not results.get("metadatas"):
                return "No se encontraron libros en la base de datos."

            # Filtrar para obtener solo un documento por libro
            seen_books = set()
            books_info = []
            
            for metadata in results["metadatas"]:
                book_id = metadata.get("book_id")
                if book_id and book_id not in seen_books:
                    seen_books.add(book_id)
                    books_info.append({
                        "título": metadata.get("title", "Sin título"),
                        "autor": metadata.get("author", "Autor desconocido"),
                        "tema": metadata.get("topic", "Sin tema")
                    })

            return json.dumps(books_info, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"Error al obtener metadata: {str(e)}"

    return Tool(
        name="ObtenerMetadata",
        description="Usa esta herramienta para obtener información general sobre los libros en la biblioteca. Útil para conocer títulos, autores y temas disponibles.",
        func=get_metadata
    )

def create_agent(vectorstore):
    """Crea y configura el agente con sus herramientas"""
    # Crear herramientas
    search_tool = create_search_tool(vectorstore)
    metadata_tool = create_metadata_tool(vectorstore)
    
    # Configurar el LLM
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0
    )
    
    # Configurar la memoria
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    
    # Crear el agente
    agent = initialize_agent(
        tools=[search_tool, metadata_tool],
        llm=llm,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        verbose=True,
        memory=memory,
        max_iterations=3,
        handle_parsing_errors=True
    )
    
    return agent

def main():
    """Función principal con interfaz interactiva"""
    console.print(Panel.fit(
        "[bold green]📚 Asistente Literario[/bold green]\n"
        "Un agente inteligente que puede ayudarte a explorar tu biblioteca personal.",
        title="Bienvenido"
    ))
    
    # Configurar API key de OpenAI
    if not setup_openai_api():
        return
    
    # Cargar la base de datos
    console.print("\n[cyan]Cargando base de datos de libros...[/cyan]")
    vectorstore = load_books_vectorstore()
    if not vectorstore:
        console.print("\n[yellow]⚠️  Para usar este agente, primero debes procesar tus libros con process_books.py[/yellow]")
        console.print("[yellow]Ejecuta: python process_books.py[/yellow]")
        return
    
    # Crear el agente
    console.print("\n[green]Creando agente...[/green]")
    agent = create_agent(vectorstore)
    
    console.print("\n[bold]💡 El agente está listo. Puedes hacer preguntas sobre tus libros.[/bold]")
    console.print("[yellow]Escribe 'salir' para terminar.[/yellow]")
    
    while True:
        try:
            query = input("\n❓ Tu pregunta: ")
            if query.lower() in ["salir", "exit", "quit"]:
                console.print("\n[blue]👋 ¡Hasta luego![/blue]")
                break
            
            # Obtener respuesta del agente
            response = agent.run(query)
            
            # Mostrar la respuesta formateada
            console.print("\n[bold]💬 Respuesta:[/bold]")
            console.print(Markdown(response))
            
        except KeyboardInterrupt:
            console.print("\n[blue]👋 ¡Hasta luego![/blue]")
            break
        except Exception as e:
            console.print(f"\n[red]Error: {str(e)}[/red]")

if __name__ == "__main__":
    main() 