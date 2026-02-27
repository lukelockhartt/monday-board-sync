#!/usr/bin/env python3
import os
import requests
import json

API_TOKEN = os.getenv("MONDAY_API_TOKEN")

if not API_TOKEN:
    raise ValueError("MONDAY_API_TOKEN environment variable is not set")

API_URL = "https://api.monday.com/v2"
HEADERS = {"Authorization": API_TOKEN, "Content-Type": "application/json"}

# Try to get Main Board with ID as integer
query = """
query {
    boards(ids: [18388403129]) {
        id
        name
        columns {
            id
            title
            type
        }
    }
}
"""

print("Trying to fetch Main Board...")
response = requests.post(API_URL, json={"query": query}, headers=HEADERS)
print(f"Status: {response.status_code}")
result = response.json()
print(json.dumps(result, indent=2))
