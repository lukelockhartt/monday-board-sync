#!/usr/bin/env python3
"""
Test Monday.com API connection using MONDAY_API_TOKEN from environment.
"""

import os
import requests
import json

API_TOKEN = os.getenv("MONDAY_API_TOKEN")

if not API_TOKEN:
    raise ValueError("MONDAY_API_TOKEN environment variable is not set")

API_URL = "https://api.monday.com/v2"
HEADERS = {
    "Authorization": API_TOKEN,
    "Content-Type": "application/json",
}

query = """
query {
    boards(limit: 10) {
        id
        name
    }
}
"""

print("Testing Monday.com API connection...")
print("=" * 80)

try:
    response = requests.post(API_URL, json={"query": query}, headers=HEADERS)
    print(f"Status Code: {response.status_code}")
    print(f"\nResponse:")
    result = response.json()
    print(json.dumps(result, indent=2))

    if "data" in result and "boards" in result["data"]:
        print("\n" + "=" * 80)
        print("BOARDS YOU HAVE ACCESS TO:")
        print("=" * 80)
        for board in result["data"]["boards"]:
            print(f"  ID: {board['id']:<15} | Name: {board['name']}")

except Exception as e:
    print(f"ERROR: {e}")
