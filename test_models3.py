import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()
token = os.environ.get("GEMINI_API_KEY")

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={token}"
response = requests.get(url)
models = response.json().get('models', [])
print(f"Status: {response.status_code}")
for m in models:
    if m['name'].startswith('models/gemini'):
        print(m['name'])
