"""LangChain v1 wiring: the model and the `create_agent` agent.

LangChain v1 note
-----------------

`bind_tools` only told the model which tools exist; we still had to run the
loop ourselves. `create_agent` builds the whole loop -- model call, tool call,
model call again. The LCEL RAG chain is gone because retrieval is now the
`search_handbook` tool.
"""

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from .config import LLM_MODEL, TEMPERATURE
from .prompts import HR_SYSTEM_PROMPT
from .rag import build_handbook_tool
from .tools import HR_TOOLS


def build_llm() -> ChatOpenAI:
    return ChatOpenAI(model=LLM_MODEL, temperature=TEMPERATURE)


def build_agent(retriever):
    """Build the HR agent: model + tools + system prompt."""
    # The handbook retriever becomes one more tool alongside the 7 HR tools.
    # That single list is what makes the routing work -- the model picks one.
    handbook_tool = build_handbook_tool(retriever)

    return create_agent(
        model=build_llm(),
        tools=[handbook_tool, *HR_TOOLS],
        system_prompt=HR_SYSTEM_PROMPT,
    )
