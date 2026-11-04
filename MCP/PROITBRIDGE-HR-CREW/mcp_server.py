
import contextlib
import logging
import sys
from datetime import date, datetime

from mcp.server import FastMCP

import database
from crew.hr_crew import (
    ask_hr as run_helpdesk_crew,
    run_resignation_crew,
)

# --------------------------------------------------
# MCP SERVER INITIALIZATION
# --------------------------------------------------

mcp = FastMCP("proitbridge-hr")

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr
)

logger = logging.getLogger(__name__)

# Initialize employee database
database.init_db()


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

@contextlib.contextmanager
def crew_output_to_stderr():
    """
    Redirect CrewAI output from stdout to stderr.

    STDIO MCP servers reserve stdout for MCP communication.
    """
    with contextlib.redirect_stdout(sys.stderr):
        yield


def find_employee(name: str):
    """
    Find an employee by full or partial name.

    Returns None if employee is not found.
    """
    name = (name or "").strip().lower()

    if not name:
        return None

    for emp in database.get_employees():
        if name in emp["name"].lower():
            return emp

    return None


def employee_summary(emp: dict | None) -> str:
    """
    Convert employee database record into readable
    text for AI agents.
    """

    if emp is None:
        return "Not Specified (anonymous question)"

    return (
        f"Name: {emp.get('name', 'Not Specified')}, "
        f"Designation: {emp.get('designation', 'Not Specified')}, "
        f"Department: {emp.get('department', 'Not Specified')}, "
        f"Date of Joining: {emp.get('date_of_joining', 'Not Specified')}, "
        f"Monthly Gross Salary: {emp.get('monthly_gross_salary', 'Not Specified')}, "
        f"Leave Balance: {emp.get('leave_balance', 'Not Specified')} days, "
        f"Notice Period: {emp.get('notice_period', 'Not Specified')} days"
    )


# --------------------------------------------------
# MCP TOOL 1: LIST EMPLOYEES
# --------------------------------------------------

@mcp.tool()
async def list_employees() -> str:
    """
    List all employees available in the HR database.

    Useful when an employee name is unknown.
    """

    logger.info("Listing employees")

    employees = database.get_employees()

    if not employees:
        return "No employees found in the HR database."

    result = []

    for emp in employees:
        result.append(employee_summary(emp))

    return "\n\n".join(result)


# --------------------------------------------------
# MCP TOOL 2: ASK HR
# --------------------------------------------------

@mcp.tool()
async def ask_hr(
    question: str,
    employee_name: str = ""
) -> str:
    """
    Ask the ProITBridge AI HR team an HR-related question.

    The HR Manager agent delegates the question to
    specialist agents and answers using company HR policy.

    Topics include:
    Leave, WFH, salary, payslip, reimbursement,
    benefits, POSH, appraisal and resignation.

    Args:
        question: Employee's HR question.
        employee_name: Optional employee name.
    """

    logger.info("ask_hr: %s", question)

    emp = find_employee(employee_name)

    question_id = database.add_question(
        emp["id"] if emp else None,
        question
    )

    try:
        with crew_output_to_stderr():
            answer = await run_helpdesk_crew(
                question,
                employee_summary(emp)
            )

        database.save_answer(question_id, answer)

        return answer

    except Exception as error:
        logger.exception("ask_hr failed")

        database.save_question_error(
            question_id,
            str(error)
        )

        return f"The HR crew failed: {error}"


# --------------------------------------------------
# MCP TOOL 3: PROCESS RESIGNATION
# --------------------------------------------------

@mcp.tool()
async def process_resignation(
    employee_name: str,
    last_working_day: str,
    reason: str,
    resignation_date: str = ""
) -> str:
    """
    Process an employee's resignation using the
    four-agent resignation crew.

    Agents handle:
    1. HR policy verification
    2. Final settlement
    3. Exit checklist
    4. Resignation acceptance letter

    Args:
        employee_name: Employee name or partial name.
        last_working_day: Requested last working day (YYYY-MM-DD).
        reason: Reason for leaving.
        resignation_date: Resignation date (YYYY-MM-DD).
                          Defaults to today.
    """

    logger.info(
        "Processing resignation for: %s",
        employee_name
    )

    # Find employee
    emp = find_employee(employee_name)

    if emp is None:
        return (
            f"No employee found matching '{employee_name}'. "
            "Use list_employees to see available employees."
        )

    # Validate dates
    try:
        datetime.strptime(last_working_day, "%Y-%m-%d")

        if not resignation_date:
            resignation_date = date.today().isoformat()

        datetime.strptime(resignation_date, "%Y-%m-%d")

    except ValueError:
        return (
            "Invalid date format. Please use YYYY-MM-DD "
            "for resignation date and last working day."
        )

    # Prepare employee context
    emp_context = employee_summary(emp)

    logger.info(
        "Running resignation crew for employee: %s",
        emp["name"]
    )

    try:
        with crew_output_to_stderr():

            result = await run_resignation_crew(
                emp_context,
                last_working_day,
                reason,
                resignation_date
            )

        logger.info(
            "Resignation processing completed for: %s",
            emp["name"]
        )

        return str(result)

    except Exception as error:
        logger.exception("Resignation processing failed")

        return (
            f"Resignation processing failed for "
            f"{emp['name']}: {error}"
        )


# --------------------------------------------------
# START MCP SERVER
# --------------------------------------------------

if __name__ == "__main__":
    logger.info("Starting ProITBridge HR MCP Server...")

    mcp.run()
