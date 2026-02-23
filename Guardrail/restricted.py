import os, sys
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader

DOC_PATH = "internal_docs.md"
DB_PATH = "./chroma_db"

api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    print("OPENROUTER_API_KEY is requred",file=sys.stderr)
    sys.exit(1)

llm = ChatOpenAI(
    model="mistralai/mistral-7b-instruct",
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
    temperature=0.3,
    max_tokens=500,
)

if not os.path.exists(DOC_PATH):
    with open(DOC_PATH, "w") as f:
        f.write("""
    # Internal Platform Docs

    Our company is building a Kafka-based data platform.
    We process streaming data with Spark and store analytics in S3 and Athena.

    Deployment is handled via GitHub Actions and Terraform.
    """)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

if not os.path.exists(DB_PATH):
    loader = TextLoader(DOC_PATH)
    docs = loader.load()
    db = Chroma.from_documents(docs, embedding=embeddings, persist_directory=DB_PATH)
    db.persist()
    print("✅ Internal docs ingested")
else:
    db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)

def policy_guard(query: str) -> bool:
    prompt = f"""
    Classify the user question.

    If the question is about internal company docs or internal systems → INTERNAL  
    If the question is about general world knowledge, news, politics, celebrities → OUTSIDE  

    Question: {query}

    Reply with only one word: INTERNAL or OUTSIDE
    """
    decision = llm.invoke(prompt).content.strip().upper()
    return decision == "INTERNAL"



def answer_query(query: str) -> str:
    docs = db.similarity_search(query, k=3)
    context = "\n".join([d.page_content for d in docs])

    prompt = f"""
    You are an internal AI assistant.
    Answer ONLY using the context below.
    If the answer is not present, say:
    "I don't have that information in my internal knowledge base."

    Context:
    {context}

    Question:
    {query}
    """
    return llm.invoke(prompt).content


# CLI Code
print("🤖 Restricted AI Agent (OpenRouter). Type 'exit' to quit.\n")

while True:
    q = input("You: ")
    if q.lower() == "exit":
        break

    if not policy_guard(q):
        print("Bot: ❌ I can only answer questions related to internal documentation.\n")
        continue

    ans = answer_query(q)
    print(f"Bot: {ans}\n")