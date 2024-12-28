"""Script to restore PostgreSQL database from SQL file."""
import subprocess
import os

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
