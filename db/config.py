import os

# Get the project root directory
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))

# Ensure data directory exists
DATA_DIR = os.path.join(ROOT_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# Database configuration
DB_PATH = os.path.join(DATA_DIR, 'test.db')
DB_URL = f"sqlite:///{DB_PATH}"
