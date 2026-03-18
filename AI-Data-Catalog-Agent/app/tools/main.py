from fastapi import FastAPI
from app.agent import run_agent

app = FastAPI()

@app.get("/")
def health():
    return {"status":"AI Data Catalog Agent is running"}

@app.get("/ask")
def ask_agent(q:str):
    try:
        response = run_agent(q)
        return {
            "query": q,
            "answer": response
        }
    except Exception as e:
        return {
            "Error": str(e)
        }
