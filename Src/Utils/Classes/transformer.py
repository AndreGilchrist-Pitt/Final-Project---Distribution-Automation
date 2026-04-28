import pandas as pd


class Transformer:
    """
    Represents a transformer in a power system network.

    A transformer connects two buses and has series impedance (r + jx)
    and optional off-nominal tap ratio.
    """

    _valid_tap_sides = {"bus1", "bus2"}
    def __init__(
            self,
            name: str,
            bus1_name: str,
            bus2_name: str,
            r: float,
            x: float,
            status: str = "Closed",
            tap: float = 1.0,
            tap_side: str = "bus1",
    ):
        if tap_side not in self._valid_tap_sides:
            raise ValueError(
                f"Invalid tap_side '{tap_side}'. Valid options: {self._valid_tap_sides}"
            )

        self.name = name
        self.bus1_name = bus1_name
        self.bus2_name = bus2_name
        self.r = r
        self.x = x
        self.status = status
        self.tap = tap
        self.tap_side = tap_side
        self._yseries = self._calc_Yseries()

    def _calc_Yseries(self):
        return 1 / (self.r + 1j * self.x)

    @property
    def Yseries(self) -> complex:
        return self._yseries

    def calc_yprim(self) -> pd.DataFrame:
        """
        Off-nominal tap transformer model.
        Assumes tap is on bus1 side and is a real magnitude tap.
        """
        a = self.tap
        y = self.Yseries
        labels = [self.bus1_name, self.bus2_name]

        if self.tap_side == "bus1":
            Y11 = y / (a * a)
            Y12 = -y / a
            Y21 = -y / a
            Y22 = y
        else:  # tap_side == "bus2"
            Y11 = y
            Y12 = -y / a
            Y21 = -y / a
            Y22 = y / (a * a)

        return pd.DataFrame(
            [[Y11, Y12], [Y21, Y22]],
            index=labels,
            columns=labels,
        )

    def __repr__(self):
        return (
            f"Transformer(name='{self.name}', bus1='{self.bus1_name}', "
            f"bus2='{self.bus2_name}', r={self.r}, x={self.x}, "
            f"tap={self.tap}, tap_side='{self.tap_side}')"
        )