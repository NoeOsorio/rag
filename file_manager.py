from langchain.document_loaders import TextLoader

def load_documents(file_path):
    loader = TextLoader(file_path)
    documents = loader.load()
    return documents



