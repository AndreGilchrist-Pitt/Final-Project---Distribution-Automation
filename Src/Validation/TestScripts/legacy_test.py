import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np

from Src.Utils.Classes.bus import Bus
from Src.Utils.Classes.circuit import Circuit
from Src.Utils.Classes.settings import Settings
from Src.Utils.Classes.powerflow import PowerFlow
from Src.Utils.Classes.solver import Solver

Bus._bus_counter = 0
Bus._bus_registry.clear()

Settings(freq=60.0, sbase=100.0)
circuit = Circuit("Milestone 8 — Five-Bus NR (Glover-style)")

circuit.add_bus("Bus1", 15.0, vpu=1.0, delta=0.0, bus_type="Slack")
circuit.add_bus("Bus2", 345.0, vpu=1.0, delta=0.0, bus_type="PQ")
circuit.add_bus("Bus3", 15.0, vpu=1.05, delta=0.0, bus_type="PV")
circuit.add_bus("Bus4", 345.0, vpu=1.0, delta=0.0, bus_type="PQ")
circuit.add_bus("Bus5", 345.0, vpu=1.0, delta=0.0, bus_type="PQ")

circuit.add_transformer("T1", "Bus1", "Bus5", 0.0015, 0.02)
circuit.add_transformer("T2", "Bus3", "Bus4", 0.00075, 0.01)

circuit.add_transmission_line("Line1", "Bus4", "Bus2", 0.009, 0.1, 0.0, 1.72)
circuit.add_transmission_line("Line2", "Bus5", "Bus2", 0.0045, 0.05, 0.0, 0.88)
circuit.add_transmission_line("Line3", "Bus5", "Bus4", 0.00225, 0.025, 0.0, 0.44)

circuit.add_generator("G1", "Bus1", 1.04, 0.0, x_subtransient=0.045)
circuit.add_generator("G2", "Bus3", 1.025, 520.0, x_subtransient=0.0225)

circuit.add_load("Load2", "Bus2", 800.0, 280.0)
circuit.add_load("Load3", "Bus3", 80.0, 40.0)

circuit.calc_ybus()


def _print_matrix(title, M, bus_names, part="imag", fmt="{:+10.5f}j"):
    """Print an N×N complex matrix with bus-name headers.
       part: 'imag', 'real', or 'both'."""
    print(f"\n{title}")
    header = "        " + "  ".join(f"{n:>10}" for n in bus_names)
    print(header)
    for i, name in enumerate(bus_names):
        cells = []
        for j in range(len(bus_names)):
            z = M[i, j]
            if part == "imag":
                cells.append(fmt.format(z.imag))
            elif part == "real":
                cells.append(fmt.format(z.real))
            else:  # both
                cells.append(f"{z.real:+.4f}{z.imag:+.4f}j")
        print(f"{name:>6}  " + "  ".join(cells))


# --- Power Flow ---
pf = circuit.solve(mode="power_flow", tol=1e-4, verbose=True)
print(f"Converged: {pf.converged} in {pf.iterations} iterations")

# Fault Study
fs = circuit.solve(mode="fault", faulted_bus_name="Bus2", prefault_voltage=1.05)
bus_names = list(circuit.buses)

ybus_fault = circuit.calc_ybus_fault()
zbus = circuit.calc_zbus(ybus_fault)

_print_matrix("Ybus_fault (imag, pu)", ybus_fault, bus_names, part="imag")
_print_matrix("Zbus (imag, pu)", zbus, bus_names, part="imag")
print(f"Fault Current: {abs(fs.fault_current):.4f} pu")
print("\n--- Fault voltage sweep (Vf = 1.05) ---")
bus_names = list(circuit.buses)
header = "           " + "  ".join(f"{n:>6}" for n in bus_names)
print(header)
fault_results = {}
for faulted in bus_names:
    fs = circuit.solve(mode="fault", faulted_bus_name=faulted, prefault_voltage=1.05)
    fault_results[faulted] = fs
for faulted in bus_names:
    fs = fault_results[faulted]
    mags = [abs(fault_results[obs].fault_voltages[faulted]) for obs in bus_names]
    row = "  ".join(f"{m:6.4f}" for m in mags)
    print(f"Fault@{faulted}  {row}  |I_f|={abs(fs.fault_current):8.4f} pu")
print()
circuit.print_elements()