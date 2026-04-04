TASKS_CONFIG = {
    "task_1_phishing": {
        "description": "Identify malicious IP from network logs.",
        "difficulty": "Easy",
        "malicious_ip": "192.168.1.100",
        "malicious_pid": None,
        "initial_alert": "Multiple failed logins followed by successful login and immediate outbound connection.",
        "network_logs": [
            {"source_ip": "10.0.0.5", "destination_ip": "192.168.1.100", "port": 443, "bytes_sent": 50000, "status": "allowed"},
            {"source_ip": "10.0.0.5", "destination_ip": "8.8.8.8", "port": 53, "bytes_sent": 120, "status": "allowed"},
            {"source_ip": "10.0.0.7", "destination_ip": "192.168.1.50", "port": 80, "bytes_sent": 1500, "status": "allowed"}
        ],
        "process_logs": [],
        "registry_data": {}
    },
    "task_2_maas_c2": {
        "description": "Isolate a C2 server IP based on anomalous traffic.",
        "difficulty": "Medium",
        "malicious_ip": "203.0.113.45",
        "malicious_pid": None,
        "initial_alert": "Anomalous beaconing activity detected on host 10.0.0.12.",
        "network_logs": [
            {"source_ip": "10.0.0.12", "destination_ip": "203.0.113.45", "port": 443, "bytes_sent": 250, "status": "allowed", "interval": "periodic"},
            {"source_ip": "10.0.0.12", "destination_ip": "203.0.113.45", "port": 443, "bytes_sent": 300, "status": "allowed", "interval": "periodic"},
            {"source_ip": "10.0.0.12", "destination_ip": "198.51.100.5", "port": 80, "bytes_sent": 12000, "status": "allowed"}
        ],
        "process_logs": [
            {"pid": "4512", "name": "svchost.exe", "user": "SYSTEM", "network_active": True},
            {"pid": "1024", "name": "chrome.exe", "user": "jdoe", "network_active": True}
        ],
        "registry_data": {}
    },
    "task_3_emotet_killchain": {
        "description": "Kill a malicious payload process and find registry persistence.",
        "difficulty": "Hard",
        "malicious_ip": "198.51.100.99",
        "malicious_pid": "8901",
        "persistence_key": "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\Updater",
        "initial_alert": "Macro execution in Office document detected, followed by suspicious child process.",
        "network_logs": [
            {"source_ip": "10.0.0.50", "destination_ip": "198.51.100.99", "port": 8080, "bytes_sent": 45000, "status": "allowed"}
        ],
        "process_logs": [
            {"pid": "3412", "name": "WINWORD.EXE", "user": "jdoe", "network_active": False},
            {"pid": "8901", "name": "powershell.exe", "parent_pid": "3412", "command_line": "-enc JABzAD0ATgBlAHcALQBPAGIAagBlAGMAdAAgAEkATwAuAE0AZQBtAG8AcgB5AFMAdAByAGUAYQBtACgAWwBDAG8AbgB2AGUAcgB0AF0AOgA6AEYAcgBvAG0AQgBhAHMAZQA2ADQAUwB0AHIAaQBuAGcAKAAiAEgA...", "network_active": True},
            {"pid": "1124", "name": "explorer.exe", "user": "jdoe", "network_active": False}
        ],
        "registry_data": {
            "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run": {"SysTray": "systray.exe"},
            "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run": {"Updater": "C:\\Users\\jdoe\\AppData\\Roaming\\updater.exe"}
        }
    }
}
