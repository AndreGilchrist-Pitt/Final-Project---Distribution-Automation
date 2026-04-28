from Src.Utils.Classes.bus import Bus
from Src.Utils.Classes.circuit import Circuit

def build_feeder_network(case_name: str = "Chapter14_Feeder_BaseCase") -> Circuit:
    """
    Build the Chapter 14 feeder network.

    Assumes Settings(...) and AreaScalar(...) have already been configured
    before this function is called.
    """
    # Reset global bus state so repeated builds do not reuse old bus indexes.
    Bus._bus_counter = 0
    Bus._bus_registry.clear()
    Bus._bus_objects.clear()

    circuit = Circuit(case_name)

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
    # Generators
    # -------------------------
    circuit.add_generator("G_Source","1_TransmissionBus",voltage_setpoint=1.0,mw_setpoint=0.0)

    # -------------------------
    # Transformers
    # -------------------------
    circuit.add_transformer("T_Left", "Left", "1_TransmissionBus", 0.1, 0.8, tap=1.05)
    circuit.add_transformer("T_Right", "Right", "1_TransmissionBus", 0.1, 0.8, tap=1.05)

    # -------------------------
    # Branches
    # -------------------------
    circuit.add_branch(
        "Tie_Left_Right",
        "Left", "Right",
        0.0, 0.01, 0.0, 0.0,
        branch_type="breaker",
        status="Closed",
    )

    circuit.add_branch("L_Left_4com", "Left", "4com", 0.0964, 0.1995, 0.0, 0.0, branch_type="line", status="Closed")
    circuit.add_branch("L_4com_5ind", "4com", "5ind", 0.0964, 0.1995, 0.0, 0.0, branch_type="line", status="Closed")
    circuit.add_branch("L_5ind_6com", "5ind", "6com", 0.0964, 0.1995, 0.0, 0.0, branch_type="line", status="Closed")
    circuit.add_branch("L_6com_7res", "6com", "7res", 0.0964, 0.1995, 0.0, 0.0, branch_type="line", status="Closed")
    circuit.add_branch("L_7res_8ind", "7res", "8ind", 0.0964, 0.1995, 0.0, 0.0, branch_type="line", status="Closed")

    circuit.add_branch("L_Right_9com", "Right", "9com", 0.0964, 0.1995, 0.0, 0.0, branch_type="line",
                       status="Closed")
    circuit.add_branch("L_9com_10res", "9com", "10res", 0.0964, 0.1995, 0.0, 0.0, branch_type="line",
                       status="Closed")
    circuit.add_branch("L_10res_11res", "10res", "11res", 0.0964, 0.1995, 0.0, 0.0, branch_type="line",
                       status="Closed")
    circuit.add_branch("L_11res_12res", "11res", "12res", 0.0964, 0.1995, 0.0, 0.0, branch_type="line",
                       status="Closed")
    circuit.add_branch("L_12res_13ind", "12res", "13ind", 0.0964, 0.1995, 0.0, 0.0, branch_type="line",
                       status="Closed")

    circuit.add_branch(
        "L_8ind_13ind",
        "8ind", "13ind",
        0.0964, 0.1995, 0.0, 0.0,
        branch_type="tie_switch",
        status="Closed",
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

    circuit.print_elements()
    return circuit
