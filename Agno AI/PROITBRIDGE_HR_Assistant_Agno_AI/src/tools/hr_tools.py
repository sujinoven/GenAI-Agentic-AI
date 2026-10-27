from datetime import datetime, timedelta


# ---------------------------------------------------------------------------
# TOOL 1 — Leave Request Validator                       (Handbook Chapter 7)
# ---------------------------------------------------------------------------
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
    (For a general policy question like "What is the casual leave policy?" this is the wrong
    specialist — that is the HR Policy Agent's handbook question.)

    Args:
        leave_type: "EL" (Earned), "CL" (Casual) or "SL" (Sick).
        days: number of leave days requested (must be greater than 0).
        is_on_probation: True if the employee is still on probation.
        advance_days: working days of advance notice given.
    """
    if days <= 0:
        return {
            "valid": False,
            "reason": "Number of leave days must be greater than 0.",
            "policy_reference": "Chapter 7",
        }

    leave_type = leave_type.upper().strip()

    if leave_type not in {"EL", "CL", "SL"}:
        return {
            "valid": False,
            "reason": "Unsupported leave type. Use EL, CL or SL.",
            "policy_reference": "Chapter 7.1",
        }

    if leave_type == "EL":
        if is_on_probation:
            return {
                "valid": False,
                "reason": "Earned Leave cannot be availed during probation. "
                "It accrues but can only be taken after confirmation.",
                "policy_reference": "Chapter 4.5 / Chapter 7.2",
            }
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

    return {
        "valid": True,
        "reason": f"{leave_type} request for {days} day(s) is valid.",
        "policy_reference": "Chapter 7",
    }


# ---------------------------------------------------------------------------
# TOOL 2 — Earned Leave Accrual                        (Handbook Chapter 7.2)
# ---------------------------------------------------------------------------
def calculate_earned_leave_accrual(completed_months: int) -> dict:
    """Calculate accrued Earned Leave for a specific number of completed months.

    Use for questions like "how much EL will I accrue after 6 months".
    Handbook rule: Earned Leave accrues at 1.5 days per completed month.

    Args:
        completed_months: completed months of service (0 or more).
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
def calculate_probation_end(joining_date: str) -> dict:
    """Calculate the probation end date for a specific joining date (YYYY-MM-DD).

    Use for questions like "when does my probation end if I joined 2026-01-01".
    Handbook rule: standard probation is 90 calendar days from the date of
    joining, unless the appointment letter specifies otherwise (for example,
    180 days for Manager and above).

    Args:
        joining_date: joining date in YYYY-MM-DD format.
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
def check_payroll_deadline(date: str) -> dict:
    """Report payroll cut-off and salary/payslip dates for a specific date (YYYY-MM-DD).

    Use for questions like "when is salary credited" or "what is the payroll deadline".
    Handbook pay cycle:
      - Attendance period: 21st of a month to the 20th of the next month.
      - Payroll cut-off: 20th of every month.
      - Salary credit: last working day of the month, before 6 PM IST.
      - Payslip: published by the 1st of the following month.

    Args:
        date: a date in YYYY-MM-DD format.
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
            "Open - inputs accepted until the 20th."
            if inputs_open
            else "Closed - the 20th cut-off has passed; inputs move to the next cycle."
        ),
        "salary_credit_date": last_day.strftime("%Y-%m-%d")
        + " (last working day before 6 PM IST; preceding working day if it is a bank holiday)",
        "payslip_by": first_next_month.strftime("%Y-%m-%d"),
        "policy_reference": "Chapter 8.1",
    }


# ---------------------------------------------------------------------------
# TOOL 5 — Reimbursement Claim Validator              (Handbook Chapter 17.4)
# ---------------------------------------------------------------------------
def validate_reimbursement_claim(
    days_since_return: int,
    amount: float = 0.0,
    has_approved_travel_request: bool = True,
    has_required_documents: bool = True,
) -> dict:
    """Check whether a SPECIFIC travel reimbursement claim is valid.

    Use for questions like "can I claim reimbursement 20 days after returning".
    Handbook rules (Chapter 17.4):
      - Submit within 15 days of returning.
      - Claims older than 45 days need Finance Head approval and may be declined.
      - Bills above Rs.500 require legible scans.
      - An approved travel request is required.
      - Manager approval normally occurs within 3 working days.
      - Claims above Rs.50,000 have Finance settlement within 10 working days.

    Note: the handbook defines only the "within 15 days" and "older than 45 days"
    cases. A claim 16-45 days after returning is UNDEFINED, so this returns
    valid=None for that window rather than guessing.

    Args:
        days_since_return: days since returning from travel (0 or more).
        amount: claim amount in INR (optional).
        has_approved_travel_request: True if an approved travel request exists (optional).
        has_required_documents: True if legible bill scans are attached (optional).
    """
    if days_since_return < 0:
        return {
            "valid": False,
            "days_after_return": days_since_return,
            "reason": "Days since returning cannot be negative.",
            "policy_reference": "Chapter 17.4",
        }

    def result(valid, reason, policy_reference="Chapter 17.4"):
        return {
            "valid": valid,
            "days_after_return": days_since_return,
            "reason": reason,
            "policy_reference": policy_reference,
        }

    if days_since_return > 45:
        return result(
            False,
            "Claim is older than 45 days; this needs Finance Head approval and may be declined.",
        )

    if days_since_return > 15:  # 16-45 days: the handbook is silent -> undefined
        return result(
            None,
            "The handbook does not explicitly define the approval status for a claim "
            "submitted 16-45 days after returning. It only states that claims should be "
            "submitted within 15 days and that claims older than 45 days need Finance Head "
            "approval. Please confirm with HR/Finance.",
        )

    if not has_approved_travel_request:
        return result(
            False,
            "An approved travel request is required before claiming. Raise a travel request "
            "in the HRMS and get manager approval first.",
            policy_reference="Chapter 17.1 / 17.4",
        )

    if amount > 500 and not has_required_documents:
        return result(
            False,
            "Bills above Rs.500 require legible scans. Attach legible scans of every bill "
            "above Rs.500, plus the approved travel request.",
        )

    settlement = (
        "Finance settles within 10 working days (claim above Rs.50,000)."
        if amount > 50000
        else "Finance settles with the next payroll cycle."
    )
    return result(
        True,
        "Claim is within the 15-day window and has the required approvals. Manager approves "
        "within 3 working days. " + settlement,
    )


# ---------------------------------------------------------------------------
# TOOL 6 — Remote Work Internet Allowance             (Handbook Chapter 18.3)
# ---------------------------------------------------------------------------
def calculate_remote_work_allowance(work_model: str) -> dict:
    """Return the internet allowance for a SPECIFIC work model.

    Use for questions like "calculate my remote-first allowance".
    Handbook rules: hybrid = Rs.1,500/month, remote-first = Rs.2,500/month.

    Args:
        work_model: work model, either "hybrid" or "remote-first".
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
def calculate_travel_daily_allowance(location_type: str, grade: int) -> dict:
    """Return the travel daily allowance for a SPECIFIC location and grade.

    Use for questions like "travel allowance for Grade 3 in a metro".
    Values are taken directly from Handbook Chapter 17.3.

    Args:
        location_type: metro, other_india, asia_middle_east or europe_americas.
        grade: employee grade from 1 to 5.
    """
    if grade < 1 or grade > 5:
        return {
            "valid": False,
            "reason": "Grade must be between 1 and 5.",
            "policy_reference": "Chapter 17.3",
        }

    location = location_type.lower().strip()

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


# The Payroll Agent owns these seven HR tools (for general HR questions).
HR_TOOLS = [
    validate_leave_request,
    calculate_earned_leave_accrual,
    calculate_probation_end,
    check_payroll_deadline,
    validate_reimbursement_claim,
    calculate_remote_work_allowance,
    calculate_travel_daily_allowance,
]
