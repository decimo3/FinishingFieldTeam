import os
from src.constants import BASE_PATH
from src.webhandler import WebHandler
from selenium.webdriver.common.by import By

if __name__ == "__main__":
	# Example usage
	driver_path = os.path.join(BASE_PATH, "chromedriver-win64", "chromedriver.exe")
	web_handler = WebHandler(driver_path)
	web_handler.navigate_to_url("http://example.com")
	element = web_handler.find_element(By.TAG_NAME, "h1")
	print(element.text)
	del web_handler
