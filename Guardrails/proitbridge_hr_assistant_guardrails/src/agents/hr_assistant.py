import re
from functools import lru_cache

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from src.core.config import MODEL
from src.core.prompts import hr_prompt
from src.tools.hr_search_tool import make_search_tool


@lru_cache
def get_model():
    return ChatOpenAI(model=MODEL, temperature=0)


def build_hr_assistant(user):
    return create_agent(model=get_model(),
                        tools=[make_search_tool(user)],
                        system_prompt=hr_prompt(user))


def ask_hr(user, question):
    result     = build_hr_assistant(user).invoke({"messages": [{"role": "user", "content": question}]})
    messages   = result["messages"]
    sources    = []
    tool_calls = []
    for message in messages:
        if message.type == "ai":
            tool_calls += [call["args"].get("query", "") for call in message.tool_calls]
        if message.type == "tool":
            for label in re.findall(r"^\[(.+?)\]$", message.content, flags=re.MULTILINE):
                label = label.replace("Handbook · page ", "Handbook p.")
                if label not in sources:
                    sources.append(label)
    return {"answer"    : messages[-1].content,
            "sources"   : sources,
            "tool_calls": tool_calls,
            "llm_calls" : sum(message.type == "ai" for message in messages)}
