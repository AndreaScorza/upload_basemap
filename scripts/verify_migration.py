"""Script to verify the migration from JSON to PostgreSQL."""
import json
import sys
import os
from datetime import datetime

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from upload_basemap.src.upload_tracker import UploadTracker, UploadRecord
from sqlalchemy.orm import Session

def verify_migration(json_file: str):
    """Verify that the data in PostgreSQL matches the JSON file."""
    # Read JSON file
    with open(json_file, 'r') as f:
        json_data = json.load(f)
    
    # Initialize tracker and create session
    tracker = UploadTracker()
    session = Session(tracker.engine)
    
    try:
        # Get all records from PostgreSQL
        db_records = session.query(UploadRecord).all()
        db_records_dict = {record.file_key: record for record in db_records}
        
        # Compare counts
        print(f"Records in JSON: {len(json_data)}")
        print(f"Records in PostgreSQL: {len(db_records_dict)}")
        
        # Sample verification (first 5 records)
        print("\nVerifying sample records:")
        for i, (file_key, json_info) in enumerate(list(json_data.items())[:5]):
            db_record = db_records_dict.get(file_key)
            if db_record:
                print(f"\nRecord {i+1}:")
                print(f"File key: {file_key}")
                print("JSON data:")
                print(f"  uploaded_at: {json_info['uploaded_at']}")
                print(f"  original_path: {json_info['original_path']}")
                print(f"  prefix: {json_info['prefix']}")
                print("PostgreSQL data:")
                print(f"  uploaded_at: {db_record.uploaded_at.isoformat()}")
                print(f"  original_path: {db_record.original_path}")
                print(f"  prefix: {db_record.prefix}")
            else:
                print(f"\nWarning: Record {file_key} not found in PostgreSQL")
        
        # Check for any missing records
        json_keys = set(json_data.keys())
        db_keys = set(db_records_dict.keys())
        
        missing_in_db = json_keys - db_keys
        if missing_in_db:
            print(f"\nWarning: {len(missing_in_db)} records from JSON are missing in PostgreSQL")
            print("First few missing keys:", list(missing_in_db)[:5])
        
        extra_in_db = db_keys - json_keys
        if extra_in_db:
            print(f"\nWarning: {len(extra_in_db)} extra records in PostgreSQL not in JSON")
            print("First few extra keys:", list(extra_in_db)[:5])
            
    finally:
        session.close()

if __name__ == "__main__":
    json_file = "upload_history.json"
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    
    verify_migration(json_file)
