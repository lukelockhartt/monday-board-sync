#!/usr/bin/env python3
"""
Check if a specific item exists
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("MONDAY_API_TOKEN")

API_URL = "https://api.monday.com/v2"
HEADERS = {
    "Authorization": API_TOKEN,
    "Content-Type": "application/json"
}

# Item ID from the log
ITEM_ID = "11250973115"

query = """
query ($itemId: [ID!]) {
    items(ids: $itemId) {
        id
        name
        board {
            id
            name
        }
    }
}
"""

response = requests.post(API_URL, json={"query": query, "variables": {"itemId": ITEM_ID}}, headers=HEADERS)
result = response.json()

print(f"Checking item ID: {ITEM_ID}")
print("=" * 80)
print(result)
