"""Script to restore PostgreSQL database from SQL file."""
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

def restore_database():
    """Restore the PostgreSQL database from backup."""
    backup_dir = "db_backup"
    backup_file = os.path.join(backup_dir, "upload_tracker_backup.sql")
    
    if not os.path.exists(backup_file):
        print(f"Backup file not found: {backup_file}")
        return
    
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
    
    # Use psql to restore the backup
    cmd = [
        "docker", "exec", "-i", container_name,
        "psql",
        "-U", db_user,
        "-d", db_name,
    ]
    
    try:
        with open(backup_file, 'r') as f:
            subprocess.run(cmd, stdin=f, check=True)
        print("Database restored successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error restoring backup: {e}")
        raise

if __name__ == "__main__":
    restore_database()
