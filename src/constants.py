''' Module to create and hold constants. '''
import os
import sys

if getattr(sys, 'frozen', False):
	# If the script is running as a frozen executable
	BASE_PATH = os.path.dirname(sys.executable)
else:
	BASE_PATH = os.path.dirname(os.path.abspath(__file__))

SERVICE_PORT = 7826

DEFAULT_TIMEOUT = 300
