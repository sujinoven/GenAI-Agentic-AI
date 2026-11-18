import re
from functools import lru_cache

from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.core.config import HANDBOOK_PDF, RECORDS_PDF, EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP, TOP_K, RECORD_K

HANDBOOK = "Handbook"
RECORDS  = "Employee records"


def read_record(text):
    found = re.search(r"([^\n]+)\nEmployee ID: (PIB-E\d{4})", text)
    return found.group(2), found.group(1).strip()


@lru_cache
def employee_directory():
    directory = {}
    for page in PdfReader(RECORDS_PDF).pages:
        employee_id, name      = read_record(page.extract_text() or "")
        directory[employee_id] = name
    return directory


def load_pages():
    pages = []
    for number, page in enumerate(PdfReader(HANDBOOK_PDF).pages, start=1):
        pages.append(Document(page_content=page.extract_text() or "",
                              metadata={"source": HANDBOOK, "page": number}))
    for number, page in enumerate(PdfReader(RECORDS_PDF).pages, start=1):
        text           = page.extract_text() or ""
        employee_id, _ = read_record(text)
        pages.append(Document(page_content=text,
                              metadata={"source": RECORDS, "page": number, "employee_id": employee_id}))
    return pages


@lru_cache
def get_vector_store():
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    chunks   = splitter.split_documents(load_pages())
    return InMemoryVectorStore.from_documents(chunks, OpenAIEmbeddings(model=EMBEDDING_MODEL))


def search(query, allowed_ids):
    store    = get_vector_store()
    handbook = store.similarity_search(query, k=TOP_K, filter=lambda doc: doc.metadata["source"] == HANDBOOK)
    records  = store.similarity_search(query, k=RECORD_K, filter=lambda doc: doc.metadata.get("employee_id") in allowed_ids)
    return records + handbook
