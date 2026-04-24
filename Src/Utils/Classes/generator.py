from Src.Utils.Classes.settings import Settings
class Generator:
    """
    Represents a generator in a power system network.

    A generator is connected to a single bus and controls voltage magnitude
    while producing active power.
    """

    def __init__(self, name: str, bus1_name: str, voltage_setpoint: float, mw_setpoint: float,x_subtransient: float = 0.0):
        """
        Initialize a Generator instance.

        Args:
            name: The name/identifier of the generator
            bus1_name: Name of the bus where the generator is connected
            voltage_setpoint: Voltage magnitude setpoint in per-unit
            mw_setpoint: Active power generation setpoint in megawatts (MW)
        """
        self.name = name
        self.bus1_name = bus1_name
        self.voltage_setpoint = voltage_setpoint
        self.mw_setpoint = mw_setpoint
        self.x_subtransient = x_subtransient
        self.p: float = self.calc_p()
    def calc_p(self) -> float:
        """
        Calculate generator active power in per-unit.
        """
        return self.mw_setpoint / Settings.sbase

    def __repr__(self):
        return (
            f"Generator(name='{self.name}', bus='{self.bus1_name}', "
            f"voltage_setpoint={self.voltage_setpoint}, mw_setpoint={self.mw_setpoint}, "
            f"p={self.p}, x_subtransient={self.x_subtransient})"
        )


if __name__ == "__main__":
    # Simple validation test
    print("=== Generator Class Validation ===\n")

    # Create generator
    gen1 = Generator("G1", "Bus 1", 1.04, 100.0)

    # Test attributes
    print(f"Generator name: {gen1.name}")
    print(f"Bus name: {gen1.bus1_name}")
    print(f"Voltage setpoint (p.u.): {gen1.voltage_setpoint}")
    print(f"Active power setpoint (MW): {gen1.mw_setpoint}")

    # Test __repr__
    print(f"\nString representation:\n{repr(gen1)}")

    # Create multiple generators
    print("\n--- Creating Multiple Generators ---")
    gen2 = Generator("G2", "Bus 5", 1.02, 150.0)
    gen3 = Generator("G3", "Bus 8", 1.05, 200.0)

    print(repr(gen2))
    print(repr(gen3))

    # Test typical setpoints
    print("\n--- Typical Generator Setpoints ---")
    print(f"G1: {gen1.voltage_setpoint} p.u. (typically 1.00-1.05)")
    print(f"G2: {gen2.voltage_setpoint} p.u.")
    print(f"Total generation: {gen1.mw_setpoint + gen2.mw_setpoint + gen3.mw_setpoint} MW")

