from upload_basemap.src.file_finder import find_tiff_files
from upload_basemap.src.upload_tracker import UploadTracker
from pprint import pprint
import os
import tempfile
import json

def test_upload_tracker_with_file_finder():
    """Test that upload tracker works correctly with file_finder output."""
    basemaps_dir = os.environ.get('BASEMAPS_DIR')
    assert basemaps_dir is not None, "BASEMAPS_DIR environment variable is not set"
    
    # Create a temporary file for the upload history
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp_file:
        tracker = UploadTracker(temp_file.name)
        
        try:
            # Get files from file_finder
            files = find_tiff_files(basemaps_dir)
            assert len(files) > 0, "No files found to test with"
            
            print("\nTesting with files:")
            pprint(files)
            
            # Test marking files as uploaded
            print("\nMarking files as uploaded...")
            for file_path, prefix in files:
                tracker.mark_uploaded(file_path, prefix)
                
                # Verify it was marked as uploaded
                assert tracker.is_uploaded(file_path, prefix), \
                    f"File {file_path} was not marked as uploaded"
                
                # Get and print upload info
                info = tracker.get_upload_info(file_path, prefix)
                print(f"\nUpload info for {os.path.basename(file_path)}:")
                pprint(info)
            
            # Print final history file content
            print("\nFinal upload history content:")
            with open(temp_file.name, 'r') as f:
                history = json.load(f)
                pprint(history)
                
            # Verify all files are in history
            assert len(history) == len(files), \
                f"History has {len(history)} entries but {len(files)} files were uploaded"
                
        finally:
            # Clean up temp file
            os.unlink(temp_file.name)

def test_upload_tracker_file_persistence():
    """Test that upload tracker correctly persists and loads data."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp_file:
        try:
            # First tracker instance - save some data
            tracker1 = UploadTracker(temp_file.name)
            test_file = "/test/path/file.tif"
            test_prefix = "regions"
            
            tracker1.mark_uploaded(test_file, test_prefix)
            
            # Create new tracker instance with same file
            tracker2 = UploadTracker(temp_file.name)
            
            # Verify data was loaded
            assert tracker2.is_uploaded(test_file, test_prefix), \
                "Second tracker instance didn't load the upload history"
            
            # Print the loaded history
            info = tracker2.get_upload_info(test_file, test_prefix)
            print("\nLoaded history from file:")
            pprint(info)
            
        finally:
            # Clean up
            os.unlink(temp_file.name)
