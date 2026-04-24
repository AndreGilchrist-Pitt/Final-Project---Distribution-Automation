from Src.Utils.Classes.settings import Settings
from Src.Utils.Classes.areascalar import AreaScalar
class Load:
    """
    Represents a load in a power system network.

    A load is connected to a single bus and consumes active power (MW)
    and reactive power (MVAR).
    """

    def __init__(self, name: str, bus1_name: str, mw: float, mvar: float):
        """
        Initialize a Load instance.

        Args:
            name: The name/identifier of the load
            bus1_name: Name of the bus where the load is connected
            mw: Active power consumption in megawatts (MW)
            mvar: Reactive power consumption in megavars (MVAR)
        """
        self.name = name
        self.bus1_name = bus1_name
        self.mw = mw
        self.mvar = mvar
        self.p = self.calc_p() * AreaScalar().scale(bus1_name)
        self.q = self.calc_q() * AreaScalar().scale(bus1_name)
    def calc_p(self) -> float:
        """
        Calculate active power in per-unit.
        """
        return self.mw / Settings.sbase

    def calc_q(self) -> float:
        """
        Calculate reactive power in per-unit.
        """
        return self.mvar / Settings.sbase

    def __repr__(self):
        return (
            f"Load(name='{self.name}', bus='{self.bus1_name}', "
            f"mw={self.mw}, mvar={self.mvar}, p={self.p}, q={self.q})"
        )


if __name__ == "__main__":
    import math
    # Simple validation test
    print("=== Load Class Validation ===\n")
    AreaScalar()
    # Create load
    load1 = Load("Load 1", "Bus 2", 50.0, 30.0)

    # Test attributes
    print(f"Load name: {load1.name}")
    print(f"Bus name: {load1.bus1_name}")
    print(f"Active power (MW): {load1.mw}")
    print(f"Reactive power (MVAR): {load1.mvar}")

    # Test __repr__
    print(f"\nString representation:\n{repr(load1)}")

    # Create multiple loads
    print("\n--- Creating Multiple Loads ---")
    load2 = Load("Residential Load", "Bus 3", 25.5, 15.2)
    load3 = Load("Industrial Load", "Bus 4", 100.0, 75.0)

    print(repr(load2))
    print(repr(load3))

    # Test power factor
    print("\n--- Power Factor Analysis ---")


    pf1 = load1.mw / math.sqrt(load1.mw ** 2 + load1.mvar ** 2)
    print(f"Load 1 power factor: {pf1:.3f}")

    pf3 = load3.mw / math.sqrt(load3.mw ** 2 + load3.mvar ** 2)
    print(f"Industrial Load power factor: {pf3:.3f}")
