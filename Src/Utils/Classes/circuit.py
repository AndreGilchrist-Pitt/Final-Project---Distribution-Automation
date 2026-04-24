from typing import Optional
import numpy as np

from Src.Utils.Classes.bus import Bus
from Src.Utils.Classes.transformer import Transformer
from Src.Utils.Classes.transmissionLine import TransmissionLine
from Src.Utils.Classes.generator import Generator
from Src.Utils.Classes.load import Load
from Src.Utils.Classes.settings import Settings
from Src.Utils.Classes.solver import Solver
from Src.Utils.Classes.branch import Branch
class Circuit:
    """
    Represents a complete power system network.

    The Circuit class serves as a container for all equipment objects
    (buses, transformers, transmission lines, generators, and loads).
    """

    def __init__(self, name: str):
        """
        Initialize a Circuit instance.

        Args:
            name: The name of the circuit
        """
        self.name = name
        self.buses = {}
        self.transformers = {}
        self.transmission_lines = {}
        self.generators = {}
        self.loads = {}
        self.ybus = None
        self.solver: Optional[Solver] = None
        self.branches = {}
    def calc_ybus(self):
        """
        Compute the system Ybus (nodal admittance) matrix.

        Assembles Ybus by stamping the primitive admittance matrices of all
        transformers and transmission lines into an N×N complex matrix,
        where N is the number of buses.

        Updates self.ybus in-place. Does not return a value.

        Raises:
            ValueError: If an element references a bus not in the circuit,
                        if a connected bus has a zero diagonal entry,
                        or if Ybus is not symmetric.
        """
        N = len(self.buses) # NxN Ybus Matrix
        self.ybus = np.zeros((N, N), dtype=complex)
        bus_index = {name: idx for idx, name in enumerate(self.buses)}

        # Collect all power delivery elements
        pd_elements = list(self.transformers.values()) + list(self.transmission_lines.values())

        # Cache each element's yprim so we don't compute it twice
        element_yprims = []
        for element in pd_elements:
            yprim = element.calc_yprim()
            element_yprims.append((element, yprim))

        # --- Validation: check that every referenced bus exists ---
        for element, yprim in element_yprims:
            for bus_name in yprim.index:
                if bus_name not in bus_index:
                    raise ValueError(
                        f"Element '{element.name}' references bus '{bus_name}' not in circuit")

        # --- Stamp each primitive matrix into Ybus ---
        # Updates Ybus with Yprim elements

        for element, yprim in element_yprims:
            indices = [bus_index[b] for b in yprim.index]
            # Use numpy advanced indexing to stamp the full 2×2 block at once
            ix = np.ix_(indices, indices)
            self.ybus[ix] += yprim.values

        # --- Post-assembly consistency checks ---
        # Check that all connected buses have non-zero diagonal entries
        # This builds a set of only the buses that have at least one element connected to them.
        # If isolated bus (no transformer or line), it would not appear because an isolated bus has a legitimately zero diagonal.

        connected_buses = set()
        for _, yprim in element_yprims:
            connected_buses.update(yprim.index)

        # For each connected bus, it checks whether the diagonal entry Ybus[i,i] is zero.
        # The diagonal of Ybus represents the self-admittance — the sum of all admittances connected to that bus.
        # If a bus has elements connected to it but its diagonal is still zero, something went wrong during stamping (a bug, or pathological element values that cancel out exactly).

        for bus_name in connected_buses:
            idx = bus_index[bus_name]
            if self.ybus[idx, idx] == 0:
                raise ValueError(f"Bus '{bus_name}' has a zero diagonal entry in Ybus")

        # This checks that Ybus equals its own transpose (within a floating-point tolerance of 1e-10).
        # Since every individual yprim is symmetric, and stamping adds them into matching [i,j] and [j,i] positions, the final Ybus must be symmetric.
        # If it's not, it means there's a bug in the stamping logic or in one of the calc_yprim() methods.
        # np.allclose is used instead of == because complex floating-point arithmetic can introduce tiny rounding errors (e.g., 1e-16 differences)

        if not np.allclose(self.ybus, self.ybus.T, atol=1e-10):
            raise ValueError("Ybus is not symmetric")

        # Summary
        # Check             What it catches                                     Why it matters
        # Zero diagonal     A connected bus with no net self-admittance         Indicates a stamping bug or degenerate element values
        # Symmetry          Ybus[i,j] ≠ Ybus[j,i]                               All bilateral elements produce symmetric yprim, so asymmetry = a bug
    def add_bus(self, name: str, nominal_kv: float,vpu:float = 1.0,delta:float = 0.0,bus_type: str = None,
                area_class: str = None):
        """
        Add a bus to the circuit.

        Args:
            name: The name of the bus
            nominal_kv: The nominal voltage in kilovolts

        Raises:
            ValueError: If a bus with the same name already exists
        """
        if name in self.buses:
            raise ValueError(f"Bus '{name}' already exists in the circuit")

        bus = Bus(name, nominal_kv,vpu=vpu,delta=delta, bus_type=bus_type, area_class=area_class)
        self.buses[name] = bus
    def add_transformer(self, name: str, bus1_name: str, bus2_name: str, r: float, x: float, status: str = "Closed"):
        """
        Add a transformer to the circuit.

        Args:
            name: The name of the transformer
            bus1_name: Name of the first bus
            bus2_name: Name of the second bus
            r: Resistance in per-unit or ohms
            x: Reactance in per-unit or ohms

        Raises:
            ValueError: If a transformer with the same name already exists
        """
        if name in self.transformers:
            raise ValueError(f"Transformer '{name}' already exists in the circuit")

        transformer = Transformer(name, bus1_name, bus2_name, r, x,status)
        self.transformers[name] = transformer
        self.add_branch(name, bus1_name, bus2_name, r, x, branch_type="transformer", status=status)
    def add_transmission_line(self, name: str, bus1_name: str, bus2_name: str,
                             r: float, x: float, g: float, b: float, status: str = "Closed"):
        """
        Add a transmission line to the circuit.

        Args:
            name: The name of the transmission line
            bus1_name: Name of the first bus
            bus2_name: Name of the second bus
            r: Series resistance in per-unit or ohms
            x: Series reactance in per-unit or ohms
            g: Shunt conductance in per-unit or siemens
            b: Shunt susceptance in per-unit or siemens

        Raises:
            ValueError: If a transmission line with the same name already exists
        """
        if name in self.transmission_lines:
            raise ValueError(f"Transmission line '{name}' already exists in the circuit")

        line = TransmissionLine(name, bus1_name, bus2_name, r, x, g, b,status)
        self.transmission_lines[name] = line
        self.add_branch(name, bus1_name, bus2_name, r, x, branch_type="line", status=status)
    def add_generator(self, name: str, bus1_name: str, voltage_setpoint: float, mw_setpoint: float,x_subtransient: float = 0.0):
        """
        Add a generator to the circuit.

        Args:
            name: The name of the generator
            bus1_name: Name of the bus where the generator is connected
            voltage_setpoint: Voltage magnitude setpoint in per-unit
            mw_setpoint: Active power generation setpoint in megawatts (MW)
            x_subtransient: Subtransient reactance in per-unit (default 0.0)
        Raises:
            ValueError: If a generator with the same name already exists
        """
        if name in self.generators:
            raise ValueError(f"Generator '{name}' already exists in the circuit")

        generator = Generator(name, bus1_name, voltage_setpoint, mw_setpoint,x_subtransient)
        self.generators[name] = generator
    def add_load(self, name: str, bus1_name: str, mw: float, mvar: float):
        """
        Add a load to the circuit.

        Args:
            name: The name of the load
            bus1_name: Name of the bus where the load is connected
            mw: Active power consumption in megawatts (MW)
            mvar: Reactive power consumption in megavars (MVAR)

        Raises:
            ValueError: If a load with the same name already exists
        """
        if name in self.loads:
            raise ValueError(f"Load '{name}' already exists in the circuit")

        load = Load(name, bus1_name, mw, mvar)
        self.loads[name] = load
    @property
    def voltage_vector_polar(self):
        return [(bus.vpu, bus.delta) for bus in self.buses.values()]
    @property
    def voltage_vector_rectangular(self):
        N = len(self.buses)
        V = np.zeros(N, dtype=complex)
        for idx, bus in enumerate(self.buses):
            magnitude = self.buses[bus].vpu
            angle = np.deg2rad(self.buses[bus].delta)
            V[idx] = magnitude * np.exp(1j * angle)
        return V

    def _real_power_injection(self, bus: Bus, ybus, voltages) -> float:
        """
        Compute real power injection at a bus using the polar form.

        Pi = |Vi| * sum_j( |Vj| * (Gij*cos(δij) + Bij*sin(δij)) )

        Args:
            bus: The Bus object at which to compute Pi
            ybus: System admittance matrix
            voltages: Complex voltage vector (per-unit)

        Returns:
            P_i: Real power injection in per-unit
        """
        i = bus.bus_index
        V_i = np.abs(voltages[i])
        delta_i = np.angle(voltages[i])

        P_i = 0.0
        for j in range(len(voltages)):
            V_j = np.abs(voltages[j])
            delta_ij = delta_i - np.angle(voltages[j])
            G_ij = ybus[i, j].real
            B_ij = ybus[i, j].imag
            P_i += V_j * (G_ij * np.cos(delta_ij) + B_ij * np.sin(delta_ij))

        return V_i * P_i
    def _reactive_power_injection(self, bus: Bus, ybus, voltages) -> float:
        """
        Compute reactive power injection at a bus using the polar form.

        Qi = |Vi| * sum_j( |Vj| * (Gij*sin(δij) - Bij*cos(δij)) )

        Args:
            bus: The Bus object at which to compute Qi
            ybus: System admittance matrix
            voltages: Complex voltage vector (per-unit)

        Returns:
            Q_i: Reactive power injection in per-unit
        """
        i = bus.bus_index
        V_i = np.abs(voltages[i])
        delta_i = np.angle(voltages[i])

        Q_i = 0.0
        for j in range(len(voltages)):
            V_j = np.abs(voltages[j])
            delta_ij = delta_i - np.angle(voltages[j])
            G_ij = ybus[i, j].real
            B_ij = ybus[i, j].imag
            Q_i += V_j * (G_ij * np.sin(delta_ij) - B_ij * np.cos(delta_ij))

        return V_i * Q_i
    def compute_power_injection(self, bus: Bus, ybus, voltages):
        """
        Compute both real and reactive power injection at a bus.

        Args:
            bus: The Bus object at which to compute power
            ybus: System admittance matrix
            voltages: Complex voltage vector (per-unit)

        Returns:
            (P_i, Q_i): Tuple of real and reactive power in per-unit
        """
        P_i = self._real_power_injection(bus, ybus, voltages)
        Q_i = self._reactive_power_injection(bus, ybus, voltages)
        return P_i, Q_i

    def compute_power_mismatch(self, buses: dict, ybus, voltages) -> np.ndarray:
        """
        Compute the power mismatch vector f for all non-slack buses.

        ΔP_i = P_spec - P_calc  (all non-slack buses)
        ΔQ_i = Q_spec - Q_calc  (PQ buses only)

        Args:
            buses: Dictionary of bus objects {name: Bus}
            ybus: System admittance matrix
            voltages: Complex voltage vector (per-unit)

        Returns:
            f: list of mismatches [ΔP (non-slack), ΔQ (PQ only)]
        """
        specs = {bus_name: [0.0, 0.0] for bus_name in buses}

        for gen in self.generators.values():
            specs[gen.bus1_name][0] += gen.p  # add generation

        for load in self.loads.values():
            specs[load.bus1_name][0] -= load.p  # subtract load P
            specs[load.bus1_name][1] -= load.q  # subtract load Q
        non_slack_buses = [b for b in buses.values() if b.bus_type != "Slack"]
        pq_buses = [b for b in buses.values() if b.bus_type == "PQ"]

        f = []

        for bus in non_slack_buses:
            p_spec, _ = specs[bus.name]
            p_calc, _ = self.compute_power_injection(bus, ybus, voltages)
            f.append(p_spec - p_calc)

        for bus in pq_buses:
            _, q_spec = specs[bus.name]
            _, q_calc = self.compute_power_injection(bus, ybus, voltages)
            f.append(q_spec - q_calc)

        return np.asarray(f, dtype=float)

    def bus_angles(self):
        angles = np.array([np.deg2rad(bus.delta) for bus in self.buses.values()])
        return angles
    def bus_voltages(self):
        voltages = np.array([bus.vpu for bus in self.buses.values()])
        return voltages

    def calc_ybus_fault(self) -> np.ndarray:
        N = len(self.buses)
        bus_index = {name: idx for idx, name in enumerate(self.buses)}
        ybus_fault = np.zeros((N, N), dtype=complex)

        for xfmr in self.transformers.values():
            i = bus_index[xfmr.bus1_name]
            j = bus_index[xfmr.bus2_name]
            y = 1 / (1j * xfmr.x)
            ybus_fault[i, i] += y
            ybus_fault[j, j] += y
            ybus_fault[i, j] -= y
            ybus_fault[j, i] -= y

        for line in self.transmission_lines.values():
            i = bus_index[line.bus1_name]
            j = bus_index[line.bus2_name]
            y = 1 / (1j * line.x)
            ybus_fault[i, i] += y
            ybus_fault[j, j] += y
            ybus_fault[i, j] -= y
            ybus_fault[j, i] -= y

        for gen in self.generators.values():
            if gen.x_subtransient == 0.0:
                raise ValueError(
                    f"Generator '{gen.name}' has x_subtransient=0. "
                    "Set a valid subtransient reactance for fault analysis."
                )
            i = bus_index[gen.bus1_name]
            ybus_fault[i, i] += 1 / (1j * gen.x_subtransient)

        return ybus_fault

    def calc_zbus(self, ybus_fault: np.ndarray) -> np.ndarray:
        """
        Compute the bus impedance matrix by inverting the faulted Ybus.

        Args:
            ybus_fault: The faulted Ybus matrix (N×N complex ndarray).

        Returns:
            zbus: N×N complex bus impedance matrix.
        """
        zbus = np.linalg.inv(ybus_fault)
        return zbus

    def calc_fault_current(self, zbus: np.ndarray, faulted_bus_name: str,
                           prefault_voltage: float = 1.0) -> complex:
        """
        Calculate the fault current for a bolted three-phase fault.

        Args:
            zbus: Bus impedance matrix (N×N complex ndarray).
            faulted_bus_name: Name of the bus where the fault occurs.
            prefault_voltage: Prefault voltage in per-unit (default 1.0).

        Returns:
            I_fault: Fault current in per-unit (complex).
        """
        bus_index = {name: idx for idx, name in enumerate(self.buses)}
        n = bus_index[faulted_bus_name]
        Z_nn = zbus[n, n]
        return prefault_voltage / Z_nn

    def calc_fault_voltages(self, zbus: np.ndarray, faulted_bus_name: str,
                            prefault_voltage: float = 1.0) -> dict:
        """
        Calculate post-fault bus voltages for a bolted three-phase fault.

        Vi_post = Vf - (Z_in / Z_nn) * Vf  for each bus i.
        The faulted bus voltage will be 0.0 p.u.

        Args:
            zbus: Bus impedance matrix (N×N complex ndarray).
            faulted_bus_name: Name of the faulted bus.
            prefault_voltage: Prefault voltage in per-unit (default 1.0).

        Returns:
            voltages: Dict of {bus_name: post-fault voltage (complex p.u.)}.
        """
        bus_index = {name: idx for idx, name in enumerate(self.buses)}
        n = bus_index[faulted_bus_name]
        Z_nn = zbus[n, n]

        voltages = {}
        for bus_name, idx in bus_index.items():
            Z_in = zbus[idx, n]
            voltages[bus_name] = prefault_voltage - (Z_in / Z_nn) * prefault_voltage

        return voltages

    def solve(self, mode: str = "power_flow", tol: float = 1e-4,
              max_iter: int = 50, faulted_bus_name: str = None,
              prefault_voltage: float = 1.0, verbose: bool = False) -> Solver:
        """
        Run power flow or fault analysis on this circuit.

        Power flow uses self.ybus (lines + transformers).
        Fault study uses self.ybus_fault (adds generator subtransient reactances).
        """
        if mode == "power_flow":
            if self.ybus is None:
                self.calc_ybus()
        elif mode == "fault":
            self.calc_ybus_fault()

        self.solver = Solver(mode=mode)
        self.solver.run(
            self,
            tol=tol,
            max_iter=max_iter,
            faulted_bus_name=faulted_bus_name,
            prefault_voltage=prefault_voltage,
            verbose=verbose,
        )
        return self.solver

    def add_branch(self, name: str, from_bus: str, to_bus: str,
                   r: float, x: float,
                   g: float = 0.0, b: float = 0.0,
                   branch_type: str = "line",
                   status: str = "Closed"):
        if name in self.branches:
            raise ValueError(f"Branch '{name}' already exists in the circuit")

        branch = Branch(from_bus, to_bus, r, x, g, b, branch_type=branch_type, status=status)
        self.branches[name] = branch
if __name__ == "__main__":
    # Validation tests from Milestone 2
    print("=== Moved to MilestoneValidationHelp ===\n")

    
