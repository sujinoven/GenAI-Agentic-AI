import os
from dotenv import load_dotenv


load_dotenv()
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
LANGSMITH_TRACING=os.getenv("LANGSMITH_TRACING")
LANGSMITH_API_KEY= os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT= os.getenv("LANGSMITH_PROJECT")

#2.Model configuration
llm_model="gpt-4o-mini"
TEMPERATURE=0

#3.RAG Configuration
from pathlib import Path
HANDBOOK_PATH=Path("langgraph_project/data/PROITBRIDGE_Employee_Handbook_2026.pdf")
EMBEDDING_MODEL="text-embedding-3-small"
CHUNK_SIZE=1000
CHUNK_OVERLAP=150
RETRIEVER_K=4

#Throw run time error if any of the required environment variables are missing.
def check_config() -> None:
    """Fail early with a clear message if a key or the handbook is nissing"""
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set. Please add it to the .env varaiable")
    if LANGSMITH_TRACING and not LANGSMITH_API_KEY:
        raise RuntimeError(
            "LANGSMITH_TRACING is true but LANGSMITH_API_KEY is not set. Please add it to the .env variable"
            )
    if not HANDBOOK_PATH.exists():
        raise FileNotFoundError(
            f"Employee handbook not found at {HANDBOOK_PATH}.Place ProITBRidge employee handbook inside the data/folder."
        )