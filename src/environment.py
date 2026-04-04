from typing import Dict, Any, Tuple
from src.models import Observation, Action
from src.tasks import TASKS_CONFIG

class SocTriageEnv:
    def __init__(self):
        self.task_id = "task_1_phishing"
        self._reset_state()
        
    def _reset_state(self):
        self.task_data = TASKS_CONFIG.get(self.task_id, TASKS_CONFIG["task_1_phishing"])
        self.target_ip_isolated = False
        self.target_pid_killed = False
        self.score = 0.0
        self.steps = 0
        self.is_done = False
        self.system_feedback = "System initialized. Waiting for commands."
        
        # State visibility flags
        self.show_network = False
        self.show_processes = False
        self.show_registry = False
        
    def reset(self, task_id: str) -> Observation:
        if task_id in TASKS_CONFIG:
            self.task_id = task_id
        self._reset_state()
        return self._get_observation()
        
    def _get_observation(self) -> Observation:
        # Hide network and process logs initially until queried
        return Observation(
            active_siem_alert=self.task_data["initial_alert"],
            network_logs=self.task_data["network_logs"] if self.show_network else [],
            process_logs=self.task_data["process_logs"] if self.show_processes else [],
            registry_data=self.task_data["registry_data"] if self.show_registry else {},
            system_feedback=self.system_feedback
        )
        
    def step(self, action: Action) -> Tuple[Observation, float, bool, Dict[str, Any]]:
        if self.is_done:
            return self._get_observation(), 0.0, True, {"msg": "Episode already done.", "score": self.score}
            
        self.steps += 1
        reward = 0.0
        
        if action.command == "query_network":
            reward = 0.05
            self.show_network = True
            self.system_feedback = "Network logs queried successfully."
            
        elif action.command == "query_processes":
            reward = 0.05
            self.show_processes = True
            self.system_feedback = "Process logs queried successfully."
            
        elif action.command == "query_registry":
            reward = 0.05
            self.show_registry = True
            self.system_feedback = "Registry data queried successfully."
            
        elif action.command == "isolate_ip":
            if "malicious_ip" in self.task_data and self.task_data["malicious_ip"]:
                if action.target == self.task_data["malicious_ip"]:
                    if not self.target_ip_isolated:
                        reward = 0.5
                        self.target_ip_isolated = True
                        self.system_feedback = f"IP {action.target} isolated successfully."
                    else:
                        self.system_feedback = f"IP {action.target} is already isolated."
                else:
                    reward = -0.5
                    self.system_feedback = f"Incorrect IP {action.target} isolated. Penalty applied."
            else:
                self.system_feedback = f"No IP isolation required for this task."
                
        elif action.command == "kill_process":
            if "malicious_pid" in self.task_data and self.task_data["malicious_pid"]:
                if action.target == self.task_data["malicious_pid"]:
                    if not self.target_pid_killed:
                        reward = 0.5
                        self.target_pid_killed = True
                        self.system_feedback = f"Process {action.target} killed successfully."
                    else:
                        self.system_feedback = f"Process {action.target} is already killed."
                else:
                    reward = -1.0
                    self.system_feedback = f"Critical system process {action.target} killed! Severe penalty."
            else:
                self.system_feedback = f"No process kill required for this task."
                
        elif action.command == "submit_report":
            self.is_done = True
            
            # Check win condition
            won = False
            if self.task_id == "task_1_phishing" or self.task_id == "task_2_maas_c2":
                won = self.target_ip_isolated
            elif self.task_id == "task_3_emotet_killchain":
                won = self.target_pid_killed
                
            if won:
                reward = 0.5
                self.system_feedback = "Report submitted. Attack successfully mitigated!"
            else:
                reward = -0.5
                self.system_feedback = "Report submitted. The threat was not fully contained."
                
        # Update score and bound between 0.0 and 1.0
        self.score += reward
        self.score = max(0.0, min(1.0, self.score))
        
        obs = self._get_observation()
        
        return obs, reward, self.is_done, {"score": self.score}