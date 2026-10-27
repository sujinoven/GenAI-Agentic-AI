from agno.agent import Agent
from agno.models.openai import OpenAIChat

from src.core.config import LLM_MODEL, TEMPERATURE
from src.knowledge.handbook import build_knowledge, load_handbook

POLICY_ROLE = "Find the resignation, notice and leave rules in the PROITBRIDGE Employee Handbook."

POLICY_INSTRUCTIONS = (
    "Always search the Employee Handbook before answering. For this employee, report the rules on the "
    "notice period, notice buy-out or waiver, leave during the notice period, Earned Leave encashment "
    "and the resignation steps. Give the handbook section number for every rule. Use only the handbook — "
    "never invent a policy. Do not calculate the settlement."
)


def build_policy_agent(db=None, knowledge=None, load: bool = True) -> Agent:
    if knowledge is None:
        knowledge = build_knowledge(db)
    if load:
        load_handbook(knowledge)
    return Agent(
        name="HR Policy Agent",
        role=POLICY_ROLE,
        model=OpenAIChat(id=LLM_MODEL, temperature=TEMPERATURE),
        knowledge=knowledge,
        search_knowledge=True,
        instructions=POLICY_INSTRUCTIONS,
        markdown=True,
    )
