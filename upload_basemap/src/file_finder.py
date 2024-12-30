"""Module for finding files to upload."""
import os
import json
from typing import Generator, Tuple, Optional
import logging

RESUME_FILE = "upload_resume.json"

def save_resume_point(subdir: str, last_file: str):
    """Save the current position to resume file."""
    with open(RESUME_FILE, 'w') as f:
        json.dump({
            'last_subdir': subdir,
            'last_file': last_file
        }, f)

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
    except OSError as e:
        logging.warning(f"Could not remove resume file: {e}")

def find_tiff_files(base_dir: str, resume: bool = True) -> Generator[Tuple[str, str], None, None]:
    """Find all TIFF files in the given directory and its subdirectories.
    
    Args:
        base_dir: Base directory to search for TIFF files
        resume: Whether to resume from last position
        
    Yields:
        Tuples (file_path, prefix) where:
        - file_path is the absolute path to the TIFF file
        - prefix is the folder name (e.g., 'regions' or 'regions_buildings')
        
    Raises:
        FileNotFoundError: If the base directory doesn't exist
    """
    if not os.path.exists(base_dir):
        raise FileNotFoundError(f"Directory not found: {base_dir}")

    subdirs = ['regions', 'regions_buildings']
    total_files = {subdir: 0 for subdir in subdirs}
    
    # Get resume point if requested
    last_subdir, last_file = get_resume_point() if resume else (None, None)
    resume_mode = resume and last_subdir is not None
    
    if resume_mode:
        logging.info(f"Resuming from {last_subdir}/{last_file}")
        # Reorder subdirs to start from last position
        if last_subdir in subdirs:
            idx = subdirs.index(last_subdir)
            subdirs = subdirs[idx:] + subdirs[:idx]
    
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
                        start_idx = files.index(os.path.basename(last_file)) + 1
                    except ValueError:
                        # File not found, start from beginning of this directory
                        pass
                    resume_mode = False  # Turn off resume mode after finding start point
                
                # Process files from the starting point
                for filename in files[start_idx:]:
                    file_path = os.path.join(dir_path, filename)
                    total_files[subdir] += 1
                    save_resume_point(subdir, filename)
                    yield (file_path, subdir)
                
                if total_files[subdir] == 0:
                    logging.warning(f"No .tif files found in {dir_path}")
                else:
                    logging.info(f"Found {total_files[subdir]} TIFF files in {subdir}/")
                    
        except PermissionError:
            logging.error(f"Permission denied accessing {dir_path}")
            continue
        except OSError as e:
            logging.error(f"Error accessing {dir_path}: {e}")
            continue
    
    total = sum(total_files.values())
    if total == 0:
        logging.warning(f"No TIFF files found in any subdirectory of {base_dir}")
    else:
        # Clear resume point after successful completion
        clear_resume_point()
