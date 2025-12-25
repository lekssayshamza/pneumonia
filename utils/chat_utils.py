import requests
import json

OPENROUTER_API_KEY = "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"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

def get_ai_response(messages):
    """
    Send messages to OpenRouter API and get response.
    messages: list of dicts with 'role' and 'content'
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://localhost:8501", # Required by OpenRouter
        "X-Title": "Pneumonia Detector App" # Optional
    }
    
    # Ensure system message exists
    if not any(m.get('role') == 'system' for m in messages):
        messages.insert(0, {
            "role": "system", 
            "content": "You are a helpful medical assistant for a Pneumonia Detection application. Provide concise and helpful information about pneumonia, lung health, and interpreting X-ray results. Always advise consulting a doctor for real medical advice."
        })

    payload = {
        "messages": messages,
        "model": "google/gemini-2.0-flash-exp:free", # Using a free, capable model
        "stream": False,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        # Fallback error handling
        if hasattr(e, 'response') and e.response is not None:
             return f"Error ({e.response.status_code}): {e.response.text}"
        return f"Error: {str(e)}"
