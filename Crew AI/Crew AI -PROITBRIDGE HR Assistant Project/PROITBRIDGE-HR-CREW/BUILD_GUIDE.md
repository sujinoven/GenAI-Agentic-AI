# ProITBridge HR Crew: Step-by-Step Build Guide (Simple Version)

We turn our **Colab CrewAI notebook** into an **AI HR Management web app** in 10 steps.
Steps 3 to 6 are the AI part and follow the Colab notebook cell by cell.

The app has two AI features, both run by the **same team of 5 agents**:
- **💬 Ask HR**: an employee types any HR question, the HR Manager picks the right specialist(s), and they answer from the company policy.
- **📄 Resignation**: the 4-task resignation crew from the Colab notebook.

```
proitbridge-hr-crew/
├── crew/
│   ├── __init__.py      (empty file that tells Python "crew" is a package)
│   ├── llm.py           Step 3
│   ├── hr_policy.md     Step 4  📖 what the agents know
│   ├── agents.py        Step 5  ⭐ the agents are created here
│   ├── tasks.py         Step 6  ⭐ the tasks are given here
│   └── hr_crew.py       Step 7
├── database.py          Step 8
├── main.py              Step 9
├── templates/           Step 10
├── static/              Step 10
├── requirements.txt     Step 2
└── .env                 Step 2
```

---

## Step 1: Create the folders

Open Terminal on your Mac:

```bash
# Install Python 3.12 once (CrewAI needs Python 3.10 to 3.13)
brew install python@3.12

mkdir -p ~/Downloads/proitbridge-hr-crew
cd ~/Downloads/proitbridge-hr-crew
mkdir crew templates static
touch crew/__init__.py
code .        # opens the folder in VS Code
```

---

## Step 2: Install the libraries and add the OpenAI key

**📄 `requirements.txt`**

```text
crewai==1.15.28         # multi-agent framework
fastapi                 # web framework
uvicorn[standard]       # runs the FastAPI app
jinja2                  # HTML templates
python-multipart        # reads HTML form data
python-dotenv           # reads the .env file
markdown                # shows the agents' Markdown answers as HTML
```

```bash
python3.12 -m venv .venv          # create a virtual environment
source .venv/bin/activate         # turn it on (you will see (.venv))
pip install -r requirements.txt
```

**📄 `.env.example`**

```bash
# Copy this file to .env and paste your key
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_MODEL=gpt-4o

# Turn off CrewAI's anonymous usage tracking
CREWAI_DISABLE_TELEMETRY=true
OTEL_SDK_DISABLED=true
```

```bash
cp .env.example .env
open -e .env        # paste your real key after OPENAI_API_KEY= and save
```

> In Colab we typed the key with `getpass()`. In a web app we keep it in `.env`. Never share this file.

---

## Step 3: Connect to OpenAI (📘 Colab cell 2)

**📄 `crew/llm.py`**

```python
"""
STEP 1 — Connect to OpenAI (the "brain" every agent uses)

📘 Colab:  os.environ["OPENAI_API_KEY"] = getpass(...)
           llm = LLM(model="gpt-4o", temperature=0)

In the web app we don't type the key every time — we keep it in the .env file.
"""
import os

from crewai import LLM
from dotenv import load_dotenv

load_dotenv()  # reads OPENAI_API_KEY and OPENAI_MODEL from the .env file

llm = LLM(
    model=os.getenv("OPENAI_MODEL", "gpt-4o"),
    temperature=0,
)
```

---

## Step 4: The company HR policy 📖

In Colab the agents answered from general knowledge. A real HR system must answer from **the company's own rules**,
so we write them in a plain text file. The agents receive it as `{hr_policy}`.

> Teaching tip: ask learners to change a rule (for example, casual leave from 12 to 15 days), ask the same question again, and watch the answer change.

**📄 `crew/hr_policy.md`**

```markdown
# ProITBridge HR Policy Handbook (SAMPLE FOR TRAINING)

This is a sample policy for learning. Replace it with your company's real HR policy.

## 1. Working Hours & Attendance
- Working days: Monday to Friday, 9:30 AM to 6:30 PM (includes a 1-hour lunch break).
- Core hours: 11:00 AM to 4:00 PM. Employees must be available during core hours.
- Attendance is marked through the HRMS portal. Three late logins (after 10:15 AM) in a month count as half a day of leave.

## 2. Work From Home (WFH) & Hybrid
- Hybrid model: 3 days in office, 2 days WFH every week.
- Extra WFH days need reporting-manager approval in the HRMS portal at least 1 day in advance.
- Employees on probation (first 3 months) must work from office.

## 3. Leave Policy (per calendar year)
- Casual Leave (CL): 12 days. Maximum 3 days at a time. Cannot be carried forward.
- Sick Leave (SL): 10 days. A medical certificate is needed for more than 2 continuous days.
- Earned Leave (EL): 18 days. Up to 30 days can be carried forward to the next year. Must be applied 7 days in advance.
- Maternity Leave: 26 weeks of paid leave, as per the Maternity Benefit Act.
- Paternity Leave: 10 working days, to be used within 3 months of the child's birth.
- Bereavement Leave: 5 days for immediate family.
- Leave during notice period: only with HR Manager approval.

## 4. Public Holidays
- 12 paid holidays per year: 9 fixed national/festival holidays + 3 optional holidays chosen by the employee.
- The holiday calendar is published on the HRMS portal every December.

## 5. Salary & Payroll
- Salary is credited on the last working day of every month.
- Payslips are available on the HRMS portal by the 2nd of the next month.
- Salary structure: Basic is 50% of gross. HRA, special allowance, PF and professional tax as per the offer letter.
- Investment declarations for income tax must be submitted by April 30; proofs by January 31.
- Payroll queries: raise a ticket in HRMS under "Payroll". Response within 2 working days.

## 6. Reimbursements & Travel
- Internet reimbursement: up to Rs. 1,000 per month for hybrid employees.
- Business travel: train 3AC or economy flights (for journeys above 500 km), with manager pre-approval.
- Hotel limit: Rs. 4,000 per night in metro cities, Rs. 2,500 in other cities.
- Daily allowance on travel: Rs. 800 per day.
- Claims must be submitted with bills within 30 days of the expense.

## 7. Benefits
- Group health insurance: Rs. 5,00,000 cover for employee, spouse and 2 children. Parents can be added at the employee's cost.
- Term life insurance: 3 times the annual gross salary.
- Provident Fund (PF): 12% of basic from employee and 12% from employer.
- Gratuity: as per the Payment of Gratuity Act, after 5 years of continuous service.
- Learning budget: Rs. 15,000 per year for courses and certifications, with manager approval.

## 8. Performance & Appraisal
- Appraisal cycle: once a year in April. Mid-year check-in in October.
- Ratings: Exceeds, Meets, Partially Meets, Below Expectations.
- Promotions are decided in the April cycle based on rating and role readiness.

## 9. Probation & Confirmation
- Probation period: 3 months for all new joiners.
- Confirmation letter is issued after a successful probation review.
- Notice period during probation: 15 days.

## 10. Code of Conduct & Workplace Safety
- Treat everyone with respect. Harassment and discrimination are not tolerated.
- Prevention of Sexual Harassment (POSH): complaints go to the Internal Committee (IC) at ic@proitbridge.com. All complaints are confidential.
- Company laptops and data must be used only for work. Sharing confidential data outside the company is a serious violation.
- Grievances can be raised with HR or anonymously through the HRMS "Speak Up" form.

## 11. Resignation & Exit
- Notice period after confirmation: 60 days (90 days for Lead / Manager and above).
- Notice shortfall can be recovered from the final settlement or waived by the HR Manager.
- Full and final settlement is processed within 2 working days after the last working day.
- Relieving and experience letters are issued after exit clearance (laptop, ID card, knowledge transfer).

## 12. HR Contacts
- HR Helpdesk: hr@proitbridge.com
- Payroll: payroll@proitbridge.com
- Internal Committee (POSH): ic@proitbridge.com
```

---

## Step 5: Create the agents ⭐ (📘 Colab: Agent 1, 2, 3, 4 + HR Manager)

This is **where the agents are created**. They are the same 5 agents as in Colab, with goals widened from "resignation" to "any HR request".
`allow_delegation=True` on the HR Manager lets him give work to the other agents.

**📄 `crew/agents.py`**

```python
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
```

---

## Step 6: Give tasks to the agents ⭐ (📘 Colab: hr_policy_task … documentation_task)

This is **where the tasks are given**. The file has two parts:

| Task | Given to | Used by |
|---|---|---|
| `hr_question_task` | **no agent**, so the **HR Manager decides** who works on it | Ask HR |
| `hr_policy_task` | `hr_policy_agent` | Resignation |
| `payroll_task` | `payroll_agent` | Resignation |
| `compliance_task` | `compliance_agent` | Resignation |
| `documentation_task` | `documentation_agent` (reads the other 3 answers through `context`) | Resignation |

🆕 **`{placeholders}`**: `{question}`, `{employee_name}`, `{hr_policy}` and the others are blanks
that are filled with real values when the crew runs (Step 7).

**📄 `crew/tasks.py`**

```python
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
```

---

## Step 7: Create the crews and run them (📘 Colab: `Crew(...)` + `kickoff_async()`)

There are **two crews with the same agents and different tasks**.

**📄 `crew/hr_crew.py`**

```python
"""
STEP 4 — CREATE THE CREWS AND RUN THEM 🚀

📘 Colab:  hr_crew = Crew(agents=[...], tasks=[...],
                          process=Process.hierarchical, manager_agent=hr_manager)
           result = await hr_crew.kickoff_async()

We make TWO crews with the SAME team of agents:
    helpdesk_crew    → answers any HR question        (1 task)
    resignation_crew → processes a resignation         (4 tasks)

Test in the terminal (no website needed):
    python -m crew.hr_crew
"""
import asyncio
from pathlib import Path

from crewai import Crew, Process

from crew.agents import compliance_agent, documentation_agent, hr_manager, hr_policy_agent, payroll_agent
from crew.tasks import compliance_task, documentation_task, hr_policy_task, hr_question_task, payroll_task

# The company HR policy handbook (crew/hr_policy.md) — given to the agents as {hr_policy}
HR_POLICY = (Path(__file__).parent / "hr_policy.md").read_text(encoding="utf-8")

ALL_SPECIALISTS = [hr_policy_agent, payroll_agent, compliance_agent, documentation_agent]

# ---------------------------------------------------------------
# Crew 1 — HR Helpdesk: answers any HR question
# ---------------------------------------------------------------
helpdesk_crew = Crew(
    agents=ALL_SPECIALISTS,
    tasks=[hr_question_task],
    process=Process.hierarchical,  # the manager decides who works on the question
    manager_agent=hr_manager,
    verbose=True,
)

# ---------------------------------------------------------------
# Crew 2 — Resignation: the same 4-task crew as the Colab notebook
# ---------------------------------------------------------------
resignation_crew = Crew(
    agents=ALL_SPECIALISTS,
    tasks=[hr_policy_task, payroll_task, compliance_task, documentation_task],
    process=Process.hierarchical,
    manager_agent=hr_manager,      # the orchestrator (NOT in the agents list)
    verbose=True,
)


async def ask_hr(question: str, employee_context: str = "Not specified") -> str:
    """Answer ONE HR question. Returns the answer as Markdown text."""
    crew = helpdesk_crew.copy()  # fresh copy, so two requests at the same time don't mix
    result = await crew.kickoff_async(inputs={
        "question": question,
        "employee_context": employee_context,
        "hr_policy": HR_POLICY,
    })
    return result.raw


async def run_resignation_crew(employee_inputs: dict) -> dict:
    """Process ONE resignation and return every agent's answer."""
    crew = resignation_crew.copy()
    result = await crew.kickoff_async(inputs={**employee_inputs, "hr_policy": HR_POLICY})

    return {
        "policy": result.tasks_output[0].raw,       # Task 1 answer
        "payroll": result.tasks_output[1].raw,      # Task 2 answer
        "compliance": result.tasks_output[2].raw,   # Task 3 answer
        "final_report": result.raw,                 # Task 4 answer (final)
    }


# Run this file directly to test, just like the Colab notebook
if __name__ == "__main__":
    question = "How many casual leaves do I get, and can I carry them forward to next year?"
    answer = asyncio.run(ask_hr(question, "Name: Arun Kumar, Senior Software Engineer, Engineering"))
    print("\n\n========== HR ANSWER ==========\n")
    print(answer)
```

✅ **Test the AI part now, before building the website:**

```bash
python -m crew.hr_crew
```

In the terminal you will see the HR Manager **delegating** the leave question to the HR Policy Specialist. Then the answer is printed, just like in Colab.

---

## Step 8: The database (saves employees, questions and requests)

We use **SQLite**, which comes with Python. The data is saved in `hr_app.db`, which is created automatically. There are 3 tables: `employees`, `questions` and `requests`.

**📄 `database.py`**

```python
"""
Database — saves employees, HR questions and resignation requests in a small SQLite file (hr_app.db).
SQLite comes with Python, so there is nothing to install.
"""
import sqlite3

DB_FILE = "hr_app.db"


def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # lets us use row["name"] instead of row[1]
    return conn


def init_db():
    """Create the tables (only the first time) and add sample employees."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT, designation TEXT, department TEXT,
                date_of_joining TEXT, monthly_salary REAL,
                leave_balance REAL, notice_period_days INTEGER
            )""")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER,        -- can be empty (anonymous question)
                question TEXT,
                status TEXT,                -- RUNNING / DONE / FAILED
                answer TEXT,
                error TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )""")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER,
                resignation_date TEXT, last_working_day TEXT, reason TEXT,
                status TEXT,                -- RUNNING / DONE / FAILED
                policy TEXT, payroll TEXT, compliance TEXT, final_report TEXT,
                error TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )""")

        # Sample employees so the app is not empty on day 1
        if conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO employees (name, designation, department, date_of_joining, "
                "monthly_salary, leave_balance, notice_period_days) VALUES (?, ?, ?, ?, ?, ?, ?)",
                [
                    ("Arun Kumar", "Senior Software Engineer", "Engineering", "2019-06-04", 120000, 20, 60),
                    ("Priya Raman", "Data Scientist", "Data Science", "2022-01-17", 90000, 14, 60),
                    ("Karthik Subramanian", "AI Trainer Lead", "Training", "2020-11-01", 105000, 30, 90),
                    ("Divya Lakshmi", "HR Executive", "HR", "2023-08-21", 48000, 9, 30),
                ],
            )


# ---------------- Employees ----------------
def get_employees():
    with get_connection() as conn:
        return conn.execute("SELECT * FROM employees ORDER BY name").fetchall()


def get_employee(employee_id):
    with get_connection() as conn:
        return conn.execute("SELECT * FROM employees WHERE id = ?", (employee_id,)).fetchone()


def add_employee(name, designation, department, date_of_joining, monthly_salary, leave_balance, notice_period_days):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO employees (name, designation, department, date_of_joining, "
            "monthly_salary, leave_balance, notice_period_days) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, designation, department, date_of_joining, monthly_salary, leave_balance, notice_period_days),
        )


# ---------------- HR questions ----------------
def add_question(employee_id, question):
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO questions (employee_id, question, status) VALUES (?, ?, 'RUNNING')",
            (employee_id, question),
        )
        return cursor.lastrowid


def get_questions():
    with get_connection() as conn:
        return conn.execute(
            "SELECT questions.*, employees.name AS employee_name "
            "FROM questions LEFT JOIN employees ON employees.id = questions.employee_id "
            "ORDER BY questions.id DESC"
        ).fetchall()


def get_question(question_id):
    with get_connection() as conn:
        return conn.execute(
            "SELECT questions.*, employees.name AS employee_name "
            "FROM questions LEFT JOIN employees ON employees.id = questions.employee_id "
            "WHERE questions.id = ?",
            (question_id,),
        ).fetchone()


def save_answer(question_id, answer):
    with get_connection() as conn:
        conn.execute("UPDATE questions SET status = 'DONE', answer = ? WHERE id = ?", (answer, question_id))


def save_question_error(question_id, error_message):
    with get_connection() as conn:
        conn.execute("UPDATE questions SET status = 'FAILED', error = ? WHERE id = ?", (error_message, question_id))


# ---------------- Resignation requests ----------------
def add_request(employee_id, resignation_date, last_working_day, reason):
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO requests (employee_id, resignation_date, last_working_day, reason, status) "
            "VALUES (?, ?, ?, ?, 'RUNNING')",
            (employee_id, resignation_date, last_working_day, reason),
        )
        return cursor.lastrowid


def get_requests():
    with get_connection() as conn:
        return conn.execute(
            "SELECT requests.*, employees.name AS employee_name, employees.department "
            "FROM requests JOIN employees ON employees.id = requests.employee_id "
            "ORDER BY requests.id DESC"
        ).fetchall()


def get_request(request_id):
    with get_connection() as conn:
        return conn.execute(
            "SELECT requests.*, employees.name AS employee_name, employees.designation, employees.department "
            "FROM requests JOIN employees ON employees.id = requests.employee_id "
            "WHERE requests.id = ?",
            (request_id,),
        ).fetchone()


def save_crew_result(request_id, answers):
    with get_connection() as conn:
        conn.execute(
            "UPDATE requests SET status = 'DONE', policy = ?, payroll = ?, compliance = ?, final_report = ? "
            "WHERE id = ?",
            (answers["policy"], answers["payroll"], answers["compliance"], answers["final_report"], request_id),
        )


def save_crew_error(request_id, error_message):
    with get_connection() as conn:
        conn.execute("UPDATE requests SET status = 'FAILED', error = ? WHERE id = ?", (error_message, request_id))
```

---

## Step 9: The website (FastAPI)

| URL | What it does |
|---|---|
| `GET /` | Dashboard with a quick "Ask HR" box |
| `GET /ask` and `POST /ask` | Ask HR form; submitting it **starts the helpdesk crew in the background** |
| `GET /questions/{id}` | Shows the answer |
| `GET /employees` and `POST /employees` | List employees and add an employee |
| `GET /resign` and `POST /resign` | Resignation form; submitting it **starts the resignation crew** |
| `GET /requests/{id}` | Shows the resignation result |

Look at `answer_question()` and `start_resignation_crew()`. They collect the data that fills the `{placeholders}` from Step 6.

**📄 `main.py`**

```python
"""
The FastAPI web app 🌐

Run:   uvicorn main:app --reload
Open:  http://127.0.0.1:8000

Pages:
    /               → Dashboard
    /ask            → Ask HR: type any HR question  →  starts the helpdesk crew
    /questions/1    → Answer for question 1
    /employees      → Employee list + add employee
    /resign         → Resignation form  →  starts the resignation crew
    /requests/1     → Result for resignation request 1
"""
import re
from datetime import date

import markdown
from fastapi import BackgroundTasks, FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import database
from crew.hr_crew import ask_hr, run_resignation_crew

app = FastAPI(title="ProITBridge HR Crew")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def markdown_to_html(text):
    """Show the agents' Markdown answers as HTML.
    Markdown needs an empty line before a list, and AI answers often skip it, so we add it."""
    is_list_item = lambda line: re.match(r"\s*([-*]|\d+\.)\s", line)
    lines = []
    for line in (text or "").splitlines():
        if is_list_item(line) and lines and lines[-1].strip() and not is_list_item(lines[-1]):
            lines.append("")
        lines.append(line)
    return markdown.markdown("\n".join(lines), extensions=["tables"])


templates.env.filters["markdown"] = markdown_to_html

database.init_db()

EXAMPLE_QUESTIONS = [
    "How many casual leaves do I get in a year?",
    "Can I work from home 3 days this week?",
    "What is the hotel limit when I travel to Bengaluru for work?",
    "How do I claim my internet reimbursement?",
    "When will I get my payslip and Form 16?",
    "I am getting married next month. What leave can I take?",
    "How do I raise a harassment complaint confidentially?",
    "What is my notice period if I resign now?",
]


def employee_summary(emp) -> str:
    """Turn an employee row into text the agents can read."""
    if emp is None:
        return "Not specified (anonymous question)"
    return (
        f"Name: {emp['name']}, Designation: {emp['designation']}, Department: {emp['department']}, "
        f"Date of joining: {emp['date_of_joining']}, Monthly gross salary: Rs. {emp['monthly_salary']}, "
        f"Leave balance: {emp['leave_balance']} days, Notice period: {emp['notice_period_days']} days"
    )


# ---------------- Dashboard ----------------
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(request, "home.html", {
        "employees": database.get_employees(),
        "questions": database.get_questions(),
        "requests": database.get_requests(),
    })


# ---------------- Ask HR → Helpdesk Crew ----------------
@app.get("/ask")
def ask_page(request: Request):
    return templates.TemplateResponse(request, "ask.html", {
        "employees": database.get_employees(),
        "questions": database.get_questions(),
        "examples": EXAMPLE_QUESTIONS,
    })


@app.post("/ask")
def submit_question(
    background_tasks: BackgroundTasks,
    question: str = Form(...),
    employee_id: str = Form(""),  # empty = anonymous
):
    emp_id = int(employee_id) if employee_id else None
    question_id = database.add_question(emp_id, question)
    background_tasks.add_task(answer_question, question_id)  # runs after the page redirects
    return RedirectResponse(f"/questions/{question_id}", status_code=303)


async def answer_question(question_id: int):
    """Run the helpdesk crew for one question and save the answer."""
    q = database.get_question(question_id)
    emp = database.get_employee(q["employee_id"]) if q["employee_id"] else None
    try:
        answer = await ask_hr(q["question"], employee_summary(emp))
        database.save_answer(question_id, answer)
    except Exception as error:
        database.save_question_error(question_id, str(error))


@app.get("/questions/{question_id}")
def question_page(request: Request, question_id: int):
    q = database.get_question(question_id)
    if q is None:
        return RedirectResponse("/ask")
    return templates.TemplateResponse(request, "question.html", {"q": q})


# ---------------- Employees ----------------
@app.get("/employees")
def employees_page(request: Request):
    return templates.TemplateResponse(request, "employees.html", {"employees": database.get_employees()})


@app.post("/employees")
def add_employee(
    name: str = Form(...),
    designation: str = Form(...),
    department: str = Form(...),
    date_of_joining: str = Form(...),
    monthly_salary: float = Form(...),
    leave_balance: float = Form(0),
    notice_period_days: int = Form(60),
):
    database.add_employee(name, designation, department, date_of_joining, monthly_salary, leave_balance, notice_period_days)
    return RedirectResponse("/employees", status_code=303)


# ---------------- Resignation → Resignation Crew ----------------
@app.get("/resign")
def resign_page(request: Request):
    return templates.TemplateResponse(request, "resign.html", {
        "employees": database.get_employees(),
        "requests": database.get_requests(),
        "today": date.today().isoformat(),
    })


@app.post("/resign")
def submit_resignation(
    background_tasks: BackgroundTasks,
    employee_id: int = Form(...),
    resignation_date: str = Form(...),
    last_working_day: str = Form(...),
    reason: str = Form(...),
):
    request_id = database.add_request(employee_id, resignation_date, last_working_day, reason)

    # The crew takes 1–3 minutes, so we run it in the BACKGROUND
    # and send the user to the result page immediately.
    background_tasks.add_task(start_resignation_crew, request_id)
    return RedirectResponse(f"/requests/{request_id}", status_code=303)


async def start_resignation_crew(request_id: int):
    """Collect the employee details → run the resignation crew → save the answers."""
    req = database.get_request(request_id)
    emp = database.get_employee(req["employee_id"])

    # These keys fill the {placeholders} in crew/tasks.py (Part B)
    employee_inputs = {
        "employee_name": emp["name"],
        "designation": emp["designation"],
        "department": emp["department"],
        "date_of_joining": emp["date_of_joining"],
        "monthly_salary": emp["monthly_salary"],
        "leave_balance": emp["leave_balance"],
        "notice_period_days": emp["notice_period_days"],
        "resignation_date": req["resignation_date"],
        "last_working_day": req["last_working_day"],
        "reason": req["reason"],
    }
    try:
        answers = await run_resignation_crew(employee_inputs)
        database.save_crew_result(request_id, answers)
    except Exception as error:
        database.save_crew_error(request_id, str(error))


@app.get("/requests/{request_id}")
def request_page(request: Request, request_id: int):
    if database.get_request(request_id) is None:
        return RedirectResponse("/")
    return templates.TemplateResponse(request, "request.html", {"req": database.get_request(request_id)})
```

---

## Step 10: HTML pages and the ProITBridge colours

Copy `logo.png` and `favicon.png` into `static/`.
`base.html` is the common layout (the left menu with the logo). Every other page `extends` it.

**📄 `templates/base.html`**

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ProITBridge HR Crew</title>
  <link rel="icon" href="/static/favicon.png">
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/static/style.css">
  {% block head %}{% endblock %}
</head>
<body>
  <!-- Left menu -->
  <aside class="sidebar">
    <a href="/" class="brand"><img src="/static/logo.png" alt="ProITBridge"></a>
    <p class="brand-sub">AI HR Management</p>
    <nav>
      <a href="/ask" class="nav-cta">💬 Ask HR</a>
      <a href="/">Dashboard</a>
      <a href="/employees">Employees</a>
      <a href="/resign">Resignation</a>
    </nav>
  </aside>

  <!-- Page content -->
  <main class="main">
    <h1>{% block heading %}{% endblock %}</h1>
    {% block content %}{% endblock %}
    <footer>© ProITBridge · Strive For Better Future</footer>
  </main>
</body>
</html>
```

**📄 `templates/home.html`**

```html
{% extends "base.html" %}
{% block heading %}Dashboard{% endblock %}
{% block content %}

<!-- How the crew works -->
<div class="hero">
  <span class="kicker">CrewAI · OpenAI · FastAPI</span>
  <h2>Your AI HR team, working as one crew.</h2>
  <div class="crew-map">
    <div class="node manager">HR Manager<small>Orchestrator</small></div>
    <div class="nodes">
      <div class="node">HR Policy<small>Agent 1</small></div>
      <div class="node">Payroll<small>Agent 2</small></div>
      <div class="node">Compliance<small>Agent 3</small></div>
      <div class="node">Documentation<small>Agent 4</small></div>
    </div>
  </div>
</div>

<!-- Quick question box: sends a POST to /ask (see main.py) -->
<form class="card form ask-box" method="post" action="/ask">
  <h3>💬 Ask HR anything</h3>
  <div class="ask-row">
    <input name="question" required placeholder="e.g. How many sick leaves do I have in a year?">
    <button class="btn" type="submit">Ask →</button>
  </div>
</form>

<div class="stats three">
  <div class="stat"><span>Employees</span><b>{{ employees|length }}</b></div>
  <div class="stat"><span>HR questions asked</span><b>{{ questions|length }}</b></div>
  <div class="stat"><span>Resignation requests</span><b>{{ requests|length }}</b></div>
</div>

<div class="card">
  <h3>Recent HR questions</h3>
  {% if questions %}
  <table class="table">
    <tr><th>#</th><th>Question</th><th>Asked by</th><th>Status</th><th></th></tr>
    {% for q in questions[:5] %}
    <tr>
      <td>{{ q.id }}</td>
      <td>{{ q.question }}</td>
      <td>{{ q.employee_name or "Anonymous" }}</td>
      <td><span class="badge {{ q.status|lower }}">{{ q.status }}</span></td>
      <td><a class="link" href="/questions/{{ q.id }}">Open →</a></td>
    </tr>
    {% endfor %}
  </table>
  {% else %}
  <p class="muted">No questions yet. <a class="link" href="/ask">Ask the first one →</a></p>
  {% endif %}
</div>

<div class="card">
  <h3>Resignation requests</h3>
  {% if requests %}
  <table class="table">
    <tr><th>#</th><th>Employee</th><th>Department</th><th>Last working day</th><th>Status</th><th></th></tr>
    {% for r in requests[:5] %}
    <tr>
      <td>{{ r.id }}</td>
      <td><b>{{ r.employee_name }}</b></td>
      <td>{{ r.department }}</td>
      <td>{{ r.last_working_day }}</td>
      <td><span class="badge {{ r.status|lower }}">{{ r.status }}</span></td>
      <td><a class="link" href="/requests/{{ r.id }}">Open →</a></td>
    </tr>
    {% endfor %}
  </table>
  {% else %}
  <p class="muted">No resignation requests yet.</p>
  {% endif %}
</div>
{% endblock %}
```

**📄 `templates/ask.html`**

```html
{% extends "base.html" %}
{% block heading %}Ask HR{% endblock %}
{% block content %}

<!-- This form sends a POST to /ask → main.py starts the helpdesk crew -->
<form class="card form" method="post" action="/ask">
  <label>Who is asking? (optional — helps the agents personalise the answer)
    <select name="employee_id">
      <option value="">— Anonymous —</option>
      {% for e in employees %}
      <option value="{{ e.id }}">{{ e.name }} — {{ e.designation }}</option>
      {% endfor %}
    </select>
  </label>
  <label>Your question
    <textarea id="question" name="question" rows="4" required placeholder="Type any HR question: leave, WFH, salary, reimbursement, benefits, policies, resignation..."></textarea>
  </label>

  <p class="muted small">Try an example (click to use it):</p>
  <div class="chips">
    {% for ex in examples %}
    <button type="button" class="chip" onclick="document.getElementById('question').value = this.textContent">{{ ex }}</button>
    {% endfor %}
  </div>

  <button class="btn" type="submit">Ask the AI HR Crew →</button>
  <p class="muted small">The HR Manager reads your question and asks the right specialist. Takes about 30–90 seconds.</p>
</form>

<div class="card">
  <h3>Previous questions</h3>
  {% if questions %}
  <table class="table">
    <tr><th>#</th><th>Question</th><th>Asked by</th><th>Status</th><th></th></tr>
    {% for q in questions %}
    <tr>
      <td>{{ q.id }}</td>
      <td>{{ q.question }}</td>
      <td>{{ q.employee_name or "Anonymous" }}</td>
      <td><span class="badge {{ q.status|lower }}">{{ q.status }}</span></td>
      <td><a class="link" href="/questions/{{ q.id }}">Open →</a></td>
    </tr>
    {% endfor %}
  </table>
  {% else %}
  <p class="muted">No questions yet.</p>
  {% endif %}
</div>
{% endblock %}
```

**📄 `templates/question.html`**

```html
{% extends "base.html" %}

{% block head %}
  {% if q.status == "RUNNING" %}
  <!-- While the crew is working, reload this page every 5 seconds -->
  <meta http-equiv="refresh" content="5">
  {% endif %}
{% endblock %}

{% block heading %}Question #{{ q.id }}{% endblock %}
{% block content %}

<div class="card question-card">
  <span class="kicker">{{ q.employee_name or "Anonymous" }} asked</span>
  <p class="question-text">“{{ q.question }}”</p>
  <span class="badge {{ q.status|lower }}">{{ q.status }}</span>
</div>

{% if q.status == "RUNNING" %}
  <div class="card working">
    <div class="spinner"></div>
    <div><b>The AI HR crew is working…</b><br>
    <span class="muted">The HR Manager is deciding which specialist should answer. Watch the terminal to see the agents thinking.
    This page refreshes automatically.</span></div>
  </div>

{% elif q.status == "FAILED" %}
  <div class="card error"><b>Crew failed:</b> {{ q.error }}</div>

{% else %}
  <div class="card report">
    <span class="kicker">HR answer</span>
    {{ q.answer|markdown|safe }}
  </div>
{% endif %}

<p><a class="btn" href="/ask">💬 Ask another question</a></p>
{% endblock %}
```

**📄 `templates/employees.html`**

```html
{% extends "base.html" %}
{% block heading %}Employees{% endblock %}
{% block content %}

<div class="card">
  <table class="table">
    <tr><th>Name</th><th>Designation</th><th>Department</th><th>Joined</th><th>Salary / month</th><th>Leave</th><th>Notice</th></tr>
    {% for e in employees %}
    <tr>
      <td><b>{{ e.name }}</b></td>
      <td>{{ e.designation }}</td>
      <td>{{ e.department }}</td>
      <td>{{ e.date_of_joining }}</td>
      <td>₹{{ "{:,.0f}".format(e.monthly_salary) }}</td>
      <td>{{ e.leave_balance }} days</td>
      <td>{{ e.notice_period_days }} days</td>
    </tr>
    {% endfor %}
  </table>
</div>

<!-- Add employee form: sends a POST to /employees (see main.py) -->
<form class="card form" method="post" action="/employees">
  <h3>Add employee</h3>
  <div class="grid">
    <label>Name<input name="name" required></label>
    <label>Designation<input name="designation" required></label>
    <label>Department<input name="department" required></label>
    <label>Date of joining<input name="date_of_joining" type="date" required></label>
    <label>Monthly salary (₹)<input name="monthly_salary" type="number" min="1" required></label>
    <label>Leave balance (days)<input name="leave_balance" type="number" min="0" value="0"></label>
    <label>Notice period (days)<input name="notice_period_days" type="number" min="0" value="60"></label>
  </div>
  <button class="btn" type="submit">Save employee</button>
</form>
{% endblock %}
```

**📄 `templates/resign.html`**

```html
{% extends "base.html" %}
{% block heading %}New resignation request{% endblock %}
{% block content %}

<!-- This form sends a POST to /resign → main.py starts the AI crew -->
<form class="card form" method="post" action="/resign">
  <label>Employee
    <select name="employee_id" required>
      {% for e in employees %}
      <option value="{{ e.id }}">{{ e.name }} — {{ e.designation }} ({{ e.notice_period_days }}-day notice)</option>
      {% endfor %}
    </select>
  </label>
  <div class="grid">
    <label>Resignation date<input type="date" name="resignation_date" value="{{ today }}" required></label>
    <label>Requested last working day<input type="date" name="last_working_day" required></label>
  </div>
  <label>Reason for leaving<textarea name="reason" rows="3" required placeholder="e.g. Higher studies / better opportunity / relocation"></textarea></label>
  <button class="btn" type="submit">Run AI HR Crew →</button>
  <p class="muted">The 5 agents take about 1–3 minutes to finish.</p>
</form>

<div class="card">
  <h3>Resignation requests</h3>
  {% if requests %}
  <table class="table">
    <tr><th>#</th><th>Employee</th><th>Last working day</th><th>Status</th><th></th></tr>
    {% for r in requests %}
    <tr>
      <td>{{ r.id }}</td>
      <td><b>{{ r.employee_name }}</b></td>
      <td>{{ r.last_working_day }}</td>
      <td><span class="badge {{ r.status|lower }}">{{ r.status }}</span></td>
      <td><a class="link" href="/requests/{{ r.id }}">Open →</a></td>
    </tr>
    {% endfor %}
  </table>
  {% else %}
  <p class="muted">No requests yet.</p>
  {% endif %}
</div>
{% endblock %}
```

**📄 `templates/request.html`**

```html
{% extends "base.html" %}

{% block head %}
  {% if req.status == "RUNNING" %}
  <!-- While the crew is working, reload this page every 5 seconds -->
  <meta http-equiv="refresh" content="5">
  {% endif %}
{% endblock %}

{% block heading %}Request #{{ req.id }} · {{ req.employee_name }}{% endblock %}
{% block content %}

<div class="card info">
  <div><span>Employee</span><b>{{ req.employee_name }}</b></div>
  <div><span>Role</span><b>{{ req.designation }}, {{ req.department }}</b></div>
  <div><span>Resigned on</span><b>{{ req.resignation_date }}</b></div>
  <div><span>Last working day</span><b>{{ req.last_working_day }}</b></div>
  <div><span>Status</span><b><span class="badge {{ req.status|lower }}">{{ req.status }}</span></b></div>
</div>

{% if req.status == "RUNNING" %}
  <div class="card working">
    <div class="spinner"></div>
    <div><b>The AI crew is working…</b><br>
    <span class="muted">HR Manager is delegating work to the Policy, Payroll, Compliance and Documentation agents.
    Watch the terminal to see each agent thinking. This page refreshes automatically.</span></div>
  </div>

{% elif req.status == "FAILED" %}
  <div class="card error"><b>Crew failed:</b> {{ req.error }}</div>

{% else %}
  <!-- Final answer (Task 4 — Documentation Agent) -->
  <div class="card report">
    <span class="kicker">Final HR response</span>
    {{ req.final_report|markdown|safe }}
  </div>

  <!-- Each agent's own answer -->
  <details class="card report"><summary>Agent 1 — HR Policy Specialist</summary>{{ req.policy|markdown|safe }}</details>
  <details class="card report"><summary>Agent 2 — Payroll Specialist</summary>{{ req.payroll|markdown|safe }}</details>
  <details class="card report"><summary>Agent 3 — Compliance Specialist</summary>{{ req.compliance|markdown|safe }}</details>
{% endif %}
{% endblock %}
```

**📄 `static/style.css`**

```css
/* ProITBridge colours (taken from the logo) */
:root {
  --navy: #002060;   /* "PRO"            */
  --cyan: #00b0f0;   /* "ITBRIDGE"       */
  --deep: #01153a;   /* globe background */
  --ink: #1a1a1a;    /* tagline text     */
  --cyan-soft: #e6f7fe;
  --muted: #5b6b82;
  --line: #e3eaf3;
  --bg: #f3f7fb;
}

* { box-sizing: border-box; }
body { margin: 0; font-family: Inter, sans-serif; color: var(--ink); background: var(--bg); font-size: 15px; line-height: 1.5; }
h1, h2, h3 { font-family: Poppins, sans-serif; color: var(--navy); margin: 0 0 14px; }
a { text-decoration: none; color: inherit; }

/* ---------- Left menu ---------- */
.sidebar { position: fixed; top: 0; bottom: 0; left: 0; width: 240px; padding: 20px 16px; background: var(--deep); }
.brand { display: block; background: white; border-radius: 12px; padding: 8px 10px; }
.brand img { width: 100%; display: block; }
.brand-sub { color: var(--cyan); font-size: 12px; letter-spacing: .08em; text-transform: uppercase; margin: 12px 4px 18px; }
.sidebar nav a { display: block; color: #cfe6f5; padding: 10px 12px; border-radius: 10px; font-weight: 500; margin-bottom: 4px; }
.sidebar nav a:hover { background: rgba(0, 176, 240, .15); color: white; }
.sidebar nav .nav-cta { background: var(--cyan); color: var(--deep); font-weight: 600; margin-top: 10px; }

/* ---------- Main area ---------- */
.main { margin-left: 240px; padding: 28px 32px; display: flex; flex-direction: column; gap: 20px; }
.main > h1 { font-size: 24px; margin: 0; }
footer { color: var(--muted); font-size: 12px; }

.card { background: white; border-radius: 14px; padding: 22px; box-shadow: 0 6px 20px rgba(1, 21, 58, .06); }
.muted { color: var(--muted); }
.link { color: var(--cyan); font-weight: 600; }
.kicker { color: var(--cyan); font-size: 12px; font-weight: 600; letter-spacing: .1em; text-transform: uppercase; }

/* ---------- Dashboard hero ---------- */
.hero { background: linear-gradient(135deg, var(--deep), var(--navy)); border-radius: 16px; padding: 28px; }
.hero h2 { color: white; font-size: 26px; margin: 6px 0 22px; }
.crew-map { display: flex; flex-direction: column; align-items: center; gap: 14px; }
.nodes { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; width: 100%; }
.node { border: 1px solid rgba(0, 176, 240, .5); background: rgba(255, 255, 255, .06); color: white; border-radius: 12px; padding: 10px; text-align: center; font-weight: 600; font-size: 14px; }
.node small { display: block; color: var(--cyan); font-weight: 500; }
.node.manager { background: var(--cyan); color: var(--deep); padding: 10px 30px; }
.node.manager small { color: var(--deep); }

.stats { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.stat { background: white; border-radius: 14px; padding: 18px 20px; border-top: 3px solid var(--cyan); }
.stat span { color: var(--muted); font-size: 13px; }
.stat b { display: block; font: 700 30px Poppins, sans-serif; color: var(--navy); }

/* ---------- Tables ---------- */
.table { width: 100%; border-collapse: collapse; }
.table th { text-align: left; font-size: 12px; text-transform: uppercase; color: var(--muted); padding: 10px; border-bottom: 2px solid var(--line); }
.table td { padding: 12px 10px; border-bottom: 1px solid var(--line); }

.badge { padding: 3px 10px; border-radius: 99px; font-size: 12px; font-weight: 600; }
.badge.running { background: var(--cyan-soft); color: #0077a8; }
.badge.done { background: #e3f7ef; color: #0f9d74; }
.badge.failed { background: #fde8e8; color: #d64545; }

/* ---------- Forms ---------- */
.form label { display: flex; flex-direction: column; gap: 6px; font-size: 13px; font-weight: 600; color: var(--navy); margin-bottom: 14px; }
.form input, .form select, .form textarea { font: 14px Inter, sans-serif; padding: 10px 12px; border: 1px solid var(--line); border-radius: 10px; }
.form input:focus, .form select:focus, .form textarea:focus { outline: none; border-color: var(--cyan); }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 0 16px; }
.btn { background: var(--navy); color: white; border: 0; padding: 11px 20px; border-radius: 10px; font: 600 14px Inter, sans-serif; cursor: pointer; }
.btn:hover { background: var(--cyan); color: var(--deep); }

/* ---------- Request page ---------- */
.info { display: flex; flex-wrap: wrap; gap: 28px; }
.info span { display: block; font-size: 11px; text-transform: uppercase; color: var(--muted); }
.info b { color: var(--navy); }
.working { display: flex; gap: 16px; align-items: center; border-left: 4px solid var(--cyan); }
.spinner { width: 34px; height: 34px; flex: none; border: 4px solid var(--cyan-soft); border-top-color: var(--cyan); border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.error { background: #fdecec; color: #8f2424; }

.report h1 { font-size: 22px; }
.report h2 { font-size: 18px; margin-top: 22px; border-bottom: 2px solid var(--cyan-soft); padding-bottom: 6px; }
.report table { border-collapse: collapse; width: 100%; margin: 10px 0; }
.report th { background: var(--navy); color: white; text-align: left; padding: 8px 12px; }
.report td { border-bottom: 1px solid var(--line); padding: 8px 12px; }
details.report summary { cursor: pointer; font: 600 16px Poppins, sans-serif; color: var(--navy); }
details.report[open] summary { margin-bottom: 12px; }

/* ---------- Phone screens ---------- */
@media (max-width: 800px) {
  .sidebar { position: static; width: auto; }
  .main { margin-left: 0; padding: 20px 16px; }
  .nodes { grid-template-columns: 1fr 1fr; }
  .table { display: block; overflow-x: auto; }
}

/* ---------- Ask HR ---------- */
.ask-box { border-left: 4px solid var(--cyan); }
.ask-row { display: flex; gap: 10px; }
.ask-row input { flex: 1; }
.stats.three { grid-template-columns: repeat(3, 1fr); }
.small { font-size: 13px; margin: 4px 0 8px; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 18px; }
.chip { border: 1px solid var(--line); background: var(--cyan-soft); color: var(--navy); border-radius: 99px; padding: 6px 12px; font: 500 13px Inter, sans-serif; cursor: pointer; }
.chip:hover { border-color: var(--cyan); background: white; }
.question-text { font: 600 20px Poppins, sans-serif; color: var(--navy); margin: 8px 0 12px; }
a.btn { display: inline-block; }
@media (max-width: 800px) { .stats.three { grid-template-columns: 1fr; } .ask-row { flex-direction: column; } }
```

---

## Run the web app 🚀

```bash
source .venv/bin/activate
uvicorn main:app --reload
```

1. Open **http://127.0.0.1:8000**.
2. Click **💬 Ask HR**, choose an employee (or Anonymous), click an example question or type your own, and press **Ask the AI HR Crew**.
3. Watch the **terminal**: the HR Manager decides which specialist to ask.
4. After 30 to 90 seconds the answer appears, with the policy section it comes from.
5. Try **Resignation** to see all 4 specialists work on one case.

FastAPI also gives you free API docs at **http://127.0.0.1:8000/docs**.

---

## Common problems

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: crewai` | Run `source .venv/bin/activate` first |
| `OPENAI_API_KEY is required` | `.env` is missing, or the key line is empty. Run `cp .env.example .env` and paste the key |
| Status shows **FAILED** with `401` | The OpenAI key in `.env` is wrong |
| `insufficient_quota` | Add billing credit to your OpenAI account |
| `model_not_found` | Change `OPENAI_MODEL` in `.env` (for example `gpt-4o-mini`) |
| The answer doesn't match your company | Edit `crew/hr_policy.md` |
| Want to start fresh | Stop the server and delete `hr_app.db` |

## Exercises for learners

1. Add a **Leave Agent** that only handles leave questions. Add it in `agents.py` and in both crews in `hr_crew.py`, then ask a leave question and see whether the manager picks it.
2. Add a new policy section (for example **"Dress Code"**) to `hr_policy.md` and ask a question about it.
3. Change `helpdesk_crew` to `Process.sequential`. Why does `hr_question_task` then need an `agent=`?
4. Show the 5 most-asked questions on the dashboard (an SQL `GROUP BY` in `database.py`).
