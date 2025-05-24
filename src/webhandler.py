'''Module to handle web interactions using Selenium WebDriver.

This module provides a high-level interface for web automation using Selenium WebDriver.
It manages the lifecycle of the WebDriver instance and ChromeDriver server process,
handles browser configuration, and provides simplified methods for common web interactions.

The module includes:
- WebHandler class for managing browser sessions
- Automatic ChromeDriver management
- Error handling through WebHandlerError
- Resource management through context manager interface
- Configuration management for Chrome browser

Key features:
- Uses Selenium WebDriver for browser automation
- Automatically manages ChromeDriver
- Handles cleanup of all resources properly
'''

from typing import Optional, Any, Union
from urllib.parse import ParseResult as URL
from selenium.webdriver import Remote
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from src.solvelib.printer import Printer
from src.constants import (
	DEFAULT_TIMEOUT, DEFAULT_WINDOW_SIZE,
	CHROME_DATA_DIR, SERVICE_PORT
)
import subprocess
import time

class WebHandlerError(Exception):
	'''Base exception for WebHandler errors.

	This exception is raised when there are issues with:
	- ChromeDriver initialization
	- WebDriver initialization
	- Browser navigation
	- Element finding
	- Resource cleanup
	'''

class WebHandler:
	'''Class to handle web interactions using Selenium WebDriver.

	This class provides a simplified interface for web automation tasks using
	Selenium WebDriver. It manages the WebDriver session lifecycle and provides
	methods for common web interactions.

	The class implements the context manager protocol for proper resource
	management and cleanup.

	Key features:
	- WebDriver session handling
	- Proper resource cleanup
	- Support for headless mode
	- Simplified web interaction methods

	Attributes:
		driver (Optional[WebDriver]): The Selenium WebDriver instance.
		headless (bool): Whether the browser runs in headless mode.
		options (Options): Chrome browser options.
	'''

	def __init__(self, headless: bool = False, remote_url: Optional[str] = None):
		'''Initialize the WebHandler.

		Sets up the WebDriver with the specified configuration.
		Initializes the Chrome options and WebDriver instance.

		Args:
			headless (bool): Whether to run Chrome in headless mode.
				Defaults to False.
			remote_url (Optional[str]): Remote Selenium Grid URL.
				If provided, skips starting local ChromeDriver.
				
		Raises:
			WebHandlerError: If WebDriver initialization fails.
		'''
		self.driver: Optional[Remote] = None
		self.chromedriver_process = None
		self.headless = headless
		self.remote_url = remote_url
		self._setup_driver()

	def _start_chromedriver(self) -> None:
		'''Start the ChromeDriver server.

		This method starts a ChromeDriver server process that the Remote WebDriver
		will connect to. It uses webdriver-manager to ensure the correct ChromeDriver
		version is installed.

		The server is started on the port specified in SERVICE_PORT.

		Raises:
			WebHandlerError: If ChromeDriver fails to start or if the correct
				version cannot be installed.
		'''
		try:
			chromedriver_path = ChromeDriverManager().install()
			# Start ChromeDriver with verbose logging and no output buffering
			self.chromedriver_process = subprocess.Popen(
				[chromedriver_path, f"--port={SERVICE_PORT}", "--verbose", "--log-path=chromedriver.log"],
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
				bufsize=1,
				universal_newlines=True
			)

			# Wait for ChromeDriver to start and be ready
			max_attempts = 5
			attempt = 0
			while attempt < max_attempts:
				try:
					import requests
					response = requests.get(f"http://localhost:{SERVICE_PORT}/status")
					if response.status_code == 200:
						break
				except requests.exceptions.ConnectionError: # type: ignore
					pass
				time.sleep(1)
				attempt += 1

			if attempt == max_attempts:
				raise WebHandlerError("ChromeDriver failed to start within the timeout period")

		except Exception as e:
			if self.chromedriver_process:
				try:
					self.chromedriver_process.terminate()
					self.chromedriver_process.wait(timeout=5)
				except Exception:
					try:
						self.chromedriver_process.kill()
					except Exception:
						pass
				self.chromedriver_process = None
			raise WebHandlerError(f"Failed to start ChromeDriver: {str(e)}") from e

	def _setup_driver(self) -> None:
		'''Set up the Remote WebDriver with proper configuration.

		This method:
		1. Starts the ChromeDriver server process if no remote_url
		2. Configures Chrome options for the Remote WebDriver
		3. Creates and initializes the Remote WebDriver instance

		The Remote WebDriver connects to the local ChromeDriver server
		on the port specified in SERVICE_PORT, unless remote_url is provided.

		Raises:
			WebHandlerError: If any step of the setup process fails.
		'''
		try:
			if not self.remote_url:
				# Start ChromeDriver server
				self._start_chromedriver()
				executor_url = f"http://localhost:{SERVICE_PORT}"
			else:
				# Use provided remote URL
				executor_url = self.remote_url

			# Set up the Options
			self.options = Options()
			self.options.add_argument(f"--user-data-dir={CHROME_DATA_DIR}")
			if self.headless:
				self.options.add_argument("--headless=new")
			self.options.add_argument(
				f"--window-size={DEFAULT_WINDOW_SIZE[0]},{DEFAULT_WINDOW_SIZE[1]}"
			)
			self.options.add_argument("--no-sandbox")
			self.options.add_argument("--disable-dev-shm-usage")
			self.options.add_argument("--disable-gpu")
			self.options.add_argument("--disable-extensions")
			self.options.add_argument("--disable-software-rasterizer")
			self.options.add_argument("--disable-features=VizDisplayCompositor")
			self.options.add_argument("--disable-features=IsolateOrigins,site-per-process")
			self.options.add_argument("--disable-web-security")
			self.options.add_argument("--allow-running-insecure-content")
			self.options.add_argument("--ignore-certificate-errors")

			# Set up the Remote WebDriver with retry logic
			max_attempts = 3
			attempt = 0
			last_error = None

			while attempt < max_attempts:
				try:
					self.driver = Remote(
						command_executor=executor_url,
						options=self.options
					)
					break
				except Exception as e:
					last_error = e
					attempt += 1
					if attempt < max_attempts:
						time.sleep(2)  # Wait before retrying
					else:
						raise WebHandlerError(
							f"Failed to initialize WebDriver after {max_attempts} attempts: {str(last_error)}"
						) from last_error

		except Exception as e:
			self.cleanup()
			raise WebHandlerError(f"Failed to initialize WebDriver: {str(e)}") from e

	def cleanup(self) -> None:
		'''Clean up resources.

		Safely stops the WebDriver, handling any exceptions that might
		occur during cleanup. Sets the driver to None after cleanup.
		'''
		if self.driver:
			try:
				self.driver.quit()
			except WebDriverException:
				pass
			self.driver = None
		if self.chromedriver_process:
			try:
				self.chromedriver_process.terminate()
				self.chromedriver_process.wait(timeout=5)
			except Exception:
				try:
					self.chromedriver_process.kill()
				except Exception:
					pass
			self.chromedriver_process = None

	def __enter__(self) -> 'WebHandler':
		'''Context manager entry.

		Returns:
			WebHandler: The current WebHandler instance.
		'''
		return self

	def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
		'''Context manager exit.

		Ensures proper cleanup of resources when exiting the context.

		Args:
			exc_type: The type of exception if any.
			exc_val: The exception value if any.
			exc_tb: The exception traceback if any.
		'''
		self.cleanup()

	def __del__(self) -> None:
		'''Destructor.

		Ensures cleanup of resources when the object is garbage collected.
		This provides a safety net in case the context manager is not used.
		'''
		self.cleanup()

	def navigate_to_url(self, url: Union[str, URL]) -> None:
		'''Navigate to the specified URL.

		Uses the WebDriver to navigate to the specified URL.

		Args:
			url (Union[str, URL]): The URL to navigate to. Can be either
				a string or a URL object.

		Raises:
			WebHandlerError: If the driver is not initialized or navigation fails.
		'''
		if not self.driver:
			raise WebHandlerError("Driver not initialized")
		try:
			self.driver.get(str(url))
		except WebDriverException as e:
			raise WebHandlerError(f"Failed to navigate to URL: {str(e)}") from e

	def find_element(self, by: By, value: str) -> Any:
		'''Find an element on the page.

		Uses the WebDriver to find an element on the current page.

		Args:
			by (By): The locator strategy (e.g., By.ID, By.CLASS_NAME).
			value (str): The locator value to search for.

		Returns:
			Any: The found Selenium WebElement.

		Raises:
			WebHandlerError: If the driver is not initialized or element is not found.
		'''
		if not self.driver:
			raise WebHandlerError("Driver not initialized")
		try:
			return self.driver.find_element(by, value)
		except WebDriverException as e:
			raise WebHandlerError(f"Failed to find element: {str(e)}") from e

# if __name__ == "__main__":
# 	# Example usage with local ChromeDriver
# 	try:
# 		with WebHandler() as web_handler:
# 			web_handler.navigate_to_url("http://example.com")
# 			element = web_handler.find_element(By.TAG_NAME, "h1")
# 			print(element.text)
# 	except WebHandlerError as e:
# 		print(f"Error: {str(e)}")

	# Example usage with remote Selenium Grid
	# REMOTE_URL = "http://your-remote-selenium-grid:4444/wd/hub"
	# try:
	# 	with WebHandler(remote_url=REMOTE_URL) as web_handler:
	# 		web_handler.navigate_to_url("http://example.com")
	# 		element = web_handler.find_element(By.TAG_NAME, "h1")
	# 		print(element.text)
	# except WebHandlerError as e:
	# 	print(f"Error: {str(e)}")

def main():
    #print("WebHandler main executed successfully!")

    try:
        with WebHandler() as web_handler:
            web_handler.navigate_to_url("http://example.com")
            h1 = web_handler.find_element(By.TAG_NAME, "h1")
            Printer.print(f'\nWebHandler main executed successfully!\nWebHandler Response: {h1.text}\n', color='green', style='bold')
    except WebHandlerError as e:
        print(f"Error: {str(e)}")

