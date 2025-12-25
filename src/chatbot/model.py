import requests


api_key = "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"
url = "https://api.groq.com/openai/v1/models"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)

print(response.json())