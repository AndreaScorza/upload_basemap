"""Script to migrate data from JSON to PostgreSQL."""
import json
import logging
from datetime import datetime
import os
import sys

# Add the parent directory to the Python path so we can import upload_basemap
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from upload_basemap.src.upload_tracker import UploadTracker, UploadRecord
from sqlalchemy.orm import Session

def migrate_json_to_postgres(json_file: str):
    """Migrate data from JSON file to PostgreSQL."""
    # Read JSON file
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        logging.error(f"Error reading JSON file: {e}")
        return
    except FileNotFoundError:
        logging.error(f"File not found: {json_file}")
        return

    # Initialize tracker
    tracker = UploadTracker()
    
    # Create session
    session = Session(tracker.engine)
    
    try:
        # Migrate each record
        for file_key, info in data.items():
            try:
                # Parse the datetime string
                uploaded_at = datetime.fromisoformat(info['uploaded_at'])
                
                record = UploadRecord(
                    file_key=file_key,
                    uploaded_at=uploaded_at,
                    original_path=info['original_path'],
                    prefix=info['prefix']
                )
                session.merge(record)  # Use merge to handle duplicates
                
            except (KeyError, ValueError) as e:
                logging.warning(f"Skipping invalid record {file_key}: {e}")
                continue
        
        # Commit all changes
        session.commit()
        print(f"Successfully migrated {len(data)} records to PostgreSQL")
        
    except Exception as e:
        session.rollback()
        logging.error(f"Error during migration: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    json_file = "upload_history.json"
    
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    
    migrate_json_to_postgres(json_file)
