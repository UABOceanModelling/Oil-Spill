from opendrift.models.openoil import OpenOil

def set_configuration(o: OpenOil):
    # o.set_config('general:use_auto_landmask', False)
    o.set_config("environment:fallback:x_wind", 0)
    o.set_config("environment:fallback:y_wind", -1)
    o.set_config("drift:vertical_mixing", True)
    # o.set_config("seed:droplet_size_distribution", "uniform")
    # o.set_config("seed:droplet_diameter_min_subsea", 0.0001)
    # o.set_config("seed:droplet_diameter_max_subsea", 0.0005)