import os
import sys
import pytest
from dotenv import load_dotenv

# Add the project root directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture(autouse=True)
def load_test_env():
    """Load environment variables from .env.test file."""
    env_test_path = os.path.join(os.path.dirname(__file__), '.env.test')
    load_dotenv(env_test_path)
