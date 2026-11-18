import re
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

from guardrails.errors import ValidationError
from guardrails.validators import FailResult

from src.access.permissions import ROLE_ACCESS, access_summary, can_see_all_records
from src.agents.hr_assistant import ask_hr
from src.audit.guard_log import log_event
from src.auth.users import DEMO_USERS
from src.core.config import has_api_key
from src.guardrails.input_guard import input_guard_for, mask_only_guard
from src.guardrails.output_guard import output_guard_for
from src.knowledge.rag import employee_directory, get_vector_store

GUARD_LOCK = Lock()

BLOCK_MESSAGES = {"ValidLength"       : "Sorry — your question is too long. Please keep it under 300 characters.",
                  "BanList"           : "Sorry — this request was blocked by the input guard.",
                  "OtherEmployeeCheck": "Sorry — you can ask only about your own record. Questions about other employees are blocked for your role."}

REASONS = {"ValidLength"       : "Longer than 300 characters",
           "BanList"           : "Attack phrase found",
           "OtherEmployeeCheck": "Asks about another employee"}


def user_card(user):
    return {"user_id"    : user.user_id,
            "name"       : user.name,
            "role"       : user.role,
            "title"      : user.title,
            "employee_id": user.employee_id,
            "all_records": can_see_all_records(user.role),
            "access"     : access_summary(user)}


def other_employees(user):
    if can_see_all_records(user.role):
        return []
    names = []
    for employee_id, name in employee_directory().items():
        if employee_id != user.employee_id:
            names += [name, *name.split(), employee_id]
    return names


def run_guard(guard, text, metadata):
    with GUARD_LOCK:
        try:
            outcome = guard.validate(text, metadata=metadata)
        except ValidationError:
            logs    = guard.history.last.iterations.last.validator_logs
            blocked = next(log.validator_name for log in logs if isinstance(log.validation_result, FailResult))
            return None, [], blocked
    return outcome.validated_output, [summary.validator_name for summary in outcome.validation_summaries], None


def check_list(guard, fixed, blocked):
    checks, stopped = [], False
    for validator in guard.get_validators("output"):
        name = type(validator).__name__
        if stopped:
            result = "skip"
        elif name == blocked:
            result, stopped = "block", True
        elif name in fixed:
            result = "fix"
        else:
            result = "pass"
        checks.append({"name": name, "result": result})
    return checks


def status_label(masked_in, masked_out):
    if masked_in and masked_out:
        return "MASKED IN · OUT"
    if masked_in:
        return "MASKED IN"
    if masked_out:
        return "MASKED OUT"
    return "PASSED"


def find_tags(*texts):
    return sorted({tag for text in texts for tag in re.findall(r"<[A-Z_]+>", text or "")})


def ask_hr_with_guardrails(user, question):
    started = time.perf_counter()

    guard                     = input_guard_for(user.role)
    to_llm, fixed_in, blocked = run_guard(guard, question, {"other_employees": other_employees(user)})
    result                    = {"user"      : user_card(user),
                                 "input"     : {"checks": check_list(guard, fixed_in, blocked), "to_llm": to_llm},
                                 "agent"     : None,
                                 "output"    : None,
                                 "masked_in" : bool(fixed_in),
                                 "masked_out": False}

    if blocked:
        logged_question, _, _ = run_guard(mask_only_guard(), question, {})
        validators            = [blocked]
        result["status"]      = "BLOCKED"
        result["answer"]      = BLOCK_MESSAGES[blocked]
        result["reason"]      = REASONS[blocked]
    else:
        reply           = ask_hr(user, to_llm)
        out_guard       = output_guard_for(user.role)
        result["agent"] = {"sources": reply["sources"], "tool_calls": reply["tool_calls"], "llm_calls": reply["llm_calls"]}
        if out_guard is None:
            answer, fixed_out = reply["answer"], []
            result["output"]  = {"active": False, "checks": []}
        else:
            answer, fixed_out, _ = run_guard(out_guard, reply["answer"], {})
            result["output"]     = {"active": True, "checks": check_list(out_guard, fixed_out, None)}
        logged_question      = to_llm
        validators           = sorted(set(fixed_in + fixed_out))
        result["masked_out"] = bool(fixed_out)
        result["status"]     = status_label(result["masked_in"], result["masked_out"])
        result["answer"]     = answer

    result["tags"]    = find_tags(to_llm, result["answer"])
    result["seconds"] = round(time.perf_counter() - started, 1)
    log_event({"user_id"   : user.user_id,
               "user"      : user.name,
               "role"      : user.role,
               "question"  : logged_question,
               "status"    : result["status"],
               "masked_in" : result["masked_in"],
               "masked_out": result["masked_out"],
               "validators": validators})
    return result


def compare_users(question):
    with ThreadPoolExecutor(max_workers=len(DEMO_USERS)) as pool:
        return list(pool.map(lambda user: ask_hr_with_guardrails(user, question), DEMO_USERS.values()))


def warm_up():
    employee_directory()
    for role in ROLE_ACCESS:
        input_guard_for(role)
        output_guard_for(role)
    mask_only_guard()
    if has_api_key():
        get_vector_store()
