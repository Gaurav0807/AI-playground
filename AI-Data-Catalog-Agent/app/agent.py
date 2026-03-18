from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_aws import ChatBedrock
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from typing import Annotated, Sequence
from pydantic import BaseModel, Field
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
import os

from app.tools.glue_tool import get_glue_table


# --- State ---
class AgentState(BaseModel):
    messages: Annotated[Sequence[AnyMessage], add_messages] = Field(default_factory=list)


# --- Tool ---
@tool
def glue_catalog_tool(query: str) -> str:
    """Use this tool to find tables and columns in AWS Glue catalog.
    Helpful when user asks about datasets, tables, schema, or user data."""
    database_name = "test__db"
    tables = get_glue_table(database_name)
    return str(tables)


tools = [glue_catalog_tool]

# --- LLM with tools bound ---
llm = ChatBedrock(
    model_id=os.getenv("BEDROCK_MODEL"),
    region_name=os.getenv("AWS_REGION"),
).bind_tools(tools)


# --- Nodes ---
def agent_node(state: AgentState):
    response = llm.invoke(state.messages)
    print("Agent Node :- ",response)
    return {"messages": [response]}


tool_node = ToolNode(tools)


# --- Conditional edge ---
def should_continue(state: AgentState):
    last_message = state.messages[-1]
    print("Last Message :- ",last_message)
    if last_message.tool_calls:
        return "tools"
    return END


# --- Build Graph ---
graph = StateGraph(AgentState)

graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
graph.add_edge("tools", "agent")

agent = graph.compile()


# --- Entry point ---
def run_agent(query: str):
    result = agent.invoke({"messages": [HumanMessage(content=query)]})
    print("Results :- ",result)
    return result["messages"][-1].content
