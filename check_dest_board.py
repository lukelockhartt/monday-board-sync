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
    boards(ids: [18399599376]) {
        id
        name
        columns {
            id
            title
            type
        }
        items_page(limit: 3) {
            items {
                id
                name
                column_values {
                    id
                    text
                    type
                }
            }
        }
    }
}
"""

print("Fetching Duplicate Board structure and sample data...")
print("="*80)
response = requests.post(API_URL, json={"query": query}, headers=HEADERS)
result = response.json()

if "data" in result and "boards" in result["data"] and result["data"]["boards"]:
    board = result["data"]["boards"][0]
    print(f"\nBoard: {board['name']}")
    print(f"\nCOLUMNS:")
    print("-"*80)
    for col in board["columns"]:
        print(f"  ID: {col['id']:<30} | Title: {col['title']:<30} | Type: {col['type']}")
    
    print(f"\n\nSAMPLE ITEMS:")
    print("-"*80)
    for item in board["items_page"]["items"]:
        print(f"\nItem: {item['name']} (ID: {item['id']})")
        for col_val in item["column_values"]:
            if col_val["text"]:
                print(f"  {col_val['id']:<30} ({col_val['type']}): {col_val['text']}")
else:
    print("ERROR:")
    print(json.dumps(result, indent=2))
