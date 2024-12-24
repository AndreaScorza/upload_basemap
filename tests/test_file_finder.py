from upload_basemap.src.file_finder import find_tiff_files
from pprint import pprint
import os

def test_find_tiff_files():
    basemaps_dir = os.environ.get('BASEMAPS_DIR')
    assert basemaps_dir is not None, "BASEMAPS_DIR environment variable is not set"
    
    # Find all tiff files
    files = find_tiff_files(basemaps_dir)
    
    # Basic validation
    assert len(files) > 0, "No files found"
    
    # Print summary and first few files
    print(f"\nFound {len(files)} files")
    print("\nFirst 3 files as examples:")
    for file_path, prefix in files[:3]:
        print(f"Prefix: {prefix}")
        print(f"File: {os.path.basename(file_path)}")
        print("-" * 40)
    
    # Validate each result
    for file_path, prefix in files:
        # Check if prefix is one of the expected values
        assert prefix in ['regions', 'regions_buildings'], f"Unexpected prefix: {prefix}"
        
        # Check if file exists and is a .tif file
        assert os.path.exists(file_path), f"File does not exist: {file_path}"
        assert file_path.endswith('.tif'), f"Not a TIFF file: {file_path}"
        
        # Check if file is in the correct subdirectory
        expected_dir = os.path.join(basemaps_dir, prefix)
        assert os.path.dirname(file_path) == expected_dir, \
            f"File {file_path} not in expected directory {expected_dir}"