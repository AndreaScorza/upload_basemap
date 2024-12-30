"""Module for finding files to upload."""
import os
import json
from typing import Generator, Tuple, Optional
import logging
from .upload_tracker import UploadTracker

RESUME_FILE = "upload_resume.json"

def save_resume_point(subdir: str, last_file: str):
    """Save the current position to resume file."""
    try:
        with open(RESUME_FILE, 'w') as f:
            json.dump({
                'last_subdir': subdir,
                'last_file': last_file
            }, f)
        logging.debug(f"Saved resume point: {subdir}/{last_file}")
    except IOError as e:
        logging.error(f"Could not save resume point: {e}")

def get_resume_point() -> Tuple[Optional[str], Optional[str]]:
    """Get the last processed position."""
    try:
        if os.path.exists(RESUME_FILE):
            with open(RESUME_FILE, 'r') as f:
                data = json.load(f)
                return data.get('last_subdir'), data.get('last_file')
    except (json.JSONDecodeError, IOError) as e:
        logging.warning(f"Could not read resume file: {e}")
    return None, None

def clear_resume_point():
    """Clear the resume point after successful completion."""
    try:
        if os.path.exists(RESUME_FILE):
            os.remove(RESUME_FILE)
            logging.debug("Cleared resume point")
    except OSError as e:
        logging.warning(f"Could not remove resume file: {e}")

def find_tiff_files(base_dir: str, resume: bool = True) -> Generator[Tuple[str, str, int], None, None]:
    """Find all TIFF files in the given directory and its subdirectories that need to be uploaded.
    
    Args:
        base_dir: Base directory to search for TIFF files
        resume: Whether to resume from last position
        
    Yields:
        Tuples (file_path, prefix, skipped_count) where:
        - file_path is the absolute path to the TIFF file
        - prefix is the folder name (e.g., 'regions' or 'regions_buildings')
        - skipped_count is the number of files skipped since last yield
        Only yields files that are not already in the database.
        
    Raises:
        FileNotFoundError: If the base directory doesn't exist
    """
    if not os.path.exists(base_dir):
        raise FileNotFoundError(f"Directory not found: {base_dir}")

    subdirs = ['regions', 'regions_buildings']
    total_files = {subdir: 0 for subdir in subdirs}
    skipped_files = {subdir: 0 for subdir in subdirs}
    
    # Get resume point if requested
    last_subdir, last_file = get_resume_point() if resume else (None, None)
    resume_mode = resume and last_subdir is not None
    
    if resume_mode:
        logging.info(f"Resuming from {last_subdir}/{last_file}")
        # Reorder subdirs to start from last position
        if last_subdir in subdirs:
            idx = subdirs.index(last_subdir)
            subdirs = subdirs[idx:] + subdirs[:idx]
    
    # Initialize upload tracker to check database
    tracker = UploadTracker()
    current_skipped = 0  # Track skipped files since last yield
    
    for subdir in subdirs:
        dir_path = os.path.join(base_dir, subdir)
        if not os.path.exists(dir_path):
            logging.warning(f"Subdirectory not found: {dir_path}")
            continue
            
        try:
            with os.scandir(dir_path) as entries:
                # Convert to sorted list for consistent ordering
                files = sorted(
                    entry.name for entry in entries 
                    if entry.is_file() and entry.name.lower().endswith('.tif')
                )
                
                # Find starting point in current directory
                start_idx = 0
                if resume_mode and subdir == last_subdir and last_file:
                    try:
                        # Start from the last file
                        start_idx = files.index(os.path.basename(last_file))
                        logging.info(f"Starting from index {start_idx} in {subdir}")
                    except ValueError:
                        # File not found, start from beginning of this directory
                        logging.warning(f"Resume file {last_file} not found in {subdir}, starting from beginning")
                        pass
                    resume_mode = False  # Turn off resume mode after finding start point
                
                # Process files from the starting point
                for filename in files[start_idx:]:
                    file_path = os.path.join(dir_path, filename)
                    total_files[subdir] += 1
                    
                    # Check if file is already in database
                    if tracker.is_uploaded(file_path, subdir):
                        skipped_files[subdir] += 1
                        current_skipped += 1
                        # Save resume point for skipped files too
                        save_resume_point(subdir, filename)
                        if skipped_files[subdir] % 100 == 0:  # Log every 100 skipped files
                            logging.info(f"Skipped {skipped_files[subdir]} already uploaded files in {subdir}")
                        continue
                    
                    # Save resume point before yielding in case of error during upload
                    save_resume_point(subdir, filename)
                    yield (file_path, subdir, current_skipped)
                    current_skipped = 0  # Reset counter after yielding
                
                if total_files[subdir] == 0:
                    logging.warning(f"No .tif files found in {dir_path}")
                else:
                    logging.info(
                        f"Found {total_files[subdir]} TIFF files in {subdir}/, "
                        f"skipped {skipped_files[subdir]} already uploaded files"
                    )
                    
        except PermissionError:
            logging.error(f"Permission denied accessing {dir_path}")
            continue
        except OSError as e:
            logging.error(f"Error accessing {dir_path}: {e}")
            continue
    
    total = sum(total_files.values())
    total_skipped = sum(skipped_files.values())
    if total == 0:
        logging.warning(f"No TIFF files found in any subdirectory of {base_dir}")
    else:
        logging.info(f"Total files processed: {total}, already uploaded: {total_skipped}")
        # Clear resume point after successful completion
        clear_resume_point()
