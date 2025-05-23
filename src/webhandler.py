import os
from selenium.webdriver.remote.webdriver import WebDriver as Remote
from selenium.webdriver.remote.client_config import ClientConfig
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from constants import BASE_PATH, SERVICE_PORT, DEFAULT_TIMEOUT

class WebHandler:
	''' Class to handle web interactions using Selenium. '''
	service: Service = None
	driver: Remote
	service_url = "http://localhost:{}".format(SERVICE_PORT)
	data_folder = os.path.join(BASE_PATH, "www")
	def __init__(self, driver_path):
		# Set up the Service
		self.service = Service(driver_path)
		self.service.port = SERVICE_PORT
		self.service.log_path = None
		self.service.start()
		# Set up the Options
		self.options = Options()
		self.options.add_argument("--user-data-dir={}".format(self.data_folder))
		self.options.add_argument("--app={}".format(self.service_url))

		# Set up the ClientConfig
		self.client_config = ClientConfig(self.service_url)
		self.client_config.timeout = DEFAULT_TIMEOUT

		# Set up the WebDriver
		self.driver = Remote(
			command_executor = self.service_url,
			options = self.options,
			client_config = self.client_config
		)
	def __del__(self):
		if self.driver:
			self.driver.quit()
			self.driver = None
		if self.service:
			self.service.stop()
			self.service = None

	def navigate_to_url(self, url: str):
		if self.driver:
			self.driver.get(url)
		else:
			raise Exception("Driver not started. Call start_driver() first.")

	def find_element(self, by: By, value: str):
		if self.driver:
			return self.driver.find_element(by, value)
		else:
			raise Exception("Driver not started. Call start_driver() first.")
