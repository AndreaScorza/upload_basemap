"""Module for finding files to upload."""
import os
from typing import List, Tuple
import logging

def find_tiff_files(base_dir: str) -> List[Tuple[str, str]]:
    """Find all TIFF files in the given directory and its subdirectories.
    
    Args:
        base_dir: Base directory to search for TIFF files
        
    Returns:
        List of tuples (file_path, prefix) where:
        - file_path is the absolute path to the TIFF file
        - prefix is the folder name (e.g., 'regions' or 'regions_buildings')
        
    Raises:
        FileNotFoundError: If the base directory doesn't exist
    """
    if not os.path.exists(base_dir):
        raise FileNotFoundError(f"Directory not found: {base_dir}")

    result = []
    subdirs = ['regions', 'regions_buildings']
    
    for subdir in subdirs:
        dir_path = os.path.join(base_dir, subdir)
        if not os.path.exists(dir_path):
            logging.warning(f"Subdirectory not found: {dir_path}")
            continue
            
        # Use scandir which is more efficient than glob
        try:
            with os.scandir(dir_path) as entries:
                tif_count = 0
                for entry in entries:
                    if entry.is_file() and entry.name.lower().endswith('.tif'):
                        result.append((entry.path, subdir))
                        tif_count += 1
                
                if tif_count == 0:
                    logging.warning(f"No .tif files found in {dir_path}")
                else:
                    logging.info(f"Found {tif_count} TIFF files in {subdir}/")
                    
        except PermissionError:
            logging.error(f"Permission denied accessing {dir_path}")
            continue
    
    if not result:
        logging.warning(f"No TIFF files found in any subdirectory of {base_dir}")
        
    return result
