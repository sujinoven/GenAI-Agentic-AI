import secrets
from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    user_id: str
    name: str
    role: str
    title: str
    employee_id: str | None = None


DEMO_USERS = {"arjun"   : User("arjun", "Arjun Kumar", "Employee", "Associate Software Engineer", "PIB-E1002"),
              "meena"   : User("meena", "Meena Selvam", "Employee", "Senior Trainer – Data Science", "PIB-E1003"),
              "hr_admin": User("hr_admin", "HR Admin", "HR Admin", "Demo account · HR & Payroll")}

SESSIONS = {}


def sign_in(user_id):
    user = DEMO_USERS.get(user_id)
    if user is None:
        return None
    token           = secrets.token_urlsafe(16)
    SESSIONS[token] = user.user_id
    return token


def current_user(token):
    user_id = SESSIONS.get(token or "")
    return DEMO_USERS.get(user_id) if user_id else None


def sign_out(token):
    SESSIONS.pop(token or "", None)
