class SettingsConfig(type):
    def __str__(cls):
        return (
            f"=== System Settings ===\n"
            f"  Frequency : {cls.freq} Hz\n"
            f"  Sbase     : {cls.sbase} MVA"
        )

class Settings(metaclass=SettingsConfig):
    """
    Centralized system-wide settings for per-unit calculations.

    This class defines the global base quantities used across the
    power system model.
    """

    freq: float = 60.0
    sbase: float = 100.0
    def __init__(self, freq: float = 60.0, sbase: float = 100.0):
        """
        Initialize a Settings instance.

        Args:
            freq: System frequency in hertz (Hz). Default is 60 Hz.
            sbase: System base apparent power in megavolt-amperes (MVA).
                   Default is 100 MVA.
        """
        Settings.freq = freq
        Settings.sbase = sbase

    def __repr__(self):
        return f"Settings(freq={Settings.freq}, sbase={Settings.sbase})"

    def __str__(self):
        return (
            f"=== System Settings ===\n"
            f"  Frequency : {Settings.freq} Hz\n"
            f"  Sbase     : {Settings.sbase} MVA"
        )

if __name__ == "__main__":
    # Simple validation test
    print("=== Settings Class Validation ===\n")

    # Default settings
    Settings()
    print("Default Settings:")
    print(f"Frequency (Hz): {Settings.freq}")
    print(f"Sbase (MVA): {Settings.sbase}")
    print(f"Representation: {repr(Settings)}\n")

    # Custom settings
    Settings(freq=50.0, sbase=200.0)
    print("Custom Settings:")
    print(f"Frequency (Hz): {Settings.freq}")
    print(f"Sbase (MVA): {Settings.sbase}")
    print(f"Representation: {repr(Settings)}")
    print(Settings)


