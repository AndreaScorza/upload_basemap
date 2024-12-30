#!/usr/bin/env python3
"""Main entry point for basemap upload tool."""
import os
import sys
import time
import json
import logging
from typing import List, Tuple
from itertools import islice
from dotenv import load_dotenv
from botocore.exceptions import ClientError, BotoCoreError, NoCredentialsError
from .src.file_finder import find_tiff_files, clear_resume_point
from .src.s3_upload import upload_to_s3
from .src.upload_tracker import UploadTracker
import boto3

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)

PROGRESS_FILE = "upload_progress.json"

def load_progress():
    """Load progress from file."""
    try:
        if os.path.exists(PROGRESS_FILE):
            with open(PROGRESS_FILE, 'r') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logging.warning(f"Could not read progress file: {e}")
    return {'total_successful': 0, 'total_skipped': 0}

def save_progress(total_successful: int, total_skipped: int):
    """Save current progress to file."""
    try:
        with open(PROGRESS_FILE, 'w') as f:
            json.dump({
                'total_successful': total_successful,
                'total_skipped': total_skipped
            }, f)
    except IOError as e:
        logging.warning(f"Could not save progress: {e}")

def clear_progress():
    """Clear progress file after successful completion."""
    try:
        if os.path.exists(PROGRESS_FILE):
            os.remove(PROGRESS_FILE)
    except OSError as e:
        logging.warning(f"Could not remove progress file: {e}")

def process_batch(
    files_batch: List[Tuple[str, str, int]], 
    tracker: UploadTracker, 
    bucket_name: str
) -> Tuple[int, int]:
    """Process a batch of files.
    
    Args:
        files_batch: List of (file_path, prefix, skipped_count) tuples
        tracker: Upload tracker instance
        bucket_name: S3 bucket name
        
    Returns:
        Tuple of (successful uploads, skipped files)
        
    Raises:
        Any exception that occurs during upload will be re-raised
    """
    successful = 0
    skipped = 0

    for file_path, prefix, skipped_count in files_batch:
        # Add the skipped files from find_tiff_files
        skipped += skipped_count
        
        logging.info(f"Uploading {file_path} to {bucket_name}/{prefix}")
        # Any error here will be raised immediately
        upload_to_s3(file_path, bucket_name, prefix)
        tracker.mark_uploaded(file_path, prefix)
        successful += 1
        save_progress(successful, skipped)

    return successful, skipped

def main():
    """Main entry point for the upload script."""
    start_time = time.time()
    batch_size = 100  # Process files in batches of 100

    try:
        # Load environment variables from .env file
        load_dotenv()

        # Get bucket name from environment variable
        bucket_name = os.environ.get("BUCKET_NAME")
        basemaps_dir = os.environ.get("BASEMAPS_DIR")
        if not bucket_name or not basemaps_dir:
            raise ValueError(
                "BUCKET_NAME or BASEMAPS_DIR not found in environment variables. "
                "Please create a .env file with these variables."
            )

        # Test S3 credentials early
        try:
            boto3.client('s3').list_buckets()
        except (BotoCoreError, NoCredentialsError) as e:
            logging.error(f"Failed to authenticate with AWS: {e}")
            sys.exit(1)

        # Initialize upload tracker
        tracker = UploadTracker()

        # Load previous progress
        progress = load_progress()
        total_successful = progress['total_successful']
        total_skipped = progress['total_skipped']

        # Process files in batches
        current_batch = []
        try:
            for file_path, prefix, skipped_count in find_tiff_files(basemaps_dir, resume=True):
                current_batch.append((file_path, prefix, skipped_count))
                
                if len(current_batch) >= batch_size:
                    successful, skipped = process_batch(current_batch, tracker, bucket_name)
                    total_successful += successful
                    total_skipped += skipped
                    current_batch = []

            # Process remaining files
            if current_batch:
                successful, skipped = process_batch(current_batch, tracker, bucket_name)
                total_successful += successful
                total_skipped += skipped

        except Exception as e:
            logging.error(f"Error during upload process: {e}", exc_info=True)
            # Save the current file as resume point - it will be retried next time
            sys.exit(1)

        # Log summary
        elapsed_time = time.time() - start_time
        logging.info(f"\nUpload process completed in {elapsed_time:.2f} seconds")
        logging.info(f"Successfully uploaded: {total_successful} files")
        logging.info(f"Skipped (already uploaded): {total_skipped} files")

        # Clear progress and resume files on successful completion
        clear_progress()
        clear_resume_point()

    except KeyboardInterrupt:
        logging.info("\nUpload process interrupted by user")
        logging.info(f"Progress saved. Run again to resume from last position.")
        sys.exit(130)
    except Exception as e:
        logging.error(f"Upload process failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
