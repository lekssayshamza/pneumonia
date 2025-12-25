import requests
import json

# 🔐 GitHub Models / Azure AI Inference token
#GITHUB_TOKEN = "**"

# 🌐 Azure AI Inference Chat Completions endpoint
#AZURE_API_URL = "https://models.inference.ai.azure.com/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Content-Type": "application/json"
}

def get_ai_response(messages):
    """
    Send messages to Azure AI (GitHub Models) and get response.
    messages: list of dicts with 'role' and 'content' (OpenAI format)
    """

    # System instruction (same logic you had)
    system_instruction = (
        "You are a helpful medical assistant for a Pneumonia Detection application. "
        "Provide concise and helpful information about pneumonia, lung health, and "
        "interpreting X-ray results. Always advise consulting a doctor for real medical advice."
    )

    # Ensure system message exists
    has_system = any(msg.get("role") == "system" for msg in messages)
    if not has_system:
        messages = [{"role": "system", "content": system_instruction}] + messages

    payload = {
        "model": "gpt-4.1",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1000
    }

    try:
        response = requests.post(
            AZURE_API_URL,
            headers=HEADERS,
            json=payload,
            timeout=60
        )
        response.raise_for_status()

        result = response.json()

        # Extract assistant reply
        return result["choices"][0]["message"]["content"]

    except requests.exceptions.HTTPError as e:
        return f"Error ({response.status_code}): {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"





