from agno.agent import Agent
from agno.models.openai import OpenAIChat

from src.core.config import LLM_MODEL, TEMPERATURE
from src.tools.employee import get_employee_record
from src.knowledge.handbook import build_knowledge, load_handbook

COMPLIANCE_ROLE = "List the exit procedures, clearances and required documents."

COMPLIANCE_INSTRUCTIONS = (
    "For a question about this specific employee, call get_employee_record to see their assets and "
    "pending items; for a general question, answer generally without it. Search the Employee "
    "Handbook for the resignation process, exit checklist, asset return, clearances, confidentiality "
    "obligations and post-exit documents (relieving letter, Form 16, PF, insurance). Turn them into a "
    "checklist for this employee with owners and timelines. Use only the handbook. Do not calculate "
    "money and do not write letters."
)


def build_compliance_agent(db=None, knowledge=None, load: bool = True) -> Agent:
    if knowledge is None:
        knowledge = build_knowledge(db)
    if load:
        load_handbook(knowledge)
    return Agent(
        name="Compliance Agent",
        role=COMPLIANCE_ROLE,
        model=OpenAIChat(id=LLM_MODEL, temperature=TEMPERATURE),
        knowledge=knowledge,
        search_knowledge=True,
        tools=[get_employee_record],
        instructions=COMPLIANCE_INSTRUCTIONS,
        markdown=True,
    )
