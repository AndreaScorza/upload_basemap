import os
from upload_basemap.src.s3_upload import upload_to_s3

def test_upload_to_s3():
    """Test uploading a file to S3."""
    # Get the bucket name from environment variables
    bucket_name = os.environ.get('BUCKET_NAME')
    if not bucket_name:
        raise ValueError("BUCKET_NAME not found in environment variables")

    # Path to the test image file
    file_path = os.path.join(os.path.dirname(__file__), "test_data", "region_5046600.tif")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Test file not found: {file_path}")
    
    # Set the prefix (folder) in S3 where the file will be uploaded
    prefix = "test_uploads"

    # Upload the file
    upload_to_s3(file_path, bucket_name, prefix)
    # If no exception is raised, the test passes
