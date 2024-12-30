#!/usr/bin/env python3
"""Main entry point for basemap upload tool."""
import os
import sys
import time
import logging
from typing import List, Tuple
from itertools import islice
from dotenv import load_dotenv
from botocore.exceptions import ClientError
from .src.file_finder import find_tiff_files
from .src.s3_upload import upload_to_s3
from .src.upload_tracker import UploadTracker

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def process_batch(
    files_batch: List[Tuple[str, str]], 
    tracker: UploadTracker, 
    bucket_name: str
) -> Tuple[int, int, List[Tuple[str, str, str]]]:
    """Process a batch of files.
    
    Args:
        files_batch: List of (file_path, prefix) tuples
        tracker: Upload tracker instance
        bucket_name: S3 bucket name
        
    Returns:
        Tuple of (successful uploads, skipped files, failed uploads)
        Failed uploads is a list of (file_path, prefix, error_message)
    """
    successful = 0
    skipped = 0
    failed = []

    for file_path, prefix in files_batch:
        try:
            # Skip if already uploaded
            if tracker.is_uploaded(file_path, prefix):
                upload_info = tracker.get_upload_info(file_path, prefix)
                logging.info(
                    f"Skipping {file_path} - already uploaded on {upload_info['uploaded_at']}"
                )
                skipped += 1
                continue

            logging.info(f"Uploading {file_path} to {bucket_name}/{prefix}")
            try:
                upload_to_s3(file_path, bucket_name, prefix)
                tracker.mark_uploaded(file_path, prefix)
                successful += 1
            except ClientError as e:
                if e.response["Error"]["Code"] == "404":
                    raise
                # If file exists in S3 (and any other S3 error), still track it
                logging.info(f"File exists in S3, tracking it in upload history")
                tracker.mark_uploaded(file_path, prefix)
                successful += 1

        except Exception as e:
            error_msg = str(e)
            logging.error(f"Failed to upload {file_path}: {error_msg}")
            failed.append((file_path, prefix, error_msg))

    return successful, skipped, failed

def main():
    """Main entry point for the upload script."""
    start_time = time.time()
    total_successful = 0
    total_skipped = 0
    failed_uploads = []
    batch_size = 100  # Process files in batches of 100

    try:
        # Load environment variables from .env file
        load_dotenv()

        # Get bucket name from environment variable
        bucket_name = os.environ.get("BUCKET_NAME")
        basemaps_dir = os.environ.get("BASEMAPS_DIR")
        if not bucket_name or not basemaps_dir:
            raise ValueError(
                "BUCKET_NAME or BASEMAPS_DIR not found in environment variables. Please create a .env file with these variables."
            )

        # Initialize upload tracker
        tracker = UploadTracker()

        # Process files in batches
        current_batch = []
        for file_path, prefix in find_tiff_files(basemaps_dir):
            current_batch.append((file_path, prefix))
            
            if len(current_batch) >= batch_size:
                successful, skipped, failed = process_batch(current_batch, tracker, bucket_name)
                total_successful += successful
                total_skipped += skipped
                failed_uploads.extend(failed)
                current_batch = []

        # Process remaining files
        if current_batch:
            successful, skipped, failed = process_batch(current_batch, tracker, bucket_name)
            total_successful += successful
            total_skipped += skipped
            failed_uploads.extend(failed)

        # Log summary
        elapsed_time = time.time() - start_time
        logging.info(f"\nUpload process completed in {elapsed_time:.2f} seconds")
        logging.info(f"Successfully uploaded: {total_successful} files")
        logging.info(f"Skipped (already uploaded): {total_skipped} files")
        logging.info(f"Failed uploads: {len(failed_uploads)} files")

        # Write failed uploads to a file if any
        if failed_uploads:
            error_file = "failed_uploads.txt"
            with open(error_file, "w") as f:
                for file_path, prefix, error in failed_uploads:
                    f.write(f"{file_path}\t{prefix}\t{error}\n")
            logging.error(f"Failed uploads have been written to {error_file}")
            sys.exit(1)

    except KeyboardInterrupt:
        logging.info("\nUpload process interrupted by user")
        sys.exit(130)
    except Exception as e:
        logging.error(f"Upload process failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
