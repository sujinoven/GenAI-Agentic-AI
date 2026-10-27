import json

# Sample HRMS record — the handbook holds the RULES (same for everyone),
# this record holds THIS employee's own facts. The agents need both.
EMPLOYEE_RECORD = {
    "employee_id": "PIB-E1042",
    "employee_name": "Arun Kumar",
    "role": "Senior Software Engineer",
    "grade": 3,
    "department": "Engineering",
    "reporting_manager": "Priya Raman",
    "date_of_joining": "2023-06-12",
    "employment_status": "Confirmed",
    "resignation_date": "2026-10-05",
    "notice_days_planned": 45,
    "requested_last_working_day": "2026-11-19",
    "salary": {
        "monthly_basic": 45000,
        "per_day_basic": 1500,
        "per_day_gross": 3000,
        "days_worked_in_final_month": 19,
    },
    "leave_balance": {"earned_leave": 22.5, "casual_leave": 3, "sick_leave": 6},
    "pending_reimbursements": [
        {"claim_id": "RC-2207", "purpose": "Client visit travel - Chennai", "amount": 8400, "status": "Approved"},
        {"claim_id": "RC-2231", "purpose": "Team offsite travel - Bengaluru", "amount": 5200, "status": "Pending manager approval"},
    ],
    "outstanding_advance": 10000,
    "assets_issued": ["Laptop", "Access card", "Headset"],
    "current_work": ["Payments API migration", "Mentor for the AI Engineering learner batch"],
}

EMPLOYEE_REQUEST = (
    "I am planning to resign from PROITBRIDGE. Based on my role, notice period, leave balance, salary, "
    "pending reimbursements and company policies, calculate my final settlement, identify everything I "
    "need to complete before my last working day, and prepare my resignation and HR handover documents."
)


def get_employee_record() -> str:
    """Return the current employee's HRMS record (PROITBRIDGE).

    Use this to load the employee's own facts — role, grade, joining date, employment status, planned
    notice, salary rates, leave balance, pending reimbursements, outstanding advance and issued assets —
    before computing a settlement, building an exit checklist, or drafting resignation documents.
    """
    return json.dumps(EMPLOYEE_RECORD, indent=2)
