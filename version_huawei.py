from netmiko import ConnectHandler
import re
import pandas as pd  # Para trabajar con archivos Excel

# Leer las IPs y descripciones desde el archivo 'listadoAR2240.txt'
with open(r'C:\Users\Desktop\listadoAR2240.txt', 'r') as file:
    device_list = file.read().splitlines()  # Divide las líneas en una lista

# Definir las credenciales de acceso (puedes adaptarlas si varían por dispositivo)
username = 'admin'
password = 'clave123'

# Lista para almacenar los resultados
device_data = []

# Función para conectarse a un equipo y obtener el número de serie del BarCode
def get_serial_number(device_ip, description):
    try:
        huawei = {
            'device_type': 'huawei_vrp',
            'ip': device_ip,
            'username': username,
            'password': password,
        }
        # Conectarse al equipo
        net_connect = ConnectHandler(**huawei)

        # Ejecutar el comando 'display elabel backplane'
        output = net_connect.send_command('display elabel backplane')

        # Buscar y extraer solo el número de serie (sin el texto 'BarCode=')
        serial_number = None
        for line in output.splitlines():
            if 'BarCode' in line:
                serial_number = line.split('=')[1].strip()  # Extraer solo el número después del '='

        # Cerrar la conexión
        net_connect.disconnect()

        if serial_number:
            print(f"{description}: {serial_number}")
            # Añadir a la lista de resultados
            device_data.append({'Dispositivo': description, 'Identificación': serial_number})
        else:
            print(f"{description}: No se encontró el número de serie.")
            device_data.append({'Dispositivo': description, 'Identificación': 'No encontrado'})

    except Exception as e:
        print(f"Error con el equipo {device_ip} ({description}): {str(e)}")
        device_data.append({'Dispositivo': description, 'Identificación': 'Error'})

# Iterar sobre la lista de dispositivos, extraer IPs y descripciones, y obtener el número de serie
for device in device_list:
    # Usamos regex para extraer la dirección IP (la primera secuencia de números y puntos)
    match = re.match(r"(\d{1,3}(?:\.\d{1,3}){3})\s+(.*)", device)
    if match:
        ip_address = match.group(1)  # Dirección IP
        description = match.group(2)  # Descripción del equipo
        get_serial_number(ip_address, description)
    else:
        print(f"No se pudo procesar la línea: {device}")

# Al finalizar, crear el DataFrame y exportar a un archivo Excel
df = pd.DataFrame(device_data)
df.to_excel(r'C:\Users\Desktop\dispositivos_identificacion.xlsx', index=False)

print("Archivo Excel creado exitosamente.")
