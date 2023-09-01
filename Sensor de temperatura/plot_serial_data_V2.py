import serial
import matplotlib.pyplot as plt

# Configurar la conexión con el puerto serial
ser = serial.Serial('COM4', 9600)  # Reemplaza 'COM4' con el puerto COM correcto en tu sistema
ser.baudrate = 9600  # Configura la velocidad de transmisión (baudrate) según corresponda

# Listas para almacenar los datos del ADC y el voltaje
adc_values = []
voltages = []

# Función para actualizar la gráfica
def update_plot(i):
    if ser.in_waiting:
        data_received = ser.readline().decode().strip()
        adc_value, voltage = data_received.split(',')
        adc_values.append(int(adc_value))
        voltages.append(float(voltage))

        plt.cla()
        plt.plot(adc_values, label='ADC Value')
        plt.plot(voltages, label='Voltage (V)')
        plt.xlabel('Muestras')
        plt.ylabel('Valor del ADC / Voltaje (V)')
        plt.legend()
        plt.tight_layout()

# Configurar la gráfica
plt.ion()
fig = plt.figure()
ani = fig.canvas.new_timer(interval=1000)
ani.add_callback(update_plot)
ani.start()

# Mantener la gráfica abierta
plt.show()