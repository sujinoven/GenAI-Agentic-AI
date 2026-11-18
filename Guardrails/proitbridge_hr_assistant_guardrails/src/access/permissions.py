ROLE_ACCESS = {"Employee": {"records": "own", "full_numbers": False},
               "HR Admin": {"records": "all", "full_numbers": True}}


def can_see_all_records(role):
    return ROLE_ACCESS[role]["records"] == "all"


def can_see_full_numbers(role):
    return ROLE_ACCESS[role]["full_numbers"]


def allowed_employee_ids(user, all_employee_ids):
    if can_see_all_records(user.role):
        return set(all_employee_ids)
    return {user.employee_id} if user.employee_id else set()


def access_summary(user):
    records = "All employee records" if can_see_all_records(user.role) else f"Own record only ({user.employee_id})"
    numbers = "Full personal numbers" if can_see_full_numbers(user.role) else "Personal numbers masked"
    return {"records": records, "numbers": numbers}
