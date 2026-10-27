from agno.db.sqlite import SqliteDb

from src.core.config import AGENTOS_DB_FILE, check_config
from src.tools.employee import EMPLOYEE_RECORD, EMPLOYEE_REQUEST
from src.core.observability import enable_tracing
from src.team.hr_manager_team import build_hr_team

SAMPLE_QUESTIONS = [
    EMPLOYEE_REQUEST,
    "What is the notice period for a confirmed employee, and how is Earned Leave encashed?",
    "Calculate my Earned Leave encashment and notice shortfall buy-out.",
    "What do I need to complete before my last working day?",
    "Draft my resignation letter and handover checklist.",
]


def main() -> None:
    print("=" * 64)
    print("PROITBRIDGE HR Assistant  (Agno Multi-Agent · HR Manager Team)")
    print("=" * 64)
    print(
        f"Sample employee loaded: {EMPLOYEE_RECORD['employee_name']} "
        f"({EMPLOYEE_RECORD['employee_id']}, {EMPLOYEE_RECORD['role']})."
    )
    print("The HR Manager delegates to: HR Policy · Payroll · Compliance · Documentation · Research.")
    print("Type 'exit' to quit.\n")
    print("Try the full resignation request, or a specific question:")
    for q in SAMPLE_QUESTIONS:
        print(f"  - {q[:92]}{'…' if len(q) > 92 else ''}")
    print()

    try:
        check_config()
        db = SqliteDb(db_file=AGENTOS_DB_FILE)
        enable_tracing(db)  # terminal runs are traced to the same DB the Control Plane reads
        team, _ = build_hr_team(db=db, load=True)
        print("Ready.\n")
    except KeyboardInterrupt:
        print("\nInterrupted during indexing. Delete the tmp/ folder and run again.")
        return
    except Exception as error:
        print(f"Startup error: {error}")
        return

    while True:
        try:
            question = input("Ask the HR Manager Team:\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break
        if question.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break
        if not question:
            continue
        try:
            team.print_response(question, stream=True)
            print()
        except Exception as error:
            print(f"\nSorry, something went wrong: {error}\n")


if __name__ == "__main__":
    main()
