import os
import yaml
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.models import Action, Observation, StepResult
from src.environment import SocTriageEnv
from src.tasks import TASKS_CONFIG

app = FastAPI(title="SOC Triage Environment")
env = SocTriageEnv()

from typing import Optional

class ResetRequest(BaseModel):
    task_id: Optional[str] = None

@app.post("/step", response_model=StepResult)
def step(action: Action):
    try:
        obs, reward, done, info = env.step(action)
        return StepResult(observation=obs, reward=reward, done=done, info=info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset", response_model=Observation)
def reset(req: Optional[ResetRequest] = None):
    target_task = req.task_id if (req and req.task_id) else "task_1_phishing"
    if target_task not in TASKS_CONFIG:
        raise HTTPException(status_code=404, detail="Task not found")
    obs = env.reset(target_task)
    return obs

@app.get("/state", response_model=Observation)
def get_state():
    return env._get_observation()

@app.get("/tasks")
def get_tasks():
    with open("openenv.yaml", "r") as f:
        config = yaml.safe_load(f)
    return {
        "tasks_config": config.get("tasks", []),
        "action_schema": Action.model_json_schema()
    }

@app.get("/grader")
def grader():
    return {
        "task_id": env.task_id,
        "score": env.score,
        "is_done": env.is_done
    }

@app.get("/")
def health_check():
    return {"status": "healthy"}

def start():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)