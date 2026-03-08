from opendrift.models.openoil import OpenOil

def set_configuration(o: OpenOil):
    o.set_config('general:use_auto_landmask', True)
    o.set_config("drift:vertical_mixing", True)
    o.set_config("drift:vertical_mixing_at_surface", True)
    # o.set_config("vertical_mixing:TSprofiles", True)
    o.set_config("drift:vertical_advection", True)
    o.set_config("drift:vertical_advection_at_surface", True)
    o.set_config("vertical_mixing:background_diffusivity", 1e-4)
    o.set_config("drift:horizontal_diffusivity", 0.033483315)
    o.set_config("environment:constant:ocean_vertical_diffusivity", 1e-4)

    # o.set_config("drift:current_uncertainty", 0)
    # o.set_config("drift:wind_uncertainty", 0)

    o.set_config("environment:fallback:x_wind", 0)
    o.set_config("environment:fallback:y_wind", 0)

    o.set_config("environment:fallback:x_sea_water_velocity", 0)
    o.set_config("environment:fallback:y_sea_water_velocity", 0)