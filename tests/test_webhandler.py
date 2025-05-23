'''Tests for the WebHandler class.

This module contains test cases for the WebHandler class, which is responsible for
managing Selenium WebDriver instances and providing a simplified interface for web automation.
The tests cover initialization, navigation, element finding, cleanup, and various edge cases.

The tests use pytest fixtures and mocking to isolate the WebHandler functionality
from actual browser interactions, making the tests reliable and fast.
'''

import pytest
from unittest.mock import patch, Mock
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from src.webhandler import WebHandler, WebHandlerError

@pytest.fixture
def mock_driver():
	'''Create a mock WebDriver instance.
	
	Returns:
		Mock: A mock WebDriver instance.
	'''
	driver = Mock(spec=WebDriver)
	driver.find_element.return_value = Mock(text="Test Element")
	return driver

@pytest.fixture
def mock_service():
	'''Create a mock Service instance.
	
	Returns:
		Mock: A mock Service instance.
	'''
	return Mock(spec=Service)

@pytest.fixture
def web_handler(mock_driver, mock_service):
	'''Create a WebHandler instance with mocked dependencies.
	
	This fixture sets up a WebHandler with mocked WebDriver and Service instances,
	allowing for isolated testing of WebHandler functionality without actual browser
	interactions.
	
	Args:
		mock_driver: The mock WebDriver instance.
		mock_service: The mock Service instance.
		
	Returns:
		WebHandler: A WebHandler instance with mocked dependencies.
	'''
	with patch('src.webhandler.Service', return_value=mock_service), \
		 patch('src.webhandler.WebDriver', return_value=mock_driver):
		handler = WebHandler()
		handler.driver = mock_driver
		handler.service = mock_service
		return handler

def test_web_handler_initialization(web_handler, mock_driver, mock_service):
	'''Test WebHandler initialization.
	
	Verifies that the WebHandler is properly initialized with the correct
	dependencies and configuration.
	'''
	assert web_handler.driver == mock_driver
	assert web_handler.service == mock_service
	assert not web_handler.headless

def test_navigate_to_url(web_handler, mock_driver):
	'''Test URL navigation.
	
	Verifies that the navigate_to_url method properly calls the WebDriver's
	get method with the correct URL.
	'''
	url = "http://example.com"
	web_handler.navigate_to_url(url)
	mock_driver.get.assert_called_once_with(url)

def test_navigate_to_url_without_driver():
	'''Test URL navigation without driver.
	
	Verifies that attempting to navigate to a URL without an initialized
	driver raises a WebHandlerError.
	'''
	with patch('src.webhandler.Service'), \
		 patch('src.webhandler.WebDriver'):
		handler = WebHandler()
		handler.driver = None
		with pytest.raises(WebHandlerError):
			handler.navigate_to_url("http://example.com")

def test_find_element(web_handler, mock_driver):
	'''Test element finding.
	
	Verifies that the find_element method properly calls the WebDriver's
	find_element method with the correct parameters.
	'''
	by = By.ID
	value = "test-id"
	element = web_handler.find_element(by, value)
	mock_driver.find_element.assert_called_once_with(by, value)
	assert element.text == "Test Element"

def test_find_element_without_driver():
	'''Test element finding without driver.
	
	Verifies that attempting to find an element without an initialized
	driver raises a WebHandlerError.
	'''
	with patch('src.webhandler.Service'), \
		 patch('src.webhandler.WebDriver'):
		handler = WebHandler()
		handler.driver = None
		with pytest.raises(WebHandlerError):
			handler.find_element(By.ID, "test-id")

def test_find_element_webdriver_exception(web_handler, mock_driver):
	'''Test element finding with WebDriver exception.
	
	Verifies that when the WebDriver's find_element method raises an
	exception, it is properly wrapped in a WebHandlerError.
	'''
	mock_driver.find_element.side_effect = WebDriverException("Test error")
	with pytest.raises(WebHandlerError):
		web_handler.find_element(By.ID, "test-id")

def test_cleanup(web_handler, mock_driver, mock_service):
	'''Test resource cleanup.
	
	Verifies that the cleanup method properly calls quit on the WebDriver
	and stop on the Service.
	'''
	web_handler.cleanup()
	mock_driver.quit.assert_called_once()
	mock_service.stop.assert_called_once()
	assert web_handler.driver is None
	assert web_handler.service is None

def test_context_manager(web_handler, mock_driver, mock_service):
	'''Test context manager functionality.
	
	Verifies that the WebHandler properly implements the context manager
	protocol, cleaning up resources when exiting the context.
	'''
	with web_handler as handler:
		assert handler == web_handler
	mock_driver.quit.assert_called_once()
	mock_service.stop.assert_called_once()

def test_headless_mode():
	'''Test headless mode initialization.
	
	Verifies that when initializing a WebHandler with headless=True,
	the headless option is properly added to the WebDriver options.
	'''
	with patch('src.webhandler.Service'), \
		 patch('src.webhandler.WebDriver') as mock_driver_class:
		handler = WebHandler(headless=True)
		mock_driver_class.assert_called_once()
		args, kwargs = mock_driver_class.call_args
		assert "--headless=new" in kwargs['options'].arguments
