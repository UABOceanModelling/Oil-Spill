import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np

from opendrift.models.openoil import OpenOil


class Plotter:
    def __init__(self):
        pass

    @staticmethod
    def plot_mask(mask_ds: xr.Dataset, directory: str, filename: str):
        import matplotlib.pyplot as plt

        mask_ds["tmask"].isel(
            z=0,
            t=0,
            x=slice(120, 430),
            y=slice(530, 750),
        ).plot()
        plt.savefig(directory + "plots/mask/" + filename)

    @staticmethod
    def plot_check(combined_ds: xr.Dataset, directory: str, filename: str):
        combined_ds["land_binary_mask"].isel(time_counter=0, deptht=45).plot()
        combined_ds["land_binary_mask"].isel(time_counter=0, X=0).plot()
        import matplotlib.pyplot as plt

        plt.savefig(directory + "plots/mask/" + filename)

    @staticmethod
    def plot_result(config, o: OpenOil):
        directory = config.output.directory
        plot = config.output.files.plot
        animation = config.output.files.animation
        lat = config.opendrift.seeding["lat"]
        lon = config.opendrift.seeding["lon"]
        o.plot(filename=directory + "plots/simulations/" + plot + f"_{lat}_{lon}.png", 
               linecolor="z", 
               buffer=10
        )

        # o.animation(filename=directory + "animations/" + animation, fast=True)

    @staticmethod
    def plot_variable(config, ds: xr.Dataset, variable: str):
        directory = config.output.directory
        da = ds[variable].isel(time_counter=0, deptht=0)
        lon = ds["lon"]
        lat = ds["lat"]

        lon_min, lon_max = float(lon.min()), float(lon.max())
        lat_min, lat_max = float(lat.min()), float(lat.max())
        print(lon_min, lon_max, lat_min, lat_max)

        da.plot()
        plt.savefig(directory + f"plots/{variable}.png")
