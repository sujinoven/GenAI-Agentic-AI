"""PROITBRIDGE HR Assistant.

This package groups the LangChain components taught in this module:

    config    -> settings (models, paths, RAG parameters)
    prompts   -> the agent's system prompt
    rag       -> load, split, embed, store, retrieve the Employee Handbook,
                 and expose it as the `search_handbook` tool
    tools     -> the 7 HR tools and their simple-Python validation
    chain     -> the model and the `create_agent` agent
    assistant -> the end-to-end HR Assistant workflow
"""
