from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.websearch import WebSearchTools

from src.core.config import LLM_MODEL, TEMPERATURE

RESEARCH_ROLE = "Research external, current HR information that is NOT PROITBRIDGE policy."

RESEARCH_INSTRUCTIONS = (
    "Use web search for external, general information only — for example typical notice-period norms in "
    "Indian IT, how Form 16 / PF withdrawal works in general, or current HR trends. Never present web "
    "results as PROITBRIDGE policy; company rules come only from the HR Policy Agent (handbook). Clearly "
    "label everything you return as external context. If web search returns an error or no results (the "
    "free DuckDuckGo backend can rate-limit), say external search is temporarily unavailable and to try "
    "again — do not invent facts."
)


def build_research_agent(db=None) -> Agent:
    return Agent(
        name="HR Research Agent",
        role=RESEARCH_ROLE,
        model=OpenAIChat(id=LLM_MODEL, temperature=TEMPERATURE),
        # backend="duckduckgo" is more reliable than "auto" (which also tries
        # Google/Bing endpoints that block automated requests).
        tools=[WebSearchTools(backend="duckduckgo", fixed_max_results=5)],
        instructions=RESEARCH_INSTRUCTIONS,
        markdown=True,
    )
