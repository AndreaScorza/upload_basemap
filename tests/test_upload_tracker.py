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
            # Get files from file_finder and take only first 2 from each prefix
            all_files = find_tiff_files(basemaps_dir)
            files_by_prefix = {}
            for file_path, prefix in all_files:
                if prefix not in files_by_prefix:
                    files_by_prefix[prefix] = []
                if len(files_by_prefix[prefix]) < 2:  # Only keep first 2 files per prefix
                    files_by_prefix[prefix].append((file_path, prefix))
            
            # Flatten the list for testing
            test_files = [item for sublist in files_by_prefix.values() for item in sublist]
            assert len(test_files) > 0, "No files found to test with"
            
            print(f"\nTesting with {len(test_files)} files:")
            for file_path, prefix in test_files:
                print(f"- {prefix}: {os.path.basename(file_path)}")
            
            # Test marking files as uploaded
            print("\nMarking files as uploaded...")
            for file_path, prefix in test_files:
                tracker.mark_uploaded(file_path, prefix)
                assert tracker.is_uploaded(file_path, prefix), \
                    f"File {file_path} was not marked as uploaded"
            
            # Print final history file content
            print("\nFinal upload history content:")
            with open(temp_file.name, 'r') as f:
                history = json.load(f)
                print(f"Total entries in history: {len(history)}")
                
            # Verify all files are in history
            assert len(history) == len(test_files), \
                f"History has {len(history)} entries but {len(test_files)} files were uploaded"
                
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
