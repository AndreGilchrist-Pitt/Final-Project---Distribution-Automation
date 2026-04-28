from Src.Paths.paths import CASE2_DATA_DIR
from Src.Utils.Classes.settings import Settings
from Src.Utils.Classes.areascalar import AreaScalar
from Src.Validation.TestScripts.feeder_builder import build_feeder_network
from Src.Utils.ProcessFiles.compare_help import (
    load_powerworld_buses_json,
    compare_voltage_vector_polar,
    load_powerworld_case_summary_json,
    compare_case_losses,
    compare_case_summary_counts,
)

Settings(freq=60.0, sbase=100.0)
AreaScalar(res_scale=1.0, com_scale=1.0, ind_scale=1.0)

circuit = build_feeder_network()
circuit.open_branch("L_Right_9com")
circuit.open_branch("L_9com_10res")
circuit.print_elements()
circuit.calc_ybus()
solver = circuit.solve(mode="power_flow", tol=1e-6, max_iter=50, verbose=True)

print()
print("Case 1 Power Flow Result")
print("-" * 80)
print(f"Converged : {solver.converged}")
print(f"Iterations: {solver.iterations}")
print("-" * 80)

powerworld_buses = load_powerworld_buses_json(
    CASE2_DATA_DIR / "Buses.json"
)

compare_voltage_vector_polar(
    circuit=circuit,
    powerworld_buses=powerworld_buses,
    voltage_tolerance=1e-4,
    angle_tolerance=1e-2,
)

powerworld_case_summary = load_powerworld_case_summary_json(
    CASE2_DATA_DIR / "Case_Summary.json"
)

circuit.print_case_losses()

compare_case_losses(
    circuit=circuit,
    powerworld_case_summary=powerworld_case_summary,
    mw_tolerance=1e-3,
    mvar_tolerance=1e-3,
)

compare_case_summary_counts(
    circuit=circuit,
    powerworld_case_summary=powerworld_case_summary,
)