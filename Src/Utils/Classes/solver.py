"""
Milestone 9: Unified Solver supporting power flow and fault study modes.
"""

import numpy as np
from Src.Utils.Classes.powerflow import PowerFlow


class Solver:
    """
    Unified solver supporting both power flow and symmetrical fault analysis.

    Modes:
        'power_flow' - Newton-Raphson power flow (delegates to PowerFlow)
        'fault'      - Symmetrical three-phase bolted fault analysis
    """

    VALID_MODES = {"power_flow", "fault"}

    def __init__(self, mode: str = "power_flow"):
        """
        Args:
            mode: Analysis mode — 'power_flow' or 'fault'.

        Raises:
            ValueError: If an invalid mode is provided.
        """
        if mode not in self.VALID_MODES:
            raise ValueError(f"Invalid mode '{mode}'. Choose from {self.VALID_MODES}")

        self.mode = mode
        self._pf = PowerFlow()

        # Power flow results
        self.converged: bool = False
        self.iterations: int = 0

        # Fault study results
        self.fault_current: complex = None
        self.fault_voltages: dict = None

    def run(self, circuit, tol: float = 1e-4, max_iter: int = 50,
            faulted_bus_name: str = None, prefault_voltage: float = 1.0,
            verbose: bool = False) -> "Solver":
        """
        Execute the analysis based on the selected mode.

        Args:
            circuit: Circuit object with calc_ybus() already called.
            tol: Convergence tolerance (power_flow only).
            max_iter: Max Newton-Raphson iterations (power_flow only).
            faulted_bus_name: Bus where the fault occurs (fault only).
            prefault_voltage: Prefault voltage in p.u. (fault only, default 1.0).
            verbose: Print iteration info (power_flow only).

        Returns:
            self, for method chaining.
        """
        if self.mode == "power_flow":
            if circuit.ybus is None:
                raise ValueError("call circuit.calc_ybus() before Solver.run()")
            self._run_power_flow(circuit, tol, max_iter, verbose)

        elif self.mode == "fault":
            self._run_fault(circuit, faulted_bus_name, prefault_voltage)

        return self

    def _run_power_flow(self, circuit, tol, max_iter, verbose):
        self._pf.solve(circuit, tol=tol, max_iter=max_iter, verbose=verbose)
        self.converged = self._pf.converged
        self.iterations = self._pf.iterations

    def _run_fault(self, circuit, faulted_bus_name: str, prefault_voltage: float):
        if faulted_bus_name is None:
            raise ValueError("faulted_bus_name is required for fault mode.")
        if faulted_bus_name not in circuit.buses:
            raise ValueError(f"Bus '{faulted_bus_name}' not found in circuit.")

        ybus_fault = circuit.calc_ybus_fault()
        zbus = circuit.calc_zbus(ybus_fault)
        self.fault_current = circuit.calc_fault_current(zbus, faulted_bus_name, prefault_voltage)
        self.fault_voltages = circuit.calc_fault_voltages(zbus, faulted_bus_name, prefault_voltage)

    def __repr__(self):
        if self.mode == "power_flow":
            return (f"Solver(mode='power_flow', converged={self.converged}, "
                    f"iterations={self.iterations})")
        else:
            i_mag = abs(self.fault_current) if self.fault_current is not None else None
            return f"Solver(mode='fault', fault_current_mag={i_mag})"