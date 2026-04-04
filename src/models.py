from pydantic import BaseModel, Field
from typing import List, Dict, Literal, Optional, Any

class Observation(BaseModel):
    active_siem_alert: str
    network_logs: List[Dict[str, Any]]
    process_logs: List[Dict[str, Any]]
    registry_data: Dict[str, Any]
    system_feedback: str

class Action(BaseModel):
    command: Literal["query_network", "query_processes", "query_registry", "kill_process", "isolate_ip", "submit_report"]
    target: str
    report_findings: Optional[str] = None

class StepResult(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: Dict[str, Any]