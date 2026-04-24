import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np

from Src.Utils.Classes.bus import Bus
from Src.Utils.Classes.circuit import Circuit
from Src.Utils.Classes.settings import Settings
from Src.Utils.Classes.powerflow import PowerFlow
from Src.Utils.Classes.solver import Solver
from Src.Utils.Classes.areascalar import AreaScalar

Bus._bus_counter = 0
Bus._bus_registry.clear()

Settings(freq=60.0, sbase=100.0)
AreaScalar(res_scale=2.0)
circuit = Circuit("Milestone 8 — Five-Bus NR (Glover-style)")

circuit.add_bus("Bus1", 15.0, vpu=1.0, delta=0.0, bus_type="Slack")
circuit.add_bus("Bus2", 345.0, vpu=1.0, delta=0.0, bus_type="PQ", area_class="Residential")
circuit.add_bus("Bus3", 15.0, vpu=1.05, delta=0.0, bus_type="PV")
circuit.add_bus("Bus4", 345.0, vpu=1.0, delta=0.0, bus_type="PQ")
circuit.add_bus("Bus5", 345.0, vpu=1.0, delta=0.0, bus_type="PQ")

circuit.add_transformer("T1", "Bus1", "Bus5", 0.0015, 0.02)
circuit.add_transformer("T2", "Bus3", "Bus4", 0.00075, 0.01)

circuit.add_transmission_line("Line1", "Bus4", "Bus2", 0.009, 0.1, 0.0, 1.72,status="Open")
circuit.add_transmission_line("Line2", "Bus5", "Bus2", 0.0045, 0.05, 0.0, 0.88)
circuit.add_transmission_line("Line3", "Bus5", "Bus4", 0.00225, 0.025, 0.0, 0.44)

circuit.add_generator("G1", "Bus1", 1.04, 0.0, x_subtransient=0.045)
circuit.add_generator("G2", "Bus3", 1.025, 520.0, x_subtransient=0.0225)
# circuit.add_generator("G1", "Bus1", 1.0, 0.0)
# circuit.add_generator("G2", "Bus3", 1.0, 520.0)

circuit.add_load("Load2", "Bus2", 800.0, 280.0)
circuit.add_load("Load3", "Bus3", 80.0, 40.0)