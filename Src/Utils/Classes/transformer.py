import pandas as pd


class Transformer:
    """
    Represents a transformer in a power system network.

    A transformer connects two buses and has series impedance (r + jx).
    """

    def __init__(self, name: str, bus1_name: str, bus2_name: str, r: float, x: float, status: str = "Closed"):
        """
        Initialize a Transformer instance.

        Args:
            name: The name/identifier of the transformer
            bus1_name: Name of the first bus (typically high voltage side)
            bus2_name: Name of the second bus (typically low voltage side)
            r: Resistance in per-unit or ohms
            x: Reactance in per-unit or ohms
            calc yprim(): returns the 2 × 2 primitive admittance matrix for a two-terminal series element
        """
        self.name = name
        self.bus1_name = bus1_name
        self.bus2_name = bus2_name
        self.r = r
        self.x = x
        self._yseries = self._calc_Yseries()
        self.status = status
    # Series admittance: Yseries = 1/(r + jx), per-unit values
    def _calc_Yseries(self):
        return 1 / (self.r + 1j * self.x)
    @property
    # Series admittance: Yseries = 1/(r + jx), per-unit values
    def Yseries(self) -> complex:
        return self._yseries

    def calc_yprim(self) -> pd.DataFrame:
        """
        Return the 2×2 primitive admittance matrix for a two-terminal series element.

        Returns:
            pandas.DataFrame: Yprim with bus1_name and bus2_name as row/column labels.
        """
        labels = [self.bus1_name, self.bus2_name]
        Yprim = pd.DataFrame(
            [[self.Yseries, -self.Yseries], [-self.Yseries, self.Yseries]],
            index=labels,
            columns=labels,
        )
        return Yprim

    def __repr__(self):
        return f"Transformer(name='{self.name}', bus1='{self.bus1_name}', bus2='{self.bus2_name}', r={self.r}, x={self.x})"


if __name__ == "__main__":
    # Milestone 3 validation: Yseries and Yprim only
    print("=== Transformer Class Validation ===\n")

    transformer1 = Transformer("T1", "Bus 1", "Bus 2", 0.01, 0.10)

    print("Series admittance:")
    print(transformer1.Yseries)

    print("\nPrimitive admittance matrix:")
    print(transformer1.calc_yprim())