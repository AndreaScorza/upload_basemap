# Basemap S3 Upload Tool

A Python tool for uploading TIFF basemap files to S3 while maintaining directory structure and tracking upload history.

## Features

- Efficient upload of large files to AWS S3
- Automatic handling of multipart uploads for large files
- Progress tracking for long-running uploads
- AWS credentials are managed securely through environment variables or IAM roles
- Upload history is stored in PostgreSQL for reliability and concurrent access

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
# or simply
poetry run upload
```

The script will:
1. Scan the specified directories for TIFF files
2. Upload new files to S3 maintaining the directory structure:
   - Files in `regions/` → `s3://bucket-name/regions/`
   - Files in `regions_buildings/` → `s3://bucket-name/regions_buildings/`
3. Track uploaded files in PostgreSQL
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
- Upload history is stored securely in PostgreSQL

## Database Management

The application uses PostgreSQL to track uploaded files. The database runs in Docker and is automatically initialized with data from `db_backup/upload_tracker_backup.sql`.

### Starting the Database

To start the PostgreSQL database:

```bash
docker-compose up -d
```

This will:
1. Start a PostgreSQL container
2. Initialize it with data from `db_backup/upload_tracker_backup.sql` (if present)
3. Store the database files in `./db_data/`

### Backing Up the Database

To create a new backup of the current database state:

```bash
poetry run python scripts/backup_db.py
```

This will create/update the file `db_backup/upload_tracker_backup.sql`. This file is versioned in git and used to initialize new instances of the database.

### Restoring the Database

If you need to restore the database from the backup:

```bash
poetry run python scripts/restore_db.py
```

### Resetting the Database

To completely reset the database:

```bash
# Stop the container
docker-compose down

# Remove the data directory
rm -rf db_data

# Start fresh
docker-compose up -d
```

This will give you a fresh database initialized with the data from `db_backup/upload_tracker_backup.sql`.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request
