#!/usr/bin/env python3
"""
Check if source_item_id was written to a newly created item
"""
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("MONDAY_API_TOKEN")
SOURCE_ITEM_ID_COLUMN = os.getenv("SOURCE_ITEM_ID_COLUMN", "text_mm034248")

# Item ID from the most recent log - David Dillard
ITEM_ID = "11251327982"

API_URL = "https://api.monday.com/v2"
HEADERS = {
    "Authorization": API_TOKEN,
    "Content-Type": "application/json"
}

query = """
query ($itemId: [ID!]) {
    items(ids: $itemId) {
        id
        name
        column_values {
            id
            text
            value
            type
        }
    }
}
"""

response = requests.post(API_URL, json={"query": query, "variables": {"itemId": ITEM_ID}}, headers=HEADERS)
result = response.json()

print(f"Checking item: {ITEM_ID}")
print("=" * 80)

if result.get("data", {}).get("items"):
    item = result["data"]["items"][0]
    print(f"Item name: {item['name']}")
    print(f"\nLooking for column: {SOURCE_ITEM_ID_COLUMN}")
    print("-" * 80)
    
    for col in item["column_values"]:
        if col["id"] == SOURCE_ITEM_ID_COLUMN:
            print(f"FOUND IT!")
            print(f"  Type: {col['type']}")
            print(f"  Text: {col['text']}")
            print(f"  Value: {col['value']}")
            break
    else:
        print(f"Column {SOURCE_ITEM_ID_COLUMN} NOT FOUND")
        print("\nAll text columns:")
        for col in item["column_values"]:
            if col["text"]:
                print(f"  {col['id']} ({col['type']}): {col['text']}")
else:
    print("Item not found or error:")
    print(json.dumps(result, indent=2))
