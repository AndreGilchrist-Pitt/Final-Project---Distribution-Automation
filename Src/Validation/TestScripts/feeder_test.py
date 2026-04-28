import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from Src.Utils.Classes.bus import Bus
from Src.Utils.Classes.circuit import Circuit
from Src.Utils.Classes.settings import Settings
from Src.Utils.Classes.areascalar import AreaScalar

# Reset global bus state
Bus._bus_counter = 0
Bus._bus_registry.clear()
Bus._bus_objects.clear()

# Base settings
Settings(freq=60.0, sbase=100.0)
AreaScalar(res_scale=1.00, com_scale=1.00, ind_scale=1.00)

circuit = Circuit("Chapter14_Feeder_BaseCase")

# -------------------------
# Buses
# -------------------------
circuit.add_bus("1_TransmissionBus", 138.0, vpu=1.0, delta=0.0, bus_type="Slack", area_class="Residential")

circuit.add_bus("Left", 13.8, vpu=1.0, delta=0.0, bus_type="PQ", area_class="Residential")
circuit.add_bus("Right", 13.8, vpu=1.0, delta=0.0, bus_type="PQ", area_class="Residential")

circuit.add_bus("4com", 13.8, vpu=1.0, delta=0.0, bus_type="PQ", area_class="Commercial")
circuit.add_bus("5ind", 13.8, vpu=1.0, delta=0.0, bus_type="PQ", area_class="Industrial")
circuit.add_bus("6com", 13.8, vpu=1.0, delta=0.0, bus_type="PQ", area_class="Commercial")
circuit.add_bus("7res", 13.8, vpu=1.0, delta=0.0, bus_type="PQ", area_class="Residential")
circuit.add_bus("8ind", 13.8, vpu=1.0, delta=0.0, bus_type="PQ", area_class="Industrial")

circuit.add_bus("9com", 13.8, vpu=1.0, delta=0.0, bus_type="PQ", area_class="Commercial")
circuit.add_bus("10res", 13.8, vpu=1.0, delta=0.0, bus_type="PQ", area_class="Residential")
circuit.add_bus("11res", 13.8, vpu=1.0, delta=0.0, bus_type="PQ", area_class="Residential")
circuit.add_bus("12res", 13.8, vpu=1.0, delta=0.0, bus_type="PQ", area_class="Residential")
circuit.add_bus("13ind", 13.8, vpu=1.0, delta=0.0, bus_type="PQ", area_class="Industrial")

# -------------------------
# Transformers
# -------------------------
# Our Transformer.calc_yprim applies the tap to bus1 by default, which matches.
circuit.add_transformer("T_Left", "Left", "1_TransmissionBus", 0.1, 0.8, tap=1.05)
circuit.add_transformer("T_Right", "Right", "1_TransmissionBus", 0.1, 0.8, tap=1.05)

# -------------------------
# Branches
# -------------------------

# Substation tie between Left and Right
circuit.add_branch(
    "Tie_Left_Right",
    "Left", "Right",
    0.0, 0.01, 0.0, 0.0,
    branch_type="breaker",
    status="Closed"
)

# Left feeder
circuit.add_branch("L_Left_4com", "Left", "4com", 0.0964, 0.1995, 0.0, 0.0, branch_type="line", status="Closed")
circuit.add_branch("L_4com_5ind", "4com", "5ind", 0.0964, 0.1995, 0.0, 0.0, branch_type="line", status="Closed")
circuit.add_branch("L_5ind_6com", "5ind", "6com", 0.0964, 0.1995, 0.0, 0.0, branch_type="line", status="Closed")
circuit.add_branch("L_6com_7res", "6com", "7res", 0.0964, 0.1995, 0.0, 0.0, branch_type="line", status="Closed")
circuit.add_branch("L_7res_8ind", "7res", "8ind", 0.0964, 0.1995, 0.0, 0.0, branch_type="line", status="Closed")

# Right feeder
circuit.add_branch("L_Right_9com", "Right", "9com", 0.0964, 0.1995, 0.0, 0.0, branch_type="line", status="Closed")
circuit.add_branch("L_9com_10res", "9com", "10res", 0.0964, 0.1995, 0.0, 0.0, branch_type="line", status="Closed")
circuit.add_branch("L_10res_11res", "10res", "11res", 0.0964, 0.1995, 0.0, 0.0, branch_type="line", status="Closed")
circuit.add_branch("L_11res_12res", "11res", "12res", 0.0964, 0.1995, 0.0, 0.0, branch_type="line", status="Closed")
circuit.add_branch("L_12res_13ind", "12res", "13ind", 0.0964, 0.1995, 0.0, 0.0, branch_type="line", status="Closed")

# Bottom tie
circuit.add_branch(
    "L_8ind_13ind",
    "8ind", "13ind",
    0.0964, 0.1995, 0.0, 0.0,
    branch_type="tie_switch",
    status="Closed"
)

# -------------------------
# Loads
# -------------------------
circuit.add_load("Load_4com", "4com", 1.00, 0.40)
circuit.add_load("Load_5ind", "5ind", 1.00, 0.60)
circuit.add_load("Load_6com", "6com", 1.00, 0.50)
circuit.add_load("Load_7res", "7res", 1.00, 0.30)
circuit.add_load("Load_8ind", "8ind", 1.00, 0.60)

circuit.add_load("Load_9com", "9com", 1.00, 0.50)
circuit.add_load("Load_10res", "10res", 1.00, 0.30)
circuit.add_load("Load_11res", "11res", 1.00, 0.30)
circuit.add_load("Load_12res", "12res", 1.00, 0.30)
circuit.add_load("Load_13ind", "13ind", 1.00, 0.60)

# -------------------------
# Switched shunts / capacitor banks
# -------------------------
circuit.add_capacitor_bank("Cap_5ind", "5ind", 1.0, status="Closed")
circuit.add_capacitor_bank("Cap_7res", "7res", 1.0, status="Closed")
circuit.add_capacitor_bank("Cap_8ind", "8ind", 1.0, status="Closed")
circuit.add_capacitor_bank("Cap_10res", "10res", 1.0, status="Closed")
circuit.add_capacitor_bank("Cap_12res", "12res", 1.0, status="Closed")
circuit.add_capacitor_bank("Cap_13ind", "13ind", 1.0, status="Closed")

# -------------------------
# Solve
# -------------------------
circuit.calc_ybus()
solver = circuit.solve(mode="power_flow", tol=1e-6, max_iter=50, verbose=True)
circuit.print_case_losses()
print("Bus Voltage Results")
print("-" * 40)
for name, bus in circuit.buses.items():
    print(f"{name:20s}  Vpu = {bus.vpu:.5f}   Angle = {bus.delta:.2f} deg")
print("Branch Statuses")
print("-" * 40)
for name, br in circuit.branches.items():
    print(f"{name:20s} {br.branch_type:15s} {'Closed' if br.status else 'Open'}")
# Diagnostic: confirm transformer bus ordering
print("Transformers")
print("-" * 40)
for name, xfmr in circuit.transformers.items():
    print(f"{name:10s} bus1={xfmr.bus1_name:20s} bus2={xfmr.bus2_name:20s} "
          f"tap={xfmr.tap} tap_side={xfmr.tap_side}")
print("Capacitor Banks")
print("-" * 40)
for name, cap in circuit.capacitor_banks.items():
    print(f"{name:15s} bus={cap.bus1_name:10s} status={'Closed' if cap.status else 'Open'}")
print(solver)
