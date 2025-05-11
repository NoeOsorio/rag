from dotenv import load_dotenv
from rich.console import Console
from langchain_openai import ChatOpenAI
import os

console = Console()
def setup_openai_api():
    """Configura y valida la API key de OpenAI"""
    # Cargar variables de entorno desde .env si existe
    load_dotenv()

    # Verificar si la API key está configurada
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print(
            "[yellow]⚠️  No se encontró la API key de OpenAI en las variables de entorno[/yellow]")
        api_key = input("Por favor, ingresa tu API key de OpenAI: ").strip()

        if not api_key:
            console.print(
                "[red]❌ No se proporcionó una API key. El programa no puede continuar.[/red]")
            return False

        # Guardar la API key en el archivo .env
        with open(".env", "w") as f:
            f.write(f"OPENAI_API_KEY={api_key}\n")
        console.print("[green]✓ API key guardada en .env[/green]")

    # Configurar la API key
    os.environ["OPENAI_API_KEY"] = api_key

    # Verificar que la API key funcione
    try:
        llm = ChatOpenAI(model="gpt-4", temperature=0)
        llm.invoke("test")
        console.print(
            "[green]✓ API key de OpenAI configurada correctamente[/green]")
        return True
    except Exception as e:
        console.print(f"[red]❌ Error al validar la API key: {str(e)}[/red]")
        return False
