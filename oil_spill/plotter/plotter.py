import xarray as xr
import matplotlib.pyplot as plt

from opendrift.models.openoil import OpenOil

from oil_spill.utils import create_directory


class Plotter:
    def __init__(self, config, o: OpenOil):
        self.directory = config.output.directory
        self.plot_name = config.output.files.plot
        self.number_of_particles = config.opendrift.seeding["number"]
        self.radius = config.opendrift.seeding["radius"]
        self.oil_type = config.opendrift.seeding["oil_type"]
        self.o = o
        self.animation = config.output.files.animation
        self.lat = config.opendrift.seeding["lat"]
        self.lon = config.opendrift.seeding["lon"]

        self.output_directory = create_directory(
            self.directory
            + "plots/simulations/"
            + f"lat_{self.lat}"
            + "_"
            + f"lon_{self.lon}"
            + "/"
            + self.oil_type
            + "/"
            + f"particles_{self.number_of_particles}-"
            + f"radius_{self.radius}_m"
        )

    def plot_main(self):
        create_directory(self.output_directory + "/plots/")
        self.o.plot(
            filename=self.output_directory + "/plots/" + self.plot_name,
            linecolor="z",
            #    buffer=1
        )

    def create_animation(self):
        create_directory(self.output_directory + "/animations/")
        self.o.animation(
            filename=self.output_directory + "/animations/" + self.animation, 
            color='z',
            fast=True
        )

    def plot_property(self, property_name: str):
        create_directory(self.output_directory + "/plots/properties/")
        self.o.plot_property(
            property_name,
            filename=self.output_directory + "/plots/properties/" + property_name + ".png",
        )
    
    def plot_oil_budget(self):
        create_directory(self.output_directory + "/plots/budget/")
        self.o.plot_oil_budget(
            filename=self.output_directory + "/plots/budget/oil_budget.png",
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
