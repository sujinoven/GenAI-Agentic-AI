
# PROITBRIDGE HR – AI-Powered MCP Server

An AI-powered Human Resources assistant built using **Python, Model Context Protocol (MCP), and CrewAI**.

The system allows AI assistants such as Claude Desktop to interact with employee records, answer HR-related questions, and process employee resignations through specialized AI agents.

---

## 1. Project Overview

PROITBRIDGE HR is an intelligent HR helpdesk that connects an AI assistant to an HR database through an MCP server.

It uses CrewAI to coordinate multiple specialized agents that handle HR queries and resignation workflows.

### Key Features

- Employee information retrieval
- AI-powered HR helpdesk
- Employee-specific HR responses
- HR policy assistance
- Leave balance information
- Salary and payslip queries
- Work-from-home policy assistance
- Reimbursement and benefits queries
- Resignation processing
- Final settlement assistance
- Exit checklist generation
- Resignation acceptance letter generation

---

## 2. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend development |
| FastMCP | MCP server implementation |
| Model Context Protocol | AI-to-system communication |
| CrewAI | Multi-agent orchestration |
| SQLite / Database | Employee information storage |
| UV | Python environment and dependency management |
| Claude Desktop | MCP client |

---

## 3. Project Structure

```text
PROITBRIDGE-HR-CREW/
│
├── crew/
│   └── hr_crew.py
│
├── .venv/
│
├── database.py
│
├── mcp_server.py
│
├── README.md
│
├── pyproject.toml
│
└── Other project files
```

---

## 4. Employee Information

The MCP server provides employee context to AI agents.

The employee database contains the following information:

| Field | Description |
|---|---|
| name | Employee name |
| designation | Job designation |
| department | Department |
| date_of_joining | Date of joining |
| monthly_gross_salary | Monthly gross salary |
| leave_balance | Available leave balance |
| notice_period | Notice period in days |

Employee records are converted into readable text using the `employee_summary()` helper function.

---

## 5. MCP Server Tools

The MCP server exposes three tools.

### Tool 1: list_employees

Retrieves employee information from the HR database.

Example:

```text
list_employees()
```

Purpose:
- Retrieve employee records.
- Identify employees by name.
- Help AI agents identify the correct employee.

### Tool 2: ask_hr

Allows employees to ask HR-related questions.

Arguments:

```python
ask_hr(
    question="How many leave days do I have?",
    employee_name="Arun"
)
```

Supported topics:

- Leave management
- Work from home
- Salary and payslips
- Reimbursements
- Employee benefits
- POSH policies
- Performance appraisals
- Resignation policies

The HR Manager agent delegates questions to relevant specialist agents.

### Tool 3: process_resignation

Processes employee resignation requests.

Arguments:

```python
process_resignation(
    employee_name="Priya",
    last_working_day="2026-12-31",
    reason="Personal reasons",
    resignation_date="2026-11-04"
)
```

The resignation workflow includes four specialist responsibilities:

1. HR policy verification
2. Final settlement calculation
3. Employee exit checklist
4. Resignation acceptance letter

---

## 6. Installation and Setup

### Prerequisites

Install the following:

- Python
- UV package manager
- Claude Desktop
- Required Python dependencies

### Step 1: Navigate to the project

Open PowerShell:

```powershell
cd "D:\ProITBridge\Courses\All Courses\Gen AI and Agentic AI\MCP\PROITBRIDGE-HR-CREW"
```

### Step 2: Activate virtual environment

```powershell
.venv\Scripts\Activate.ps1
```

### Step 3: Install dependencies

If your project uses `pyproject.toml`:

```powershell
uv sync
```

### Step 4: Initialize the database

The database is initialized automatically when the MCP server starts:

```python
database.init_db()
```

---

## 7. Running the MCP Server

Run the following command from the project directory:

```powershell
uv run mcp_server.py
```

The server starts with:

```python
mcp = FastMCP("proitbridge-hr")
```

The MCP server communicates using STDIO.

Important:
- MCP communication uses stdout.
- Application logs should go to stderr.
- CrewAI verbose output is redirected to stderr to avoid interfering with MCP communication.

---

## 8. Claude Desktop Configuration – Windows

Open:

```text
%APPDATA%\Claude\claude_desktop_config.json
```

Add the following MCP configuration:

```json
{
  "mcpServers": {
    "proitbridge-hr": {
      "command": "D:\\ProITBridge\\Courses\\All Courses\\Gen AI and Agentic AI\\MCP\\PROITBRIDGE-HR-CREW\\.venv\\Scripts\\uv.exe",
      "args": [
        "--directory",
        "D:\\ProITBridge\\Courses\\All Courses\\Gen AI and Agentic AI\\MCP\\PROITBRIDGE-HR-CREW",
        "run",
        "mcp_server.py"
      ]
    }
  }
}
```

Save the configuration and restart Claude Desktop.

Navigate to:

**Settings → Developer**

Verify that the `proitbridge-hr` MCP server is connected.

---

## 9. Example Questions

Once connected, try the following questions in Claude Desktop.

### Employee Information

- List all employees.
- Find the details of Arun.
- What is Arun's designation?
- What is Arun's joining date?

### HR Helpdesk

- How many leave days do I have?
- What is the company's work-from-home policy?
- Explain the reimbursement policy.
- What is the notice period for employees?
- What benefits are available to employees?

### Salary and Benefits

- What is my monthly gross salary?
- Explain the salary structure.
- How can I request my payslip?

### Resignation

- What is the resignation procedure?
- Process Priya's resignation.
- Calculate the final settlement.
- Generate an employee exit checklist.

---

## 10. Troubleshooting

### MCP Server Not Connecting

Check:

1. Python virtual environment exists.
2. UV executable path is correct.
3. Project directory is correct.
4. `mcp_server.py` exists.
5. Dependencies are installed.
6. Claude Desktop configuration contains valid JSON.

### Python Import Errors

Run:

```powershell
uv sync
```

### Database Errors

Check:

- Database file exists or can be created.
- `database.py` is available.
- `database.init_db()` executes successfully.

### MCP Communication Errors

Ensure that application logs and CrewAI output are sent to stderr rather than stdout.

Restart Claude Desktop after making configuration changes.

---

## 11. Security and Privacy

- Restrict access to employee records.
- Protect salary and personal employee information.
- Do not expose sensitive HR data to unauthorized users.
- Validate employee identity and permissions before processing sensitive requests.
- Protect database credentials and API keys.
- Review AI-generated resignation and settlement outputs before official approval.

**Important:** Connecting an MCP server does not automatically provide employee-level authorization. Implement access controls in the server before using it with real employee data.

---

## 12. Future Enhancements

Potential improvements include:

- Employee authentication
- Role-based access control
- HR document retrieval using RAG
- Payslip generation
- Automated leave approval workflows
- Email notifications
- HR analytics dashboard
- Integration with payroll systems
- Resignation approval workflows
- Audit logging

---

## 13. Project Summary

PROITBRIDGE HR demonstrates how MCP and CrewAI can be combined to build an intelligent HR automation system.

The architecture connects:

**Claude Desktop → MCP Server → CrewAI Agents → HR Database**

This approach allows AI assistants to interact with enterprise HR systems through structured tools and specialized AI agents.

---

**Project:** PROITBRIDGE HR  
**Framework:** CrewAI + FastMCP  
**Language:** Python  
**MCP Client:** Claude Desktop  
**Status:** Working MCP integration
