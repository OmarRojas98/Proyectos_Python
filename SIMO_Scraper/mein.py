from scraper import scrap

from dotenv import load_dotenv
import os
import keyboard


load_dotenv()
username = os.getenv("user")
password = os.getenv("password")
path = path = r'C:\Users\OMAR ROJAS\OneDrive\Documentos\Proyectos_Python\SIMO_Scraper\Chrome_Driver\chromedriver.exe'

def on_esc_key():
    simo.quit_driver()
    print("Driver closed due to 'Esc' key press")
    # Opcionalmente, puedes salir del programa
    exit()




if __name__ == "__main__":
    simo = scrap(driver_path=path)
    simo.open_driver()
    simo.fill_input("//input[@name = 'username']", username )
    simo.fill_input("//input[@name = 'password']", password )
    simo.clickbutton("//input[@id = 'dijit_form_Button_8_label_button_simo' ]")
    simo.wait_for_escape()


    # Asigna la función on_esc_key a la tecla 'esc'
    keyboard.add_hotkey('esc', on_esc_key)

    # Mantén el programa corriendo para detectar la tecla 'esc'
    keyboard.wait('esc')


