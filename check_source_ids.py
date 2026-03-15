#!/usr/bin/env python3
"""
Check which items in destination board have source_item_id populated
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("MONDAY_API_TOKEN")
DEST_BOARD_ID = os.getenv("DEST_BOARD_ID", "YOUR_DEST_BOARD_ID")
SOURCE_ITEM_ID_COLUMN = os.getenv("SOURCE_ITEM_ID_COLUMN", "YOUR_SOURCE_ITEM_ID_COLUMN")

API_URL = "https://api.monday.com/v2"
HEADERS = {
    "Authorization": API_TOKEN,
    "Content-Type": "application/json"
}

def get_dest_items():
    query = """
    query ($boardId: [ID!]) {
        boards(ids: $boardId) {
            items_page(limit: 500) {
                items {
                    id
                    name
                    column_values {
                        id
                        title
                        text
                    }
                }
            }
        }
    }
    """
    
    response = requests.post(API_URL, json={"query": query, "variables": {"boardId": DEST_BOARD_ID}}, headers=HEADERS)
    result = response.json()
    
    if result.get("data", {}).get("boards"):
        return result["data"]["boards"][0]["items_page"]["items"]
    return []

def main():
    print(f"\nChecking destination board for source_item_id column: {SOURCE_ITEM_ID_COLUMN}\n")
    print("=" * 80)
    
    items = get_dest_items()
    
    # Look for specific target names - replace with actual names to search for
    target_names = ["Client Name 1", "Client Name 2", "Client Name 3"]
    
    for item in items:
        if any(name.lower() in item["name"].lower() for name in target_names):
            print(f"\nItem: {item['name']} (ID: {item['id']})")
            
            # Find source_item_id column
            source_id = None
            for col in item["column_values"]:
                if col["id"] == SOURCE_ITEM_ID_COLUMN:
                    source_id = col["text"]
                    print(f"  ✓ source_item_id ({SOURCE_ITEM_ID_COLUMN}): {source_id}")
                    break
            
            if not source_id:
                print(f"  ✗ source_item_id column NOT FOUND or EMPTY")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
