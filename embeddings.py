from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from file_manager import load_documents

documents = load_documents("file.txt")
if not documents:
    print("No documents found")
    exit()
splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.split_documents(documents)

embeddings = OpenAIEmbeddings()
vector_store = Chroma.from_documents(chunks, embeddings, persist_directory="db")


vector_store.add_documents(chunks)

retriever = vector_store.as_retriever()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

qa = RetrievalQA.from_chain_type(
    llm=llm, chain_type="stuff", retriever=retriever
)

while True:
    query = input("Enter a query: ")
    if query.lower() == "exit":
        break
    response = qa.invoke({"query": query})
    print(response)
