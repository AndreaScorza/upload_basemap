"""Module for handling S3 uploads."""

import logging
import boto3
import os
from botocore.exceptions import BotoCoreError, ClientError


def upload_to_s3(
    file_path: str, bucket_name: str, prefix: str, overwrite: bool = False
) -> None:
    """Upload a local file to an S3 bucket with KMS encryption.

    Args:
        file_path: Path to the local file to upload
        bucket_name: Name of the S3 bucket
        prefix: Prefix (folder path) in the S3 bucket
        overwrite: If True, will overwrite existing file in S3. If False, will skip if file exists.

    Raises:
        FileNotFoundError: If the local file doesn't exist
        BotoCoreError: If there's an AWS-related error
        ClientError: If there's an S3 client error
    """
    try:
        s3_client = boto3.client("s3")

        # Construct the S3 key using the prefix and file_name
        file_name = os.path.basename(file_path)
        s3_key = f"{prefix.rstrip('/')}/{file_name}"

        # Check if file already exists in S3
        try:
            s3_client.head_object(Bucket=bucket_name, Key=s3_key)
            if not overwrite:
                logging.info(
                    f"File {s3_key} already exists in bucket {bucket_name}. Skipping upload."
                )
                return
        except ClientError as e:
            if e.response["Error"]["Code"] != "404":
                # If error is not 404 (not found), re-raise it
                raise

        # Upload the file to S3
        with open(file_path, "rb") as file:
            s3_client.upload_fileobj(
                file,
                bucket_name,
                s3_key,
                ExtraArgs={
                    "ServerSideEncryption": "aws:kms",
                    "ContentType": "image/tiff",
                },
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
