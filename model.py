from pyomo.environ import *

class VRPModel:
    def __init__(self, clientes, centros, vehiculos, productos, distancias, tiempos, demandas, capacidad_vehiculo, rango_vehiculo, costos_km, costos_minuto, costos_mantenimiento, costos_recarga, capacidades_centro):
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
        self.costos_km = costos_km
        self.costos_minuto = costos_minuto
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

