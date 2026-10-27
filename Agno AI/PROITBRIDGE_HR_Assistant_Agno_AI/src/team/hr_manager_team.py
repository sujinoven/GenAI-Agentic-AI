from agno.models.openai import OpenAIChat
from agno.team import Team
from agno.team.mode import TeamMode

from src.agents.compliance_agent import build_compliance_agent
from src.core.config import LLM_MODEL, TEMPERATURE
from src.agents.documentation_agent import build_documentation_agent
from src.knowledge.handbook import build_knowledge, load_handbook
from src.agents.payroll_agent import build_payroll_agent
from src.agents.policy_agent import build_policy_agent
from src.agents.research_agent import build_research_agent

TEAM_INSTRUCTIONS = (
    "You are the PROITBRIDGE HR Manager. First decide what the user actually needs, then act — do NOT "
    "run the whole workflow by default:\n"
    "- If the message is a greeting, small talk, or vague (e.g. 'hi'), reply briefly yourself and ask "
    "what they need. Do NOT delegate and do NOT run the resignation workflow.\n"
    "- For a specific question, delegate to ONLY the specialist(s) it needs and give a focused answer — "
    "not the full report: policy or rules -> HR Policy Agent; a calculation or settlement -> Payroll "
    "Agent; exit checklist or clearances -> Compliance Agent; a letter, handover or HR email -> "
    "Documentation Agent; external, non-company information -> HR Research Agent.\n"
    "- Only the FULL resignation request (calculate the settlement AND list the exit steps AND prepare "
    "the documents) uses all four specialists and the five-section Final HR Response: Applicable Policy, "
    "Final Settlement, Exit Checklist, Resignation & Handover Documents, Next Steps.\n"
    "For questions about the specific employee, the relevant members load the record via "
    "get_employee_record; for general questions they answer generally without it. Use only the members' "
    "findings — never invent policy or numbers."
)


def build_hr_team(db=None, load: bool = True):
    """Build the PROITBRIDGE HR Manager Team and return (team, knowledge)."""
    knowledge = build_knowledge(db)
    if load:
        load_handbook(knowledge)

    policy_agent = build_policy_agent(knowledge=knowledge, load=False)
    payroll_agent = build_payroll_agent(knowledge=knowledge, load=False)
    compliance_agent = build_compliance_agent(knowledge=knowledge, load=False)
    documentation_agent = build_documentation_agent()
    research_agent = build_research_agent()

    team = Team(
        name="HR Manager Team",
        model=OpenAIChat(id=LLM_MODEL, temperature=TEMPERATURE),
        members=[policy_agent, payroll_agent, compliance_agent, documentation_agent, research_agent],
        db=db,
        mode=TeamMode.coordinate,
        instructions=TEAM_INSTRUCTIONS,
        share_member_interactions=True,
        show_members_responses=True,
        markdown=True,
    )
    return team, knowledge
