from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import logging

# Configuración del log
logging.basicConfig(level=logging.INFO)

class Scraper:
    def __init__(self, driver_path, base_url):
        self.driver_path = driver_path
        self.base_url = base_url
        self.driver = self._initialize_driver()
    
    def _initialize_driver(self):
        service = Service(executable_path=self.driver_path)
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-extensions")
        options.add_argument("--profile-directory=Default")
        options.add_argument("--incognito")
        options.add_argument("--disable-plugins-discovery")
        options.add_argument("--start-maximized")
        options.add_argument("--ignore-certificate-errors")  # Ignorar errores de certificado SSL
        options.add_argument("--allow-insecure-localhost")   # Permitir conexiones inseguras (para pruebas locales)
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    
    def open_page(self):
        try:
            logging.info(f"Opening page: {self.base_url}")
            self.driver.get(self.base_url)
            WebDriverWait(self.driver, 120).until(
                EC.presence_of_element_located((By.XPATH, "//body"))
            )
            logging.info("Page loaded successfully")
        except TimeoutException:
            logging.error("Timed out waiting for page to load")
            # No cerrar el driver aquí para permitir depuración
        except Exception as e:
            logging.error(f"An error occurred: {e}")
    
    def close_driver(self):
        if self.driver:
            self.driver.quit()
    

    def click_button_by_xpath(self, button_xpath):
        try:
            button_element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, button_xpath))
            )
            button_element.click()
        except TimeoutException:
            print(f"Button with xpath {button_xpath} not found or not clickable.")


    def fill_input(self, input_xpath, text):
        # Espera hasta que el elemento input esté presente y sea interactivo
        input_element = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, input_xpath))
        )
        input_element.clear()
        input_element.send_keys(text)


    def buscar(self):
        artists = self.driver.find_elements(By.XPATH, '//div[@class = "y780Kgtic5r7Cod_zQVq"]')
        # Extraer y print el texto de cada elemento
        artist_texts = [artist.text for artist in artists]
        
        return artist_texts
        