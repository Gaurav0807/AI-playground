from langchain_community.tools import DuckDuckGoSearchRun
from langchain_aws import ChatBedrock
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv

load_dotenv()

# 🔎 Search tool
search_tool = DuckDuckGoSearchRun()

# 🧠 LLM (Claude 3 Haiku on Bedrock)
llm = ChatBedrock(
    model_id="anthropic.claude-3-haiku-20240307-v1:0",
    region_name="us-east-1",
    model_kwargs={"max_tokens": 200, "temperature": 0.2}
)

# 📝 Prompt to understand user intent
prompt = PromptTemplate(
    template="""
You are an AI assistant.
Based on the user's query and the search results, summarize in 2–3 lines what the user is actually asking about.

User Query:
{topic}

Search Results:
{results}
""",
    input_variables=["topic", "results"]
)

parser = StrOutputParser()

# 🔗 Chain: User query → Search → Prompt → LLM → Output
chain = (
    RunnableLambda(lambda x: {
        "topic": x["topic"],
        "results": search_tool.run(x["topic"])
    })
    | prompt
    | llm
    | parser
)

# 🖥 CLI loop
if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        answer = chain.invoke({"topic": user_input})
        print("AI:", answer)