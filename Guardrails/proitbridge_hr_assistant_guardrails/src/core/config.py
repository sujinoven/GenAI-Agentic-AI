import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

DATA_DIR     = BASE_DIR / "data"
HANDBOOK_PDF = DATA_DIR / "PROITBRIDGE_Employee_Handbook_2026_1.pdf"
RECORDS_PDF  = DATA_DIR / "PROITBRIDGE_Employee_Records_SYNTHETIC.pdf"
FRONTEND_DIR = BASE_DIR / "frontend"
TMP_DIR      = BASE_DIR / "tmp"
GUARD_LOG    = TMP_DIR / "guard_log.jsonl"

MODEL           = "gpt-4.1-mini"
EMBEDDING_MODEL = "text-embedding-3-small"
CHUNK_SIZE      = 1000
CHUNK_OVERLAP   = 150
TOP_K           = 4
RECORD_K        = 2

MAX_QUESTION_CHARS = 300
BANNED_PHRASES     = ["ignore all previous instructions", "developer mode", "system prompt"]
INPUT_PII          = ["PHONE_NUMBER", "EMAIL_ADDRESS"]
OUTPUT_PII         = ["PHONE_NUMBER"]

os.environ.setdefault("GUARDRAILS_RUN_SYNC", "true")


def has_api_key():
    return os.getenv("OPENAI_API_KEY", "").startswith("sk-")
