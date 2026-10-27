"""
STEP 4 — CREATE THE CREWS AND RUN THEM 🚀

📘 Colab:  hr_crew = Crew(agents=[...], tasks=[...],
                          process=Process.hierarchical, manager_agent=hr_manager)
           result = await hr_crew.kickoff_async()

We make TWO crews with the SAME team of agents:
    helpdesk_crew    → answers any HR question        (1 task)
    resignation_crew → processes a resignation         (4 tasks)

Test in the terminal (no website needed):
    python -m crew.hr_crew
"""
import asyncio
from pathlib import Path

from crewai import Crew, Process

from crew.agents import compliance_agent, documentation_agent, hr_manager, hr_policy_agent, payroll_agent
from crew.tasks import compliance_task, documentation_task, hr_policy_task, hr_question_task, payroll_task

# The company HR policy handbook (crew/hr_policy.md) — given to the agents as {hr_policy}
HR_POLICY = (Path(__file__).parent / "hr_policy.md").read_text(encoding="utf-8")

ALL_SPECIALISTS = [hr_policy_agent, payroll_agent, compliance_agent, documentation_agent]

# ---------------------------------------------------------------
# Crew 1 — HR Helpdesk: answers any HR question
# ---------------------------------------------------------------
helpdesk_crew = Crew(
    agents=ALL_SPECIALISTS,
    tasks=[hr_question_task],
    process=Process.hierarchical,  # the manager decides who works on the question
    manager_agent=hr_manager,
    verbose=True,
)

# ---------------------------------------------------------------
# Crew 2 — Resignation: the same 4-task crew as the Colab notebook
# ---------------------------------------------------------------
resignation_crew = Crew(
    agents=ALL_SPECIALISTS,
    tasks=[hr_policy_task, payroll_task, compliance_task, documentation_task],
    process=Process.hierarchical,
    manager_agent=hr_manager,      # the orchestrator (NOT in the agents list)
    verbose=True,
)


async def ask_hr(question: str, employee_context: str = "Not specified") -> str:
    """Answer ONE HR question. Returns the answer as Markdown text."""
    crew = helpdesk_crew.copy()  # fresh copy, so two requests at the same time don't mix
    result = await crew.kickoff_async(inputs={
        "question": question,
        "employee_context": employee_context,
        "hr_policy": HR_POLICY,
    })
    return result.raw


async def run_resignation_crew(employee_inputs: dict) -> dict:
    """Process ONE resignation and return every agent's answer."""
    crew = resignation_crew.copy()
    result = await crew.kickoff_async(inputs={**employee_inputs, "hr_policy": HR_POLICY})

    return {
        "policy": result.tasks_output[0].raw,       # Task 1 answer
        "payroll": result.tasks_output[1].raw,      # Task 2 answer
        "compliance": result.tasks_output[2].raw,   # Task 3 answer
        "final_report": result.raw,                 # Task 4 answer (final)
    }


# Run this file directly to test, just like the Colab notebook
if __name__ == "__main__":
    question = "How many casual leaves do I get, and can I carry them forward to next year?"
    answer = asyncio.run(ask_hr(question, "Name: Arun Kumar, Senior Software Engineer, Engineering"))
    print("\n\n========== HR ANSWER ==========\n")
    print(answer)
