import pandas as pd
import numpy as np

class Branch:
    _branch_status = {"Closed": True, "Open": False}
    _branch_types = ("line", "transformer", "breaker", "sectionalizer", "tie_switch")

    def __init__(
            self,
            name: str,
            from_bus: str,
            to_bus: str,
            r: float,
            x: float,
            g: float = 0.0,
            b: float = 0.0,
            branch_type: str = "line",
            status: str = "Closed"
    ):
        self.name = name
        self.from_bus = from_bus
        self.to_bus = to_bus
        self.r = r
        self.x = x
        self.g = g
        self.b = b
        self.status = self._validate_status(status)
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

    @property
    def Yseries(self) -> complex:
        z = complex(self.r, self.x)
        if np.isclose(z, 0.0 + 0.0j):
            raise ValueError("Branch impedance cannot be zero.")
        return 1 / z

    @property
    def Yshunt(self) -> complex:
        return complex(self.g, self.b)

    def calc_yprim(self) -> pd.DataFrame:
        labels = [self.from_bus, self.to_bus]
        Y11 = self.Yseries + self.Yshunt / 2
        Y12 = -self.Yseries
        return pd.DataFrame(
            [[Y11, Y12], [Y12, Y11]],
            index=labels,
            columns=labels
        )

    def __repr__(self) -> str:
        status_str = "Closed" if self.status else "Open"
        return (
            f"Branch(name='{self.name}', from_bus='{self.from_bus}', to_bus='{self.to_bus}', "
            f"r={self.r}, x={self.x}, g={self.g}, b={self.b}, "
            f"branch_type='{self.branch_type}', status='{status_str}')"
        )