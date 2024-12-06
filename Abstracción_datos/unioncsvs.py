import os
import pandas as pd

# Ruta donde se encuentran los archivos CSV
ruta_csv = 'case_4_costs_vehicles'

# Crear una lista para almacenar los datos combinados
dataframes = []

# Leer todos los archivos CSV de la carpeta
for archivo in os.listdir(ruta_csv):
    if archivo.endswith('.csv'):  # Filtrar solo archivos CSV
        ruta_archivo = os.path.join(ruta_csv, archivo)
        df = pd.read_csv(ruta_archivo)
        dataframes.append(df)

# Combinar todos los DataFrames en uno solo
df_combinado = pd.concat(dataframes, ignore_index=True)

# Guardar el archivo combinado en un nuevo CSV
ruta_salida = os.path.join(ruta_csv, 'costos_operativos_combinados4.csv')
df_combinado.to_csv(ruta_salida, index=False)

print(f"Archivos combinados y guardados en: {ruta_salida}")
