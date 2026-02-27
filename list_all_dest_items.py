#!/usr/bin/env python3
"""
List all items in destination board
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("MONDAY_API_TOKEN")
DEST_BOARD_ID = os.getenv("DEST_BOARD_ID", "18399599376")
SOURCE_ITEM_ID_COLUMN = os.getenv("SOURCE_ITEM_ID_COLUMN", "text_mm034248")

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
    print(f"\nListing ALL items in destination board\n")
    print("=" * 100)
    
    items = get_dest_items()
    
    print(f"Total items: {len(items)}\n")
    
    items_with_source_id = 0
    items_without_source_id = 0
    
    for item in items:
        # Find source_item_id column
        source_id = None
        for col in item["column_values"]:
            if col["id"] == SOURCE_ITEM_ID_COLUMN:
                source_id = col["text"]
                break
        
        if source_id:
            items_with_source_id += 1
            print(f"✓ {item['name']:<40} | Dest ID: {item['id']} | Source ID: {source_id}")
        else:
            items_without_source_id += 1
            print(f"✗ {item['name']:<40} | Dest ID: {item['id']} | Source ID: MISSING")
    
    print("\n" + "=" * 100)
    print(f"Items WITH source_item_id: {items_with_source_id}")
    print(f"Items WITHOUT source_item_id: {items_without_source_id}")
    print("=" * 100)

if __name__ == "__main__":
    main()
