#!/usr/bin/env python3
"""
Check if files were transferred to the duplicate board
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("MONDAY_API_TOKEN")
DEST_BOARD_ID = os.getenv("DEST_BOARD_ID", "18399599376")
API_URL = "https://api.monday.com/v2"
HEADERS = {
    "Authorization": API_TOKEN,
    "Content-Type": "application/json"
}

# Item IDs created in the last sync for items with files
ITEMS_TO_CHECK = {
    "11250852698": "Janie Schulz",
    "11250851133": "UT - Integrative Biology"
}

query = """
query ($itemIds: [ID!]) {
    items(ids: $itemIds) {
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

variables = {"itemIds": list(ITEMS_TO_CHECK.keys())}

print("Checking if files were transferred to duplicate board...")
print("=" * 80)

response = requests.post(API_URL, json={"query": query, "variables": variables}, headers=HEADERS)
result = response.json()

if "data" in result and "items" in result["data"]:
    for item in result["data"]["items"]:
        print(f"\nItem: {item['name']} (ID: {item['id']})")
        print("-" * 80)
        
        # Find the file column
        for col_val in item["column_values"]:
            if col_val["id"] == "file_mkz618tm":
                print(f"File Column (file_mkz618tm):")
                print(f"  Text: {col_val['text']}")
                print(f"  Value: {col_val['value']}")
                
                if col_val['value'] and col_val['value'] != 'null':
                    parsed = json.loads(col_val['value'])
                    if 'files' in parsed and parsed['files']:
                        print(f"  ✓ FILES FOUND: {len(parsed['files'])} file(s)")
                        for f in parsed['files']:
                            print(f"    - {f.get('name', 'Unknown')}")
                    else:
                        print("  ✗ NO FILES (empty files array)")
                else:
                    print("  ✗ NO FILES (null value)")
                break
else:
    print("Error fetching items:")
    print(json.dumps(result, indent=2))

print("\n" + "=" * 80)
