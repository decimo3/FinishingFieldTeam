'''Module to create and hold constants.

This module defines and manages all constant values used throughout the application.
It handles path resolution for both frozen (executable) and unfrozen (development) environments,
and ensures required directories exist for browser automation.

The module includes:
- Base path resolution for different execution environments
- WebDriver configuration settings
- Browser configuration settings
- Directory management for Chrome data and driver

All constants are marked as Final to prevent accidental modification.
'''

import os
import sys
from typing import Final, Tuple

# Base path resolution based on execution environment
if getattr(sys, 'frozen', False):
	# If the script is running as a frozen executable
	BASE_PATH: Final[str] = os.path.dirname(sys.executable)
else:
	# If the script is running in development mode
	BASE_PATH: Final[str] = os.path.dirname(os.path.abspath(__file__))

# WebDriver Configuration
SERVICE_PORT: Final[int] = 7826  # Port number for the WebDriver service
DEFAULT_TIMEOUT: Final[int] = 300  # Default timeout in seconds for WebDriver operations
DEFAULT_WINDOW_SIZE: Final[Tuple[int, int]] = (1920, 1080)  # Default browser window size

# Browser Configuration
CHROME_DATA_DIR: Final[str] = os.path.join(BASE_PATH, "www")  # Chrome user data directory
CHROME_DRIVER_DIR: Final[str] = os.path.join(BASE_PATH, "chromedriver")  # ChromeDriver directory

# Ensure required directories exist
os.makedirs(CHROME_DATA_DIR, exist_ok=True)  # Create Chrome data directory if needed
os.makedirs(CHROME_DRIVER_DIR, exist_ok=True)  # Create ChromeDriver directory if needed
