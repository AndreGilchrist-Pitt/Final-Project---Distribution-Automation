from Src.Paths.paths import BASELINE_DATA_DIR
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

circuit = build_feeder_network()

circuit.calc_ybus()

powerworld_ybus_bus_names, powerworld_ybus = load_powerworld_ybus_json(
    BASELINE_DATA_DIR / "YBus.json"
)

compare_ybus(
    circuit=circuit,
    powerworld_ybus=powerworld_ybus,
    powerworld_bus_names=powerworld_ybus_bus_names,
    tolerance=1e-2,
)

solver = circuit.solve(mode="power_flow", tol=1e-6, max_iter=50, verbose=True)

powerworld_buses = load_powerworld_buses_json(
    BASELINE_DATA_DIR / "Buses.json"
)