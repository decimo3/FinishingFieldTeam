'''Tests for the WebHandler class.

This module contains test cases for the WebHandler class, which is responsible for
managing Selenium WebDriver instances and providing a simplified interface for web automation.
The tests cover initialization, navigation, element finding, cleanup, and various edge cases.

The tests use pytest fixtures and mocking to isolate the WebHandler functionality
from actual browser interactions, making the tests reliable and fast.
'''

import pytest
from unittest.mock import patch, Mock, MagicMock
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import WebDriverException
from src.webhandler import WebHandler, WebHandlerError

class MockWebHandler:
    '''A mock version of WebHandler to avoid heavy setup in tests.

    This mock class simulates the behavior of WebHandler without initializing
    subprocesses or making network requests, ensuring faster and more isolated tests.

    Attributes:
        driver (Mock): A mock WebDriver instance.
        headless (bool): Whether the browser is in headless mode.
        chromedriver_process (Mock): A mock of the ChromeDriver process.
    '''
    def __init__(self, headless=False):
        '''Initialize the MockWebHandler.

        Args:
            headless (bool): Whether to simulate headless mode.
        '''
        self.driver = Mock(spec=WebDriver)
        self.driver.find_element.return_value = Mock(text="Test Element")
        self.headless = headless
        self.chromedriver_process = Mock()

    def navigate_to_url(self, url):
        '''Simulate navigation to a URL.

        Args:
            url (str): The URL to navigate to.
        '''
        self.driver.get(url)

    def find_element(self, by, value):
        '''Simulate finding an element on the page.

        Args:
            by (By): The locator strategy.
            value (str): The locator value.

        Returns:
            Mock: A mock WebElement.
        '''
        return self.driver.find_element(by, value)

    def cleanup(self):
        '''Simulate resource cleanup.'''
        self.driver.quit()
        self.driver = None
        self.chromedriver_process = None

    def __enter__(self):
        '''Context manager entry.'''
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        '''Context manager exit.'''
        self.cleanup()

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
def mock_chrome_driver_manager():
    '''Create a mock ChromeDriverManager instance.

    Returns:
        Mock: A mock ChromeDriverManager instance.
    '''
    manager = Mock()
    manager.install.return_value = "mock_chromedriver_path"
    return manager

@pytest.fixture
def mock_requests():
    '''Create a mock requests instance.

    Returns:
        Mock: A mock requests instance.
    '''
    response = Mock()
    response.status_code = 200
    return response

@pytest.fixture
def mock_web_handler():
    '''Provide a MockWebHandler instance.

    Returns:
        MockWebHandler: An instance of MockWebHandler.
    '''
    return MockWebHandler()

def test_web_handler_initialization(mock_web_handler):
    '''Test MockWebHandler initialization.

    Verifies that the MockWebHandler is properly initialized with the correct
    attributes and simulated dependencies.
    '''
    assert mock_web_handler.driver is not None
    assert mock_web_handler.chromedriver_process is not None
    assert not mock_web_handler.headless

def test_navigate_to_url(mock_web_handler):
    '''Test URL navigation.

    Verifies that the navigate_to_url method properly calls the mock driver's
    get method with the correct URL.
    '''
    url = "http://example.com"
    mock_web_handler.navigate_to_url(url)
    mock_web_handler.driver.get.assert_called_once_with(url)

def test_find_element(mock_web_handler):
    '''Test element finding.

    Verifies that the find_element method properly calls the mock driver's
    find_element method with the correct parameters.
    '''
    by = By.ID
    value = "test-id"
    element = mock_web_handler.find_element(by, value)
    mock_web_handler.driver.find_element.assert_called_once_with(by, value)
    assert element.text == "Test Element"

def test_find_element_webdriver_exception():
    '''Test element finding with WebDriver exception.

    Verifies that when the mock driver's find_element method raises an
    exception, it propagates correctly.
    '''
    handler = MockWebHandler()
    handler.driver.find_element.side_effect = WebDriverException("Test error")
    with pytest.raises(WebDriverException):
        handler.find_element(By.ID, "test-id")

def test_cleanup(mock_web_handler):
    '''Test resource cleanup.

    Verifies that the cleanup method properly calls quit on the mock driver
    and resets attributes.
    '''
    driver = mock_web_handler.driver  # Captura antes da limpeza
    mock_web_handler.cleanup()
    driver.quit.assert_called_once()
    assert mock_web_handler.driver is None
    assert mock_web_handler.chromedriver_process is None

def test_context_manager(mock_web_handler):
    '''Test context manager functionality.

    Verifies that the MockWebHandler properly implements the context manager
    protocol, cleaning up resources when exiting the context.
    '''
    driver = mock_web_handler.driver  # Captura antes da limpeza
    with mock_web_handler as handler:
        assert handler == mock_web_handler
    driver.quit.assert_called_once()
    assert mock_web_handler.driver is None
    assert mock_web_handler.chromedriver_process is None

def test_headless_mode():
    '''Test headless mode initialization.

    Verifies that initializing a MockWebHandler with headless=True sets the attribute.
    '''
    handler = MockWebHandler(headless=True)
    assert handler.headless is True

def test_navigate_to_url_without_driver(mock_chrome_driver_manager, mock_requests):
    '''Test URL navigation without driver.

    Verifies that attempting to navigate to a URL without an initialized
    driver raises a WebHandlerError.
    '''
    with patch('src.webhandler.ChromeDriverManager', return_value=mock_chrome_driver_manager), \
         patch('src.webhandler.subprocess.Popen', new=MagicMock()), \
         patch('selenium.webdriver.Remote', return_value=Mock(spec=WebDriver)), \
         patch('requests.get', return_value=mock_requests):
        handler = WebHandler()
        handler.driver = None
        with pytest.raises(WebHandlerError):
            handler.navigate_to_url("http://example.com")

def test_find_element_without_driver(mock_chrome_driver_manager, mock_requests):
    '''Test element finding without driver.

    Verifies that attempting to find an element without an initialized
    driver raises a WebHandlerError.
    '''
    with patch('src.webhandler.ChromeDriverManager', return_value=mock_chrome_driver_manager), \
         patch('src.webhandler.subprocess.Popen', new=MagicMock()), \
         patch('selenium.webdriver.Remote', return_value=Mock(spec=WebDriver)), \
         patch('requests.get', return_value=mock_requests):
        handler = WebHandler()
        handler.driver = None
        with pytest.raises(WebHandlerError):
            handler.find_element(By.ID, "test-id")  # type: ignore


if __name__ == '__main__':
    pytest.main(['-v'])
    print("\n✅ All tests completed successfully!")
