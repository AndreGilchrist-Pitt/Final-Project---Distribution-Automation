import numpy as np

class Jacobian:
    """
    Builds the Newton-Raphson Jacobian matrix for power flow.

    Row order:
    1. Delta P rows for all non-slack buses
    2. Delta Q rows for PQ buses only

    Column order:
    1. Delta angle columns for all non-slack buses
    2. Delta |V| columns for PQ buses only
    """

    def __init__(self):
        self.J = None

    def _non_slack_buses(self, buses: dict):
        return [
            bus for bus in buses.values()
            if bus.bus_type != "Slack" and getattr(bus, "in_service", True)
        ]

    def _pq_buses(self, buses: dict):
        return [
            bus for bus in buses.values()
            if bus.bus_type == "PQ" and getattr(bus, "in_service", True)
        ]
    def PQ_BUSES(self, buses: dict):
        return self._pq_buses(buses)

    def NON_SLACK_BUSES(self, buses: dict):
        return self._non_slack_buses(buses)

    def _power_injections(self, ybus, angles, voltages):
        n = len(voltages)
        P = np.zeros(n)
        Q = np.zeros(n)

        for i in range(n):
            for j in range(n):
                Gij = ybus[i, j].real
                Bij = ybus[i, j].imag
                delta_ij = angles[i] - angles[j]

                P[i] += voltages[i] * voltages[j] * (
                        Gij * np.cos(delta_ij) + Bij * np.sin(delta_ij)
                )
                Q[i] += voltages[i] * voltages[j] * (
                        Gij * np.sin(delta_ij) - Bij * np.cos(delta_ij)
                )

        return P, Q

    def _build_j1(self, ybus, angles, voltages, p_buses):
        m = len(p_buses)
        J1 = np.zeros((m, m))
        P, Q = self._power_injections(ybus, angles, voltages)

        for r, bus_i in enumerate(p_buses):
            i = bus_i.bus_index
            Vi = voltages[i]

            for c, bus_k in enumerate(p_buses):
                k = bus_k.bus_index
                Vk = voltages[k]
                Gik = ybus[i, k].real
                Bik = ybus[i, k].imag
                delta_ik = angles[i] - angles[k]

                if i == k:
                    Bii = ybus[i, i].imag
                    J1[r, c] = -Q[i] - (Vi ** 2) * Bii
                else:
                    J1[r, c] = Vi * Vk * (
                            Gik * np.sin(delta_ik) - Bik * np.cos(delta_ik)
                    )

        return J1

    def _build_j2(self, ybus, angles, voltages, p_buses, pq_buses):
        rows = len(p_buses)
        cols = len(pq_buses)
        J2 = np.zeros((rows, cols))
        P, Q = self._power_injections(ybus, angles, voltages)

        for r, bus_i in enumerate(p_buses):
            i = bus_i.bus_index
            Vi = voltages[i]

            for c, bus_k in enumerate(pq_buses):
                k = bus_k.bus_index
                Gik = ybus[i, k].real
                Bik = ybus[i, k].imag
                delta_ik = angles[i] - angles[k]

                if i == k:
                    if np.isclose(Vi, 0.0):
                        raise ValueError(
                            f"Jacobian J2 received zero-voltage active bus '{bus_i.name}'. "
                            "This bus should have been excluded by in_service filtering."
                        )
                    Gii = ybus[i, i].real
                    J2[r, c] = (P[i] / Vi) + Gii * Vi
                else:
                    J2[r, c] = Vi * (
                            Gik * np.cos(delta_ik) + Bik * np.sin(delta_ik)
                    )

        return J2

    def _build_j3(self, ybus, angles, voltages, pq_buses, p_buses):
        rows = len(pq_buses)
        cols = len(p_buses)
        J3 = np.zeros((rows, cols))
        P, Q = self._power_injections(ybus, angles, voltages)

        for r, bus_i in enumerate(pq_buses):
            i = bus_i.bus_index
            Vi = voltages[i]

            for c, bus_k in enumerate(p_buses):
                k = bus_k.bus_index
                Vk = voltages[k]
                Gik = ybus[i, k].real
                Bik = ybus[i, k].imag
                delta_ik = angles[i] - angles[k]

                if i == k:
                    Gii = ybus[i, i].real
                    J3[r, c] = P[i] - (Vi ** 2) * Gii
                else:
                    J3[r, c] = -Vi * Vk * (
                            Gik * np.cos(delta_ik) + Bik * np.sin(delta_ik)
                    )

        return J3

    def _build_j4(self, ybus, angles, voltages, pq_buses):
        m = len(pq_buses)
        J4 = np.zeros((m, m))
        P, Q = self._power_injections(ybus, angles, voltages)

        for r, bus_i in enumerate(pq_buses):
            i = bus_i.bus_index
            Vi = voltages[i]

            for c, bus_k in enumerate(pq_buses):
                k = bus_k.bus_index
                Gik = ybus[i, k].real
                Bik = ybus[i, k].imag
                delta_ik = angles[i] - angles[k]

                if i == k:
                    if np.isclose(Vi, 0.0):
                        raise ValueError(
                            f"Jacobian J4 received zero-voltage active PQ bus '{bus_i.name}'. "
                            "This bus should have been excluded by in_service filtering."
                        )
                    Bii = ybus[i, i].imag
                    J4[r, c] = (Q[i] / Vi) - Bii * Vi
                else:
                    J4[r, c] = Vi * (
                            Gik * np.sin(delta_ik) - Bik * np.cos(delta_ik)
                    )

        return J4

    def calculate_jacobian(self, buses: dict, ybus, angles, voltages):
        p_buses = self._non_slack_buses(buses)
        pq_buses = self._pq_buses(buses)

        J1 = self._build_j1(ybus, angles, voltages, p_buses)
        J2 = self._build_j2(ybus, angles, voltages, p_buses, pq_buses)
        J3 = self._build_j3(ybus, angles, voltages, pq_buses, p_buses)
        J4 = self._build_j4(ybus, angles, voltages, pq_buses)

        self.J = np.block([
            [J1, J2],
            [J3, J4]
        ])
        return self.J