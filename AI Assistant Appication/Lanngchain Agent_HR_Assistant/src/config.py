"""Configuration only — no business logic lives here.

Everything that might change between environments (API key, model names,
RAG settings, file paths) is kept in one place so the rest of the code can
stay focused on LangChain concepts.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load variables from a local .env file (see .env.example).
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- Models ---------------------------------------------------------------
# gpt-4.1-mini with temperature 0 keeps HR answers consistent and factual.
LLM_MODEL = "gpt-4.1-mini"
TEMPERATURE = 0

# text-embedding-3-small is sufficient for a 57-page HR handbook.
EMBEDDING_MODEL = "text-embedding-3-small"

# --- RAG settings ---------------------------------------------------------
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
RETRIEVER_K = 4

# --- Paths ----------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
HANDBOOK_PATH = DATA_DIR / "PROITBRIDGE_Employee_Handbook_2026_1.pdf"


def check_config() -> None:
    """Fail early with a clear message if the key or handbook is missing."""
    if not OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY is not set."
        )
    if not HANDBOOK_PATH.exists():
        raise FileNotFoundError(
            f"Employee Handbook not found at: {HANDBOOK_PATH}\n"
            "Place PROITBRIDGE_Employee_Handbook_2026_1.pdf inside the data/ folder."
        )
