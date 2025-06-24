# FastAPI + Celery Background Task Version
from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_community.chat_models import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import Tool, initialize_agent, AgentType
from dotenv import load_dotenv
import os
import logging

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger("uvicorn")

search = DuckDuckGoSearchRun()
tools = [
    Tool(
        name="DuckDuckGo Search",
        func=search.run,
        description="Useful for searching recent academic articles or blog posts"
    )
]

llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

class QueryRequest(BaseModel):
    query: str

responses = {}  # Simple in-memory store (use Redis or DB in production)

@app.post("/ask")
async def ask_agent(request: QueryRequest, background_tasks: BackgroundTasks):
    task_id = str(hash(request.query))
    background_tasks.add_task(run_agent_task, request.query, task_id)
    return {"message": "Query is being processed", "task_id": task_id}

@app.get("/result/{task_id}")
async def get_result(task_id: str):
    result = responses.get(task_id)
    if result:
        return {"response": result}
    return {"status": "processing"}

def run_agent_task(query: str, task_id: str):
    try:
        prompt = (
            f"You are a pharma research assistant. Find recent articles on: {query}. "
            f"Summarize the key findings in 150 words. Mention trials, drugs, companies, and safety data where available."
        )
        result = agent.run(prompt)
        responses[task_id] = result
    except Exception as e:
        responses[task_id] = f"Error: {str(e)}"

# Run with: uvicorn app:app --reload
