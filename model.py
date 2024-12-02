from pyomo.environ import *
import pandas as pd

# Cambiar las rutas de los archivos
clients = pd.read_csv(r'case_1_base/Clients.csv')  # Clientes
depots = pd.read_csv(r'case_1_base/Depots.csv')    # Depósitos
distancias = pd.read_csv(r'Matrices/distancias1.csv')  # Matriz de distancias
tiempos = pd.read_csv(r'Matrices/tiempos1.csv')        # Matriz de tiempos
vehicles = pd.read_csv(r'case_1_base/Vehicles.csv')    # Vehículos

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


vehicles['ID'] = ['V' + str(i + 1) for i in range(len(vehicles))]
# Crear conjuntos
clientes = clients['ClientID'].tolist()  # IDs de los clientes
centros = depots['DepotID'].tolist()   # IDs de los depósitos
vehiculos = vehicles['ID'].tolist()  # IDs de los vehículos
productos = ['Product']  # Definimos tipos de productos (puedes ajustar según el problema)
nodos = clientes + centros  # Todos los nodos (clientes + depósitos)

clients.columns = clients.columns.str.strip()
# Crear parámetros
# 1. Demandas de clientes por producto (puede venir de Clients.csv o ser constante)
demandas = {(row['ClientID'], p): row['Product'] for _, row in clients.iterrows() for p in productos}

# 2. Capacidades de los vehículos (Vehicles.csv)
capacidad_vehiculo = {row['ID']: row['Capacity'] for _, row in vehicles.iterrows()}

# 3. Rango máximo de los vehículos (Vehicles.csv)
rango_vehiculo = {row['ID']: row['Range'] for _, row in vehicles.iterrows()}

# 5. Costos de mantenimiento y recarga (Vehicles.csv)
costos_mantenimiento = {row['ID']: row['Costo_Mantenimiento'] for _, row in vehicles.iterrows()}
costos_recarga = {row['ID']: row['Costo_Recarga'] for _, row in vehicles.iterrows()}

# 6. Capacidades de los centros de distribución (Depots.csv)
capacidades_centro = {(row['DepotID'], p): row[f'Capacidad_{p}'] for _, row in depots.iterrows() for p in productos}

# 7. Distancias y tiempos (distancias1.csv y tiempos1.csv)
# Convertir archivos CSV a diccionarios
distancias_dict = {(row['Desde'], row['Hacia']): row['Distancia'] for _, row in distancias.iterrows()}
tiempos_dict = {(row['Desde'], row['Hacia']): row['Tiempo'] for _, row in tiempos.iterrows()}

# Validar dimensiones
print(f"Clientes: {len(clientes)}, Centros: {len(centros)}, Vehículos: {len(vehiculos)}, Nodos: {len(nodos)}")

pass
class VRPModel:
    def __init__(self, clientes, centros, vehiculos, productos, distancias, tiempos, demandas, capacidad_vehiculo, rango_vehiculo, costos_operativos, costos_mantenimiento, costos_recarga, capacidades_centro):
        """
        Inicializar parámetros del modelo VRP.
        """
        # Conjuntos y parámetros
        self.clientes = clientes
        self.centros = centros
        self.vehiculos = vehiculos
        self.productos = productos
        self.nodos = clientes + centros
        self.distancias = distancias
        self.tiempos = tiempos
        self.demandas = demandas
        self.capacidad_vehiculo = capacidad_vehiculo
        self.rango_vehiculo = rango_vehiculo
        self.costos_operativos= costos_operativos
        self.costos_mantenimiento = costos_mantenimiento
        self.costos_recarga = costos_recarga
        self.capacidades_centro = capacidades_centro

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
        model.z = Var(model.V, within=Binary)  # Activación del vehículo
        model.q = Var(model.N, model.P, model.V, within=NonNegativeReals)  # Carga transportada

        # Función objetivo: Minimizar costos
        def obj_expression(model):
            return sum(
                # Costos por distancia
                model.x[i, j, v] * self.distancias[i, j] * self.costos_km[v]
                for i in model.N for j in model.N for v in model.V if i != j
            ) + sum(
                # Costos por tiempo
                model.x[i, j, v] * self.tiempos[i, j] * self.costos_minuto[v]
                for i in model.N for j in model.N for v in model.V if i != j
            ) + sum(
                # Costos de mantenimiento
                model.z[v] * self.costos_mantenimiento[v] for v in model.V
            ) + sum(
                # Costos de recarga
                self.costos_recarga[v] * model.z[v] for v in model.V
            )
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
        def restriccion_capacidad_vehiculo(model, v):
            return sum(model.q[i, p, v] for i in model.C for p in model.P) <= self.capacidad_vehiculo[v]
        model.restriccion_capacidad_vehiculo = Constraint(model.V, rule=restriccion_capacidad_vehiculo)

        # 4. Carga transportada debe respetar las demandas
        def restriccion_demanda(model, i, p):
            return sum(model.q[i, p, v] for v in model.V) == self.demandas[i, p]
        model.restriccion_demanda = Constraint(model.C, model.P, rule=restriccion_demanda)

        # 5. Capacidad de los centros de distribución
        def restriccion_capacidad_centro(model, k, p):
            return sum(model.q[i, p, v] for i in model.C for v in model.V) <= self.capacidades_centro[k, p]
        model.restriccion_capacidad_centro = Constraint(model.D, model.P, rule=restriccion_capacidad_centro)

        # 6. Límite de rango de los vehículos
        def restriccion_rango_vehiculo(model, v):
            return sum(self.distancias[i, j] * model.x[i, j, v] for i in model.N for j in model.N if i != j) <= self.rango_vehiculo[v]
        model.restriccion_rango_vehiculo = Constraint(model.V, rule=restriccion_rango_vehiculo)

        # 7. Eliminación de subtours (MTZ)
        model.u = Var(model.C, model.V, within=NonNegativeReals)
        def restriccion_subtours(model, i, j, v):
            if i != j:
                return model.u[i, v] - model.u[j, v] + len(model.C) * model.x[i, j, v] <= len(model.C) - 1
            return Constraint.Skip
        model.restriccion_subtours = Constraint(model.C, model.C, model.V, rule=restriccion_subtours)

        return model

    def solve_model(self):
        """
        Resolver el modelo utilizando HiGHS.
        """
        solver_name = "appsi_highs"
        solver = pyo.SolverFactory(solver_name)
        solver.options['parallel'] = 'on'
        solver.options['time_limit'] = 3600  # 1-hour time limit
        solver.options['presolve'] = 'on'
        solver.options['mip_rel_gap'] = 0.01  # 1% relative gap
        solver.options['simplex_strategy'] = 1  # Dual simplex
        solver.options['simplex_max_concurrency'] = 8  # Max concurrency
        solver.options['mip_min_logging_interval'] = 10  # Log every 10 seconds
        solver.options['mip_heuristic_effort'] = 0.2  # Increase heuristic effort

        result = solver.solve(self.model, tee=True)

        # Check solver status
        if result.solver.termination_condition == pyo.TerminationCondition.optimal:
            print("Optimal solution found.")
        elif result.solver.termination_condition == pyo.TerminationCondition.maxTimeLimit:
            print("Time limit reached, solution may be suboptimal.")
        else:
            print(f"Solver terminated with condition: {result.solver.termination_condition}")

        print(result)
        

    def display_results(self):
        """
        Mostrar los resultados del modelo.
        """
        self.model.display()

