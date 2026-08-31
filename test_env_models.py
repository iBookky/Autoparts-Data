import os
import requests

key = os.environ.get("GEMINI_API_KEY")
if not key:
    print("No GEMINI_API_KEY in env")
else:
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
    response = requests.get(url)
    models = response.json().get('models', [])
    print(f"Status: {response.status_code}")
    for m in models:
        if 'pro' in m['name']:
            print(m['name'])
