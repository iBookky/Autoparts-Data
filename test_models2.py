import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()
token = os.environ.get("GEMINI_API_KEY")

headers = {"Content-Type": "application/json"}
headers["x-goog-api-key"] = token

payload = {
    "contents": [{"parts": [{"text": "Hello"}]}],
}

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"
print(f"Testing gemini-1.5-pro...")
response = requests.post(url, json=payload, headers=headers)
print(response.status_code)
print(response.text[:200])

url2 = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
print(f"\nTesting gemini-1.5-flash...")
response2 = requests.post(url2, json=payload, headers=headers)
print(response2.status_code)
print(response2.text[:200])
