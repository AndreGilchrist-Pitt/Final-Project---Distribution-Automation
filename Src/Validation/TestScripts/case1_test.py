from Src.Paths.paths import CASE1_DATA_DIR
from Src.Utils.Classes.settings import Settings
from Src.Utils.Classes.areascalar import AreaScalar
from Src.Validation.TestScripts.feeder_builder import build_feeder_network
from Src.Utils.ProcessFiles.compare_help import (
    load_powerworld_buses_json,
    compare_voltage_vector_polar,
    load_powerworld_case_summary_json,
    compare_case_losses,
    compare_case_summary_counts,
    load_powerworld_ybus_json,
    compare_ybus,
)

Settings(freq=60.0, sbase=100.0)
AreaScalar(res_scale=1.0, com_scale=1.0, ind_scale=1.0)
AUTO_RESTORE = False
circuit = build_feeder_network()
circuit.open_branch("Tie_Left_Right")
circuit.open_branch("L_8ind_13ind")
circuit.print_elements()
print()
restoration_result = circuit.apply_distribution_automation(
    enabled=AUTO_RESTORE,
    faulted_buses=set(),
    allowed_branch_types={"tie_switch"},
)

circuit.calc_ybus()
print()
powerworld_ybus_bus_names, powerworld_ybus = load_powerworld_ybus_json(
    CASE1_DATA_DIR / "YBus.json"
)
print()
compare_ybus(
    circuit=circuit,
    powerworld_ybus=powerworld_ybus,
    powerworld_bus_names=powerworld_ybus_bus_names,
    tolerance=1e-2,
)

solver = circuit.solve(mode="power_flow", tol=1e-6, max_iter=50, verbose=True)

print()
print("Case 1 Power Flow Result")
print("-" * 80)
print(f"Converged : {solver.converged}")
print(f"Iterations: {solver.iterations}")
print("-" * 80)

powerworld_buses = load_powerworld_buses_json(
    CASE1_DATA_DIR / "Buses.json"
)
print()
compare_voltage_vector_polar(
    circuit=circuit,
    powerworld_buses=powerworld_buses,
    voltage_tolerance=1e-4,
    angle_tolerance=1e-2,
)
print()
powerworld_case_summary = load_powerworld_case_summary_json(
    CASE1_DATA_DIR / "Case_Summary.json"
)
print()
circuit.print_case_losses()
print()
compare_case_losses(
    circuit=circuit,
    powerworld_case_summary=powerworld_case_summary,
    mw_tolerance=1e-3,
    mvar_tolerance=1e-3,
)
print()
compare_case_summary_counts(
    circuit=circuit,
    powerworld_case_summary=powerworld_case_summary,
)