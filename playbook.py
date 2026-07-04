import json
import requests
import subprocess
from datetime import datetime
from config import VT_API_KEY, LOG_FILE

def load_alert(path):
    with open(path, "r") as f:
        return json.load(f)

def check_ip_reputation(ip):
    url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
    headers = {"x-apikey": VT_API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        malicious = data["data"]["attributes"]["last_analysis_stats"]["malicious"]
        return malicious
    return 0

def block_ip(ip):
    rule_name = f"Block_{ip}"
    command = f'netsh advfirewall firewall add rule name="{rule_name}" dir=in action=block remoteip={ip}'
    subprocess.run(command, shell=True)
    print(f"[ACTION] Blocked IP: {ip}")

def log_incident(alert, decision):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now()} | AlertID: {alert['alert_id']} | IP: {alert['source_ip']} | Decision: {decision}\n")

def triage(alert):
    ip = alert["source_ip"]
    severity = alert["severity"]
    malicious_score = check_ip_reputation(ip)

    print(f"[INFO] Checking {ip} | VT Malicious Score: {malicious_score} | Severity: {severity}")

    if severity == "high" and malicious_score > 3:
        decision = "BLOCKED - High severity + confirmed malicious IP"
        block_ip(ip)
    elif severity == "high":
        decision = "ESCALATED - High severity, manual review needed"
    else:
        decision = "IGNORED - Low severity"

    log_incident(alert, decision)
    print(f"[RESULT] {decision}")

import sys

if __name__ == "__main__":
    alert_file = sys.argv[1] if len(sys.argv) > 1 else "alerts/alert1.json"
    alert = load_alert(alert_file)
    triage(alert)

