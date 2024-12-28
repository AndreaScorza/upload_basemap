"""Script to backup PostgreSQL database to SQL file."""
import subprocess
import os
from datetime import datetime

def backup_database():
    """Create a backup of the PostgreSQL database."""
    backup_dir = "db_backup"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Database connection details from docker-compose
    db_name = "upload_tracker"
    db_user = "upload_user"
    container_name = "upload_basemap_db_1"
    
    # Create backup file name with timestamp
    backup_file = os.path.join(backup_dir, f"upload_tracker_backup.sql")
    
    # Use pg_dump inside the container to create backup
    cmd = [
        "docker", "exec", container_name,
        "pg_dump",
        "-U", db_user,
        "-d", db_name,
        "--clean",  # Add DROP statements
        "--if-exists",  # Avoid errors if objects don't exist
    ]
    
    try:
        with open(backup_file, 'w') as f:
            subprocess.run(cmd, stdout=f, check=True)
        print(f"Database backup created successfully: {backup_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error creating backup: {e}")
        raise

if __name__ == "__main__":
    backup_database()
