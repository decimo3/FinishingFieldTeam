'''Module to handle web interactions using Selenium.

This module provides a high-level interface for web automation using Selenium WebDriver.
It manages the lifecycle of the WebDriver instance, handles browser configuration,
and provides simplified methods for common web interactions.

The module includes:
- WebHandler class for managing browser sessions
- Error handling through WebHandlerError
- Resource management through context manager interface
- Configuration management for Chrome browser
'''

from typing import Optional, Any, Union
from urllib.parse import ParseResult as URL
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from src.constants import (
	SERVICE_PORT, DEFAULT_TIMEOUT, DEFAULT_WINDOW_SIZE,
	CHROME_DATA_DIR
)

class WebHandlerError(Exception):
	'''Base exception for WebHandler errors.
	
	This exception is raised when there are issues with:
	- WebDriver initialization
	- Browser navigation
	- Element finding
	- Resource cleanup
	'''

class WebHandler:
	'''Class to handle web interactions using Selenium.
	
	This class provides a simplified interface for web automation tasks using
	Selenium WebDriver. It manages the browser session lifecycle and provides
	methods for common web interactions.
	
	The class implements the context manager protocol for proper resource
	management and cleanup.
	
	Attributes:
		service (Optional[Service]): The Selenium Service instance.
		driver (Optional[WebDriver]): The Selenium WebDriver instance.
		headless (bool): Whether the browser runs in headless mode.
		options (Options): Chrome browser options.
	'''
	
	def __init__(self, headless: bool = False):
		'''Initialize the WebHandler.
		
		Sets up the Chrome WebDriver with the specified configuration.
		Initializes the service, options, and WebDriver instance.
		
		Args:
			headless (bool): Whether to run Chrome in headless mode.
				Defaults to False.
				
		Raises:
			WebHandlerError: If WebDriver initialization fails.
		'''
		self.service: Optional[Service] = None
		self.driver: Optional[WebDriver] = None
		self.headless = headless
		self._setup_driver()

	def _setup_driver(self) -> None:
		'''Set up the Chrome WebDriver with proper configuration.
		
		This method:
		1. Initializes the ChromeDriver service
		2. Configures Chrome options
		3. Creates the WebDriver instance
		
		Raises:
			WebHandlerError: If any step of the setup process fails.
		'''
		try:
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

			# Set up the Service with ChromeDriverManager
			self.service = Service(ChromeDriverManager().install())

			# Set up the WebDriver
			self.driver = WebDriver(
				service=self.service,
				options=self.options
			)
		except Exception as e:
			self.cleanup()
			raise WebHandlerError(f"Failed to initialize WebDriver: {str(e)}") from e

	def cleanup(self) -> None:
		'''Clean up resources.
		
		Safely stops the WebDriver and Service instances, handling any
		exceptions that might occur during cleanup. Sets both instances
		to None after cleanup.
		'''
		if self.driver:
			try:
				self.driver.quit()
			except WebDriverException:
				pass
			self.driver = None
		if self.service:
			try:
				self.service.stop()
			except WebDriverException:
				pass
			self.service = None

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
		'''
		self.cleanup()

	def navigate_to_url(self, url: Union[str, URL]) -> None:
		'''Navigate to the specified URL.
		
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

if __name__ == "__main__":
	# Example usage
	try:
		with WebHandler() as web_handler:
			web_handler.navigate_to_url("http://example.com")
			element = web_handler.find_element(By.TAG_NAME, "h1")
			print(element.text)
	except WebHandlerError as e:
		print(f"Error: {str(e)}")
