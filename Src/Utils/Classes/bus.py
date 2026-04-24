from enum import Enum



class Bus:
    """
    Represents a bus (node) in a power system network.

    Each bus has a unique index assigned automatically using a class-level counter.
    A dictionary tracks all created buses by name.
    """

    # Class-level counter for unique bus indices
    _bus_counter = 0

    # Dictionary to track all buses: {name: bus_index}
    _bus_registry = {}
    _bus_objects = {}
    # Valid bus types: label -> type code
    _valid_bus_types = {"Slack": 0, "PQ": 1, "PV": 2}
    _valid_area_classifiers = {"Residential", "Commercial", "Industrial"}
    def __init__(self, name: str, nominal_kv: float, vpu: float = 1.0, delta: float = 0.0, bus_type: str = None,
                 area_class: str = None):
        """
        Initialize a Bus instance.

        Args:
            name: The name of the bus
            nominal_kv: The nominal voltage in kilovolts
            area_class: Customer class of the load ('res', 'com', or 'ind')
        """
        self.name = name
        self.nominal_kv = nominal_kv

        # Assign unique bus index and increment counter
        self.bus_index = Bus._bus_counter
        Bus._bus_counter += 1

        self.vpu = vpu
        self.delta = delta
        self.bus_type = Bus._validate_bus_type(bus_type)
        self.area_class = self._validate_area_class(area_class)

        # Register this bus in the dictionary
        Bus._bus_registry[self.name] = self.bus_index
        Bus._bus_objects[self.name] = self
    @classmethod
    def get_bus_index(cls, name: str):
        """
        Get the bus index for a given bus name.

        Args:
            name: The name of the bus

        Returns:
            The bus index, or None if the bus doesn't exist
        """
        return cls._bus_registry.get(name)

    @classmethod
    def _validate_bus_type(cls, bus_type: str) -> str:
        """
        Validate a bus type string.

        Args:
            bus_type: Bus type string (case-insensitive)

        Returns:
            The matched label string

        Raises:
            ValueError: If bus_type is None or not valid
        """
        if bus_type is None:
            raise ValueError(f"Bus type must be specified. Valid types: {list(cls._valid_bus_types.keys())}")
        for label in cls._valid_bus_types:
            if label.upper() == bus_type.upper():
                return label
        raise ValueError(f"Invalid bus type '{bus_type}'. Valid types: {list(cls._valid_bus_types.keys())}")
    def _validate_area_class(self, area_class: str) -> str | None:
        if area_class is not None:
            if area_class not in self._valid_area_classifiers:
                raise ValueError(f"Invalid area class '{area_class}'. Valid classifiers: {self._valid_area_classifiers}")
            return area_class
        return None
    @classmethod
    def get_bus(cls, name: str) -> "Bus | None":
        """Return the Bus instance for a given name, or None."""
        return cls._bus_objects.get(name)

if __name__ == "__main__":
    # Simple validation test
    print("=== Bus Class Validation ===\n")

    # Create buses
    bus1 = Bus("Bus1", 20.0,bus_type="PV")
    print(bus1.bus_type)
    bus2 = Bus("Bus2", 230.0, bus_type="PV")
    bus3 = Bus("Bus3", 115.0, bus_type="PV", area_class="Residential")

    # Test bus creation
    print(f"Bus1: name={bus1.name}, nominal_kv={bus1.nominal_kv}, index={bus1.bus_index}")
    print(f"Bus2: name={bus2.name}, nominal_kv={bus2.nominal_kv}, index={bus2.bus_index}")
    print(f"Bus3: name={bus3.name}, nominal_kv={bus3.nominal_kv}, index={bus3.bus_index}, area_class={bus3.area_class}")

    # Test registry
    print(f"\nBus Registry: {Bus._bus_registry}")

    # Test get_bus_index
    print(f"\nLookup 'Bus1' index: {Bus.get_bus_index('Bus1')}")
    print(f"Lookup 'Bus3' index: {Bus.get_bus_index('Bus3')}")
    print(f"Lookup 'Nonexistent' index: {Bus.get_bus_index('Nonexistent')}")