"""
STEP 3 — GIVE TASKS TO THE AGENTS 📋

Every task has 3 things:
    description     → what to do
    expected_output → what the answer should look like
    agent           → WHO does this task

This app has TWO kinds of HR work:
    PART A — "Ask HR"      : 1 task, the HR Manager decides who answers it
    PART B — "Resignation" : 4 tasks, one for each specialist (same as Colab)

🆕 Difference from Colab:
We write {placeholders} like {question} or {employee_name}.
CrewAI fills them when we call  crew.kickoff_async(inputs={...})  in hr_crew.py.
{hr_policy} is filled with the text of crew/hr_policy.md.
"""
from crewai import Task

from crew.agents import compliance_agent, documentation_agent, hr_policy_agent, payroll_agent

# =================================================================
# PART A — ASK HR (any HR question from an employee)
# =================================================================

# No "agent=" here on purpose!
# In a hierarchical crew, a task without an agent goes to the HR Manager,
# and HE decides which specialist(s) should work on it.
hr_question_task = Task(
    description=(
        "An employee has asked the HR department this question:\n\n"
        '"{question}"\n\n'
        "About the employee who is asking:\n{employee_context}\n\n"
        "Answer the question using the ProITBridge HR policy below. "
        "Ask the right specialist for help: HR Policy for rules, Payroll for money "
        "and calculations, Compliance for procedures and legal steps, Documentation "
        "for letters or emails. If the policy does not cover the question, say so "
        "politely and suggest whom to contact.\n\n"
        "ProITBridge HR policy:\n{hr_policy}"
    ),
    expected_output=(
        "A friendly, clear answer in Markdown with these parts:\n"
        "1. **Answer** — a direct answer in 1–3 sentences\n"
        "2. **Details** — the important rules, numbers or calculation, as bullet points\n"
        "3. **Policy reference** — which policy section(s) this comes from\n"
        "4. **Next steps** — what the employee should do now"
    ),
)

# =================================================================
# PART B — RESIGNATION (4 tasks, one for each specialist)
# =================================================================

# Employee details shared by the resignation tasks
EMPLOYEE_DETAILS = """
Employee details:
- Name: {employee_name}
- Designation: {designation}
- Department: {department}
- Date of joining: {date_of_joining}
- Resignation date: {resignation_date}
- Requested last working day: {last_working_day}
- Notice period as per contract: {notice_period_days} days
- Monthly gross salary: Rs. {monthly_salary}
- Leave balance: {leave_balance} days
- Reason for leaving: {reason}
"""

# Task 1 → HR Policy Agent
hr_policy_task = Task(
    description=(
        "Analyze the employee's resignation request and "
        "identify the applicable notice period, leave policy "
        "and resignation rules. Check whether the requested last "
        "working day completes the notice period. If not, say how "
        "many days are short.\n" + EMPLOYEE_DETAILS +
        "\nProITBridge HR policy:\n{hr_policy}"
    ),
    expected_output=(
        "A clear summary (in Markdown bullet points) of the applicable HR policies, "
        "including notice period, leave rules and resignation requirements."
    ),
    agent=hr_policy_agent,
)

# Task 2 → Payroll Agent
payroll_task = Task(
    description=(
        "Calculate the employee's final settlement using "
        "salary, leave balance, applicable encashment, "
        "deductions and pending reimbursements.\n"
        "Use these simple rules:\n"
        "- Per-day salary = monthly gross salary / 30\n"
        "- Leave encashment = per-day salary x leave balance\n"
        "- If notice is short, deduct per-day salary x short days\n"
        + EMPLOYEE_DETAILS
    ),
    expected_output=(
        "A Markdown table with the breakdown of salary, leave encashment, "
        "deductions, reimbursements and the final settlement amount in rupees, "
        "followed by the calculation steps."
    ),
    agent=payroll_agent,
)

# Task 3 → Compliance Agent
compliance_task = Task(
    description=(
        "Identify everything the employee must complete "
        "before the last working day, including exit "
        "procedures, clearances and required documents.\n" + EMPLOYEE_DETAILS +
        "\nProITBridge HR policy:\n{hr_policy}"
    ),
    expected_output=(
        "A complete employee exit checklist (Markdown bullet list) containing "
        "all required procedures, clearances and documents."
    ),
    agent=compliance_agent,
)

# Task 4 → Documentation Agent
# context = this task can READ the answers of tasks 1, 2 and 3
documentation_task = Task(
    description=(
        "Prepare the employee's resignation acceptance letter, "
        "handover checklist and required HR communication "
        "using the information from the policy, payroll and "
        "compliance specialists.\n" + EMPLOYEE_DETAILS
    ),
    expected_output=(
        "A complete HR response in Markdown containing:\n"
        "1. Applicable HR policies\n"
        "2. Final settlement details\n"
        "3. Exit and compliance requirements\n"
        "4. Resignation acceptance letter and handover checklist"
    ),
    agent=documentation_agent,
    context=[hr_policy_task, payroll_task, compliance_task],
)
