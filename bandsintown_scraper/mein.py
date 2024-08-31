from dotenv import load_dotenv
import os
import pandas as pd

import time
import json

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.chrome.options import Options

def extraer_artistas(driver):
    div_texts = []
    hrefs = []

    load_more_button = driver.find_element(By.XPATH, "//div[@class = 'aM5QHbhlJjUYWcPVV0Am']")
    # print(f'Texto antes del While: {load_more_button.text}')
    
    while load_more_button.text=="Show More":

        load_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@class = 'aM5QHbhlJjUYWcPVV0Am']"))
                )
        # print(f'Texto en While: {load_more_button.text}')
        
        #print(i)
        load_more_button.click()
        time.sleep(2)

        div_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@class = "y780Kgtic5r7Cod_zQVq"]'))
        )
        div_texts = [div.text.replace("\nView Concerts", "") for div in div_elements]

        a_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//a[@class = "tlhOE0qLeWoH8o_cp5ZE"]'))
        )
        hrefs = [a.get_attribute('href') for a in a_elements]
        
        print(f'Num de artistas: {len(div_texts)}')

        # Verificar si hemos alcanzado el límite
        if load_more_button.text == "Show Less":
            print(f'Saliendo de Extraer_artistas...')
            load_more_button.click()
            break
        else:
            pass
        
    return div_texts, hrefs


# Cargar las variables de entorno
load_dotenv()
search_artist = os.getenv("search_artist")
path = os.getenv("path_driver")

# Configurar el servicio y las opciones del navegador
service = Service(executable_path=path)
options = Options()
# options.add_argument("--headless")
options.add_argument('--disable-gpu')  # Desactivar GPU, necesario para algunos sistemas
options.add_argument('--no-sandbox')  # Añadir sandbox (opcional, puede ser necesario en algunos entornos)
options.add_argument('--disable-dev-shm-usage')  # Solucionar problemas de recursos compartidos en contenedores
options.add_argument('start-maximized')  # Iniciar maximizado
options.add_argument('window-size=1920x1080')  # Tamaño de ventana (resolución)

# Inicializar el driver
driver = webdriver.Chrome(service=service, options=options)

# Abrir la URL
driver.get(search_artist)

time.sleep(2)
div_texts = []
a_texts =[]
div_elements_categorical = []

# Esperar a que los elementos estén presentes
try:
    div_elements_categorical = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@class = "rpqBan0EsClkP_Nsp47Q "]'))
        )
    for div in div_elements_categorical:
        
        try:
            driver.execute_script("window.scrollTo(0, 0);")
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@class="rpqBan0EsClkP_Nsp47Q "]'))
            )
            div.click()
            time.sleep(2)
            name_artists, href_artist = extraer_artistas(driver)
            div_texts.extend(name_artists)
            a_texts.extend(href_artist)
            print(f'Categoria: {div.text}  |  Total de artista: {len(div_texts)}')
            driver.execute_script("window.scrollTo(0, 0);")
            div.click()
            

        except ElementClickInterceptedException:
            print("Elemento no clicable, intentando de nuevo después de desplazarse...")
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)
            div.click()


    time.sleep(2)

    print("Guardando... Archivo")
    dic ={'Artista': div_texts,'link': a_texts}

    df = pd.DataFrame(dic)

    df_sin_duplicados = df.drop_duplicates()

    dic = df_sin_duplicados.to_dict(orient='list')

    #df_sin_duplicados.to_csv('Artista_limpio.json', orient='records', indent=4, force_ascii=False)
    with open('Artista_limpio.json', 'w', encoding='utf-8') as file:
        json.dump(dic, file, indent=4,ensure_ascii=False)


except TimeoutException:
    print("No se encontraron elementos div con la clase especificada.")
    
    


finally:
# Cerrar el driver de forma correcta
    if driver:
        driver.quit()




