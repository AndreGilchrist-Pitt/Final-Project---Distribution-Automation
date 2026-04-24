from Src.Utils.Classes.settings import Settings


class CapacitorBank:
    _valid_status = {"Closed": True, "Open": False}

    def __init__(self, name: str, bus1_name: str, mvar_nominal: float, status: str = "Closed"):
        self.name = name
        self.bus1_name = bus1_name
        self.mvar_nominal = mvar_nominal
        self.status = self._validate_status(status)

    @classmethod
    def _validate_status(cls, status: str) -> bool:
        if status not in cls._valid_status:
            raise ValueError(
                f"Invalid status: {status}. Valid options are: {list(cls._valid_status.keys())}"
            )
        return cls._valid_status[status]

    def is_closed(self) -> bool:
        return self.status

    def open(self) -> None:
        self.status = False

    def close(self) -> None:
        self.status = True

    @property
    def b_shunt_pu(self) -> float:
        if not self.status:
            return 0.0
        return self.mvar_nominal / Settings.sbase

    def __repr__(self):
        status_str = "Closed" if self.status else "Open"
        return (
            f"CapacitorBank(name='{self.name}', bus='{self.bus1_name}', "
            f"mvar_nominal={self.mvar_nominal}, b_shunt_pu={self.b_shunt_pu}, "
            f"status='{status_str}')"
        )


if __name__ == "__main__":
    print("=== CapacitorBank Class Validation ===\n")

    cap1 = CapacitorBank("Cap1", "Bus7", 1.0, status="Closed")
    print(cap1)

    cap1.open()
    print("After open():", cap1)

    cap1.close()
    print("After close():", cap1)