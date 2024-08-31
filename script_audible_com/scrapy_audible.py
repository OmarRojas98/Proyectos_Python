from selenium import webdriver
from selenium.webdriver.chrome.service import Service


class audible():

    def __init__(self, driver_path, base_url="https://www.audible.com/"):
        self.driver_path = driver_path
        self.base_url = base_url
        self.driver = self._initialize_driver()
    
    def _initialize_driver(self):
        service = Service(executable_path=self.driver_path)
        driver = webdriver.Chrome(service=service)
        return driver
    
    def open_page(self):
        self.driver.get(self.base_url)


