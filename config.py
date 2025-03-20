import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Jira configuration constants
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
TARGET_START_FIELD = "customfield_15360"
TARGET_END_FIELD = "customfield_15361"
