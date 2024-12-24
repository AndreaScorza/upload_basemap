import logging
import boto3
from botocore.exceptions import BotoCoreError, ClientError
import os

def upload_to_s3(file_path: str, bucket_name: str, prefix: str):
    """Uploads a local file to an S3 bucket with optional KMS encryption."""
    try:
        s3_client = boto3.client("s3")
        
        # Construct the S3 key using the prefix and file_name
        file_name = os.path.basename(file_path)
        s3_key = f"{prefix.rstrip('/')}/{file_name}"

        # Upload the file to S3
        with open(file_path, 'rb') as file:
            s3_client.upload_fileobj(
                file, 
                bucket_name, 
                s3_key,
                ExtraArgs={
                    "ServerSideEncryption": "aws:kms",
                    "ContentType": "image/tiff"
                }
            )
        
        logging.info(f"File {file_path} uploaded to S3 as {s3_key}")

    except FileNotFoundError as e:
        logging.error(f"Failed to find local file {file_path}: {e}", exc_info=True)
        raise
    except (BotoCoreError, ClientError) as e:
        logging.error(f"Failed to upload file to S3: {e}", exc_info=True)
        raise
    except ValueError as e:
        logging.error(f"Validation error: {e}", exc_info=True)
        raise