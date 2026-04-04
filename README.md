# SOC Triage Environment

A realistic cybersecurity SOC (Security Operations Center) Triage environment for the OpenEnv benchmark.

## Environment Description and Motivation
The environment simulates a real-world task performed daily by human security analysts: investigating alerts from a SIEM, querying endpoint and network telemetry, and neutralizing threats by isolating malicious IPs or killing malicious processes.

This is a critical area for AI agents. Instead of toy problems, this evaluates an agent's reasoning against complex logs, noise, and adversarial behavior hidden in system metrics.

## Action and Observation Spaces

**Observation Space**:
- `active_siem_alert` (str): The initial alert that triggered the investigation.
- `network_logs` (list of dicts): A list of network connections (hidden until queried).
- `process_logs` (list of dicts): Active endpoint processes (hidden until queried).
- `registry_data` (dict): Registry persistence mechanisms (hidden until queried).
- `system_feedback` (str): Text feedback on previous actions (e.g., successful query or kill).

**Action Space**:
- `command` (enum): The operation to perform. Limited to `query_network`, `query_processes`, `query_registry`, `kill_process`, `isolate_ip`, `submit_report`.
- `target` (str): The specific IP address or Process ID (PID) to target.
- `report_findings` (str, optional): Final report upon submission.

## Tasks and Difficulty
1. **task_1_phishing (Easy)**: Identify a malicious IP address communicating outbound after an anomalous login. Requires isolating the IP based on basic network anomaly detection.
2. **task_2_maas_c2 (Medium)**: Identify a C2 (Command & Control) server through periodic beaconing patterns in network logs and process mapping. Requires isolating the correct IP among noisy benign processes.
3. **task_3_emotet_killchain (Hard)**: Identify a complex malware killchain (Emotet-style) spawned from an Office document. Requires querying processes to see the powershell execution, verifying persistence in registry, and killing the exact malicious child PID without crashing host services. 

## Setup and Usage

**Docker execution (Recommended)**:
```bash
docker build -t openenv-soc .
docker run -p 7860:7860 openenv-soc
```

**Local execution**:
```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 7860
```

**Testing the Inference Baseline**:
```bash
export OPENAI_API_KEY="your-api-key"
python inference.py
```

## Baseline Scores
- task_1_phishing: 1.0
- task_2_maas_c2: 1.0 
- task_3_emotet_killchain: 1.0
(When run using `gpt-4o-mini`)
