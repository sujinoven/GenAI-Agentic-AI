"""The 7 PROITBRIDGE HR tools.

Each is a plain Python function turned into a LangChain tool with @tool.
Validation is simple Python (if/else) and runs before the operation.
Every value comes from the PROITBRIDGE Employee Handbook (see policy_reference).
"""

from datetime import datetime, timedelta

from langchain_core.tools import tool


# ---------------------------------------------------------------------------
# TOOL 1 — Leave Request Validator                       (Handbook Chapter 7)
# ---------------------------------------------------------------------------
@tool
def validate_leave_request(
    leave_type: str,
    days: int,
    is_on_probation: bool,
    advance_days: int,
) -> dict:
    """Check whether a SPECIFIC leave request is allowed or prohibited.

    Use this whenever the employee asks whether a particular leave request is allowed,
    permitted, valid, or prohibited -- e.g. "Can I take 4 days of casual leave in a row?",
    "Can I take 5 days of EL during probation?", "Is 2 days of CL with 1 day notice okay?".
    (For a general policy question like "What is the casual leave policy?" do not use this tool.)

    leave_type: "EL" (Earned), "CL" (Casual) or "SL" (Sick).
    days: number of leave days requested.
    is_on_probation: True if the employee is still on probation.
    advance_days: working days of advance notice given.
    """
    leave_type = leave_type.upper().strip()

    # --- Validation (runs before any decision is returned) ---
    if days <= 0:
        return {
            "valid": False,
            "reason": "Leave days must be greater than 0.",
            "policy_reference": "Chapter 7",
        }

    if leave_type not in {"EL", "CL", "SL"}:
        return {
            "valid": False,
            "reason": "Unsupported leave type. Use EL, CL or SL.",
            "policy_reference": "Chapter 7.1",
        }

    if leave_type == "EL":
        # EL accrues during probation but cannot be availed until confirmation.
        if is_on_probation:
            return {
                "valid": False,
                "reason": "Earned Leave cannot be availed during probation. "
                "It accrues but can only be taken after confirmation.",
                "policy_reference": "Chapter 4.5 / Chapter 7.2",
            }
        # Advance-notice rule depends on the length of the leave.
        if days <= 3 and advance_days < 7:
            return {
                "valid": False,
                "reason": "Earned Leave of 1-3 days needs at least 7 working days notice.",
                "policy_reference": "Chapter 7.2",
            }
        if days >= 4 and advance_days < 21:
            return {
                "valid": False,
                "reason": "Earned Leave of 4 or more days needs at least 21 working days notice.",
                "policy_reference": "Chapter 7.2",
            }

    if leave_type == "CL" and days > 3:
        return {
            "valid": False,
            "reason": "Casual Leave cannot exceed 3 consecutive days.",
            "policy_reference": "Chapter 7.3",
        }

    # --- Valid request ---
    return {
        "valid": True,
        "reason": f"{leave_type} request for {days} day(s) is valid.",
        "policy_reference": "Chapter 7",
    }


# ---------------------------------------------------------------------------
# TOOL 2 — Earned Leave Accrual                        (Handbook Chapter 7.2)
# ---------------------------------------------------------------------------
@tool
def calculate_earned_leave_accrual(completed_months: int) -> dict:
    """Calculate accrued Earned Leave for a specific number of completed months.

    Use for questions like "how much EL will I accrue after 6 months".
    Handbook rule: Earned Leave accrues at 1.5 days per completed month.
    """
    if completed_months < 0:
        return {
            "valid": False,
            "reason": "Completed months cannot be negative.",
            "policy_reference": "Chapter 7.2",
        }

    accrual_rate = 1.5
    earned_leave_days = completed_months * accrual_rate

    return {
        "valid": True,
        "completed_months": completed_months,
        "accrual_rate_per_month": accrual_rate,
        "earned_leave_days": earned_leave_days,
        "policy_reference": "Chapter 7.2",
    }


# ---------------------------------------------------------------------------
# TOOL 3 — Probation End Calculator                    (Handbook Chapter 4.5)
# ---------------------------------------------------------------------------
@tool
def calculate_probation_end(joining_date: str) -> dict:
    """Calculate the probation end date for a specific joining date (YYYY-MM-DD).

    Use for questions like "when does my probation end if I joined 2026-01-01".
    Handbook rule: standard probation is 90 calendar days from the date of
    joining, unless the appointment letter specifies otherwise (for example,
    180 days for Manager and above).
    """
    try:
        start = datetime.strptime(joining_date.strip(), "%Y-%m-%d")
    except ValueError:
        return {
            "valid": False,
            "reason": "joining_date must be in YYYY-MM-DD format.",
            "policy_reference": "Chapter 4.5",
        }

    probation_days = 90
    end = start + timedelta(days=probation_days)

    return {
        "valid": True,
        "joining_date": start.strftime("%Y-%m-%d"),
        "probation_days": probation_days,
        "probation_end_date": end.strftime("%Y-%m-%d"),
        "note": "Standard probation is 90 calendar days unless your appointment "
        "letter specifies otherwise (e.g., 180 days for Manager and above).",
        "policy_reference": "Chapter 4.5",
    }


# ---------------------------------------------------------------------------
# TOOL 4 — Payroll Deadline Checker                    (Handbook Chapter 8.1)
# ---------------------------------------------------------------------------
@tool
def check_payroll_deadline(date: str) -> dict:
    """Report payroll cut-off and salary/payslip dates for a specific date (YYYY-MM-DD).

    Use for questions like "when is salary credited" or "what is the payroll deadline".
    Handbook pay cycle:
      - Attendance period: 21st of a month to the 20th of the next month.
      - Payroll cut-off: 20th of every month.
      - Salary credit: last working day of the month, before 6 PM IST.
      - Payslip: published by the 1st of the following month.
    """
    try:
        d = datetime.strptime(date.strip(), "%Y-%m-%d")
    except ValueError:
        return {
            "valid": False,
            "reason": "date must be in YYYY-MM-DD format.",
            "policy_reference": "Chapter 8.1",
        }

    cutoff_day = 20
    inputs_open = d.day <= cutoff_day

    # Last calendar day of the current month.
    if d.month == 12:
        first_next_month = datetime(d.year + 1, 1, 1)
    else:
        first_next_month = datetime(d.year, d.month + 1, 1)
    last_day = first_next_month - timedelta(days=1)

    return {
        "valid": True,
        "date": d.strftime("%Y-%m-%d"),
        "attendance_period": "21st to 20th",
        "payroll_cutoff": d.replace(day=cutoff_day).strftime("%Y-%m-%d"),
        "payroll_inputs_status": (
            "Open — inputs accepted until the 20th."
            if inputs_open
            else "Closed — the 20th cut-off has passed; inputs move to the next cycle."
        ),
        "salary_credit_date": last_day.strftime("%Y-%m-%d")
        + " (last working day before 6 PM IST; preceding working day if it is a bank holiday)",
        "payslip_by": first_next_month.strftime("%Y-%m-%d"),
        "policy_reference": "Chapter 8.1",
    }


# ---------------------------------------------------------------------------
# TOOL 5 — Reimbursement Claim Validator              (Handbook Chapter 17.4)
# ---------------------------------------------------------------------------
@tool
def validate_reimbursement_claim(
    days_since_return: int,
    amount: float,
    has_approved_travel_request: bool,
    has_required_documents: bool,
) -> dict:
    """Check whether a SPECIFIC travel reimbursement claim is valid.

    Use for questions like "can I claim reimbursement 20 days after returning" or
    "is my claim valid". Handbook rules:
      - Submit within 15 days of returning.
      - Claims older than 45 days need Finance Head approval and may be declined.
      - Bills above Rs.500 require legible scans.
      - An approved travel request is required.
      - Manager approval normally occurs within 3 working days.
      - Claims above Rs.50,000 have Finance settlement within 10 working days.
    """
    if amount <= 0:
        return {
            "valid": False,
            "reason": "Claim amount must be greater than 0.",
            "next_step": "Enter the actual claim amount.",
            "policy_reference": "Chapter 17.4",
        }

    if not has_approved_travel_request:
        return {
            "valid": False,
            "reason": "An approved travel request is required before claiming.",
            "next_step": "Raise a travel request in the HRMS and get manager approval first.",
            "policy_reference": "Chapter 17.1 / 17.4",
        }

    if amount > 500 and not has_required_documents:
        return {
            "valid": False,
            "reason": "Bills above Rs.500 require legible scans.",
            "next_step": "Attach legible scans of every bill above Rs.500, plus the approved travel request.",
            "policy_reference": "Chapter 17.4",
        }

    if days_since_return > 45:
        return {
            "valid": False,
            "reason": "Claim is older than 45 days.",
            "next_step": "This needs Finance Head approval and may be declined.",
            "policy_reference": "Chapter 17.4",
        }

    # The handbook states submission within 15 days, and Finance Head approval
    # beyond 45 days, but is silent on the 16-45 day window. We do not infer a
    # rule for it — we report that it is undefined and defer to HR/Finance.
    if days_since_return > 15:
        return {
            "valid": None,
            "reason": "The handbook does not explicitly define the approval status for a claim "
            "submitted 16-45 days after returning. It only states that claims should be submitted "
            "within 15 days and that claims older than 45 days need Finance Head approval.",
            "next_step": "Please confirm with HR/Finance.",
            "policy_reference": "Chapter 17.4",
        }

    settlement = (
        "Finance settles within 10 working days (claim above Rs.50,000)."
        if amount > 50000
        else "Finance settles with the next payroll cycle."
    )

    return {
        "valid": True,
        "reason": "Claim is within the 15-day window and has the required approvals.",
        "next_step": "Manager approves within 3 working days. " + settlement,
        "policy_reference": "Chapter 17.4",
    }


# ---------------------------------------------------------------------------
# TOOL 6 — Remote Work Internet Allowance             (Handbook Chapter 18.3)
# ---------------------------------------------------------------------------
@tool
def calculate_remote_work_allowance(work_model: str) -> dict:
    """Return the internet allowance for a SPECIFIC work model.

    Use for questions like "calculate my remote-first allowance" or "what allowance do I
    get on hybrid". Not for the general allowance policy.
    Handbook rules: hybrid = Rs.1,500/month, remote-first = Rs.2,500/month.
    """
    model = work_model.lower().strip().replace("_", "-").replace(" ", "-")

    allowances = {"hybrid": 1500, "remote-first": 2500}

    if model not in allowances:
        return {
            "valid": False,
            "reason": "Unsupported work model. Supported models: hybrid, remote-first.",
            "policy_reference": "Chapter 18.3",
        }

    return {
        "valid": True,
        "work_model": model,
        "internet_allowance_per_month": allowances[model],
        "currency": "INR",
        "policy_reference": "Chapter 18.3",
    }


# ---------------------------------------------------------------------------
# TOOL 7 — Travel Daily Allowance                      (Handbook Chapter 17.3)
# ---------------------------------------------------------------------------
@tool
def calculate_travel_daily_allowance(location_type: str, grade: int) -> dict:
    """Return the travel daily allowance for a SPECIFIC location and grade.

    Use for questions like "travel allowance for Grade 3 in a metro".
    location_type: metro, other_india, asia_middle_east or europe_americas.
    grade: employee grade from 1 to 5.
    Values are taken directly from Handbook Chapter 17.3.
    """
    location = location_type.lower().strip()

    # Rates keyed by location, then by grade band. (amount, currency)
    rates = {
        "metro": {"1-2": (1200, "INR"), "3": (1600, "INR"), "4-5": (2200, "INR")},
        "other_india": {"1-2": (900, "INR"), "3": (1200, "INR"), "4-5": (1600, "INR")},
        "asia_middle_east": {"1-2": (45, "USD"), "3": (60, "USD"), "4-5": (80, "USD")},
        "europe_americas": {"1-2": (65, "USD"), "3": (85, "USD"), "4-5": (110, "USD")},
    }

    if location not in rates:
        return {
            "valid": False,
            "reason": "Unsupported location. Use metro, other_india, "
            "asia_middle_east or europe_americas.",
            "policy_reference": "Chapter 17.3",
        }

    if grade not in (1, 2, 3, 4, 5):
        return {
            "valid": False,
            "reason": "Grade must be between 1 and 5.",
            "policy_reference": "Chapter 17.3",
        }

    band = "1-2" if grade in (1, 2) else "3" if grade == 3 else "4-5"
    amount, currency = rates[location][band]

    return {
        "valid": True,
        "location_type": location,
        "grade": grade,
        "daily_allowance": amount,
        "currency": currency,
        "policy_reference": "Chapter 17.3",
    }


# ---------------------------------------------------------------------------
# Tool registry — connects a tool name to its function.
# HR_TOOLS is the list we bind to the LLM; TOOL_REGISTRY is used to execute
# the tool the LLM selects.
# ---------------------------------------------------------------------------
HR_TOOLS = [
    validate_leave_request,
    calculate_earned_leave_accrual,
    calculate_probation_end,
    check_payroll_deadline,
    validate_reimbursement_claim,
    calculate_remote_work_allowance,
    calculate_travel_daily_allowance,
]

TOOL_REGISTRY = {hr_tool.name: hr_tool for hr_tool in HR_TOOLS}
