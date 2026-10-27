"""
STEP 1 — Connect to OpenAI (the "brain" every agent uses)

📘 Colab:  os.environ["OPENAI_API_KEY"] = getpass(...).strip()
           llm = LLM(model="gpt-4o", temperature=0)

In the web app we don't type the key every time — we keep it in the .env file.
"""
import os
from pathlib import Path

from crewai import LLM
from dotenv import load_dotenv

# Read the .env file from the project folder (one level above this crew/ folder)
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_FILE, override=True)

# .strip() removes extra spaces, new lines and quotes copied with the key
api_key = os.getenv("OPENAI_API_KEY", "").strip().strip('"').strip("'").strip()

# Stop early with a clear message if the key is missing
if not api_key.startswith("sk-") or "your-openai-key" in api_key:
    raise SystemExit(
        "\n❌ OPENAI_API_KEY not found in " + str(ENV_FILE) + "\n"
        "   1. Run:  cp .env.example .env\n"
        "   2. Open the .env file (NOT .env.example) and paste your key after OPENAI_API_KEY=\n"
    )

os.environ["OPENAI_API_KEY"] = api_key  # save the clean key (same as in Colab)

llm = LLM(
    model=os.getenv("OPENAI_MODEL", "gpt-4o").strip(),
    api_key=api_key,
    temperature=0,
)
