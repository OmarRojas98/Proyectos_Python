import machine
import time
import urequests
import network
import json

# Dirección del MCP4725
MCP4725_ADDR = 0x62

# Definir el pin ADC en el que se medirá el voltaje
adc_pin = machine.ADC(26)  # Puedes cambiar 26 por GP27, GP28 o GP29 si lo deseas.

# Definir los pines SDA y SCL para el bus I2C
sda_pin = machine.Pin(0)  # Pin GPIO0 como SDA
scl_pin = machine.Pin(1)  # Pin GPIO1 como SCL

# Crear una instancia del bus I2C para el MCP4725
i2c_dac = machine.I2C(0, sda=sda_pin, scl=scl_pin)

# Conectar a la red Wi-Fi
def connect_to_wifi(ssid, password):
    station = network.WLAN(network.STA_IF)
    if not station.isconnected():
        print("Conectando a la red Wi-Fi...")
        station.active(True)
        station.connect(ssid, password)
        while not station.isconnected():
            pass
    print("Conexión Wi-Fi establecida.")
    print("Dirección IP:", station.ifconfig()[0])

# Escribir un valor de tensión en el MCP4725
def write_dac_value(value):
    # Convertir el valor de voltaje a un valor adecuado para el MCP4725
    # El MCP4725 acepta un valor de 12 bits, por lo que se multiplica el voltaje
    # por 4095 (2^12 - 1) y se divide por el voltaje máximo del MCP4725 (3.3V)
    dac_value = int((value * 4095) / 3.28)

    # Escribir el valor en el MCP4725
    data = bytearray([(dac_value >> 8) & 0xFF, dac_value & 0xFF])
    i2c_dac.writeto(MCP4725_ADDR, data)

# Función para configurar el valor por defecto del MCP4725
def set_default_dac_value(value):
    # Convertir el valor de voltaje a un valor adecuado para el MCP4725
    dac_value = int((value * 4095) / 3.28)

    # Escribir el valor en el MCP4725 con el bit "PD1" configurado como 0 para que sea el valor por defecto
    data = bytearray([0x60, (dac_value >> 8) & 0xFF, dac_value & 0xFF])
    i2c_dac.writeto(MCP4725_ADDR, data)

# Función para enviar datos a ThingSpeak
def send_to_thingspeak(data):
    url = "https://api.thingspeak.com/update?api_key=25DC21NQAU4RTUNE&field1="
    try:
        response = urequests.get(url+str(data))
        print("Datos enviados a ThingSpeak. Respuesta:", response.text)
        response.close()
    except Exception as e:
        print("Error al enviar datos:", e)
        
# Función para enviar datos a Firebase
def send_to_firebase(data):
    url = "https://sensortempv1-default-rtdb.firebaseio.com/sensor.json"  # Reemplaza con la URL correcta de tu proyecto y nodo en Firebase
    headers = {'Content-Type': 'application/json'}
    try:
        response = urequests.put(url, data=json.dumps(data), headers=headers)
        print("Datos enviados a Firebase. Respuesta:", response.text)
        response.close()
    except Exception as e:
        print("Error al enviar datos:", e)

# Conectar a la red Wi-Fi
wifi_ssid = "CLARO_VASQUEZ"
wifi_password = "Hijos_112029"
connect_to_wifi(wifi_ssid, wifi_password)

# Ejecutar la función de escaneo de direcciones
print("Direcciones de dispositivos I2C para el MCP4725:")
print([hex(addr) for addr in i2c_dac.scan()])

# Configurar el valor por defecto del MCP4725 (por ejemplo, 2.5V)
default_voltage = 2.5
set_default_dac_value(default_voltage)

# Función para medir el voltaje analógico desde el pin ADC
def measure_voltage():
    # Leer el valor analógico del pin ADC
    analog_value = adc_pin.read_u16()
    voltage = analog_value * 3.3 / 65535.0
    return voltage

# Bucle infinito para medir y enviar datos a ThingSpeak
try:
    while True:
        write_dac_value(default_voltage)
        # Leer el voltaje medido desde el pin ADC
        measured_voltage = measure_voltage()
        print("Voltaje medido:", measured_voltage, "V")
        # Enviar el valor a ThingSpeak
        #send_to_thingspeak(measured_voltage)
        send_to_firebase(measured_voltage)
        # Esperar un tiempo antes de volver a medir y enviar datos
        time.sleep(1)
except KeyboardInterrupt:
    print("Programa detenido por el usuario")
