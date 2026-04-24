class Branch:
    _branch_status = {"Closed": True, "Open": False}
    _branch_types = ("line", "transformer", "breaker", "sectionalizer", "tie_switch")

    def __init__(
            self,
            from_bus: str,
            to_bus: str,
            r: float,
            x: float,
            g: float = 0.0,
            b: float = 0.0,
            branch_type: str = "line",
            status: str = "Closed"
    ):
        self.from_bus = from_bus
        self.to_bus = to_bus
        self.r = r
        self.x = x
        self.g = g
        self.b = b
        self.status = self._validate_status(status)  # True = closed, False = open
        self.branch_type = self._validate_branch_type(branch_type)

    @classmethod
    def _validate_status(cls, status: str) -> bool:
        if status is None:
            return True
        if status not in cls._branch_status:
            raise ValueError(
                f"Invalid status: {status}. Valid options are: {list(cls._branch_status.keys())}"
            )
        return cls._branch_status[status]

    @classmethod
    def _validate_branch_type(cls, branch_type: str) -> str:
        if branch_type not in cls._branch_types:
            raise ValueError(
                f"Invalid branch type: {branch_type}. Valid options are: {list(cls._branch_types)}"
            )
        return branch_type

    def is_closed(self) -> bool:
        return self.status

    def open(self) -> None:
        self.status = False

    def close(self) -> None:
        self.status = True

    def series_impedance(self) -> complex:
        return complex(self.r, self.x)

    def __repr__(self) -> str:
        status_str = "Closed" if self.status else "Open"
        return (
            f"Branch(from_bus='{self.from_bus}', to_bus='{self.to_bus}', "
            f"r={self.r}, x={self.x}, branch_type='{self.branch_type}', "
            f"status='{status_str}')"
        )


if __name__ == "__main__":
    print("=== Branch Class Validation ===\n")

    branch1 = Branch("Bus1", "Bus2", 0.1, 0.2, status="Closed")
    branch2 = Branch("Bus2", "Bus3", 0.05, 0.15, branch_type="tie_switch", status="Open")

    print(branch1)
    print(branch2)

    print("\n--- Switch Operations ---")
    print(f"Before: {branch2}")
    branch2.close()
    print(f"After close(): {branch2}")
    branch2.open()
    print(f"After open(): {branch2}")