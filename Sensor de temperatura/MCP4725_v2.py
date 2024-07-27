import machine
import time
import urequests

# Dirección del MCP4725
MCP4725_ADDR = 0x62

# Definir los pines SDA y SCL para el bus I2C
sda_pin = machine.Pin(0)  # Pin GPIO0 como SDA
scl_pin = machine.Pin(1)  # Pin GPIO1 como SCL

# Crear una instancia del bus I2C
i2c = machine.I2C(0, sda=sda_pin, scl=scl_pin)
# Configura tu API Key de ThingSpeak
API_KEY = "25DC21NQAU4RTUNE"

# URL del servidor ThingSpeak
URL = "https://thingspeak.com/channels/2226520/private_show"



def setup_wifi():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print("Conectando a WiFi...")
        sta_if.active(True)
        sta_if.connect("TU_RED_WIFI", "TU_CONTRASEÑA_WIFI")
        while not sta_if.isconnected():
            pass
    print("Conexión WiFi establecida")
    print("Dirección IP:", sta_if.ifconfig()[0])
    
# Función para enviar datos a ThingSpeak
def send_to_thingspeak(data):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = 'field1={}'.format(data)
    try:
        response = urequests.post(URL, data=data, headers=headers)
        print("Datos enviados a ThingSpeak. Respuesta:", response.text)
        response.close()
    except Exception as e:
        print("Error al enviar datos:", e)

# Escanear direcciones de dispositivos I2C
def scan_i2c():
    devices = i2c.scan()
    print("Direcciones de dispositivos I2C detectadas:")
    for device in devices:
        print(hex(device))

# Escribir un valor de tensión en el MCP4725
def write_dac_value(value):
    # Convertir el valor de voltaje a un valor adecuado para el MCP4725
    # El MCP4725 acepta un valor de 12 bits, por lo que se multiplica el voltaje
    # por 4095 (2^12 - 1) y se divide por el voltaje máximo del MCP4725 (3.3V)
    dac_value = int((value * 4095) / 3.281)
    
    print("Valor de DAC:", dac_value)

    # Escribir el valor en el MCP4725
    data = bytearray([(dac_value >> 8) & 0xFF, dac_value & 0xFF])
    i2c.writeto(MCP4725_ADDR, data)
    

# Función para configurar el valor por defecto del MCP4725
def set_default_dac_value(value):
    # Convertir el valor de voltaje a un valor adecuado para el MCP4725
    dac_value = int((value * 4095) / 3.281)

    # Escribir el valor en el MCP4725 con el bit "PD1" configurado como 1 para que sea el valor por defecto
    data = bytearray([(1 << 7) | (1 << 6) | ((dac_value >> 8) & 0xFF), dac_value & 0xFF])
    i2c.writeto(MCP4725_ADDR, data)

# Ejecutar la función de escaneo de direcciones
default_voltage = 2.5
set_default_dac_value(default_voltage)
scan_i2c()

# Bucle para ingresar continuamente nuevos valores de voltaje
while True:
    try:
        voltage = float(input("Ingresa el nuevo valor de voltaje (en V): "))
        write_dac_value(voltage)
        
        
    except ValueError:
        print("Entrada inválida. Ingresa un número válido.")
    
    time.sleep(1)  # Esperar 1 segundo antes de ingresar el siguiente valor
    
    except KeyboardInterrupt:
        print("Programa detenido por el usuario")
        break