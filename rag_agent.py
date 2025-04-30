from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from file_manager import load_documents
from dotenv import load_dotenv
import os

def init_vector_store(docs, embedding, db_path="db"):
    from pathlib import Path
    if Path(db_path).exists():
        print("Loading existing vector store...")
        return Chroma(persist_directory=db_path, embedding_function=embedding)
    else:
        print("Creating new vector store and adding documents...")
        return Chroma.from_documents(docs, embedding, persist_directory=db_path)

def create_qa_chain(vector_store, model_name="gpt-4o-mini", temperature=0):
    llm = ChatOpenAI(model=model_name, temperature=temperature)
    retriever = vector_store.as_retriever()
    return RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)

def main():
    documents = load_documents("file.txt")
    if not documents:
        print("No documents found")
        return
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings()
    vector_store = init_vector_store(chunks, embeddings)
    qa = create_qa_chain(vector_store)

    while True:
        query = input("Enter a query (or 'exit' to quit): ")
        if query.lower() == "exit":
            break
        response = qa.invoke({"query": query})
        print(response)

if __name__ == "__main__":
    load_dotenv()
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
    main()
