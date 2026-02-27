#!/usr/bin/env python3
import os
import requests
import json

API_TOKEN = os.getenv("MONDAY_API_TOKEN")

if not API_TOKEN:
    raise ValueError("MONDAY_API_TOKEN environment variable is not set")

API_URL = "https://api.monday.com/v2"
HEADERS = {"Authorization": API_TOKEN, "Content-Type": "application/json"}

query = """
query {
    boards(ids: [18388403129]) {
        name
        items_page(limit: 10) {
            items {
                id
                name
                column_values {
                    id
                    text
                    value
                }
            }
        }
    }
}
"""

print("Checking Main Board items...")
print("="*80)
response = requests.post(API_URL, json={"query": query}, headers=HEADERS)
result = response.json()

if "data" in result and "boards" in result["data"]:
    board = result["data"]["boards"][0]
    items = board["items_page"]["items"]
    
    print(f"\nBoard: {board['name']}")
    print(f"Total items: {len(items)}\n")
    
    for item in items:
        print(f"\nItem: '{item['name']}' (ID: {item['id']})")
        print("-"*80)
        
        # Find the Internal ID column
        internal_id = None
        for col in item["column_values"]:
            if col["id"] == "text_mkxykxdr":
                internal_id = col["text"]
                print(f"  >>> Internal ID (text_mkxykxdr): '{internal_id}'")
                break
        
        if not internal_id:
            print(f"  >>> Internal ID is EMPTY - this item will be skipped!")
        
        # Show all non-empty columns
        print("\n  All non-empty columns:")
        for col in item["column_values"]:
            if col["text"]:
                print(f"    {col['id']}: {col['text']}")
else:
    print("ERROR:")
    print(json.dumps(result, indent=2))
