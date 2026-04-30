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
from Src.Utils.Classes.capacitorbank import CapacitorBank
from Src.Utils.Classes.areascalar import AreaScalar
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
        self.capacitor_banks = {}

    def calc_ybus(self):
        N = len(self.buses)
        self.ybus = np.zeros((N, N), dtype=complex)
        bus_index = {name: idx for idx, name in enumerate(self.buses)}

        active_elements = []

        for xfmr in self.transformers.values():
            if xfmr.status == "Closed" or xfmr.status is True:
                active_elements.append(xfmr)

        for branch in self.branches.values():
            if branch.branch_type != "transformer" and branch.is_closed():
                active_elements.append(branch)

        element_yprims = []
        for element in active_elements:
            yprim = element.calc_yprim()
            element_yprims.append((element, yprim))

        for element, yprim in element_yprims:
            for bus_name in yprim.index:
                if bus_name not in bus_index:
                    raise ValueError(
                        f"Element '{element.name}' references bus '{bus_name}' not in circuit"
                    )

        for element, yprim in element_yprims:
            indices = [bus_index[b] for b in yprim.index]
            ix = np.ix_(indices, indices)
            self.ybus[ix] += yprim.values

        # Stamp closed capacitor banks as bus shunt susceptance
        for cap in self.capacitor_banks.values():
            if not cap.is_closed():
                continue

            if cap.bus1_name not in bus_index:
                raise ValueError(
                    f"Capacitor bank '{cap.name}' references bus '{cap.bus1_name}' not in circuit"
                )

            bus = self.buses[cap.bus1_name]

            if not getattr(bus, "in_service", True):
                continue

            i = bus_index[cap.bus1_name]
            self.ybus[i, i] += 1j * cap.b_shunt_pu

        if not np.allclose(self.ybus, self.ybus.T, atol=1e-10):
            raise ValueError("Ybus is not symmetric")
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
    def add_transformer(self, name: str, bus1_name: str, bus2_name: str, r: float, x: float, status: str = "Closed",
                        tap: float = 1.0, tap_side: str = "bus1"):
        """
        Add a transformer to the circuit.

        Args:
            name: The name of the transformer
            bus1_name: Name of the first bus
            bus2_name: Name of the second bus
            r: Resistance in per-unit or ohms
            x: Reactance in per-unit or ohms
            tap: Off-nominal tap ratio (default: 1.0)
            tap_side: Which bus the tap is on — "bus1" or "bus2" (default: "bus1")
        Raises:
            ValueError: If a transformer with the same name already exists
        """
        if name in self.transformers:
            raise ValueError(f"Transformer '{name}' already exists in the circuit")

        transformer = Transformer(name, bus1_name, bus2_name, r, x,status,tap=tap, tap_side=tap_side)
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
        self.add_branch(name, bus1_name, bus2_name, r, x, g, b, branch_type="line", status=status)
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
        Compute the power mismatch vector f for energized buses only.

        ΔP_i = P_spec - P_calc  for energized non-slack buses
        ΔQ_i = Q_spec - Q_calc  for energized PQ buses only

        De-energized/islanded buses are excluded from the Newton-Raphson solve.
        """
        specs = {bus_name: [0.0, 0.0] for bus_name in buses}

        for gen in self.generators.values():
            bus = self.buses[gen.bus1_name]

            if getattr(bus, "in_service", True):
                specs[gen.bus1_name][0] += gen.p

        for load in self.loads.values():
            bus = self.buses[load.bus1_name]

            if not getattr(bus, "in_service", True):
                continue

            specs[load.bus1_name][0] -= load.p
            specs[load.bus1_name][1] -= load.q

        non_slack_buses = [
            b for b in buses.values()
            if b.bus_type != "Slack" and getattr(b, "in_service", True)
        ]

        pq_buses = [
            b for b in buses.values()
            if b.bus_type == "PQ" and getattr(b, "in_service", True)
        ]

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

        for branch in self.branches.values():
            if not branch.status:
                continue

            i = bus_index[branch.from_bus]
            j = bus_index[branch.to_bus]

            # Fault studies usually ignore resistance and shunt charging,
            # using reactance-only models
            if branch.x == 0.0:
                raise ValueError(
                    f"Branch between {branch.from_bus} and {branch.to_bus} has x=0.0 in fault model."
                )

            y = 1 / (1j * branch.x)
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

        This method does not automatically change switch states.
        Any manual or automatic distribution automation switching should be
        applied before calling solve().
        """
        if mode == "power_flow":
            self.update_bus_energization()
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

        branch = Branch(name,from_bus, to_bus, r, x, g, b, branch_type=branch_type, status=status)
        self.branches[name] = branch

    def add_capacitor_bank(self, name: str, bus1_name: str, mvar_nominal: float, status: str = "Closed"):
        """
        Add a bus-connected switched shunt capacitor bank.

        Args:
            name: Capacitor bank name
            bus1_name: Name of the connected bus
            mvar_nominal: Nominal reactive injection in Mvar
            status: "Closed" or "Open"

        Raises:
            ValueError: If a capacitor with the same name already exists
        """
        if name in self.capacitor_banks:
            raise ValueError(f"Capacitor bank '{name}' already exists in the circuit")

        if bus1_name not in self.buses:
            raise ValueError(f"Bus '{bus1_name}' not found in the circuit")

        cap = CapacitorBank(name, bus1_name, mvar_nominal, status)
        self.capacitor_banks[name] = cap

    def open_branch(self, name: str) -> None:
        if name not in self.branches:
            raise ValueError(f"Branch '{name}' not found")
        self.branches[name].open()
        self.ybus = None

    def close_branch(self, name: str) -> None:
        if name not in self.branches:
            raise ValueError(f"Branch '{name}' not found")
        self.branches[name].close()
        self.ybus = None

    def active_power_delivery_elements(self):
        """
        Return active two-terminal elements connected to energized buses only.

        This should match the same physical elements used in calc_ybus().
        """
        active_elements = []

        for xfmr in self.transformers.values():
            if not (xfmr.status == "Closed" or xfmr.status is True):
                continue

            if not getattr(self.buses[xfmr.bus1_name], "in_service", True):
                continue

            if not getattr(self.buses[xfmr.bus2_name], "in_service", True):
                continue

            active_elements.append(xfmr)

        for branch in self.branches.values():
            if branch.branch_type == "transformer":
                continue

            if not branch.is_closed():
                continue

            if not getattr(self.buses[branch.from_bus], "in_service", True):
                continue

            if not getattr(self.buses[branch.to_bus], "in_service", True):
                continue

            active_elements.append(branch)

        return active_elements

    def calc_branch_losses(self):
        """
        Calculate complex power losses for each active branch/transformer.

        Returns:
            dict:
                {
                    element_name: {
                        "from_bus": str,
                        "to_bus": str,
                        "s_from_to_pu": complex,
                        "s_to_from_pu": complex,
                        "loss_pu": complex,
                        "loss_mw": float,
                        "loss_mvar": float,
                    }
                }
        """
        if self.ybus is None:
            self.calc_ybus()

        voltages = self.voltage_vector_rectangular
        bus_index = {name: idx for idx, name in enumerate(self.buses)}

        losses = {}

        for element in self.active_power_delivery_elements():
            yprim = element.calc_yprim()

            bus_names = list(yprim.index)
            from_bus = bus_names[0]
            to_bus = bus_names[1]

            i = bus_index[from_bus]
            j = bus_index[to_bus]

            v_local = np.array([voltages[i], voltages[j]], dtype=complex)

            # Current injected into the element from each terminal
            i_local = yprim.values @ v_local

            s_from = v_local[0] * np.conj(i_local[0])
            s_to = v_local[1] * np.conj(i_local[1])

            s_loss = s_from + s_to

            losses[element.name] = {
                "from_bus": from_bus,
                "to_bus": to_bus,
                "s_from_to_pu": s_from,
                "s_to_from_pu": s_to,
                "loss_pu": s_loss,
                "loss_mw": s_loss.real * Settings.sbase,
                "loss_mvar": s_loss.imag * Settings.sbase,
            }

        return losses

    def calc_case_losses(self):
        """
        Calculate total case losses.

        Returns:
            tuple:
                (total_loss_pu, total_loss_mw, total_loss_mvar)
        """
        branch_losses = self.calc_branch_losses()

        total_loss_pu = sum(
            item["loss_pu"] for item in branch_losses.values()
        )

        total_loss_mw = total_loss_pu.real * Settings.sbase
        total_loss_mvar = total_loss_pu.imag * Settings.sbase

        return total_loss_pu, total_loss_mw, total_loss_mvar

    def print_case_losses(self):
        total_loss_pu, total_loss_mw, total_loss_mvar = self.calc_case_losses()

        print("Case Losses")
        print("-" * 40)
        print(f"Total Loss: {total_loss_pu.real:.8f} pu")
        print(f"Total Loss: {total_loss_mw:.6f} MW")
        print(f"Reactive Loss: {total_loss_mvar:.6f} Mvar")

    def find_energized_buses(self) -> set[str]:
        """
        Return all buses reachable from any Slack bus through closed branches.

        Buses not returned by this function are de-energized/islanded
        from the source and should not be included in the active power-flow solve.
        """
        slack_buses = [
            bus.name for bus in self.buses.values()
            if bus.bus_type == "Slack"
        ]

        if not slack_buses:
            raise ValueError("No Slack bus found in circuit.")

        neighbors = self.build_neighbor_map(closed_only=True)

        energized = set()
        stack = list(slack_buses)

        while stack:
            current = stack.pop()

            if current in energized:
                continue

            energized.add(current)

            for neighbor in neighbors[current]:
                if neighbor not in energized:
                    stack.append(neighbor)

        return energized

    def update_bus_energization(self) -> set[str]:
        """
        Update each bus with an in_service flag based on source connectivity.

        Energized buses:
            in_service = True
            If voltage was previously forced to 0.0 because the bus was de-energized,
            reset it to a valid Newton-Raphson starting guess.

        De-energized buses:
            in_service = False
            vpu = 0.0
            delta = 0.0

        Returns:
            Set of energized bus names.
        """
        energized = self.find_energized_buses()

        for bus in self.buses.values():
            bus.in_service = bus.name in energized

            if bus.in_service:
                # If this bus was previously de-energized, its voltage may still be 0.0.
                # Newton-Raphson cannot use a zero voltage magnitude for an active PQ bus.
                if np.isclose(bus.vpu, 0.0):
                    bus.vpu = 1.0
                    bus.delta = 0.0

            else:
                bus.vpu = 0.0
                bus.delta = 0.0

        return energized
    def print_elements(self) -> None:
        """
        Print all elements in the circuit and their main parameters.
        """

        print("=" * 80)
        print(f"Circuit: {self.name}")
        print("=" * 80)

        print("\nSettings")
        print("-" * 80)
        print(f"Frequency : {Settings.freq} Hz")
        print(f"Sbase     : {Settings.sbase} MVA")

        print("\nArea Scalars")
        print("-" * 80)
        print(f"Residential : {AreaScalar.res_scale}")
        print(f"Commercial  : {AreaScalar.com_scale}")
        print(f"Industrial  : {AreaScalar.ind_scale}")

        print("\nBuses")
        print("-" * 80)
        if not self.buses:
            print("No buses defined.")
        else:
            print(f"{'Name':20s} {'Index':>5s} {'kV':>10s} {'Type':>8s} {'Area':>15s} {'Vpu':>10s} {'Angle':>10s}")
            for bus in self.buses.values():
                print(
                    f"{bus.name:20s} "
                    f"{bus.bus_index:5d} "
                    f"{bus.nominal_kv:10.4f} "
                    f"{bus.bus_type:>8s} "
                    f"{str(bus.area_class):>15s} "
                    f"{bus.vpu:10.5f} "
                    f"{bus.delta:10.4f}"
                )

        print("\nTransformers")
        print("-" * 80)
        if not self.transformers:
            print("No transformers defined.")
        else:
            print(
                f"{'Name':20s} {'Bus 1':20s} {'Bus 2':20s} "
                f"{'R':>10s} {'X':>10s} {'Tap':>10s} {'Tap Side':>10s} {'Status':>10s}"
            )
            for xfmr in self.transformers.values():
                status = "Closed" if xfmr.status == "Closed" or xfmr.status is True else "Open"
                print(
                    f"{xfmr.name:20s} "
                    f"{xfmr.bus1_name:20s} "
                    f"{xfmr.bus2_name:20s} "
                    f"{xfmr.r:10.5f} "
                    f"{xfmr.x:10.5f} "
                    f"{xfmr.tap:10.5f} "
                    f"{xfmr.tap_side:>10s} "
                    f"{status:>10s}"
                )

        print("\nBranches")
        print("-" * 80)
        if not self.branches:
            print("No branches defined.")
        else:
            print(
                f"{'Name':20s} {'From Bus':20s} {'To Bus':20s} "
                f"{'Type':>15s} {'R':>10s} {'X':>10s} {'G':>10s} {'B':>10s} {'Status':>10s}"
            )
            for branch in self.branches.values():
                status = "Closed" if branch.status else "Open"
                print(
                    f"{branch.name:20s} "
                    f"{branch.from_bus:20s} "
                    f"{branch.to_bus:20s} "
                    f"{branch.branch_type:>15s} "
                    f"{branch.r:10.5f} "
                    f"{branch.x:10.5f} "
                    f"{branch.g:10.5f} "
                    f"{branch.b:10.5f} "
                    f"{status:>10s}"
                )

        print("\nTransmission Lines")
        print("-" * 80)
        if not self.transmission_lines:
            print("No transmission lines defined.")
        else:
            print(
                f"{'Name':20s} {'Bus 1':20s} {'Bus 2':20s} "
                f"{'R':>10s} {'X':>10s} {'G':>10s} {'B':>10s} {'Status':>10s}"
            )
            for line in self.transmission_lines.values():
                print(
                    f"{line.name:20s} "
                    f"{line.bus1_name:20s} "
                    f"{line.bus2_name:20s} "
                    f"{line.r:10.5f} "
                    f"{line.x:10.5f} "
                    f"{line.g:10.5f} "
                    f"{line.b:10.5f} "
                    f"{line.status:>10s}"
                )

        print("\nGenerators")
        print("-" * 80)
        if not self.generators:
            print("No generators defined.")
        else:
            print(
                f"{'Name':20s} {'Bus':20s} "
                f"{'V Setpoint':>12s} {'MW':>10s} {'P pu':>10s} {'Xsub':>10s}"
            )
            for gen in self.generators.values():
                print(
                    f"{gen.name:20s} "
                    f"{gen.bus1_name:20s} "
                    f"{gen.voltage_setpoint:12.5f} "
                    f"{gen.mw_setpoint:10.5f} "
                    f"{gen.p:10.5f} "
                    f"{gen.x_subtransient:10.5f}"
                )

        print("\nLoads")
        print("-" * 80)
        if not self.loads:
            print("No loads defined.")
        else:
            print(
                f"{'Name':20s} {'Bus':20s} "
                f"{'MW':>10s} {'Mvar':>10s} {'P pu':>10s} {'Q pu':>10s}"
            )
            for load in self.loads.values():
                print(
                    f"{load.name:20s} "
                    f"{load.bus1_name:20s} "
                    f"{load.mw:10.5f} "
                    f"{load.mvar:10.5f} "
                    f"{load.p:10.5f} "
                    f"{load.q:10.5f}"
                )

        print("\nCapacitor Banks")
        print("-" * 80)
        if not self.capacitor_banks:
            print("No capacitor banks defined.")
        else:
            print(
                f"{'Name':20s} {'Bus':20s} "
                f"{'Mvar Nominal':>15s} {'B Shunt pu':>15s} {'Status':>10s}"
            )
            for cap in self.capacitor_banks.values():
                status = "Closed" if cap.status else "Open"
                print(
                    f"{cap.name:20s} "
                    f"{cap.bus1_name:20s} "
                    f"{cap.mvar_nominal:15.5f} "
                    f"{cap.b_shunt_pu:15.5f} "
                    f"{status:>10s}"
                )

        print("=" * 80)

    def build_neighbor_map(self, closed_only: bool = True) -> dict[str, set[str]]:
        """
        Build a bus-neighbor map.

        Args:
            closed_only:
                If True, only closed branches are included.
                If False, all branches are included.

        Returns:
            Dictionary mapping each bus name to a set of neighboring bus names.
        """
        neighbors = {bus_name: set() for bus_name in self.buses}

        for branch in self.branches.values():
            if closed_only and not branch.is_closed():
                continue

            neighbors[branch.from_bus].add(branch.to_bus)
            neighbors[branch.to_bus].add(branch.from_bus)

        return neighbors

    def find_deenergized_buses(self) -> set[str]:
        """
        Return all buses that are not reachable from any Slack bus through closed branches.
        """
        energized = self.find_energized_buses()
        return set(self.buses.keys()) - energized

    def print_energization_status(self) -> None:
        """
        Print whether each bus is energized or de-energized.
        """
        energized = self.find_energized_buses()

        print("Bus Energization Status")
        print("-" * 80)

        for bus in self.buses.values():
            status = "Energized" if bus.name in energized else "De-energized"
            print(f"{bus.name:20s} {status}")

    def find_open_boundary_switches(
            self,
            faulted_buses: set[str] | None = None,
            allowed_branch_types: set[str] | None = None,
    ):
        """
        Find open branches that connect energized buses to de-energized buses.

        These are candidate restoration switches.

        Args:
            faulted_buses:
                Buses that must not be re-energized.

            allowed_branch_types:
                Branch types allowed to be used for restoration.
                Defaults to {"tie_switch", "breaker", "sectionalizer"}.

        Returns:
            List of candidate Branch objects.
        """
        if faulted_buses is None:
            faulted_buses = set()

        if allowed_branch_types is None:
            allowed_branch_types = {"tie_switch", "breaker", "sectionalizer"}

        energized = self.find_energized_buses()
        deenergized = set(self.buses.keys()) - energized

        candidates = []

        for branch in self.branches.values():
            if branch.is_closed():
                continue

            if branch.branch_type not in allowed_branch_types:
                continue

            a = branch.from_bus
            b = branch.to_bus

            a_energized = a in energized
            b_energized = b in energized
            a_deenergized = a in deenergized
            b_deenergized = b in deenergized

            crosses_boundary = (
                    (a_energized and b_deenergized) or
                    (b_energized and a_deenergized)
            )

            if not crosses_boundary:
                continue

            # Do not directly close into a known faulted bus.
            if a in faulted_buses or b in faulted_buses:
                continue

            candidates.append(branch)

        return candidates

    def evaluate_neighbor_restoration_candidate(
            self,
            branch_name: str,
            faulted_buses: set[str],
    ):
        """
        Temporarily close a candidate branch and evaluate restoration impact.

        Args:
            branch_name:
                Name of the open candidate branch.

            faulted_buses:
                Buses that must remain de-energized.

        Returns:
            Dictionary describing the restoration result.
        """
        if branch_name not in self.branches:
            raise ValueError(f"Branch '{branch_name}' not found.")

        branch = self.branches[branch_name]

        if branch.is_closed():
            raise ValueError(f"Branch '{branch_name}' is already closed.")

        before_energized = self.find_energized_buses()
        before_deenergized = set(self.buses.keys()) - before_energized

        # Temporarily close candidate.
        branch.close()
        self.ybus = None

        after_energized = self.find_energized_buses()
        after_deenergized = set(self.buses.keys()) - after_energized

        restored_buses = after_energized - before_energized
        fault_reenergized = faulted_buses & after_energized

        # Restore original state.
        branch.open()
        self.ybus = None

        valid_topology = (
                len(restored_buses) > 0 and
                len(fault_reenergized) == 0
        )

        return {
            "branch_name": branch.name,
            "from_bus": branch.from_bus,
            "to_bus": branch.to_bus,
            "branch_type": branch.branch_type,
            "before_energized": before_energized,
            "before_deenergized": before_deenergized,
            "after_energized": after_energized,
            "after_deenergized": after_deenergized,
            "restored_buses": restored_buses,
            "fault_reenergized": fault_reenergized,
            "valid_topology": valid_topology,
        }

    def auto_restore_by_neighbors(
            self,
            faulted_buses: set[str],
            allowed_branch_types: set[str] | None = None,
    ):
        """
        Automatically restore healthy de-energized buses by closing an open branch
        that connects an energized region to a de-energized region.

        The method rejects candidates that would re-energize faulted buses.

        Args:
            faulted_buses:
                Set of buses that must remain de-energized.

            allowed_branch_types:
                Branch types allowed for restoration.
                Defaults to {"tie_switch", "breaker", "sectionalizer"}.

        Returns:
            Dictionary with selected restoration result, or None if no valid
            restoration option is found.
        """
        candidates = self.find_open_boundary_switches(
            faulted_buses=faulted_buses,
            allowed_branch_types=allowed_branch_types,
        )

        if not candidates:
            return None

        best_result = None

        for branch in candidates:
            result = self.evaluate_neighbor_restoration_candidate(
                branch_name=branch.name,
                faulted_buses=faulted_buses,
            )

            if not result["valid_topology"]:
                continue

            if best_result is None:
                best_result = result
            elif len(result["restored_buses"]) > len(best_result["restored_buses"]):
                best_result = result

        if best_result is None:
            return None

        # Apply selected restoration action.
        self.close_branch(best_result["branch_name"])

        # Update bus statuses after applying restoration.
        self.update_bus_energization()

        return best_result

    def apply_distribution_automation(
            self,
            enabled: bool = False,
            faulted_buses: set[str] | None = None,
            allowed_branch_types: set[str] | None = None,
    ):
        """
        Optionally apply automatic distribution automation restoration.

        If enabled=False, this method does nothing. This allows existing
        validation cases to run without automatic switching.

        Args:
            enabled:
                If True, run automatic restoration logic.
                If False, leave branch statuses unchanged.

            faulted_buses:
                Buses that must remain de-energized. Example: {"9com"}.

            allowed_branch_types:
                Branch types allowed for automatic restoration.
                Example: {"tie_switch"}.

        Returns:
            Restoration result dictionary, or None.
        """
        if not enabled:
            return None

        if faulted_buses is None:
            faulted_buses = set()

        if allowed_branch_types is None:
            allowed_branch_types = {"tie_switch"}

        return self.auto_restore_by_neighbors(
            faulted_buses=faulted_buses,
            allowed_branch_types=allowed_branch_types,
        )

    def print_restoration_result(self, result: dict | None) -> None:
        """
        Print the result of an automatic restoration attempt.
        """
        print("Distribution Automation Restoration Result")
        print("-" * 80)

        if result is None:
            print("No valid restoration switching action found.")
            return

        print(f"Selected branch : {result['branch_name']}")
        print(f"From bus        : {result['from_bus']}")
        print(f"To bus          : {result['to_bus']}")
        print(f"Branch type     : {result['branch_type']}")
        print(f"Valid topology  : {result['valid_topology']}")

        print()
        print("Restored buses:")
        if result["restored_buses"]:
            for bus in sorted(result["restored_buses"]):
                print(f"  {bus}")
        else:
            print("  None")

        print()
        print("Faulted buses re-energized:")
        if result["fault_reenergized"]:
            for bus in sorted(result["fault_reenergized"]):
                print(f"  {bus}")
        else:
            print("  None")