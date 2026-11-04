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
