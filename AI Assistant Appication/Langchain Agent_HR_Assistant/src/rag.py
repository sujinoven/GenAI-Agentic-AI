"""RAG over the Employee Handbook: Load & Split, Store, Retrieve, Expose."""

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    EMBEDDING_MODEL,
    HANDBOOK_PATH,
    RETRIEVER_K,
)


# STEP 1 — Load & Split
def load_and_split() -> list[Document]:
    loader = PyPDFLoader(str(HANDBOOK_PATH))
    documents = loader.load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    return splitter.split_documents(documents)


# STEP 2 — Store
def build_vector_store() -> InMemoryVectorStore:
    chunks = load_and_split()
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    vector_store = InMemoryVectorStore(embeddings)
    vector_store.add_documents(chunks)
    return vector_store


# STEP 3 — Retrieve
def build_retriever():
    vector_store = build_vector_store()
    return vector_store.as_retriever(search_kwargs={"k": RETRIEVER_K})


def format_docs(docs: list[Document]) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


# STEP 4 — Expose retrieval to the agent as a tool (LangChain v1)
def build_handbook_tool(retriever):
    """Wrap the retriever in a tool the agent can choose to call.

    The docstring of the inner function is what the model reads when it decides
    whether to use it, so it describes the ROUTE 1 case from the system prompt.
    """

    @tool("search_handbook")
    def search_handbook(query: str) -> str:
        """Search the PROITBRIDGE Employee Handbook and return the relevant text.

        Use this for GENERAL policy or knowledge questions -- questions that ask
        what a rule IS, e.g. "What is the casual leave policy?", "What is the
        standard probation period?", "What is the remote work allowance policy?".

        Do NOT use this to calculate a value or to check whether one specific
        request is allowed -- use the matching HR tool for that.

        query: the employee's policy question, in plain English.
        """
        documents = retriever.invoke(query)
        context = format_docs(documents)
        return context or "No relevant section was found in the Employee Handbook."

    return search_handbook
