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
    load_powerworld_ybus_json,
    compare_ybus,
)

Settings(freq=60.0, sbase=100.0)
AreaScalar(res_scale=1.0, com_scale=1.0, ind_scale=1.0)

AUTO_RESTORE = True

circuit = build_feeder_network("Case3: Case2_Auto_DA")

# Match the PowerWorld Case 2 source-side topology.
circuit.close_branch("Tie_Left_Right")

# Leave the bottom restoration tie open initially.
# The DA logic should decide to close this.
circuit.open_branch("L_8ind_13ind")

# Fault isolation around 9com.
# These two open branches isolate 9com from both sides.
circuit.open_branch("L_Right_9com")
circuit.open_branch("L_9com_10res")

print()
print("Before Automatic DA Restoration")
print("-" * 80)
circuit.update_bus_energization()
circuit.print_energization_status()

restoration_result = circuit.apply_distribution_automation(
    enabled=AUTO_RESTORE,
    faulted_buses={"9com"},
    allowed_branch_types={"tie_switch"},
)

print()
circuit.print_restoration_result(restoration_result)

print()
print("After Automatic DA Restoration")
print("-" * 80)
circuit.update_bus_energization()
circuit.print_energization_status()

circuit.calc_ybus()

powerworld_ybus_bus_names, powerworld_ybus = load_powerworld_ybus_json(
    CASE2_DATA_DIR / "YBus.json"
)

compare_ybus(
    circuit=circuit,
    powerworld_ybus=powerworld_ybus,
    powerworld_bus_names=powerworld_ybus_bus_names,
    tolerance=1e-2,
)

solver = circuit.solve(mode="power_flow", tol=1e-6, max_iter=50, verbose=True)

print()
print("Case 3 Automatic DA Power Flow Result")