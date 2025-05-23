''' Module for testing the WebHandler class. '''
import os
import pytest
from selenium.webdriver.common.by import By
from src.webhandler import WebHandler
from src.constants import BASE_PATH, SERVICE_PORT

@pytest.fixture
def web_handler():
	driver_path = os.path.join(BASE_PATH, "chromedriver-win64", "chromedriver.exe")
	handler = WebHandler(driver_path)
	yield handler
	del handler

def test_web_handler_initialization(web_handler):
	assert web_handler.service is not None
	assert web_handler.driver is not None
	assert web_handler.service_url == f"http://localhost:{SERVICE_PORT}"

def test_navigate_to_url(web_handler):
	test_url = "https://example.com/"
	web_handler.navigate_to_url(test_url)
	assert web_handler.driver.current_url == test_url

def test_find_element(web_handler):
	test_url = "https://example.com/"
	web_handler.navigate_to_url(test_url)
	element = web_handler.find_element(By.TAG_NAME, "h1")
	assert element is not None
	assert element.tag_name == "h1"
