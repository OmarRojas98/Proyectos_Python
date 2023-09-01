import serial
import matplotlib.pyplot as plt
import threading
import copy

# Configurar la conexión con el puerto serial
ser = serial.Serial("COM4", 9600)  # Reemplaza 'COM4' con el puerto COM correcto en tu sistema
ser.baudrate = 9600  # Configura la velocidad de transmisión (baudrate) según corresponda

# Listas para almacenar los datos del ADC y la temperatura
temperatures = []

# Función para tomar datos del puerto serial en un hilo
def read_serial_data():
    num_samples = 80
    samples = []

    while True:
        data_received = ser.readline().decode().strip()
        if data_received:
            voltage = float(data_received)
            temperature = 51.171 * voltage - 53.619
            samples.append(temperature)

            # Si se han tomado suficientes muestras, calcular el promedio y agregarlo a la lista de temperaturas
            if len(samples) == num_samples:
                avg_temperature = sum(samples) / num_samples
                temperatures.append(avg_temperature)
                samples = []  # Reiniciar la lista de muestras para el siguiente promedio
                print("Voltage:", voltage, "Average Temperature:", round(avg_temperature,1))

# Función para actualizar la gráfica en un hilo
def update_plot():
    plt.ion()  # Modo interactivo para actualizar la gráfica en tiempo real

    # Configurar la gráfica
    fig, ax = plt.subplots()
    line_temperature, = ax.plot([], [], label='Temperature (°C)')
    ax.set_xlabel('Muestras')
    ax.set_ylabel('Temperature (°C)')
    ax.legend()

    # Agregar texto para mostrar el valor actual de temperatura
    text_temperature = ax.text(0.02, 0.95, '', transform=ax.transAxes, fontsize=12, color='red')
    ax.set_ylim(0, 100)
    while True:
        # Hacer una copia de la lista de temperaturas para evitar modificaciones durante la actualización
        temperatures_copy = copy.copy(temperatures)
        x_data = range(len(temperatures_copy))

        # Actualizar la gráfica con los nuevos datos
        line_temperature.set_data(x_data, temperatures_copy)
        ax.relim()
        ax.autoscale_view()

        # Mostrar el valor actual de temperatura en el texto
        if temperatures_copy:
            current_temperature = temperatures_copy[-1]
            text_temperature.set_text(f'Current Temperature: {int(current_temperature)} °C')

        plt.pause(0.0125)  # Pausa para actualizar la gráfica y permitir que se muestre

try:
    # Crear los hilos para ejecutar las funciones en paralelo
    data_thread = threading.Thread(target=read_serial_data)
    plot_thread = threading.Thread(target=update_plot)

    # Iniciar los hilos
    data_thread.start()
    plot_thread.start()

    # Esperar a que ambos hilos finalicen (esto nunca ocurrirá debido a los bucles infinitos)
    data_thread.join()
    plot_thread.join()

except KeyboardInterrupt:
    print("Programa detenido por el usuario")

finally:
    # Cierra la conexión con el puerto serial al finalizar
    ser.close()




