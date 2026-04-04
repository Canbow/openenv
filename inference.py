import os
import requests
import json
import time
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY", "dummy")

ENV_BASE_URL = "http://localhost:7860"

def run_episode(task_id: str):
    client = OpenAI(api_key=API_KEY, base_url=API_BASE_URL)
    
    try:
        res = requests.post(f"{ENV_BASE_URL}/reset", json={"task_id": task_id})
        res.raise_for_status()
        obs = res.json()
    except Exception as e:
        # Ignore initial setup errors if the server isn't up
        return
        
    print(f"[START] task={task_id} env=soc-triage-env model={MODEL_NAME}")
    
    done = False
    step_num = 0
    rewards = []
    
    messages = [
        {"role": "system", "content": "You are an autonomous AI agent for a cybersecurity environment. Your available actions are: query_network, query_processes, query_registry, isolate_ip, kill_process, submit_report. Format your response exactly as a JSON object containing 'command' and 'target'."}
    ]
    
    while not done and step_num < 20:
        step_num += 1
        
        # Prepare context
        obs_str = json.dumps(obs)
        messages.append({"role": "user", "content": f"Observation: {obs_str}\nNext action (JSON):"})
        
        try:
            # Query LLM
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                response_format={ "type": "json_object" }
            )
            action_content = response.choices[0].message.content
            action_dict = json.loads(action_content)
            
            cmd = action_dict.get("command", "submit_report")
            target = action_dict.get("target", "none")
            action_str = f"{cmd} {target}"
            
            # Step the environment
            step_res = requests.post(f"{ENV_BASE_URL}/step", json={"command": cmd, "target": target}).json()
            
            if "observation" not in step_res:
                print(f"[STEP] step={step_num} action={action_str} reward=0.00 done=true error=invalid_response")
                done = True
                continue
                
            obs = step_res["observation"]
            reward = float(step_res["reward"])
            done = bool(step_res["done"])
            
            rewards.append(reward)
            
            print(f"[STEP] step={step_num} action={action_str} reward={reward:.2f} done={str(done).lower()} error=null")
            
            messages.append({"role": "assistant", "content": action_content})
            
        except Exception as e:
            msg = str(e).replace('\n', ' ').replace('\r', '')
            print(f"[STEP] step={step_num} action=error reward=0.00 done=true error={msg}")
            done = True
            
    try:
        grader_res = requests.get(f"{ENV_BASE_URL}/grader").json()
        success = bool(grader_res.get("score", 0.0) > 0.5)
    except:
        success = False
        
    rewards_str = ",".join([f"{r:.2f}" for r in rewards]) if rewards else "0.00"
    print(f"[END] success={str(success).lower()} steps={step_num} rewards={rewards_str}")

if __name__ == "__main__":
    for _ in range(5):
        try:
            requests.get(ENV_BASE_URL)
            break
        except requests.exceptions.ConnectionError:
            time.sleep(1)
            
    tasks = ["task_1_phishing", "task_2_maas_c2", "task_3_emotet_killchain"]
    for task in tasks:
        run_episode(task)
