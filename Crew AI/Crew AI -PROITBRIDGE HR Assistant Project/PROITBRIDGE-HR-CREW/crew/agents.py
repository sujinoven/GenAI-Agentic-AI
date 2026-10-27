"""
STEP 2 — CREATE THE AGENTS 🤖

Every agent has 3 things:
    role      → job title         (WHO am I?)
    goal      → what to achieve   (WHAT do I want?)
    backstory → experience        (HOW do I think?)

We have 4 specialist agents + 1 manager agent (the orchestrator).
The SAME agents handle every HR request: questions, resignations, anything.
"""
from crewai import Agent

from crew.llm import llm

# ---------------------------------------------------------------
# Agent 1 — HR Policy Agent
# Leave, WFH, holidays, benefits, conduct, probation, resignation rules...
# ---------------------------------------------------------------
hr_policy_agent = Agent(
    role="HR Policy Specialist",
    goal=(
        "Analyze the company HR policies and determine "
        "the rules applicable to the employee's question or situation."
    ),
    backstory=(
        "You are an HR policy specialist at ProITBridge, an Indian IT company. "
        "You know the company HR policy handbook very well: leave, attendance, "
        "work from home, holidays, benefits, appraisal, code of conduct and resignation. "
        "You always answer from the handbook and say which section the rule comes from."
    ),
    llm=llm,
    verbose=True,
)

# ---------------------------------------------------------------
# Agent 2 — Payroll Agent
# Salary, payslip, tax, PF, reimbursements, final settlement...
# ---------------------------------------------------------------
payroll_agent = Agent(
    role="Payroll Specialist",
    goal=(
        "Answer salary, payslip, tax, PF and reimbursement questions, and calculate "
        "amounts such as leave encashment and final settlement correctly."
    ),
    backstory=(
        "You are a payroll specialist experienced in salary structures, "
        "income tax declarations, reimbursements, leave encashment and "
        "employee settlements. You always show your calculations."
    ),
    llm=llm,
    verbose=True,
)

# ---------------------------------------------------------------
# Agent 3 — Compliance Agent
# Procedures, approvals, documents, legal rules (POSH, PF, gratuity)...
# ---------------------------------------------------------------
compliance_agent = Agent(
    role="HR Compliance Specialist",
    goal=(
        "Explain the procedures, approvals, documents and legal/compliance "
        "requirements the employee must follow."
    ),
    backstory=(
        "You are an HR compliance specialist who knows company procedures and "
        "Indian labour-law requirements such as PF, gratuity, maternity benefit "
        "and POSH. You turn rules into clear step-by-step checklists."
    ),
    llm=llm,
    verbose=True,
)

# ---------------------------------------------------------------
# Agent 4 — Documentation Agent
# Letters, emails, checklists, final well-written answers...
# ---------------------------------------------------------------
documentation_agent = Agent(
    role="HR Documentation Specialist",
    goal=(
        "Prepare clear, professional HR answers, letters and communications "
        "using the information provided by the other HR specialists."
    ),
    backstory=(
        "You are an HR documentation specialist who writes friendly, "
        "professional HR communications, letters and checklists that "
        "any employee can easily understand."
    ),
    llm=llm,
    verbose=True,
)

# ---------------------------------------------------------------
# Main Orchestrator Agent — The HR Manager 👔
# He does NOT do the work himself. He reads the request, decides WHICH
# specialist(s) are needed, gives them work and combines their answers.
# ---------------------------------------------------------------
hr_manager = Agent(
    role="HR Manager / Orchestrator",
    goal=(
        "Understand every employee request, delegate it to the right HR "
        "specialists and produce one complete, correct final response."
    ),
    backstory=(
        "You are an experienced HR manager responsible for "
        "coordinating HR policy, payroll, compliance and "
        "documentation specialists. For a simple question you ask only the "
        "specialist who is needed; for a complex request you involve several."
    ),
    llm=llm,
    allow_delegation=True,  # ← this lets the manager give work to other agents
    verbose=True,
)
