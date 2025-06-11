#!/usr/bin/env python3
"""
GraphiVault Backend Entry Point
Main entry point for the GraphiVault backend system
Provides command-line interface and configuration management
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Import the IPC Gateway
from ipc_gateway import main as ipc_main

if __name__ == '__main__':
    # Set up environment
    os.environ['GRAPHIVAULT_BACKEND'] = str(backend_dir)
    
    # Run the IPC Gateway
    ipc_main()
