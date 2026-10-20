from typing import Literal,TypedDict
from typing_extensions import Annotated
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

Route=Literal["policy_question","hr_action","out_of_scope"]

class HRState(TypedDict):
    messages:Annotated[list[AnyMessage],add_messages]
    route:Route 
    policy_context:str
    rejection_explained:bool