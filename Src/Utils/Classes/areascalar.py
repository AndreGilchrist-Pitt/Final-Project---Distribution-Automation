from Src.Utils.Classes.bus import Bus


class AreaConfig(type):
    def __str__(cls):
        return (
            f"=== Area Scalar Settings ===\n"
            f"Residential   : {cls.res_scale}\n"
            f"Commercial    : {cls.com_scale}\n"
            f"Industrial    : {cls.ind_scale}\n"
        )
class AreaScalar(metaclass=AreaConfig):
    res_scale: float = 1.0
    com_scale: float = 1.0
    ind_scale: float = 1.0

    def __init__(self, res_scale: float = None, com_scale: float = None, ind_scale: float = None):
        if res_scale is not None:
            AreaScalar.res_scale = res_scale
        if com_scale is not None:
            AreaScalar.com_scale = com_scale
        if ind_scale is not None:
            AreaScalar.ind_scale = ind_scale

    def scale(self, bus_name: str) -> float:
        bus = Bus.get_bus(bus_name)
        if bus is None:
            return 1.0

        if bus.area_class == 'Residential':
            return AreaScalar.res_scale
        elif bus.area_class == 'Commercial':
            return AreaScalar.com_scale
        elif bus.area_class == 'Industrial':
            return AreaScalar.ind_scale
        else:
            return 1.0

    def __repr__(self):
        return f"AreaScalar(res_scale={self.res_scale}, com_scale={self.com_scale}, ind_scale={self.ind_scale})"