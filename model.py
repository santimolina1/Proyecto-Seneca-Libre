from pyomo.environ import * 

import pandas as pd

# Cambiar las rutas de los archivos
clients = pd.read_csv(r'case_1_base/Clients.csv')  # Clientes
depots = pd.read_csv(r'case_1_base/Depots.csv')    # Depósitos
distancias = pd.read_csv(r'Matrices/distancias1.csv')  # Matriz de distancias
tiempos = pd.read_csv(r'Matrices/tiempos1.csv')        # Matriz de tiempos
vehicles = pd.read_csv(r'case_1_base/Vehicles.csv')    # Vehículos
costos_operativos = pd.read_csv(r'case_1_costs_vehicules\costos_operativos_combinados1.csv')   # Costos Operativos 

# Freight Rate [COP/km]
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
    'V1': 30000,
    'V2': 30000,
    'V3': 30000,
    'V4': 30000,
    'V5': 21000,
    'V6': 21000,
    'V7': 21000,
    'V8': 21000,
    'V9': 21000,
    'V10': 3000,
    'V11': 3000,
    'V12': 3000,
}

# Recharge/Fuel Cost [COP/(gal or kWh)]
costos_recarga = {
    'V1': 16000,
    'V2': 16000,
    'V3': 16000,
    'V4': 16000,
    'V5': 0,
    'V6': 0,
    'V7': 0,
    'V8': 0,
    'V9': 0,
    'V10': 220.73,
    'V11': 220.73,
    'V12': 220.73,
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


vehicles['ID'] = ['V' + str(i+1) for i in range(len(vehicles))]

# Crear conjuntos
distancias_dict = {(int(row["Desde"]+1), int(row["Hacia"]+1)): row["Distancia"] for _, row in distancias.iterrows()}


clientes = clients['LocationID'].tolist()  # IDs de los clientes
centros = depots['LocationID'].tolist()   # IDs de los depósitos
vehiculos = vehicles['ID'].tolist()  # IDs de los vehículos
productos = ['Product']  # Definimos tipos de productos (puedes ajustar según el problema)
nodos = centros + clientes  # Todos los nodos (clientes + depósitos)
clients.columns = clients.columns.str.strip()
depots.columns = depots.columns.str.strip()

# Crear parámetros
# 1. Demandas de clientes por producto (puede venir de Clients.csv o ser constante)
demandas_clients = {(row['LocationID'], p): row['Product'] for _, row in clients.iterrows() for p in productos}
demanda_centros = {
    (row['LocationID'], p): 0
    for _, row in depots.iterrows()
    for p in productos
}
demandas = {**demandas_clients, **demanda_centros}



# 2. Capacidades de los vehículos (Vehicles.csv)
capacidad_vehiculo = {row['ID']: row['Capacity'] for _, row in vehicles.iterrows()}

# 3. Rango máximo de los vehículos (Vehicles.csv)
rango_vehiculo = {row['ID']: row['Range'] for _, row in vehicles.iterrows()}

# 4. Costo operativo 
costos_operativos_dict = {(row['Vehiculo'], row['Desde'], row['Hacia']): row['Costo'] 
                          for _, row in costos_operativos.iterrows()}

# 5. Costos de mantenimiento y recarga (Vehicles.csv)   
#costos_mantenimiento = {row['ID']: row['Costo_Mantenimiento'] for _, row in vehicles.iterrows()}
#costos_recarga = {row['ID']: row['Costo_Recarga'] for _, row in vehicles.iterrows()}

# 6. Capacidades de los centros de distribución (Depots.csv)
#capacidades_centro = {(row['DepotID'], p): row[f'Capacidad_{p}'] for _, row in depots.iterrows() for p in productos}

# 7. Distancias y tiempos (distancias1.csv y tiempos1.csv)
# Convertir archivos CSV a diccionarios

tiempos_dict = {(row['Desde'], row['Hacia']): row['Tiempo'] for _, row in tiempos.iterrows()}

# Validar dimensiones
print(f"Clientes: {len(clientes)}, Centros: {len(centros)}, Vehículos: {len(vehiculos)}, Nodos: {len(nodos)}")


class VRPModel:
    def __init__(self, clientes, centros, vehiculos, productos, distancias_dict, tiempos, demandas, capacidad_vehiculo, rango_vehiculo, costos_operativos_dict, costos_mantenimiento, costos_recarga):
        """
        Inicializar parámetros del modelo VRP.
        """
        # Conjuntos y parámetros
        self.clientes = clientes
        self.centros = centros
        self.vehiculos = vehiculos
        self.productos = productos
        self.nodos = clientes + centros
        self.distancias_dict = distancias_dict
        self.tiempos = tiempos
        self.demandas = demandas
        self.capacidad_vehiculo = capacidad_vehiculo
        self.rango_vehiculo = rango_vehiculo
        self.costos_operativos_dict= costos_operativos_dict
        self.costos_mantenimiento = costos_mantenimiento
        self.costos_recarga = costos_recarga

        print(self.clientes)
        print(self.centros)
        
        # Crear modelo Pyomo
        self.model = ConcreteModel()

    def build_model(self):
        """
        Construir el modelo de optimización.
        """
        model = self.model

        # Sets
        model.C = Set(initialize=self.clientes)
        model.D = Set(initialize=self.centros)
        model.V = Set(initialize=self.vehiculos)
        model.P = Set(initialize=self.productos)
        model.N = Set(initialize=self.nodos) 

        # Variables
        model.x = Var(model.N, model.N, model.V, within=Binary)  # Ruta del vehículo
       # model.z = Var(model.V, within=Binary)  # Activación del vehículo
        #model.q = Var(model.N, model.P, model.V, within=NonNegativeReals)  # Carga transportada

        # Función objetivo: Minimizar costos
        def obj_expression(model):
            return sum(
                # Costos por distancia
                model.x[i, j, v] * costos_operativos_dict[(v, i, j)]
                for v in model.V for i in model.N for j in model.N if (v, i, j) in costos_operativos_dict)
            #  + sum(
            #     # Costos de mantenimiento
            #     model.z[v] * self.costos_mantenimiento[v] for v in model.V)
            #  + sum(
            #     # Costos de recarga
            #     self.costos_recarga[v] * model.z[v] for v in model.V
            # )
        model.obj = Objective(rule=obj_expression, sense=minimize)

        # Restricciones

        # 1. Cada cliente debe ser visitado exactamente una vez
        def restriccion_visita_unica(model, i):
            return sum(model.x[i, j, v] for j in model.N for v in model.V if i != j) == 1
        model.restriccion_visita_unica = Constraint(model.C, rule=restriccion_visita_unica)

        # 2. Conservación del flujo en los nodos
        def restriccion_flujo(model, i, v):
            return sum(model.x[i, j, v] for j in model.N if i != j) == sum(model.x[j, i, v] for j in model.N if i != j)
        model.restriccion_flujo = Constraint(model.N, model.V, rule=restriccion_flujo)

        # 3. Capacidad de los vehículos
        # def restriccion_capacidad_vehiculo(model, v):
        #     return sum(model.q[i, p, v] for i in model.C for p in model.P) <= self.capacidad_vehiculo[v]
        # model.restriccion_capacidad_vehiculo = Constraint(model.V, rule=restriccion_capacidad_vehiculo)

        # # 4. Carga transportada debe respetar las demandas
        # def restriccion_demanda(model, i, p):
        #     return sum(model.q[i, p, v] for v in model.V) == self.demandas[i, p]
        # model.restriccion_demanda = Constraint(model.C, model.P, rule=restriccion_demanda)

        # 5. Capacidad de los centros de distribución
        # def restriccion_capacidad_centro(model, k, p):
        #     return sum(model.q[i, p, v] for i in model.C for v in model.V) <= self.capacidades_centro[k, p]
        # model.restriccion_capacidad_centro = Constraint(model.D, model.P, rule=restriccion_capacidad_centro)

        # 6. Límite de rango de los vehículos
        # def restriccion_rango_vehiculo(model, v):
        #     return sum(self.distancias_dict[(i, j)] * model.x[i, j, v] for i in model.N for j in model.N if i != j) <= self.rango_vehiculo[v]
        # model.restriccion_rango_vehiculo = Constraint(model.V, rule=restriccion_rango_vehiculo)

        # 7. Restricción de activación de vehículos
        # M= len(self.nodos)
        # def restriccion_activacion_vehiculo(model, v):
        #     return sum(model.x[i, j, v] for i in model.N for j in model.N if i != j) <= M * model.z[v]
        # model.restriccion_activacion_vehiculo = Constraint(model.V, rule=restriccion_activacion_vehiculo)

        # 8. Eliminación de subtours (MTZ)
        model.u = Var(model.N, model.V, within=NonNegativeReals)
        def restriccion_subtours(model, i, j, v):
            if i != j:
                return model.u[i, v] - model.u[j, v] + len(model.N) * model.x[i, j, v] <= len(model.N) - 1
            return Constraint.Skip
        model.restriccion_subtours = Constraint(model.C, model.C, model.V, rule=restriccion_subtours)

        #9. Sale de un centro depot
        def restriccion_sale_vehiculo(model,v):
            return sum(model.x[d,j,v] for d in model.D for j in model.N)==1
        model.restriccion_sale_vehiculo= Constraint(model.V, rule= restriccion_sale_vehiculo)
        
        return model
    

    
    
    def solve_model(self):
        """
        Resolver el modelo utilizando HiGHS.
        """
        solver_name = "appsi_highs"
        solver = SolverFactory(solver_name)
        solver.options['parallel'] = 'on'
        solver.options['time_limit'] = 3600  # 1-hour time limit
        solver.options['presolve'] = 'on'
        solver.options['mip_rel_gap'] = 0.01  # 1% relative gap
        solver.options['simplex_strategy'] = 1  # Dual simplex
        solver.options['simplex_max_concurrency'] = 8  # Max concurrency
        solver.options['mip_min_logging_interval'] = 10  # Log every 10 seconds
        solver.options['mip_heuristic_effort'] = 0.2  # Increase heuristic effort

        # Resolver el modelo
        result = solver.solve(self.model, tee=False)

        # Verificar el estado del solver
        if result.solver.termination_condition == TerminationCondition.infeasible:
            print("El modelo es infactible.")
        elif result.solver.termination_condition == TerminationCondition.optimal:
            print("Se encontró una solución óptima.")
            # Cargar la solución si es óptima
            self.model.solutions.load_from(result)
        elif result.solver.termination_condition == TerminationCondition.unbounded:
            print("El modelo es no acotado.")
        elif result.solver.termination_condition == TerminationCondition.maxTimeLimit:
            print("Se alcanzó el límite de tiempo.")
        else:
            print(f"Condición de terminación desconocida: {result.solver.termination_condition}")

        print(result)

        

    def display_results(self):
        """
        Mostrar los resultados del modelo.
        """
        self.model.x.display()

# Instanciar la clase del modelo
vrp = VRPModel(
    clientes=clientes,
    centros=centros,
    vehiculos=vehiculos,
    productos=productos,
    distancias_dict=distancias_dict,
    tiempos=tiempos,
    demandas=demandas,
    capacidad_vehiculo=capacidad_vehiculo,
    rango_vehiculo=rango_vehiculo,
    costos_operativos_dict=costos_operativos_dict,
    costos_mantenimiento=costos_mantenimiento,
    costos_recarga=costos_recarga
)

# Construir el modelo
vrp.build_model()

# Resolver el modelo
vrp.solve_model()

vrp.display_results()