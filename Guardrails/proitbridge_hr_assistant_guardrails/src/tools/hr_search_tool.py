from langchain.tools import tool

from src.access.permissions import allowed_employee_ids
from src.knowledge.rag import RECORDS, employee_directory, search


def source_label(doc):
    if doc.metadata["source"] == RECORDS:
        return f"[{RECORDS} · {doc.metadata['employee_id']}]"
    return f"[{doc.metadata['source']} · page {doc.metadata['page']}]"


def make_search_tool(user):
    allowed_ids = allowed_employee_ids(user, employee_directory())

    @tool
    def search_hr_docs(query: str) -> str:
        """Search the PROITBRIDGE Employee Handbook and the employee records this user is allowed to see. Use it for every HR question."""
        docs = search(query, allowed_ids)
        return "\n\n".join(f"{source_label(doc)}\n{doc.page_content}" for doc in docs)

    return search_hr_docs
