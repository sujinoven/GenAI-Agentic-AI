# ProITBridge HR Crew 🤖 — AI HR Management System (Simple Version)

A multi-agent HR management web app built with **CrewAI + OpenAI + FastAPI**.
The AI code is the **same code as our Colab notebook**, split into small files.

**What it can do**
- 💬 **Ask HR**: any employee can ask any HR question (leave, WFH, salary, reimbursement, benefits, POSH, resignation and more) and get an answer based on the company HR policy.
- 📄 **Resignation**: process a full resignation (policy check, settlement, exit checklist and letters).
- 👥 **Employees**: list and add employees.

## 📁 Folder structure

```
proitbridge-hr-crew/
│
├── crew/                  🧠 THE AI PART (same as the Colab notebook)
│   ├── llm.py             Step 1 – connect to OpenAI
│   ├── agents.py          Step 2 – CREATE THE AGENTS      ⭐
│   ├── tasks.py           Step 3 – GIVE TASKS TO AGENTS   ⭐
│   ├── hr_crew.py         Step 4 – make the Crews and run them
│   └── hr_policy.md       📖 the company HR policy the agents read
│
├── main.py                🌐 the website (FastAPI pages)
├── database.py            💾 saves employees, questions & requests (SQLite)
│
├── templates/             🎨 HTML pages
├── static/                🎨 colours (style.css) + logo
│
├── pyproject.toml         📦 project + libraries list (used by uv)
├── uv.lock                📦 exact library versions (same setup for every learner)
├── .python-version        📦 Python version for this project (3.12)
├── requirements.txt       (only for people who still use pip)
└── .env                   🔑 your OpenAI key (secret!)
```

## 🗺️ Colab notebook → project file

| Colab cell | What it does | Project file |
|---|---|---|
| `pip install crewai` | install | `pyproject.toml` (`uv add crewai`) |
| `os.environ[...] = getpass(...)`, `llm = LLM(...)` | OpenAI key + model | `crew/llm.py` (the key comes from `.env`) |
| `hr_policy_agent = Agent(...)` … `hr_manager = Agent(...)` | **create agents** | `crew/agents.py` |
| `hr_policy_task = Task(...)` … `documentation_task = Task(...)` | **give tasks** | `crew/tasks.py` (Part B) |
| `final_hr_task` for the HR Manager | a general HR task | `crew/tasks.py` → `hr_question_task` (Part A) |
| `hr_crew = Crew(..., process=Process.hierarchical, manager_agent=hr_manager)` | build the crew | `crew/hr_crew.py` |
| `result = await hr_crew.kickoff_async()` | run it | `crew/hr_crew.py` → `ask_hr()` / `run_resignation_crew()` |

## 🧠 One team, two crews

The **same 5 agents** do all the HR work. We only change the tasks:

| Crew | Tasks | Who decides who works? |
|---|---|---|
| `helpdesk_crew` (Ask HR) | 1 task: `hr_question_task`, with **no agent assigned** | The **HR Manager** reads the question and delegates to the right specialist(s) |
| `resignation_crew` | 4 tasks, one per specialist | Each task already names its agent; the HR Manager coordinates |

Examples of how the HR Manager delegates a question:
- *"How many casual leaves do I get?"* → HR Policy Agent
- *"How much leave encashment will I get?"* → HR Policy + Payroll Agents
- *"Write an email to request paternity leave"* → HR Policy + Documentation Agents

## 🔄 What happens when an employee asks a question

```
templates/ask.html  (question form)
   │  POST /ask
   ▼
main.py  ── saves the question (RUNNING) ── answer_question() runs in the background
   │
   ▼
crew/hr_crew.py  ask_hr(question, employee details)
   │
   ▼
HR Manager 👔 ── reads the question ── delegates ──► HR Policy / Payroll / Compliance / Documentation
   │
   ▼
database.py  saves the answer (DONE)
   │
   ▼
templates/question.html shows the answer (the page refreshes every 5 s until it is done)
```

## ▶️ Run it (macOS) — with uv

We use **[uv](https://docs.astral.sh/uv/)** instead of pip. It is much faster, installs Python for you,
and `uv run` always uses the project's own environment, so there is **no `source .venv/bin/activate`** to forget.

**1. Install uv (one time only)**
```bash
brew install uv
```

**2. Set up the project**
```bash
cd ~/Downloads/proitbridge-hr-crew
uv sync                     # creates .venv and installs everything from uv.lock
cp .env.example .env        # then open .env (NOT .env.example) and paste your OpenAI key
open -e .env
```

**3. Test 1: ask one HR question in the terminal (like Colab)**
```bash
uv run python -m crew.hr_crew
```

**4. Test 2: run the full website**
```bash
uv run uvicorn main:app --reload
```
Open http://127.0.0.1:8000, click **💬 Ask HR** and ask anything.

### 📦 uv commands learners will use

| Command | What it does | pip version |
|---|---|---|
| `uv sync` | Install everything the project needs | `pip install -r requirements.txt` |
| `uv run <command>` | Run inside the project's environment | `source .venv/bin/activate` then the command |
| `uv add <library>` | Install a new library **and** save it in `pyproject.toml` | `pip install <library>` + edit requirements.txt |
| `uv remove <library>` | Uninstall and remove it from `pyproject.toml` | `pip uninstall <library>` |

> 💡 How this project was created with uv (for reference):
> ```bash
> uv init --python 3.12 --bare      # creates pyproject.toml
> uv add -r requirements.txt        # adds the libraries + creates uv.lock
> ```

To change what the agents know, edit **`crew/hr_policy.md`**. It is plain text, so learners can add their own company's rules.

Step-by-step teaching guide with all the code: **BUILD_GUIDE.md**
