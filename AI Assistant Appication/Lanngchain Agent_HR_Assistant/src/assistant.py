import ast
import json

from langchain_core.messages import HumanMessage

from .chain import build_agent
from .config import check_config
from .rag import build_retriever


def _validation_status(tool_output) -> str:
    valid = tool_output.get("valid") if isinstance(tool_output, dict) else None
    if valid is True:
        return "passed"
    if valid is False:
        return "failed"
    return "undetermined"


def _as_dict(content):
    """A tool result arrives as text on the ToolMessage; parse it back to a dict."""
    if isinstance(content, dict):
        return content
    if not isinstance(content, str):
        return None
    for parse in (json.loads, ast.literal_eval):
        try:
            parsed = parse(content)
        except Exception:
            continue
        if isinstance(parsed, dict):
            return parsed
    return None


class HRAssistant:
    def __init__(self, show_steps: bool = False) -> None:
        check_config()
        self.show_steps = show_steps

        # Loads and indexes the handbook once (Load & Split -> Store -> Retrieve).
        self.retriever = build_retriever()

        # The agent holds the model, the tools and the system prompt.
        self.agent = build_agent(self.retriever)

    def _trace(self, message: str) -> None:
        if self.show_steps:
            print(message)

    def _trace_run(self, messages) -> None:
        """Replay what the agent did, from the conversation it returned."""
        if not self.show_steps:
            return

        # tool_call_id -> tool name, so a ToolMessage can be labelled.
        called_tools = {}

        for message in messages:
            kind = getattr(message, "type", None)

            if kind == "ai":
                tool_calls = getattr(message, "tool_calls", None)
                if not tool_calls:
                    self._trace("[LLM] Generating the final answer.")
                    continue
                for tool_call in tool_calls:
                    called_tools[tool_call["id"]] = tool_call["name"]
                    if tool_call["name"] == "search_handbook":
                        self._trace("[LLM] No HR tool needed — knowledge question.")
                        self._trace("[RAG] Retrieving handbook context.")
                    else:
                        self._trace(f"[LLM] Tool selected: {tool_call['name']}")

            elif kind == "tool":
                # The handbook tool returns raw text, not a validation result.
                if called_tools.get(message.tool_call_id) == "search_handbook":
                    continue
                result = _as_dict(message.content)
                self._trace(f"[TOOL] Validation: {_validation_status(result)}")
                self._trace(f"[TOOL] Result: {message.content}")

    def ask(self, question: str) -> str:
        self._trace("[LLM] Deciding: knowledge question, or tool needed?")

        result = self.agent.invoke({"messages": [HumanMessage(content=question)]})
        self._trace_run(result["messages"])

        # The agent returns the full conversation; the last message is the answer.
        # `.text` replaces the StrOutputParser we used to run by hand.
        return result["messages"][-1].text
