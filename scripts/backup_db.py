"""Script to backup PostgreSQL database to SQL file."""
import subprocess
import os
import time

def wait_for_postgres(container_name: str, max_attempts: int = 30):
    """Wait for PostgreSQL to be ready to accept connections."""
    print("Waiting for PostgreSQL to be ready...")
    cmd = [
        "docker", "exec", container_name,
        "pg_isready",
        "-U", "upload_user"
    ]
    
    for i in range(max_attempts):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("PostgreSQL is ready!")
                return True
        except subprocess.CalledProcessError:
            pass
        
        print(f"Waiting... ({i+1}/{max_attempts})")
        time.sleep(1)
    
    return False

def ensure_container_running():
    """Ensure the PostgreSQL container is running."""
    # Check if container exists and is running
    result = subprocess.run(
        ["docker", "ps", "-q", "-f", "name=upload_basemap_db_1"],
        capture_output=True,
        text=True
    )
    
    if not result.stdout.strip():
        print("Container not running. Starting it...")
        subprocess.run(["docker-compose", "up", "-d"], check=True)
        return True
    return False

def backup_database():
    """Create a backup of the PostgreSQL database."""
    backup_dir = "db_backup"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Database connection details from docker-compose
    db_name = "upload_tracker"
    db_user = "upload_user"
    container_name = "upload_basemap_db_1"
    
    # Ensure container is running
    container_started = ensure_container_running()
    
    # Wait for PostgreSQL to be ready
    if not wait_for_postgres(container_name):
        print("PostgreSQL did not become ready in time")
        return
    
    # Create backup file name
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
