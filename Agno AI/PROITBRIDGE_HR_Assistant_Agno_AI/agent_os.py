from agno.db.sqlite import SqliteDb
from agno.os import AgentOS

from src.core.config import AGENTOS_DB_FILE, check_config
from src.team.hr_manager_team import build_hr_team

check_config()

db = SqliteDb(db_file=AGENTOS_DB_FILE)

team, knowledge = build_hr_team(db=db, load=True)
print("HR Manager Team ready. Starting AgentOS on http://localhost:7777 …")

agent_os = AgentOS(
    name="PROITBRIDGE HR Assistant (Agno V2)",
    description="PROITBRIDGE HR Manager Team — Policy, Payroll, Compliance, Documentation, Research — with tracing.",
    teams=[team],
    knowledge=[knowledge],
    db=db,
    tracing=True,
)
app = agent_os.get_app()


if __name__ == "__main__":
    agent_os.serve(app=app)
