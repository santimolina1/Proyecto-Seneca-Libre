import pandas as pd
import requests

# Cargar datos relevantes
clients = pd.read_csv('case_4_multi_product\Clients.csv')  # Ubicaciones de los clientes
depots = pd.read_csv('case_4_multi_product\Depots.csv')    # Ubicaciones de los depósitos
vehicles = pd.read_csv('case_4_multi_product\Vehicles.csv')  # Parámetros de los vehículos
ubicaciones = pd.concat([clients[['Longitude', 'Latitude']], depots[['Longitude', 'Latitude']]])


def obtener_matrices_osrm(ubicaciones):
    """
    Obtiene matrices de distancias y tiempos utilizando la API de OSRM.

    Args:
        ubicaciones (pd.DataFrame): DataFrame con las ubicaciones (Longitude, Latitude).

    Returns:
        tuple: Dos diccionarios (distancias, tiempos) con las matrices generadas.
    """
    # Formatear las ubicaciones para la API
    result = ';'.join(f"{row['Longitude']},{row['Latitude']}" for _, row in ubicaciones.iterrows())
    
    # URL para la API de OSRM
    url = f'http://router.project-osrm.org/table/v1/driving/{result}?annotations=distance,duration'
    response = requests.get(url)

    # Verificar si la solicitud fue exitosa
    if response.status_code == 200:
        data = response.json()
        distancias = data['distances']
        tiempos = data['durations']

        # Convertir matrices a diccionarios
        distancias_dict = {
            (i, j): distancias[i][j]
            for i in range(len(ubicaciones))
            for j in range(len(ubicaciones))
        }
        tiempos_dict = {
            (i, j): tiempos[i][j]
            for i in range(len(ubicaciones))
            for j in range(len(ubicaciones))
        }

        return distancias_dict, tiempos_dict
    else:
        raise Exception(f"Error en la solicitud OSRM: {response.status_code}, {response.text}")

# Supongamos que `ubicaciones` ya contiene las coordenadas
# Cargar datos relevantes
  # Ubicaciones de los depósitos

# Combinar clientes y depósitos para obtener todas las ubicaciones
ubicaciones = pd.concat([clients[['Longitude', 'Latitude']], depots[['Longitude', 'Latitude']]])

# Obtener matrices de distancias y tiempos
distancias, tiempos = obtener_matrices_osrm(ubicaciones)

# Mostrar todas las matrices
print("Matriz de Distancias (completa):")
for key, value in distancias.items():
    print(f"{key}: {value}")

print("\nMatriz de Tiempos (completa):")
for key, value in tiempos.items():
    print(f"{key}: {value}")

# Guardar las matrices en archivos CSV
distancias_df = pd.DataFrame.from_dict(distancias, orient='index', columns=['Distancia']).reset_index()
distancias_df[['Desde', 'Hacia']] = pd.DataFrame(distancias_df['index'].tolist(), index=distancias_df.index)
distancias_df = distancias_df.drop(columns=['index'])
distancias_df.to_csv('distancias4.csv', index=False)

tiempos_df = pd.DataFrame.from_dict(tiempos, orient='index', columns=['Tiempo']).reset_index()
tiempos_df[['Desde', 'Hacia']] = pd.DataFrame(tiempos_df['index'].tolist(), index=tiempos_df.index)
tiempos_df = tiempos_df.drop(columns=['index'])
tiempos_df.to_csv('tiempos4.csv', index=False)

print("\nMatrices guardadas en 'distancias.csv' y 'tiempos.csv'.")
