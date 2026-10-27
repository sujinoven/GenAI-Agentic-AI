"""
Database — saves employees, HR questions and resignation requests in a small SQLite file (hr_app.db).
SQLite comes with Python, so there is nothing to install.
"""
import sqlite3

DB_FILE = "hr_app.db"


def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # lets us use row["name"] instead of row[1]
    return conn


def init_db():
    """Create the tables (only the first time) and add sample employees."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT, designation TEXT, department TEXT,
                date_of_joining TEXT, monthly_salary REAL,
                leave_balance REAL, notice_period_days INTEGER
            )""")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER,        -- can be empty (anonymous question)
                question TEXT,
                status TEXT,                -- RUNNING / DONE / FAILED
                answer TEXT,
                error TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )""")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER,
                resignation_date TEXT, last_working_day TEXT, reason TEXT,
                status TEXT,                -- RUNNING / DONE / FAILED
                policy TEXT, payroll TEXT, compliance TEXT, final_report TEXT,
                error TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )""")

        # Sample employees so the app is not empty on day 1
        if conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO employees (name, designation, department, date_of_joining, "
                "monthly_salary, leave_balance, notice_period_days) VALUES (?, ?, ?, ?, ?, ?, ?)",
                [
                    ("Arun Kumar", "Senior Software Engineer", "Engineering", "2019-06-04", 120000, 20, 60),
                    ("Priya Raman", "Data Scientist", "Data Science", "2022-01-17", 90000, 14, 60),
                    ("Karthik Subramanian", "AI Trainer Lead", "Training", "2020-11-01", 105000, 30, 90),
                    ("Divya Lakshmi", "HR Executive", "HR", "2023-08-21", 48000, 9, 30),
                ],
            )


# ---------------- Employees ----------------
def get_employees():
    with get_connection() as conn:
        return conn.execute("SELECT * FROM employees ORDER BY name").fetchall()


def get_employee(employee_id):
    with get_connection() as conn:
        return conn.execute("SELECT * FROM employees WHERE id = ?", (employee_id,)).fetchone()


def add_employee(name, designation, department, date_of_joining, monthly_salary, leave_balance, notice_period_days):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO employees (name, designation, department, date_of_joining, "
            "monthly_salary, leave_balance, notice_period_days) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, designation, department, date_of_joining, monthly_salary, leave_balance, notice_period_days),
        )


# ---------------- HR questions ----------------
def add_question(employee_id, question):
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO questions (employee_id, question, status) VALUES (?, ?, 'RUNNING')",
            (employee_id, question),
        )
        return cursor.lastrowid


def get_questions():
    with get_connection() as conn:
        return conn.execute(
            "SELECT questions.*, employees.name AS employee_name "
            "FROM questions LEFT JOIN employees ON employees.id = questions.employee_id "
            "ORDER BY questions.id DESC"
        ).fetchall()


def get_question(question_id):
    with get_connection() as conn:
        return conn.execute(
            "SELECT questions.*, employees.name AS employee_name "
            "FROM questions LEFT JOIN employees ON employees.id = questions.employee_id "
            "WHERE questions.id = ?",
            (question_id,),
        ).fetchone()


def save_answer(question_id, answer):
    with get_connection() as conn:
        conn.execute("UPDATE questions SET status = 'DONE', answer = ? WHERE id = ?", (answer, question_id))


def save_question_error(question_id, error_message):
    with get_connection() as conn:
        conn.execute("UPDATE questions SET status = 'FAILED', error = ? WHERE id = ?", (error_message, question_id))


# ---------------- Resignation requests ----------------
def add_request(employee_id, resignation_date, last_working_day, reason):
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO requests (employee_id, resignation_date, last_working_day, reason, status) "
            "VALUES (?, ?, ?, ?, 'RUNNING')",
            (employee_id, resignation_date, last_working_day, reason),
        )
        return cursor.lastrowid


def get_requests():
    with get_connection() as conn:
        return conn.execute(
            "SELECT requests.*, employees.name AS employee_name, employees.department "
            "FROM requests JOIN employees ON employees.id = requests.employee_id "
            "ORDER BY requests.id DESC"
        ).fetchall()


def get_request(request_id):
    with get_connection() as conn:
        return conn.execute(
            "SELECT requests.*, employees.name AS employee_name, employees.designation, employees.department "
            "FROM requests JOIN employees ON employees.id = requests.employee_id "
            "WHERE requests.id = ?",
            (request_id,),
        ).fetchone()


def save_crew_result(request_id, answers):
    with get_connection() as conn:
        conn.execute(
            "UPDATE requests SET status = 'DONE', policy = ?, payroll = ?, compliance = ?, final_report = ? "
            "WHERE id = ?",
            (answers["policy"], answers["payroll"], answers["compliance"], answers["final_report"], request_id),
        )


def save_crew_error(request_id, error_message):
    with get_connection() as conn:
        conn.execute("UPDATE requests SET status = 'FAILED', error = ? WHERE id = ?", (error_message, request_id))
