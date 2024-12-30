"""Module for finding files to upload."""
import os
from typing import Generator, Tuple
import logging

def find_tiff_files(base_dir: str) -> Generator[Tuple[str, str], None, None]:
    """Find all TIFF files in the given directory and its subdirectories.
    
    Args:
        base_dir: Base directory to search for TIFF files
        
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
    
    for subdir in subdirs:
        dir_path = os.path.join(base_dir, subdir)
        if not os.path.exists(dir_path):
            logging.warning(f"Subdirectory not found: {dir_path}")
            continue
            
        try:
            with os.scandir(dir_path) as entries:
                for entry in entries:
                    if entry.is_file() and entry.name.lower().endswith('.tif'):
                        total_files[subdir] += 1
                        yield (entry.path, subdir)
                
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
