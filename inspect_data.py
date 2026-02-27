#!/usr/bin/env python3
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

API_TOKEN = os.getenv("MONDAY_API_TOKEN")
API_URL = "https://api.monday.com/v2"
HEADERS = {"Authorization": API_TOKEN, "Content-Type": "application/json"}

# Get first 5 items from source board
query = """
query {
    boards(ids: [18269603341]) {
        items_page(limit: 5) {
            items {
                id
                name
                column_values {
                    id
                    type
                    text
                    value
                }
            }
        }
    }
}
"""

print("Fetching first 5 items from source board...")
print("="*80)
response = requests.post(API_URL, json={"query": query}, headers=HEADERS)
result = response.json()

if "data" in result and "boards" in result["data"]:
    items = result["data"]["boards"][0]["items_page"]["items"]
    
    for item in items:
        print(f"\n{'='*80}")
        print(f"ITEM: {item['name']} (ID: {item['id']})")
        print(f"{'='*80}")
        
        for col in item["column_values"]:
            if col["value"] and col["value"] != "null":
                print(f"\nColumn ID: {col['id']}")
                print(f"Type: {col['type']}")
                print(f"Text: {col['text']}")
                print(f"Value: {col['value']}")
                
                # Try to parse the value
                try:
                    parsed = json.loads(col["value"])
                    print(f"Parsed: {json.dumps(parsed, indent=2)}")
                except:
                    pass
else:
    print("ERROR:")
    print(json.dumps(result, indent=2))
