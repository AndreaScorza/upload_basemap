from upload_basemap.src.file_finder import find_tiff_files
from pprint import pprint
import os

def test_upload_to_s3():
    basemaps_dir = os.environ.get('BASEMAPS_DIR')
    res = find_tiff_files(basemaps_dir)
    print(res)