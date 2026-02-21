from langchain_aws import ChatBedrock
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field

load_dotenv()

llm = ChatBedrock(
    model_id="anthropic.claude-3-haiku-20240307-v1:0",
    region_name="us-east-1",
    model_kwargs={ 
        "max_tokens": 300
    }
)

class GraphSchema(BaseModel):
    topic: str = Field(description="The topic of the graph")
    post: str = Field(description="The LinkedIn post content")
    curated_post: str = Field(description="The curated LinkedIn post content")

def create_post(state: GraphSchema) -> GraphSchema:
    post = llm.invoke(
        f"Write a concise LinkedIn post about: {state.topic}"
    ).content

    return GraphSchema(
        topic=state.topic,
        post=post,
        curated_post=state.curated_post
    )

def curate_post(state: GraphSchema) -> GraphSchema:
    curated_post = llm.invoke(
        f"Curate the following LinkedIn post in a Gen Z tone:\n\n{state.post}"
    ).content

    return GraphSchema(
        topic=state.topic,
        post=state.post,
        curated_post=curated_post
    )

graph = StateGraph(GraphSchema)
graph.add_node("create_post", create_post)
graph.add_node("curate_post", curate_post)

graph.add_edge(START, "create_post")
graph.add_edge("create_post", "curate_post")
graph.add_edge("curate_post", END)

app = graph.compile()

result = app.invoke(
    GraphSchema(
        topic="The importance of data privacy in the digital age",
        post="",
        curated_post=""
    )
)

print(result)
