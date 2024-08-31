from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import time
import keyboard



class scrap():

    def __init__(self, driver_path, base_url="https://simo.cnsc.gov.co/"):
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
        driver = webdriver.Chrome(service=service)
        return driver
    
    def open_driver(self):
        try:
            self.driver.get(self.base_url)
            # Esperar a que algún elemento crucial esté presente, incrementando el tiempo de espera
            WebDriverWait(self.driver, 120).until(
                EC.presence_of_element_located((By.XPATH, "//body"))
            )
        except TimeoutException:
            print("Timed out waiting for page to load")
            self.quit_driver()
       

    def quit_driver(self):
        self.driver.quit()
        exit()


    def fill_input(self, input_xpath, text):
        # Espera hasta que el elemento input esté presente y sea interactivo
        input_element = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, input_xpath))
        )
        print(input_element)
        input_element.clear()
        input_element.send_keys(text)

    def clickbutton(self, button_xpath):
        # Espera un poco para asegurarse de que el elemento esté presente
        button_element = WebDriverWait(self.driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, button_xpath))
        )
        button_element.click()

    def wait_for_escape(self):
        # Espera indefinidamente hasta que se presione la tecla "Esc"
        print("Presiona 'Esc' para cerrar el navegador.")
        while True:
            if keyboard.is_pressed('esc'):
                self.quit_driver()
                break
            time.sleep(0.1)