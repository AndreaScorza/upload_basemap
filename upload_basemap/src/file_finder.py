"""Module for finding files to upload."""
import os
import glob
import logging
from typing import List, Dict, Tuple

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
    
    # Look for tiff files in regions and regions_buildings subdirectories
    subdirs = ['regions', 'regions_buildings']
    
    for subdir in subdirs:
        dir_path = os.path.join(base_dir, subdir)
        if not os.path.exists(dir_path):
            logging.warning(f"Subdirectory not found: {dir_path}")
            continue
            
        # Find all .tif files in the subdirectory
        pattern = os.path.join(dir_path, "*.tif")
        tif_files = glob.glob(pattern)
        
        if not tif_files:
            logging.warning(f"No .tif files found in {dir_path}")
            continue
            
        # Add files with their prefix
        for file_path in tif_files:
            result.append((file_path, subdir))
        
        logging.info(f"Found {len(tif_files)} TIFF files in {subdir}/")
    
    if not result:
        logging.warning(f"No TIFF files found in any subdirectory of {base_dir}")
        
    return result
