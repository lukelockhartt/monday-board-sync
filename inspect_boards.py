#!/usr/bin/env python3
"""
Script to inspect Monday.com boards and understand their structure
"""

import os
import requests
import json

API_TOKEN = os.getenv("MONDAY_API_TOKEN")
SOURCE_BOARD_ID = "18269603341"  # Correct Main Board ID
DEST_BOARD_ID = "18399599376"
CLIENT_ID_COLUMN = "pulse_id_mkxvh6ca"

if not API_TOKEN:
    raise ValueError("MONDAY_API_TOKEN environment variable is not set")

API_URL = "https://api.monday.com/v2"
HEADERS = {
    "Authorization": API_TOKEN,
    "Content-Type": "application/json",
}

def execute_query(query, variables=None):
    """Execute a GraphQL query"""
    data = {"query": query}
    if variables:
        data["variables"] = variables
    
    response = requests.post(API_URL, json=data, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def inspect_board(board_id, board_name):
    """Inspect a board's structure and data"""
    print(f"\n{'='*80}")
    print(f"INSPECTING {board_name} (ID: {board_id})")
    print(f"{'='*80}\n")
    
    # Get board columns
    query = """
    query ($boardId: [ID!]) {
        boards(ids: $boardId) {
            name
            columns {
                id
                title
                type
            }
            items_page(limit: 5) {
                items {
                    id
                    name
                    column_values {
                        id
                        title
                        text
                        value
                        type
                    }
                }
            }
        }
    }
    """
    
    result = execute_query(query, {"boardId": board_id})
    
    if not result.get("data", {}).get("boards"):
        print(f"ERROR: Could not fetch board {board_id}")
        return
    
    board = result["data"]["boards"][0]
    
    print(f"Board Name: {board['name']}")
    print(f"\nCOLUMNS ({len(board['columns'])} total):")
    print("-" * 80)
    
    for col in board["columns"]:
        print(f"  ID: {col['id']:<30} | Title: {col['title']:<30} | Type: {col['type']}")
    
    items = board["items_page"]["items"]
    print(f"\n\nSAMPLE ITEMS ({len(items)} shown):")
    print("-" * 80)
    
    for idx, item in enumerate(items, 1):
        print(f"\nItem #{idx}: {item['name']} (ID: {item['id']})")
        print("  Column Values:")
        
        for col_val in item["column_values"]:
            if col_val["text"]:  # Only show non-empty values
                print(f"    {col_val['title']:<30} ({col_val['id']}): {col_val['text']}")
        
        # Specifically check for the client_id column in source board
        if board_id == SOURCE_BOARD_ID:
            client_id_value = None
            for col_val in item["column_values"]:
                if col_val["id"] == CLIENT_ID_COLUMN:
                    client_id_value = col_val["text"]
                    break
            print(f"    >>> CLIENT_ID VALUE: {client_id_value}")
        
        # Specifically check for source_item_id in dest board
        if board_id == DEST_BOARD_ID:
            source_item_id_value = None
            for col_val in item["column_values"]:
                if col_val["id"] == "source_item_id":
                    source_item_id_value = col_val["text"]
                    break
            print(f"    >>> SOURCE_ITEM_ID VALUE: {source_item_id_value}")

def main():
    print("\n" + "="*80)
    print("MONDAY.COM BOARD INSPECTION TOOL")
    print("="*80)
    
    # Inspect source board
    inspect_board(SOURCE_BOARD_ID, "SOURCE BOARD (Main Board)")
    
    # Inspect destination board
    inspect_board(DEST_BOARD_ID, "DESTINATION BOARD (Duplicate)")
    
    print("\n" + "="*80)
    print("INSPECTION COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
