import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

# Add the parent directory of 'pages' to the Python path
parent_dir = os.path.dirname(project_root)
sys.path.insert(0, parent_dir)

import streamlit as st
from pages.advanced import main

if __name__ == '__main__':
    main()