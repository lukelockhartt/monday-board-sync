#!/usr/bin/env python3
"""Test sync with first 5 items only"""
import os
import sys
from dotenv import load_dotenv

# Add the current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from monday_sync import MondaySync
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

load_dotenv()

api_token = os.getenv("MONDAY_API_TOKEN")
source_board_id = os.getenv("SOURCE_BOARD_ID", "18269603341")
dest_board_id = os.getenv("DEST_BOARD_ID", "18399599376")
client_id_column = os.getenv("CLIENT_ID_COLUMN", "item_id")

syncer = MondaySync(
    api_token=api_token,
    source_board_id=source_board_id,
    dest_board_id=dest_board_id,
    client_id_column=client_id_column
)

# Get first 5 items from source
logger.info("Fetching first 5 items from source board...")
source_items = syncer.get_board_items(source_board_id)[:5]
logger.info(f"Got {len(source_items)} items")

# Get destination items
dest_items = syncer.get_board_items(dest_board_id)
columns_info = syncer.get_column_mapping(source_board_id)

# Build destination lookup
dest_lookup = {}
for item in dest_items:
    for col_value in item["column_values"]:
        if col_value["id"] == "source_item_id":
            source_id = col_value["text"]
            if source_id:
                dest_lookup[source_id] = item["id"]
            break

logger.info(f"Found {len(dest_lookup)} existing items in destination")

# Process first 5 items
for source_item in source_items:
    try:
        client_id = source_item["id"]
        logger.info(f"\nProcessing: {source_item['name']} (ID: {client_id})")
        
        column_values = syncer.prepare_column_values(source_item, columns_info)
        column_values["source_item_id"] = client_id
        
        logger.info(f"Column values to sync: {list(column_values.keys())}")
        
        if client_id in dest_lookup:
            dest_item_id = dest_lookup[client_id]
            logger.info(f"Updating existing item {dest_item_id}")
            syncer.update_item(dest_board_id, dest_item_id, column_values)
        else:
            logger.info(f"Creating new item")
            syncer.create_item(dest_board_id, source_item["name"], column_values)
            
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()

logger.info("\nTest sync complete!")
