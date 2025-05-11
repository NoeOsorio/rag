from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# Cargar embeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-small", dimensions=384)

# Cargar base vectorial
vs = Chroma(
    persist_directory="books_db",
    collection_name="books",
    embedding_function=embeddings
)

# Hacer búsqueda
results = vs.similarity_search("iron will", k=5)
for doc in results:
    print(doc.page_content[:300])