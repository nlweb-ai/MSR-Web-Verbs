"""
Configuration settings for verb_ingress module.

This file contains configuration variables and paths used throughout the module.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Path to the NLWeb repository root
NLWeb_root = os.getenv('NLWEB_ROOT')

# Add the Python code directory to sys.path for module imports
python_code_path = os.path.join(NLWeb_root, 'code', 'python')
if python_code_path not in sys.path:
    sys.path.append(python_code_path)
