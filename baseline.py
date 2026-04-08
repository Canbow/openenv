# baseline.py
import os
import requests
import json
from openai import OpenAI

# Initialize the OpenAI client (Requires API_KEY and API_BASE_URL environment variables)
client = OpenAI(api_key=os.environ["API_KEY"], base_url=os.environ["API_BASE_URL"])

BASE_URL = "http://localhost:8000"

def get_action_schema():
    """Fetches the required JSON schema for the Action space from the API."""
    response = requests.get(f"{BASE_URL}/tasks")
    response.raise_for_status()
    return response.json()["action_schema"]

def run_agent_on_task(task_id: str, action_schema: dict):
    """Runs a single episode of the specified task using an LLM."""
    print(f"\n--- Starting {task_id} ---")
    
    # 1. Reset the environment for the specific task
    res = requests.post(f"{BASE_URL}/reset", json={"task_id": task_id})
    res.raise_for_status()
    observation = res.json()
    
    system_prompt = f"""You are an autonomous Cybersecurity SOC Analyst. 
Your goal is to investigate SIEM alerts and neutralize threats.
You must output ONLY valid JSON matching this schema: {json.dumps(action_schema)}
Think step-by-step. Query logs first, identify the malicious artifact, take a mitigation action (isolate/kill), and finally submit_report."""

    messages = [{"role": "system", "content": system_prompt}]
    
    for step in range(10): # Max steps safeguard
        print(f"Step {step + 1} | Observation: {observation['system_feedback']}")
        
        # Add the current observation to the agent's memory
        messages.append({"role": "user", "content": f"Current Observation: {json.dumps(observation)}"})
        
        # 2. Call OpenAI to get the next action
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        action_payload = json.loads(response.choices[0].message.content)
        print(f"Agent Action: {action_payload['command']} -> {action_payload.get('target', 'N/A')}")
        
        # 3. Execute the action in the environment
        step_res = requests.post(f"{BASE_URL}/step", json=action_payload)
        step_res.raise_for_status()
        step_data = step_res.json()
        
        observation = step_data["observation"]
        
        if step_data["done"]:
            print(f"Episode Finished. Final Feedback: {observation['system_feedback']}")
            break

    # 4. Fetch the final grader score
    grader_res = requests.get(f"{BASE_URL}/grader")
    final_score = grader_res.json()["score"]
    print(f"Final Score for {task_id}: {final_score}/1.0")
    return final_score

if __name__ == "__main__":
    try:
        # Verify the server is running
        requests.get(BASE_URL).raise_for_status()
    except requests.exceptions.ConnectionError:
        print("Error: FastAPI server is not running. Start it with: uvicorn main:app --reload")
        exit(1)
        
    if not os.environ.get("API_KEY") or not os.environ.get("API_BASE_URL"):
        print("Error: API_KEY or API_BASE_URL environment variable is missing.")
        exit(1)

    action_schema = get_action_schema()
    tasks = ["task_1_phishing", "task_2_maas_c2", "task_3_emotet_killchain"]
    
    total_score = 0
    for task in tasks:
        score = run_agent_on_task(task, action_schema)
        total_score += score
        
    print(f"\n=============================")
    print(f"BASELINE COMPLETE. Total Score: {total_score}/3.0")
    print(f"=============================")