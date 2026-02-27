#!/usr/bin/env python3
"""
Check board items with better error handling
"""
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("MONDAY_API_TOKEN")
DEST_BOARD_ID = os.getenv("DEST_BOARD_ID", "18399599376")

API_URL = "https://api.monday.com/v2"
HEADERS = {
    "Authorization": API_TOKEN,
    "Content-Type": "application/json"
}

query = """
query ($boardId: ID!) {
    boards(ids: [$boardId]) {
        id
        name
        items_page(limit: 10) {
            cursor
            items {
                id
                name
            }
        }
    }
}
"""

response = requests.post(API_URL, json={"query": query, "variables": {"boardId": DEST_BOARD_ID}}, headers=HEADERS)
result = response.json()

print(f"Checking board ID: {DEST_BOARD_ID}")
print("=" * 80)
print(json.dumps(result, indent=2))
