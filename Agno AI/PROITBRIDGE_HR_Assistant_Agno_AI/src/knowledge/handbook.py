from agno.knowledge.chunking.recursive import RecursiveChunking
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.reader.pdf_reader import PDFReader
from agno.vectordb.lancedb import LanceDb
from agno.vectordb.search import SearchType

from src.core.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    EMBEDDING_MODEL,
    HANDBOOK_PATH,
    LANCEDB_TABLE,
    LANCEDB_URI,
    MAX_RESULTS,
)


def build_vector_db() -> LanceDb:
    """Embedded, file-based vector store for the handbook (no server needed)."""
    return LanceDb(
        uri=LANCEDB_URI,
        table_name=LANCEDB_TABLE,
        search_type=SearchType.vector,
        embedder=OpenAIEmbedder(id=EMBEDDING_MODEL, enable_batch=True),
    )


def build_knowledge(db=None) -> Knowledge:
    """Create the Knowledge object backed by the handbook vector store."""
    return Knowledge(
        name="PROITBRIDGE Employee Handbook",
        vector_db=build_vector_db(),
        contents_db=db,
        max_results=MAX_RESULTS,
    )


def handbook_indexed(knowledge: Knowledge) -> bool:
    """True if the handbook is already embedded in the local LanceDB store."""
    vector_db = knowledge.vector_db
    try:
        return vector_db.exists() and vector_db.get_count() > 0
    except Exception:
        return False


def load_handbook(knowledge: Knowledge) -> bool:
    """Index the Employee Handbook into LanceDB ONCE, then reuse it on later runs."""
    if handbook_indexed(knowledge):
        print("Reusing the saved Employee Handbook index.")
        return False

    import asyncio

    print("Indexing the Employee Handbook (first run only — a few seconds)…")
    kwargs = dict(
        name="PROITBRIDGE Employee Handbook",
        path=str(HANDBOOK_PATH),
        reader=PDFReader(
            chunking_strategy=RecursiveChunking(chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP),
        ),
        skip_if_exists=True,
    )
    try:
        asyncio.run(knowledge.ainsert(**kwargs))
    except RuntimeError as error:
        if "running event loop" in str(error).lower():
            knowledge.insert(**kwargs)
        else:
            raise
    return True