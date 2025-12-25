import requests
import json

# 🔐 GitHub Personal Access Token
#GITHUB_TOKEN = "**"

# 🌐 Azure AI Inference models endpoint
#URL = "https://models.inference.ai.azure.com/models"

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Content-Type": "application/json"
}

try:
    response = requests.get(URL, headers=HEADERS)
    data = response.json()

    print("Status Code:", response.status_code)

    if isinstance(data, list):
        print("Available Models:")
        for model in data:
            print("-", model.get("id", model))
    else:
        print("Response:", json.dumps(data, indent=2))

except Exception as e:
    print(f"Error: {e}")
