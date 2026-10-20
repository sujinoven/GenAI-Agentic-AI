from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .config import(
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    EMBEDDING_MODEL,
    HANDBOOK_PATH,
    RETRIEVER_K
)

#Step 1: Load & Split
def load_and_split() -> list[Document]:
    loader=PyPDFLoader(str(HANDBOOK_PATH))
    documents=loader.load()
    splitter=RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    return splitter.split_documents(documents)

#STEP 2: STORE
def build_vector_store() -> InMemoryVectorStore:
    chunks=load_and_split()
    embeddings=OpenAIEmbeddings(model=EMBEDDING_MODEL)
    vector_store=InMemoryVectorStore(embeddings)
    vector_store.add_documents(chunks)
    return vector_store

#Step 3:Retrieve
def build_retriever():
    vector_store=build_vector_store()
    return vector_store.as_retriever(search_kwargs={"k":RETRIEVER_K})

def format_docs(docs: list[Document]) -> str:
    return "\n\n".join(doc.page_content for doc in docs)