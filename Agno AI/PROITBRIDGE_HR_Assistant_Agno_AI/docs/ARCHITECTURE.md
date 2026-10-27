# Architecture — PROITBRIDGE HR Assistant (Agno Multi-Agent · V2)

An employee resignation, handled by a five-agent **HR Manager Team**. The handbook
holds the rules; the employee record holds this employee's numbers; the team turns
them into a settlement, an exit checklist and the resignation documents.

```
                 EMPLOYEE REQUEST  (Arun Kumar — "I'm resigning…")
                              |
                              v
                 +-------------------------------+
                 |        HR MANAGER TEAM        |   coordinate mode
                 |  delegates in order,          |   gpt-4.1-mini
                 |  synthesizes Final Response   |
                 +---------------+---------------+
          delegates (in order)   |
   +--------------+--------------+--------------+-----------------+
   |              |              |              |                 |
   v              v              v              v                 v
+--------+  +-----------+  +------------+  +--------------+  +-----------+
| POLICY |  | PAYROLL   |  | COMPLIANCE |  |DOCUMENTATION |  | RESEARCH  |
+---+----+  +-----+-----+  +-----+------+  +------+-------+  +-----+-----+
    |             |              |                |                |
    v             v              v                v                v
 Handbook    Handbook +      Handbook +       record +         Web search
 (RAG)       Calculator +    record           findings ->      (external
             record +                         documents        only)
             7 HR tools
    |             |              |                |                |
    +-------------+------+-------+--------+-------+----------------+
                         |
                         v
                  FINAL HR RESPONSE
          Applicable Policy · Final Settlement ·
          Exit Checklist · Resignation & Handover
          Documents · Next Steps
                         |
                         v
            AGENTOS (tracing=True)  ->  AGNO CONTROL PLANE (os.agno.com)
```

## The two inputs

- **Employee Handbook (RAG)** — the rules, same for everyone. Policy, Payroll and
  Compliance all search it. Values are never invented; if the handbook doesn't
  cover something, the agent says so and defers to HR/Finance.
- **Employee record** (`src/tools/employee.py`) — this employee's own facts (Arun Kumar),
  read through the `get_employee_record` tool.

## The agents

- **HR Policy Agent** (handbook) — notice period, buy-out/waiver, leave during
  notice, EL encashment, resignation steps, with section numbers.
- **Payroll Agent** (handbook + Calculator + record + the 7 HR tools) — the
  full-and-final settlement, line by line in INR.
- **Compliance Agent** (handbook + record) — the exit checklist: asset return,
  clearances, confidentiality, post-exit documents, with owners and timelines.
- **Documentation Agent** (record + findings) — resignation letter, handover
  checklist, HR email. No handbook, no math — pure drafting.
- **HR Research Agent** (web) — external context only (e.g. general notice-period
  norms, Form 16 / PF process). Never presented as PROITBRIDGE policy.
- **HR Manager Team** (coordinate) — delegates in order and combines the results.

## Grounding rule

Internal policy and numbers come only from the handbook (Policy) and the employee
record + tools (Payroll / Compliance). Web results are external context, never
company policy. Missing facts become a `[placeholder]`, never an invented value.

## Why VS Code (vs the Colab)

Same agents, same problem as the Module 8 notebook — but a structured, runnable,
**observable** project: a modular `src/`, uv dependency management, a terminal app,
and AgentOS tracing you watch live in the Control Plane. That last part — a running
runtime with a live multi-agent trace — is the step the notebook can't show, and
it's the headline of this module.
