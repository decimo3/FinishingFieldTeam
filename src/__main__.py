import os
from src.webhandler import WebHandler
from selenium.webdriver.common.by import By

if __name__ == "__main__":
	# Example usage
	web_handler = WebHandler()
	web_handler.navigate_to_url("http://example.com")
	element = web_handler.find_element(By.TAG_NAME, "h1")
	print(element.text)
	del web_handler
