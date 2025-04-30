# Importación de las bibliotecas necesarias
from openai import OpenAI  # Cliente oficial de OpenAI
import os  # Para manejar variables de entorno
from dotenv import load_dotenv  # Para cargar variables de entorno desde .env

# Carga las variables de entorno desde el archivo .env
# Esto permite mantener la API key segura y no hardcodeada en el código
load_dotenv()

# Inicializa el cliente de OpenAI con la API key desde las variables de entorno
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),  # Obtiene la API key de las variables de entorno
)

# Crea una solicitud de completado de chat usando el modelo GPT-3.5-turbo
response = client.chat.completions.create(
    model="gpt-3.5-turbo",  # Especifica el modelo a usar
    messages=[{"role": "user", "content": "Hello, how are you?"}],  # Mensaje del usuario
)

# Imprime la respuesta generada por el modelo
print(response.choices[0].message.content)
