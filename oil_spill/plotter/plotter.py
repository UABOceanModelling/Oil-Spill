import xarray as xr
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

from opendrift.models.openoil import OpenOil

from oil_spill.utils import create_directory
from oil_spill.config import ConfigReader


class Plotter:
    def __init__(self, config: ConfigReader, o: OpenOil):
        self.directory = config.output.directory
        self.plot_name = config.output.files["plot"]
        self.start_time = config.opendrift.seeding["time"]
        self.end_time = config.opendrift.end_time
        self.number_of_particles = config.opendrift.seeding["number"]
        self.radius = config.opendrift.seeding["radius"]
        self.z = config.opendrift.seeding["z"]
        self.oil_type = config.opendrift.seeding["oil_type"]
        self.o = o
        self.animation = config.output.files["animation"]
        self.lat = config.opendrift.seeding["lat"]
        self.lon = config.opendrift.seeding["lon"]

        self.cmap = ListedColormap([cfeature.COLORS["water"], cfeature.COLORS["land"]])

        self.output_directory = create_directory(self.directory + "simulations/" + f"{self.start_time}-{self.end_time}/")

    def plot_main(self):
        create_directory(self.output_directory + "/plots/")
        self.o.plot(
            filename=self.output_directory
            + "/plots/"
            + f"trajectories_{self.oil_type}_lat_{self.lat}_lon_{self.lon}_{self.number_of_particles}_particles.png",
            linecolor="z",
            # background="land_binary_mask",
            # cmap=self.cmap,
            # hide_landmask=True,
            # background=['x_sea_water_velocity', 'y_sea_water_velocity']
            # background=['sea_ice_x_velocity', 'sea_ice_x_velocity']
            # background='sea_ice_area_fraction',
            # buffer=0.5
        )

    def create_animation(self):
        create_directory(self.output_directory + "/animations/")
        self.o.animation(
            filename=self.output_directory + "/animations/" + self.animation,
            # background="land_binary_mask",
            color="z",
            fast=True,
            # cmap=self.cmap,
        )

    def animate_vertical_distribution(self):
        create_directory(self.output_directory + "/animations/")
        self.o.animate_vertical_distribution(
            filename=self.output_directory
            + "/animations/"
            + f"vertical_distribution_{self.oil_type}_lat_{self.lat}_lon_{self.lon}_{self.number_of_particles}_particles.png",
        )

    def plot_property(self, property_name: str):
        create_directory(self.output_directory + "/plots/properties/")
        self.o.plot_property(
            property_name,
            filename=self.output_directory
            + "/plots/properties/"
            + f"{property_name}_{self.oil_type}_lat_{self.lat}_lon_{self.lon}_{self.number_of_particles}_particles.png",
        )

    def plot_oil_budget(self):
        create_directory(self.output_directory + "/plots/budget/")
        self.o.plot_oil_budget(
            filename=self.output_directory
            + "/plots/budget/"
            + f"oil_budget_{self.oil_type}_lat_{self.lat}_lon_{self.lon}_{self.number_of_particles}_particles.png",
        )

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
