# Basemap S3 Upload Tool

A Python tool for uploading TIFF basemap files to S3 while maintaining directory structure and tracking upload history.

## Features

- Scans specified directories (`regions` and `regions_buildings`) for TIFF files
- Maintains directory structure when uploading to S3
- Tracks upload history to avoid re-uploading files
- Uses AWS KMS encryption for secure storage
- Provides detailed logging of the upload process

## Installation

1. Clone the repository:
```bash
git clone git@github.com:AndreaScorza/upload_basemap.git
cd upload_basemap
```

2. Install dependencies using Poetry:
```bash
poetry install
```

## Configuration

Create a `.env` file in the project root with the following variables:

```env
BUCKET_NAME=your-s3-bucket-name
BASEMAPS_DIR=/path/to/your/basemaps/directory
```

Make sure your AWS credentials are properly configured either through:
- Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
- AWS credentials file
- IAM role (if running on AWS infrastructure)

## Usage

Run the upload script:

```bash
poetry run python -m upload_basemap.main
```

The script will:
1. Scan the specified directories for TIFF files
2. Upload new files to S3 maintaining the directory structure:
   - Files in `regions/` → `s3://bucket-name/regions/`
   - Files in `regions_buildings/` → `s3://bucket-name/regions_buildings/`
3. Track uploaded files in `upload_history.json`
4. Log the process to stdout

## Directory Structure

```
upload_basemap/
├── upload_basemap/
│   ├── src/
│   │   ├── file_finder.py    # Finds TIFF files in directories
│   │   ├── s3_upload.py      # Handles S3 uploads with KMS encryption
│   │   └── upload_tracker.py # Tracks upload history
│   └── main.py              # Main entry point
├── tests/
│   ├── test_file_finder.py
│   ├── test_upload_tracker.py
│   └── test_upload.py
├── .env                     # Environment variables
├── pyproject.toml          # Poetry dependencies
└── README.md
```

## Development

### Running Tests

```bash
poetry run pytest
```

For verbose output:
```bash
poetry run pytest -v
```

### Environment Variables for Testing

Create a `.env.test` file in the `tests/` directory:

```env
BUCKET_NAME=test-bucket-name
BASEMAPS_DIR=/path/to/test/basemaps
```

## Dependencies

- Python 3.11+
- boto3: AWS SDK for Python
- python-dotenv: Environment variable management

## Error Handling

The tool includes comprehensive error handling for:
- Missing environment variables
- File system errors
- AWS/S3 upload errors
- Permission issues

All errors are logged with appropriate context for debugging.

## Security

- Files are uploaded with AWS KMS encryption
- AWS credentials are managed securely through environment variables or IAM roles
- Upload history is stored locally in JSON format

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request
