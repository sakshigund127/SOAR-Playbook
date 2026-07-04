import os
from dotenv import load_dotenv

load_dotenv()

VT_API_KEY = os.getenv("VT_API_KEY")
SEVERITY_THRESHOLD = "high"
LOG_FILE = "logs/incident_log.txt"