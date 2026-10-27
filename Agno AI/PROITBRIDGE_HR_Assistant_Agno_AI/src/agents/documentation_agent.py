from agno.agent import Agent
from agno.models.openai import OpenAIChat

from src.core.config import LLM_MODEL, TEMPERATURE
from src.tools.employee import get_employee_record

DOCUMENTATION_ROLE = "Prepare the resignation letter, handover checklist and HR communication."

DOCUMENTATION_INSTRUCTIONS = (
    "Using the employee record and the other agents' findings, draft three documents: (1) a Resignation "
    "Letter to the reporting manager, to be submitted through the HRMS; (2) a Handover Checklist covering "
    "live work, credentials, contacts, pending decisions and known risks; (3) a short HR Communication "
    "email. You can call get_employee_record for the employee's own details. Use only the facts you are "
    "given and leave a [placeholder] for anything missing. Do not invent dates or numbers."
)


def build_documentation_agent(db=None) -> Agent:
    return Agent(
        name="Documentation Agent",
        role=DOCUMENTATION_ROLE,
        model=OpenAIChat(id=LLM_MODEL, temperature=TEMPERATURE),
        tools=[get_employee_record],
        instructions=DOCUMENTATION_INSTRUCTIONS,
        markdown=True,
    )
