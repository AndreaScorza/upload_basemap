#!/usr/bin/env python3
"""Main entry point for basemap upload tool."""
import os
import logging
from dotenv import load_dotenv
from botocore.exceptions import ClientError
from .src.file_finder import find_tiff_files
from .src.s3_upload import upload_to_s3
from .src.upload_tracker import UploadTracker

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def main():
    """Main entry point for the upload script."""
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

        # Find all TIFF files with their prefixes
        files_and_prefixes = find_tiff_files(basemaps_dir)

        if not files_and_prefixes:
            logging.warning("No files found to upload")
            return

        # Count total and new files
        total_files = len(files_and_prefixes)
        new_files = sum(
            1
            for file_path, prefix in files_and_prefixes
            if not tracker.is_uploaded(file_path, prefix)
        )

        logging.info(
            f"Found {total_files} total files, {new_files} new files to upload"
        )

        # Upload each file with its corresponding prefix
        for file_path, prefix in files_and_prefixes:
            try:
                # Skip if already uploaded
                if tracker.is_uploaded(file_path, prefix):
                    upload_info = tracker.get_upload_info(file_path, prefix)
                    logging.info(
                        f"Skipping {file_path} - already uploaded on {upload_info['uploaded_at']}"
                    )
                    continue

                logging.info(f"Uploading {file_path} to {bucket_name}/{prefix}")
                try:
                    upload_to_s3(file_path, bucket_name, prefix)
                except Exception as e:
                    if hasattr(e, 'response') and e.response["Error"]["Code"] == "404":
                        raise
                    # If file exists in S3 (and any other S3 error), still track it
                    logging.info(f"File exists in S3, tracking it in upload history")
                
                # Mark as uploaded in both cases - whether we uploaded it or it existed
                tracker.mark_uploaded(file_path, prefix)

            except Exception as e:
                logging.error(f"Failed to upload {file_path}: {e}")
                continue

        logging.info("Upload process completed")

    except Exception as e:
        logging.error(f"Upload process failed: {e}")
        raise


if __name__ == "__main__":
    main()
