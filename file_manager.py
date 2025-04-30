# Importa el TextLoader de langchain para cargar documentos de texto
from langchain.document_loaders import TextLoader

def load_documents(file_path):
    """
    Carga y procesa documentos de texto usando TextLoader de langchain.
    
    Args:
        file_path (str): Ruta al archivo de texto que se desea cargar
        
    Returns:
        list: Lista de documentos cargados y procesados
    """
    # Crea una instancia del TextLoader con la ruta del archivo
    loader = TextLoader(file_path)
    
    # Carga y procesa el documento
    documents = loader.load()
    
    return documents



