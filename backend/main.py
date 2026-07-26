import sys
import os

# Ensure the 'backend' directory is in the Python path
# so that 'from app...' imports work correctly.
sys.path.insert(0, os.path.dirname(__file__))

from app.main import app
