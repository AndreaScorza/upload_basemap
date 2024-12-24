"""Module for tracking uploaded files."""
import os
import json
import logging
from typing import Set, Dict
from datetime import datetime

class UploadTracker:
    def __init__(self, tracker_file: str = "upload_history.json"):
        """Initialize the upload tracker.
        
        Args:
            tracker_file: Path to the JSON file that stores upload history
        """
        self.tracker_file = tracker_file
        self.history = self._load_history()

    def _load_history(self) -> Dict:
        """Load upload history from file."""
        if os.path.exists(self.tracker_file):
            try:
                with open(self.tracker_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logging.error(f"Error reading tracker file {self.tracker_file}")
                return {}
        return {}

    def _save_history(self):
        """Save upload history to file."""
        try:
            with open(self.tracker_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving tracker file: {e}")

    def is_uploaded(self, file_path: str, prefix: str) -> bool:
        """Check if a file has been uploaded.
        
        Args:
            file_path: Path to the file
            prefix: S3 prefix where the file was uploaded
            
        Returns:
            True if the file has been uploaded, False otherwise
        """
        file_key = f"{prefix}/{os.path.basename(file_path)}"
        return file_key in self.history

    def mark_uploaded(self, file_path: str, prefix: str):
        """Mark a file as uploaded.
        
        Args:
            file_path: Path to the file
            prefix: S3 prefix where the file was uploaded
        """
        file_key = f"{prefix}/{os.path.basename(file_path)}"
        self.history[file_key] = {
            "uploaded_at": datetime.now().isoformat(),
            "original_path": file_path,
            "prefix": prefix
        }
        self._save_history()

    def get_upload_info(self, file_path: str, prefix: str) -> Dict:
        """Get upload information for a file.
        
        Args:
            file_path: Path to the file
            prefix: S3 prefix where the file was uploaded
            
        Returns:
            Dictionary with upload information or None if not found
        """
        file_key = f"{prefix}/{os.path.basename(file_path)}"
        return self.history.get(file_key)
