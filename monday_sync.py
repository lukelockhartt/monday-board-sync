#!/usr/bin/env python3
"""
Monday.com Board Sync Script
Syncs data from Main Board to Duplicate Board daily
"""

import os
import json
import requests
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monday_sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MondaySync:
    """Handles syncing between two Monday.com boards"""
    
    def __init__(self, api_token: str, source_board_id: str, dest_board_id: str, client_id_column: str):
        self.api_token = api_token
        self.source_board_id = source_board_id
        self.dest_board_id = dest_board_id
        self.client_id_column = client_id_column
        self.api_url = "https://api.monday.com/v2"
        self.headers = {
            "Authorization": api_token,
            "Content-Type": "application/json"
        }
        
    def _execute_query(self, query: str, variables: Optional[Dict] = None) -> Dict:
        """Execute a GraphQL query against Monday.com API"""
        data = {"query": query}
        if variables:
            data["variables"] = variables
            
        try:
            response = requests.post(self.api_url, json=data, headers=self.headers)
            response.raise_for_status()
            result = response.json()
            
            if "errors" in result:
                logger.error(f"API errors: {result['errors']}")
                raise Exception(f"Monday.com API error: {result['errors']}")
                
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise
    
    def get_board_items(self, board_id: str) -> List[Dict]:
        """Fetch all items from a board with their column values"""
        query = """
        query ($boardId: [ID!]) {
            boards(ids: $boardId) {
                items_page(limit: 500) {
                    cursor
                    items {
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
            }
        }
        """
        
        variables = {"boardId": board_id}
        result = self._execute_query(query, variables)
        
        items = []
        if result.get("data", {}).get("boards"):
            board_data = result["data"]["boards"][0]
            items = board_data["items_page"]["items"]
            
        logger.info(f"Retrieved {len(items)} items from board {board_id}")
        return items
    
    def get_column_mapping(self, board_id: str) -> Dict[str, Dict]:
        """Get column definitions for a board"""
        query = """
        query ($boardId: [ID!]) {
            boards(ids: $boardId) {
                columns {
                    id
                    title
                    type
                }
            }
        }
        """
        
        variables = {"boardId": board_id}
        result = self._execute_query(query, variables)
        
        columns = {}
        if result.get("data", {}).get("boards"):
            for col in result["data"]["boards"][0]["columns"]:
                columns[col["id"]] = {
                    "title": col["title"],
                    "type": col["type"]
                }
                
        logger.info(f"Retrieved {len(columns)} columns from board {board_id}")
        return columns
    
    def create_item(self, board_id: str, item_name: str, column_values: Dict[str, Any]) -> str:
        """Create a new item in a board"""
        query = """
        mutation ($boardId: ID!, $itemName: String!, $columnValues: JSON!) {
            create_item(
                board_id: $boardId,
                item_name: $itemName,
                column_values: $columnValues
            ) {
                id
            }
        }
        """
        
        # Convert column values to JSON string format
        column_values_json = json.dumps(column_values)
        
        variables = {
            "boardId": board_id,
            "itemName": item_name,
            "columnValues": column_values_json
        }
        
        result = self._execute_query(query, variables)
        item_id = result["data"]["create_item"]["id"]
        logger.info(f"Created new item: {item_name} (ID: {item_id})")
        return item_id
    
    def update_item(self, board_id: str, item_id: str, column_values: Dict[str, Any]) -> None:
        """Update an existing item's column values"""
        query = """
        mutation ($boardId: ID!, $itemId: ID!, $columnValues: JSON!) {
            change_multiple_column_values(
                board_id: $boardId,
                item_id: $itemId,
                column_values: $columnValues
            ) {
                id
            }
        }
        """
        
        # Convert column values to JSON string format
        column_values_json = json.dumps(column_values)
        
        variables = {
            "boardId": board_id,
            "itemId": item_id,
            "columnValues": column_values_json
        }
        
        self._execute_query(query, variables)
        logger.info(f"Updated item ID: {item_id}")
    
    def prepare_column_values(self, item: Dict, columns_info: Dict) -> Dict[str, Any]:
        """Convert item column values to the format needed for create/update"""
        column_values = {}
        
        for col_value in item["column_values"]:
            col_id = col_value["id"]
            col_type = col_value["type"]
            raw_value = col_value["value"]
            
            # Skip empty values
            if not raw_value or raw_value == "null":
                continue
            
            try:
                # Parse the JSON value
                parsed_value = json.loads(raw_value) if isinstance(raw_value, str) else raw_value
                
                # Handle different column types
                if col_type == "text":
                    column_values[col_id] = col_value["text"]
                elif col_type == "status":
                    if parsed_value and "label" in parsed_value:
                        column_values[col_id] = {"label": parsed_value["label"]}
                elif col_type == "date":
                    if parsed_value and "date" in parsed_value:
                        column_values[col_id] = {"date": parsed_value["date"]}
                elif col_type == "people":
                    if parsed_value and "personsAndTeams" in parsed_value:
                        column_values[col_id] = {"personsAndTeams": parsed_value["personsAndTeams"]}
                elif col_type == "numeric" or col_type == "numbers":
                    if col_value["text"]:
                        column_values[col_id] = col_value["text"]
                elif col_type == "email":
                    if parsed_value and "email" in parsed_value:
                        column_values[col_id] = {"email": parsed_value["email"], "text": parsed_value.get("text", "")}
                elif col_type == "phone":
                    if parsed_value and "phone" in parsed_value:
                        column_values[col_id] = {"phone": parsed_value["phone"]}
                elif col_type == "link":
                    if parsed_value and "url" in parsed_value:
                        column_values[col_id] = {"url": parsed_value["url"], "text": parsed_value.get("text", "")}
                elif col_type == "dropdown":
                    if parsed_value and "ids" in parsed_value:
                        column_values[col_id] = {"ids": parsed_value["ids"]}
                elif col_type == "checkbox":
                    if parsed_value and "checked" in parsed_value:
                        column_values[col_id] = {"checked": parsed_value["checked"]}
                elif col_type == "timeline":
                    if parsed_value and "from" in parsed_value:
                        column_values[col_id] = {"from": parsed_value["from"], "to": parsed_value.get("to")}
                elif col_type == "long-text":
                    if col_value["text"]:
                        column_values[col_id] = {"text": col_value["text"]}
                else:
                    # For other types, try to use the raw value
                    if col_value["text"]:
                        column_values[col_id] = col_value["text"]
                        
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                logger.warning(f"Could not parse column {col_id} ({col_type}): {e}")
                continue
        
        return column_values
    
    def sync_boards(self) -> Dict[str, int]:
        """Main sync function - syncs source board to destination board"""
        logger.info("=" * 60)
        logger.info(f"Starting sync at {datetime.now().isoformat()}")
        logger.info("=" * 60)
        
        stats = {
            "items_created": 0,
            "items_updated": 0,
            "items_skipped": 0,
            "errors": 0
        }
        
        try:
            # Get all items from source board
            logger.info(f"Fetching items from source board: {self.source_board_id}")
            source_items = self.get_board_items(self.source_board_id)
            
            # Get all items from destination board
            logger.info(f"Fetching items from destination board: {self.dest_board_id}")
            dest_items = self.get_board_items(self.dest_board_id)
            
            # Get column info
            columns_info = self.get_column_mapping(self.source_board_id)
            
            # Build a lookup map of destination items by source_item_id
            dest_lookup = {}
            for item in dest_items:
                for col_value in item["column_values"]:
                    if col_value["id"] == "source_item_id":
                        source_id = col_value["text"]
                        if source_id:
                            dest_lookup[source_id] = item["id"]
                        break
            
            logger.info(f"Found {len(dest_lookup)} existing items in destination board")
            
            # Process each source item
            for source_item in source_items:
                try:
                    # Get the client_id from source item
                    client_id = None
                    for col_value in source_item["column_values"]:
                        if col_value["id"] == self.client_id_column:
                            client_id = col_value["text"]
                            break
                    
                    if not client_id:
                        logger.warning(f"Item '{source_item['name']}' has no client_id, skipping")
                        stats["items_skipped"] += 1
                        continue
                    
                    # Prepare column values for sync
                    column_values = self.prepare_column_values(source_item, columns_info)
                    
                    # Add the source_item_id to track the relationship
                    column_values["source_item_id"] = client_id
                    
                    # Check if item exists in destination
                    if client_id in dest_lookup:
                        # Update existing item
                        dest_item_id = dest_lookup[client_id]
                        self.update_item(self.dest_board_id, dest_item_id, column_values)
                        stats["items_updated"] += 1
                    else:
                        # Create new item
                        self.create_item(self.dest_board_id, source_item["name"], column_values)
                        stats["items_created"] += 1
                        
                except Exception as e:
                    logger.error(f"Error processing item '{source_item.get('name', 'Unknown')}': {e}")
                    stats["errors"] += 1
                    continue
            
            logger.info("=" * 60)
            logger.info("Sync completed successfully!")
            logger.info(f"Items created: {stats['items_created']}")
            logger.info(f"Items updated: {stats['items_updated']}")
            logger.info(f"Items skipped: {stats['items_skipped']}")
            logger.info(f"Errors: {stats['errors']}")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Fatal error during sync: {e}")
            stats["errors"] += 1
            raise
        
        return stats


def main():
    """Main entry point"""
    # Load configuration from environment variables
    api_token = os.getenv("MONDAY_API_TOKEN")
    source_board_id = os.getenv("SOURCE_BOARD_ID", "18388403129")
    dest_board_id = os.getenv("DEST_BOARD_ID", "18399599376")
    client_id_column = os.getenv("CLIENT_ID_COLUMN", "text_mkxykxdr")
    
    if not api_token:
        logger.error("MONDAY_API_TOKEN environment variable not set!")
        raise ValueError("MONDAY_API_TOKEN is required")
    
    # Initialize and run sync
    syncer = MondaySync(
        api_token=api_token,
        source_board_id=source_board_id,
        dest_board_id=dest_board_id,
        client_id_column=client_id_column
    )
    
    syncer.sync_boards()


if __name__ == "__main__":
    main()
