import requests

# API endpoint
url = 'http://175.27.243.21:7861/chat/knowledge_base_chat'

# Request headers
headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
}

query = "金山办公在AI领域有哪些投入？"

# Request payload
data = {
    "query": query,
    "knowledge_base_name": "wps-db",
    "top_k": 3,
    "score_threshold": 1,
    "history": [],
    "stream": False,
    "temperature": 0.7,
    "prompt_name": "knowledge_base_chat",
    "local_doc_url": False
}

# Make POST request
response = requests.post(url, json=data, headers=headers)

# Check if request was successful
if response.status_code == 200:
    # Print response content
    print(response.json())
else:
    print('Error:', response.status_code)
