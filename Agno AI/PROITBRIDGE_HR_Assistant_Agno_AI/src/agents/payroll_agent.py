from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.calculator import CalculatorTools

from src.core.config import LLM_MODEL, TEMPERATURE
from src.tools.employee import get_employee_record
from src.knowledge.handbook import build_knowledge, load_handbook
from src.tools.hr_tools import HR_TOOLS

PAYROLL_ROLE = "Calculate the employee's full and final settlement."

PAYROLL_INSTRUCTIONS = (
    "For a question about this specific employee (it says 'my', names the employee, or is the resignation "
    "request), call get_employee_record first for their numbers; for a general HR question, answer "
    "generally and do NOT fetch the record. Search the Employee Handbook for what is included in and "
    "deducted from the full and final settlement. Use the calculator for every amount, and use the "
    "per-day rates from the record (NOT the full monthly salary): final-month salary = "
    "days_worked_in_final_month x per_day_gross; Earned Leave encashment = earned_leave x per_day_basic; "
    "notice shortfall buy-out = days short x per_day_basic; then add approved reimbursements and subtract "
    "the outstanding advance for the net estimate. You may also use the PROITBRIDGE HR tools (leave, "
    "reimbursement, payroll-date, allowance checks) when a specific validation or calculation helps. Show "
    "each line item with its amount in INR. Mark items the record does not give (TDS, professional tax, "
    "statutory bonus) as 'computed by Payroll'. Do not write letters or checklists."
)


def build_payroll_agent(db=None, knowledge=None, load: bool = True) -> Agent:
    if knowledge is None:
        knowledge = build_knowledge(db)
    if load:
        load_handbook(knowledge)
    return Agent(
        name="Payroll Agent",
        role=PAYROLL_ROLE,
        model=OpenAIChat(id=LLM_MODEL, temperature=TEMPERATURE),
        knowledge=knowledge,
        search_knowledge=True,
        tools=[CalculatorTools(), get_employee_record, *HR_TOOLS],
        instructions=PAYROLL_INSTRUCTIONS,
        markdown=True,
    )
