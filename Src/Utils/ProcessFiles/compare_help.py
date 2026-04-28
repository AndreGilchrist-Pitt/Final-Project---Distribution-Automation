import json
import re
from pathlib import Path

import numpy as np

from Src.Paths.paths import BASELINE_DATA_DIR
from Src.Utils.Classes.settings import Settings
from Src.Utils.Classes.areascalar import AreaScalar
from Src.Validation.TestScripts.feeder_builder import build_feeder_network


def parse_powerworld_complex(value: str) -> complex:
    """
    Convert a PowerWorld complex string into a Python complex number.

    Examples:
        "0.31 - j2.46"  -> 0.31 - 2.46j
        "-0.15 + j1.17" -> -0.15 + 1.17j
        ""              -> 0.0 + 0.0j
    """
    if value is None:
        return 0.0 + 0.0j

    value = str(value).strip()

    if value == "":
        return 0.0 + 0.0j

    cleaned = value.replace(" ", "")

    pattern = r"^([+-]?\d*\.?\d+)([+-])j(\d*\.?\d+)$"
    match = re.match(pattern, cleaned)

    if not match:
        raise ValueError(f"Could not parse PowerWorld complex value: {value}")

    real_part = float(match.group(1))
    imag_sign = match.group(2)
    imag_part = float(match.group(3))

    if imag_sign == "-":
        imag_part *= -1.0

    return complex(real_part, imag_part)


def load_powerworld_ybus_json(ybus_json_path: str | Path) -> tuple[list[str], np.ndarray]:
    """
    Load PowerWorld YBus.json into a bus-name list and complex NumPy matrix.

    Args:
        ybus_json_path: Path to PowerWorld YBus.json.

    Returns:
        Tuple of:
            bus_names: Bus names in PowerWorld YBus order.
            ybus: Complex YBus matrix.
    """
    ybus_json_path = Path(ybus_json_path)

    with ybus_json_path.open("r", encoding="utf-8") as file:
        rows = json.load(file)

    bus_names = [row["Name"] for row in rows]
    n = len(rows)

    ybus = np.zeros((n, n), dtype=complex)

    for i, row in enumerate(rows):
        for j in range(n):
            column_name = f"Bus{j + 1:6d}"
            ybus[i, j] = parse_powerworld_complex(row.get(column_name, ""))

    return bus_names, ybus


def reorder_circuit_ybus_to_powerworld_order(circuit, powerworld_bus_names: list[str]) -> np.ndarray:
    """
    Reorder circuit.ybus so its row/column order matches PowerWorld's YBus order.

    Args:
        circuit: Circuit object with calculated ybus.
        powerworld_bus_names: Bus names in PowerWorld YBus order.

    Returns:
        Reordered circuit YBus matrix.
    """
    if circuit.ybus is None:
        circuit.calc_ybus()

    circuit_bus_names = list(circuit.buses.keys())
    circuit_bus_index = {
        bus_name: index
        for index, bus_name in enumerate(circuit_bus_names)
    }

    missing_buses = [
        bus_name
        for bus_name in powerworld_bus_names
        if bus_name not in circuit_bus_index
    ]

    if missing_buses:
        raise ValueError(f"These PowerWorld buses are missing from the circuit: {missing_buses}")

    reorder_indices = [
        circuit_bus_index[bus_name]
        for bus_name in powerworld_bus_names
    ]

    return circuit.ybus[np.ix_(reorder_indices, reorder_indices)]


def format_complex(value: complex, width: int = 26, precision: int = 6) -> str:
    """
    Format a complex number as one fixed-width table field.

    Example:
        0.307692 - j2.461538
    """
    formatted = f"{value.real:.{precision}f} {'+' if value.imag >= 0 else '-'} j{abs(value.imag):.{precision}f}"
    return f"{formatted:>{width}s}"


def compare_ybus(circuit, powerworld_ybus: np.ndarray, powerworld_bus_names: list[str],
                 tolerance: float = 1e-2) -> None:
    """
    Compare circuit.ybus against PowerWorld YBus and display every matrix entry.

    Args:
        circuit: Circuit object with calculated ybus.
        powerworld_ybus: Complex PowerWorld YBus matrix.
        powerworld_bus_names: Bus names in PowerWorld YBus order.
        tolerance: Maximum allowed absolute complex difference.
    """
    circuit_ybus_ordered = reorder_circuit_ybus_to_powerworld_order(
        circuit,
        powerworld_bus_names,
    )

    difference = circuit_ybus_ordered - powerworld_ybus
    abs_difference = np.abs(difference)
    max_difference = np.max(abs_difference)

    table_width = 132

    print("YBus Comparison Summary")
    print("-" * table_width)
    print(f"PowerWorld YBus shape : {powerworld_ybus.shape}")
    print(f"Circuit YBus shape    : {circuit_ybus_ordered.shape}")
    print(f"Max abs difference    : {max_difference:.8f}")
    print(f"Tolerance             : {tolerance:.8f}")
    print(f"Pass                  : {max_difference <= tolerance}")
    print("-" * table_width)

    print("All YBus Entries")
    print("-" * table_width)
    print(
        f"{'Row Bus':20s} "
        f"{'Column Bus':20s} "
        f"{'Circuit YBus':>26s} "
        f"{'PowerWorld YBus':>26s} "
        f"{'Difference':>26s} "
        f"{'|Diff|':>12s} "
        f"{'Pass':>8s}"
    )
    print("-" * table_width)

    n_rows, n_cols = powerworld_ybus.shape

    for i in range(n_rows):
        for j in range(n_cols):
            row_bus = powerworld_bus_names[i]
            col_bus = powerworld_bus_names[j]

            circuit_value = circuit_ybus_ordered[i, j]
            powerworld_value = powerworld_ybus[i, j]
            diff_value = difference[i, j]
            abs_diff_value = abs_difference[i, j]
            entry_passed = abs_diff_value <= tolerance

            print(
                f"{row_bus:20s} "
                f"{col_bus:20s} "
                f"{format_complex(circuit_value)} "
                f"{format_complex(powerworld_value)} "
                f"{format_complex(diff_value)} "
                f"{abs_diff_value:12.6f} "
                f"{str(entry_passed):>8s}"
            )

    print("-" * table_width)


def main():
    Settings(freq=60.0, sbase=100.0)
    AreaScalar(res_scale=1.0, com_scale=1.0, ind_scale=1.0)

    circuit = build_feeder_network("Chapter14_Feeder_BaseCase")
    circuit.calc_ybus()

    ybus_json_path = BASELINE_DATA_DIR / "YBus.json"

    powerworld_bus_names, powerworld_ybus = load_powerworld_ybus_json(ybus_json_path)

    compare_ybus(
        circuit=circuit,
        powerworld_ybus=powerworld_ybus,
        powerworld_bus_names=powerworld_bus_names,
        tolerance=1e-2,
    )


def load_powerworld_buses_json(buses_json_path: str | Path) -> list[dict]:
    """
    Load PowerWorld Buses.json.

    Args:
        buses_json_path: Path to Buses.json.

    Returns:
        List of bus dictionaries from PowerWorld.
    """
    buses_json_path = Path(buses_json_path)

    with buses_json_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def reorder_circuit_buses_to_powerworld_order(circuit, powerworld_bus_names: list[str]) -> list:
    """
    Reorder circuit bus objects to match PowerWorld bus order.

    Args:
        circuit: Circuit object.
        powerworld_bus_names: Bus names from PowerWorld Buses.json.

    Returns:
        List of circuit Bus objects in PowerWorld order.
    """
    missing_buses = [
        bus_name
        for bus_name in powerworld_bus_names
        if bus_name not in circuit.buses
    ]

    if missing_buses:
        raise ValueError(f"These PowerWorld buses are missing from the circuit: {missing_buses}")

    return [
        circuit.buses[bus_name]
        for bus_name in powerworld_bus_names
    ]


def compare_voltage_vector_polar(circuit, powerworld_buses: list[dict],
                                 voltage_tolerance: float = 1e-4,
                                 angle_tolerance: float = 1e-2) -> None:
    """
    Compare circuit voltage_vector_polar against PowerWorld Buses.json.

    Compares:
        circuit bus.vpu   vs PowerWorld 'PU Volt'
        circuit bus.delta vs PowerWorld 'Angle (Deg)'

    Args:
        circuit: Circuit object after power flow solve.
        powerworld_buses: List of bus dictionaries loaded from Buses.json.
        voltage_tolerance: Maximum allowed voltage magnitude difference in pu.
        angle_tolerance: Maximum allowed angle difference in degrees.
    """
    powerworld_bus_names = [
        row["Name"]
        for row in powerworld_buses
    ]

    circuit_buses_ordered = reorder_circuit_buses_to_powerworld_order(
        circuit,
        powerworld_bus_names,
    )

    voltage_differences = []
    angle_differences = []

    for bus, powerworld_row in zip(circuit_buses_ordered, powerworld_buses):
        voltage_differences.append(bus.vpu - float(powerworld_row["PU Volt"]))
        angle_differences.append(bus.delta - float(powerworld_row["Angle (Deg)"]))

    max_voltage_difference = max(abs(value) for value in voltage_differences)
    max_angle_difference = max(abs(value) for value in angle_differences)

    voltage_passed = max_voltage_difference <= voltage_tolerance
    angle_passed = max_angle_difference <= angle_tolerance
    overall_passed = voltage_passed and angle_passed

    table_width = 146

    print("Voltage Vector Polar Comparison Summary")
    print("-" * table_width)
    print(f"PowerWorld bus count      : {len(powerworld_buses)}")
    print(f"Circuit bus count         : {len(circuit.buses)}")
    print(f"Max voltage difference    : {max_voltage_difference:.8f} pu")
    print(f"Voltage tolerance         : {voltage_tolerance:.8f} pu")
    print(f"Voltage pass              : {voltage_passed}")
    print(f"Max angle difference      : {max_angle_difference:.8f} deg")
    print(f"Angle tolerance           : {angle_tolerance:.8f} deg")
    print(f"Angle pass                : {angle_passed}")
    print(f"Overall pass              : {overall_passed}")
    print("-" * table_width)

    print("All Voltage Vector Polar Entries")
    print("-" * table_width)
    print(
        f"{'Bus Name':20s} "
        f"{'Circuit Vpu':>12s} "
        f"{'PowerWorld Vpu':>16s} "
        f"{'V Diff':>12s} "
        f"{'V Pass':>8s} "
        f"{'Circuit Angle':>16s} "
        f"{'PowerWorld Angle':>18s} "
        f"{'Angle Diff':>14s} "
        f"{'Angle Pass':>10s}"
    )
    print("-" * table_width)

    for bus, powerworld_row, v_diff, angle_diff in zip(
            circuit_buses_ordered,
            powerworld_buses,
            voltage_differences,
            angle_differences,
    ):
        powerworld_vpu = float(powerworld_row["PU Volt"])
        powerworld_angle = float(powerworld_row["Angle (Deg)"])

        voltage_entry_passed = abs(v_diff) <= voltage_tolerance
        angle_entry_passed = abs(angle_diff) <= angle_tolerance

        print(
            f"{bus.name:20s} "
            f"{bus.vpu:12.6f} "
            f"{powerworld_vpu:16.6f} "
            f"{v_diff:12.6f} "
            f"{str(voltage_entry_passed):>8s} "
            f"{bus.delta:16.6f} "
            f"{powerworld_angle:18.6f} "
            f"{angle_diff:14.6f} "
            f"{str(angle_entry_passed):>10s}"
        )

    print("-" * table_width)


def load_powerworld_case_summary_json(case_summary_json_path: str | Path) -> dict:
    """
    Load PowerWorld Case_Summary.json.

    Args:
        case_summary_json_path: Path to Case_Summary.json.

    Returns:
        Case summary dictionary from PowerWorld.
    """
    case_summary_json_path = Path(case_summary_json_path)

    with case_summary_json_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not data:
        raise ValueError(f"Case summary file is empty: {case_summary_json_path}")

    return data[0]


def compare_case_losses(circuit, powerworld_case_summary: dict,
                        mw_tolerance: float = 1e-3,
                        mvar_tolerance: float = 1e-3) -> None:
    """
    Compare circuit case losses against PowerWorld Case_Summary.json.

    Compares:
        circuit.calc_case_losses()[1] vs PowerWorld 'Losses MW'
        circuit.calc_case_losses()[2] vs PowerWorld 'Losses Mvar'

    Args:
        circuit: Circuit object after power flow solve.
        powerworld_case_summary: Dictionary loaded from Case_Summary.json.
        mw_tolerance: Maximum allowed MW loss difference.
        mvar_tolerance: Maximum allowed Mvar loss difference.
    """
    total_loss_pu, circuit_loss_mw, circuit_loss_mvar = circuit.calc_case_losses()

    powerworld_loss_mw = float(powerworld_case_summary["Losses MW"])
    powerworld_loss_mvar = float(powerworld_case_summary["Losses Mvar"])

    mw_difference = circuit_loss_mw - powerworld_loss_mw
    mvar_difference = circuit_loss_mvar - powerworld_loss_mvar

    mw_passed = abs(mw_difference) <= mw_tolerance
    mvar_passed = abs(mvar_difference) <= mvar_tolerance
    overall_passed = mw_passed and mvar_passed

    table_width = 110

    print("Case Loss Comparison Summary")
    print("-" * table_width)
    print(f"Circuit total loss pu : {total_loss_pu.real:.8f} + j{total_loss_pu.imag:.8f}")
    print(f"MW tolerance          : {mw_tolerance:.8f}")
    print(f"Mvar tolerance        : {mvar_tolerance:.8f}")
    print(f"Overall pass          : {overall_passed}")
    print("-" * table_width)

    print("Case Loss Values")
    print("-" * table_width)
    print(
        f"{'Quantity':20s} "
        f"{'Circuit':>16s} "
        f"{'PowerWorld':>16s} "
        f"{'Difference':>16s} "
        f"{'Tolerance':>16s} "
        f"{'Pass':>8s}"
    )
    print("-" * table_width)

    print(
        f"{'Losses MW':20s} "
        f"{circuit_loss_mw:16.6f} "
        f"{powerworld_loss_mw:16.6f} "
        f"{mw_difference:16.6f} "
        f"{mw_tolerance:16.6f} "
        f"{str(mw_passed):>8s}"
    )

    print(
        f"{'Losses Mvar':20s} "
        f"{circuit_loss_mvar:16.6f} "
        f"{powerworld_loss_mvar:16.6f} "
        f"{mvar_difference:16.6f} "
        f"{mvar_tolerance:16.6f} "
        f"{str(mvar_passed):>8s}"
    )

    print("-" * table_width)


def compare_case_summary_counts(circuit, powerworld_case_summary: dict) -> None:
    """
    Compare basic circuit element counts against PowerWorld Case_Summary.json.

    Args:
        circuit: Circuit object.
        powerworld_case_summary: Dictionary loaded from Case_Summary.json.
    """
    comparisons = [
        ("# of Buses", len(circuit.buses), int(powerworld_case_summary["# of Buses"])),
        ("# of Loads", len(circuit.loads), int(powerworld_case_summary["# of Loads"])),
        ("# of Gens", len(circuit.generators), int(powerworld_case_summary["# of Gens"])),
        ("# of Switched Shunts", len(circuit.capacitor_banks),
         int(powerworld_case_summary["# of Switched Shunts"])),
    ]

    table_width = 80
    all_passed = all(circuit_value == powerworld_value for _, circuit_value, powerworld_value in comparisons)

    print("Case Summary Count Comparison")
    print("-" * table_width)
    print(f"Overall pass: {all_passed}")
    print("-" * table_width)
    print(
        f"{'Quantity':25s} "
        f"{'Circuit':>12s} "
        f"{'PowerWorld':>12s} "
        f"{'Difference':>12s} "
        f"{'Pass':>8s}"
    )
    print("-" * table_width)

    for quantity, circuit_value, powerworld_value in comparisons:
        difference = circuit_value - powerworld_value
        passed = circuit_value == powerworld_value

        print(
            f"{quantity:25s} "
            f"{circuit_value:12d} "
            f"{powerworld_value:12d} "
            f"{difference:12d} "
            f"{str(passed):>8s}"
        )

    print("-" * table_width)


if __name__ == "__main__":
    main()
