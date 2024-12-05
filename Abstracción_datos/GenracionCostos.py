import pandas as pd

# Datos ya cargados
vehicles = pd.read_csv('case_4_multi_product\Vehicles.csv')  # Vehículos
vehicles['ID'] = ['V' + str(i + 1) for i in range(len(vehicles))]  # Generar IDs para vehículos
distancias = pd.read_csv('Matrices/distancias4.csv')  # Matriz de distancias
tiempos = pd.read_csv('Matrices/tiempos4.csv')  # Matriz de tiempos

costos_km = {
    'Gas Car': 5000,
    'drone': 500,
    'EV': 4000
}

# Time Rate [COP/min]
costos_minuto = {
    'Gas Car': 500,
    'drone': 500,
    'EV': 500
}

# Daily Maintenance [COP/day]
costos_mantenimiento = {
    'Gas Car': 30000,
    'drone': 3000,
    'EV': 21000
}

# Recharge/Fuel Cost [COP/(gal or kWh)]
costos_recarga = {
    'Gas Car': 16000,
    'drone': 220.73,
    'EV': 0  # Asumimos que no tiene costo de recarga
}

# Recharge/Fuel Time [min/10% charge]
tiempo_recarga = {
    'Gas Car': 0.1,
    'drone': 2,
    'EV': 0  # Asumimos que no necesita recarga
}

# Gas Efficiency [km/gal]
eficiencia_combustible = {
    'Gas Car': 10,
    'drone': 0,  # No aplica
    'EV': 0  # No aplica
}

# Electricity Efficiency [kWh/km]
eficiencia_electrica = {
    'Gas Car': 0,  # No aplica
    'drone': 0.15,
    'EV': 0.15
}

# Cálculo de costos de operación
def calcular_costos_operativos(distancias, tiempos, vehicles, costos_km, costos_minuto):
    """
    Calcula los costos operativos (por distancia y tiempo) para cada ruta y vehículo.
    """
    costos_operativos = {}  # Diccionario para almacenar los costos

    # Iterar sobre cada vehículo
    for _, vehicle in vehicles.iterrows():
        vehiculo_id = vehicle['ID']
        tipo_vehiculo = vehicle['VehicleType']

        # Obtener costos específicos del tipo de vehículo
        c_km = costos_km[tipo_vehiculo]
        c_min = costos_minuto[tipo_vehiculo]

        # Calcular costos operativos para cada ruta
        costos_operativos[vehiculo_id] = {
            (row['Desde'], row['Hacia']): c_km * row['Distancia']/1000 + c_min * row['Tiempo']/60
            for _, row in distancias.merge(tiempos, on=['Desde', 'Hacia']).iterrows()
        }

    return costos_operativos

# Calcular costos operativos
costos_operativos = calcular_costos_operativos(
    distancias=distancias.rename(columns={"Tiempo": "Tiempo", "Desde": "Desde", "Hacia": "Hacia", "Distancia": "Distancia"}),
    tiempos=tiempos.rename(columns={"Tiempo": "Tiempo", "Desde": "Desde", "Hacia": "Hacia"}),
    vehicles=vehicles,
    costos_km=costos_km,
    costos_minuto=costos_minuto
)

# Mostrar resultados para un ejemplo
print("Costos Operativos (ejemplo para el primer vehículo):")
primer_vehiculo = vehicles['ID'].iloc[0]
for (desde, hacia), costo in list(costos_operativos[primer_vehiculo].items())[:10]:
    print(f"Ruta ({desde} -> {hacia}): Costo = {costo:.2f} COP")

# Guardar los costos en un archivo CSV para cada vehículo
for vehiculo, costos in costos_operativos.items():
    costos_df = pd.DataFrame([
        {'Vehiculo': vehiculo, 'Desde': desde, 'Hacia': hacia, 'Costo': costo}
        for (desde, hacia), costo in costos.items()
    ])
    costos_df.to_csv(f'costos_operativos_{vehiculo}.csv', index=False)

print("\nCostos operativos guardados en archivos CSV por vehículo.")
