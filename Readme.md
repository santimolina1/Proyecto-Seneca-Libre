# Repository: Multi-Depot Capacitated Vehicle Routing Problem Skeleton (R-MDMCVRP)

## Overview

This repository is designed to provide a framework for solving the **Multi-Depot Capacitated Vehicle Routing Problem (MDMCVRP)**. It includes synthetic datasets, a model skeleton, and tools for generating, managing, and solving optimization problems in logistics and transportation. The repository is ideal for academic purposes and hands-on learning.

---

## File Structure

```plaintext
.
├── case_1_base/                     # Base datasets for initial case studies
├── case_1_base_old/                 # Archived version of case 1 base datasets
├── case_2_5_clients_per_vehicle_old/ # Archived version of case 2 datasets
├── case_2_cost/                     # Datasets for cost-based cases
├── case_3_big_distances_small_demands_old/ # Archived version of case 3 datasets
├── case_3_supply_limits/            # Case with supply constraints
├── case_4_capacitated_depots_old/       # Archived version of case 4 Case with depot capacity constraints
├── case_4_multi_product/            # multi-product cases
├── case_5_recharge_nodes/           # Case with recharge nodes for vehicles
├── class-based-model.py             # Python example on how a class based model with pyomo should look like
├── cvrp_map.html                    # Example HTML visualization for routes
├── Docs/                            # Documentation files
│   ├── EnunciadoEntrega2SenecaLibre.pdf  # Case problem statement
│   ├── Propuesta Formal de Seneca Libre.pdf # Formal proposal document
│   └── main.tex                     # LaTeX source for the document
├── GeoSpatialData/                  # Geospatial data files for mapping
├── HiGHsSolverTutorial.ipynb        # Notebook explaining HiGHs solver installation and usage
├── loading_costs.csv                # Data for loading and unloading costs
├── Readme.md                        # This README file
├── SinteticDataFactory.ipynb        # Notebook for synthetic dataset generation
├── single_depot.csv                 # Example dataset for single depot case
└── vehicles_data.csv                # Dataset with vehicle parameters
```

---

## Key Components

### 1. **Synthetic Data Generation**
- **File**: `SinteticDataFactory.ipynb`
- **Description**: 
  - Contains the code to generate synthetic datasets for testing the model.
  - Demonstrates how to create and load data using pandas DataFrames.
  - Provides a structured skeleton (`SenecaLibreModel`) with clear guidelines for implementing the MDMCVRP solution.
  - Includes placeholders for data preparation, cost matrices, model building, and constraints.
- **Usage**:
  - Modify parameters to customize datasets.
  - Export datasets for different cases.
- **Purpose**: 
  - Serve as a starting point for building optimization models.

---

### 2. **Model Skeleton**
- **File**: `class-based-model.py`
- **Description**:
  - An example Python script showing how to structure a class-based model using Pyomo.
---

### 3. **HiGHs Solver Tutorial**
- **File**: `HiGHsSolverTutorial.ipynb`
- **Description**:
  - Explains how to install and configure the HiGHs solver for Pyomo.
  - Provides example optimization problems solved using HiGHs.
- **Usage**:
  - Follow the notebook to understand solver integration.
  - Test basic linear programming problems with HiGHs.

---

## Datasets

The repository includes several cases, each with its corresponding dataset:

- **`case_1_base/`**: Basic example for initial testing.
- **`case_2_cost/`**: Includes a harder situation that is a lot closer to the real problem.
- **`case_3_supply_limits/`**: Includes depot capacity constraints.
- **`case_4_multi_product/`**: Adds multiple products and constraints.
- **`case_5_recharge_nodes/`**: Adds recharge nodes for the vehicles.

Each case contains:
- `Clients.csv`: Client location and demand data.
- `Depots.csv`: Depot location data.
- `Vehicles.csv`: Vehicle capacity, range, and other parameters.

> **Note**: You can swap Depots.csv with single_depot.csv for single depot if your inital model is for a single depot.

For advanced cases:
- `DepotCapacities.csv`: Specifies product limits for each depot.
- `RechargeNodes.csv`: Details recharge node locations and attributes.

---

## How to Use

1. **Clone the repository**:
   ```bash
   git clone <repository_url>
   cd r-mdmcvrp-skeleton
   ```

2. **Install dependencies**:
   - Use a Python environment with Pyomo installed.
   - Refer to `HiGHsSolverTutorial.ipynb` for installing HiGHs.

3. **Generate synthetic data**:
   - Open `SinteticDataFactory.ipynb` in Jupyter Notebook.
   - Modify parameters and export datasets.

4. **Implement the model**:
   - Use `class-based-model.py` as a starting point.
   - Follow the provided guidelines to build and test the MDMCVRP.

5. **Run and visualize results**:
   - Solve the problem using Pyomo and visualize routes using `cvrp_map.html` or network visualization tools.

---

## Contributions

Contributions to improve the model skeleton, datasets, or documentation are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or fix.
3. Submit a pull request with a clear explanation of your changes.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

For any questions or issues, feel free to open an issue in the repository. Happy optimizing! 🚛📍
