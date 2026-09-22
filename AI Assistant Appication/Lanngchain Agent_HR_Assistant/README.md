# PROITBRIDGE HR Assistant

## Business Problem

Employees ask HR the same policy and calculation questions again and again —
leave rules, probation dates, payroll timing, travel allowances. This assistant
answers those questions from the official handbook and performs the common HR
calculations, so employees get a fast, consistent, policy-grounded answer.

## Objective

Build a working HR assistant using LangChain components, and in doing so learn
how each component works and how they connect through `create_agent`.

## LangChain Concepts

- System Prompt
- RAG
- Retriever (exposed as a tool)
- LLM
- Tool Calling
- Tool Validation
- Agent (`create_agent`)

## Architecture

The agent decides first whether a tool is needed. RAG is **not** a mandatory
first step — it runs only for knowledge questions, as the `search_handbook`
tool.

## Project Structure

```
proitbridge_hr_assistant/
├── app.py                 # Terminal interface — ask questions in a loop.
├── .env.example           # Template for your OpenAI API key.
├── requirements.txt       # Python dependencies.
├── README.md              # This file.
├── data/
│   └── PROITBRIDGE_Employee_Handbook_2026_1.pdf   # RAG knowledge source.
├── src/
    ├── config.py          # Settings: model names, RAG params, file paths.
    ├── prompts.py         # The agent's system prompt.
    ├── rag.py             # Load, split, embed, retrieve + the search_handbook tool.
    ├── tools.py           # The 7 HR tools + simple-Python validation.
    ├── chain.py           # The model and the create_agent agent.
    └── assistant.py       # Builds the agent and answers a question.

```

## Setup

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS / Linux
   source .venv/bin/activate
   ```

2. Install the requirements:

   ```bash
   pip install -r requirements.txt
   ```

3. Create your `.env` file from the template and add your key:

   ```bash
   # .env
   OPENAI_API_KEY=your_key_here
   ```

## Run

```bash
python app.py
```

The handbook is loaded and indexed once at startup, then you can ask questions
in a loop.

## Example Questions

- What is the casual leave policy?
- What is the standard probation period?
- When is salary normally credited?
- What is the internet allowance for remote-first employees?
- How much EL will I accrue after 6 completed months?
- Can I take 5 days of EL during probation?
- Can I submit a travel reimbursement claim 20 days after returning?
- What is the daily travel allowance for Grade 3 in a metro city?