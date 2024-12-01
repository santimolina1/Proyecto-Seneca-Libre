from pyomo.environ import *

class SensorPlacementModel:
    def __init__(self, sensor_types, locations, coverage_matrix, energy_costs, install_costs, communication_costs, adjacency_matrix):
        """
        Initialize the model parameters.
        """
        self.sensor_types = sensor_types
        self.locations = locations
        self.coverage_matrix = coverage_matrix
        self.energy_costs = energy_costs
        self.install_costs = install_costs
        self.communication_costs = communication_costs
        self.adjacency_matrix = adjacency_matrix  # New adjacency matrix (C_z)

        # Create the Pyomo model
        self.model = ConcreteModel()

    def build_model(self):
        """
        Build the optimization model.
        """
        model = self.model

        # Sets
        model.sensor_types = Set(initialize=self.sensor_types)  # Different sensor types
        model.locations = Set(initialize=self.locations)  # Possible installation locations

        # Decision Variables
        model.x = Var(model.sensor_types, model.locations, domain=Binary)  # Binary variable for sensor placement
        model.y = Var(model.sensor_types, domain=NonNegativeIntegers)  # Total number of sensors of each t
        # Objective: Minimize total cost (energy, installation, and communication costs)
        def obj_expression(model):
            energy_cost = sum(model.y[s] * self.energy_costs[s] for s in model.sensor_types)
            installation_cost = sum(model.x[s, l] * self.install_costs[l] for s in model.sensor_types for l in model.locations)
            communication_cost = sum(
                model.x[s, l] * self.communication_costs[l,s]
                for s in model.sensor_types for l in model.locations
            )
            return energy_cost + installation_cost + communication_cost

        model.obj = Objective(rule=obj_expression, sense=minimize)

        # Constraints: Full coverage for each location with connection restriction
        model.full_coverage = ConstraintList()
        for l in model.locations:
            for s in model.sensor_types:
                if self.coverage_matrix[s, l] == 1:  # Sensor can cover location
                    # Ensure that each location is covered, but only if it is connected via the adjacency matrix
                    model.full_coverage.add(
                        sum(model.x[s, loc] for loc in model.locations if self.coverage_matrix[s, loc] == 1 and (loc, l) in self.adjacency_matrix and self.adjacency_matrix[loc, l] == 1) >= 1
                    )

        # Consistency Constraint: Total number of sensors of type s must match the placement decisions
        def sensor_consistency_rule(model, s):
            return model.y[s] == sum(model.x[s, l] for l in model.locations)

        model.sensor_consistency = Constraint(model.sensor_types, rule=sensor_consistency_rule)

        return model

    def solve_model(self):
        """
        Solve the model using the given solver.
        """
        solver = pyo.SolverFactory('highs' )
        results = solver.solve(self.model)
        return results

    def display_results(self):
        """
        Display the results of the optimization.
        """
        self.model.display()
    def print_output(self):
        """
        Plot sensor placement solutions on directed graphs using NetworkX for each sensor type in a subplot.
        """
        # Assign colors to sensor types
        sensor_type_colors = {
            self.sensor_types[0]: 'red',
            self.sensor_types[1]: 'green',
            self.sensor_types[2]: 'blue'
        }

        # Create subplots: 1 row, 3 columns (one for each sensor type)
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        
        # Iterate over each sensor type
        for idx, s in enumerate(self.sensor_types):
            G = nx.DiGraph()  # Create a new directed graph for each sensor type

            # Add directed edges based on adjacency and sensor coverage for sensor type 's'
            for loc1 in self.locations:
                for loc2 in self.locations:
                    # Add a directed edge if the adjacency matrix indicates they are connected and covered by the sensor
                    if loc1 != loc2 and self.adjacency_matrix[loc1, loc2] == 1:
                        # Check if sensor type 's' is installed in loc1, and mark the edge color
                        if self.model.x[s, loc1]() == 1 and self.coverage_matrix[s, loc2] == 1:
                            G.add_edge(loc1, loc2, color=sensor_type_colors[s])  # Use sensor type color
                        else:
                            G.add_edge(loc1, loc2, color='black')  # Uncolored edges as black

            # Create node color mapping based on the decision variable
            node_colors = []
            for loc in G.nodes():
                if self.model.x[s, loc]() == 1:
                    node_colors.append(sensor_type_colors[s])  # Color nodes where this sensor is installed
                else:
                    node_colors.append('lightgray')  # Gray for nodes where this sensor is not installed

            # Get edge colors from the graph attributes
            edge_colors = [G[u][v]['color'] for u, v in G.edges]

            # Generate positions for nodes
            pos = nx.spring_layout(G)

            # Draw the directed graph with node and edge colors in the current axis
            nx.draw(G, pos, ax=axes[idx], node_color=node_colors, edge_color=edge_colors, with_labels=True, node_size=500, font_weight='bold', arrows=True)

            # Set the title for this subplot
            axes[idx].set_title(f"Sensor Type: {s}", fontsize=15)

        # Adjust layout to prevent overlapping
        plt.tight_layout()
        
        # Show the combined plot
        plt.show()
