# How It Works — PROITBRIDGE HR Assistant (Agno Multi-Agent · V2)

One employee request — Arun Kumar is resigning — flows through the HR Manager Team.
The rule that never changes: policy and numbers come only from the handbook and the
employee record, never invented, and web results are never company policy.

## The full flow (the resignation request)

**Request:** "I'm resigning — calculate my settlement, tell me what to finish before
my last day, and prepare my resignation and handover documents."

1. **HR Manager Team** receives it and delegates in order.
2. **HR Policy Agent** searches the handbook → notice period (confirmed = 60 days),
   notice buy-out, leave during notice, Earned Leave encashment ("at basic, on
   separation"), resignation steps — each with its section number.
3. **Payroll Agent** calls `get_employee_record`, searches the handbook for what a
   full-and-final includes, and uses the calculator for each line: final-month
   salary (19 days × ₹3,000 gross), EL encashment (22.5 × ₹1,500 basic = ₹33,750),
   approved reimbursements (₹8,400), the notice shortfall buy-out (planned 45 vs
   required 60 → 15 days short), minus the ₹10,000 outstanding advance → net estimate.
4. **Compliance Agent** builds the exit checklist from the handbook + record: return
   Laptop / Access card / Headset, clearances (IT, Finance, Admin, Library, manager),
   confidentiality, relieving letter (within 7 working days of clearance), Form 16,
   PF — with owners and timelines.
5. **Documentation Agent** drafts the resignation letter (to Priya Raman, via HRMS),
   the handover checklist (Payments API migration, mentoring, credentials, risks),
   and a short HR email — `[placeholder]` for anything missing.
6. **HR Manager** combines it into one **Final HR Response**: Applicable Policy ·
   Final Settlement · Exit Checklist · Resignation & Handover Documents · Next Steps.
7. AgentOS records the whole trace: the leader delegating → each specialist → its
   handbook / tool / calculator / web calls.

## Targeted questions (one specialist each)

- "What is the notice period for a confirmed employee, and how is EL encashed?" →
  **HR Policy Agent** → handbook.
- "Calculate my EL encashment and notice shortfall buy-out." → **Payroll Agent** →
  record + calculator.
- "What must I complete before my last working day?" → **Compliance Agent** →
  handbook + record.
- "Draft my resignation letter and handover checklist." → **Documentation Agent**.
- "What's the typical notice period in Indian IT?" → **HR Research Agent** → web
  (clearly labelled external, not PROITBRIDGE policy).

## The 7 HR tools (general HR questions)

The Payroll Agent also carries the 7 PROITBRIDGE HR tools for everyday questions
beyond the resignation (same values as the earlier project): leave validation, EL
accrual, probation end, payroll dates, reimbursement validation, remote-work
allowance, travel allowance. For example: "How much EL will I accrue after 6
months?" → 6 × 1.5 = **9 days**; "Can I take 4 days of casual leave in a row?" →
not allowed (max 3).

## When the handbook doesn't cover it

If a rule isn't in the handbook, the agent says so and defers to HR/Finance — it
never fabricates a policy or fills the gap from the web. That grounding discipline
is the whole point.
