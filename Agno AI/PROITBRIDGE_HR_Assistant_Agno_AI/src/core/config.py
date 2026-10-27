import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Models
LLM_MODEL = "gpt-4.1-mini"
TEMPERATURE = 0
EMBEDDING_MODEL = "text-embedding-3-small"

# Knowledge / RAG settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
MAX_RESULTS = 5  # handbook chunks retrieved per search (k)

# Paths — this file lives in src/core/, so the project root is two levels up.
CORE_DIR = Path(__file__).resolve().parent   # src/core/
SRC_DIR = CORE_DIR.parent                     # src/
BASE_DIR = SRC_DIR.parent                     # project root
DATA_DIR = BASE_DIR / "data"
HANDBOOK_PATH = DATA_DIR / "PROITBRIDGE_Employee_Handbook_2026_1.pdf"

# Runtime artefacts (git-ignored), rebuilt on first run.
TMP_DIR = BASE_DIR / "tmp"
LANCEDB_URI = str(TMP_DIR / "lancedb")
LANCEDB_TABLE = "proitbridge_handbook"
AGENTOS_DB_FILE = str(TMP_DIR / "agentos.db")


def check_config() -> None:
    """Fail early with a clear message if the key or handbook is missing."""
    if not OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    if not HANDBOOK_PATH.exists():
        raise FileNotFoundError(
            f"Employee Handbook not found at: {HANDBOOK_PATH}\n"
            "Place PROITBRIDGE_Employee_Handbook_2026_1.pdf inside the data/ folder."
        )
    TMP_DIR.mkdir(parents=True, exist_ok=True)
