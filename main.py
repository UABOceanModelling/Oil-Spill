# stdlib
from datetime import timedelta
import pprint
import xarray as xr
import numpy as np

# opendrift
from opendrift.models.openoil import OpenOil
from opendrift.readers.reader_netCDF_CF_generic import Reader

# local
from oil_spill.dataset_utils import DatasetHandler, NemoConverter
from oil_spill.reader import DatasetReader


def set_configuration(o: OpenOil):
    # o.set_config('general:use_auto_landmask', False)
    o.set_config("environment:fallback:x_wind", 3)
    o.set_config("environment:fallback:y_wind", -7)
    # o.set_config("drift:vertical_mixing", True)
    # o.set_config("seed:droplet_size_distribution", "uniform")
    # o.set_config("seed:droplet_diameter_min_subsea", 0.0001)
    # o.set_config("seed:droplet_diameter_max_subsea", 0.0005)

def run():
    o = OpenOil(loglevel=0)
    dr = DatasetReader()
    dh = DatasetHandler()
    nc = NemoConverter()
    ds_U, ds_V, ds_T, ds_W = dr.read()

    combined_ds = nc.adapt_dataset(ds_U, ds_V, ds_T, ds_W)

    combined_ds = dh.add_mask(combined_ds)

    combined_ds = dh.clean_dataset(combined_ds)

    combined_ds = dh.select_subset_of_data(combined_ds, {"Y": slice(530, 750), "X": slice(120, 430)})

    T_reader = Reader(combined_ds, name="NEMO dataset")

    o.add_reader([T_reader])

    set_configuration(o)

    o.seed_elements(lon=-100, lat=81, number=1000, radius=10000, time=T_reader.start_time, oil_type="GENERIC DIESEL")

    o.run()
    o.plot(filename="oil_spill/output/plots/oil_spill_simulation.png", linecolor='z')

    o.animation(filename="oil_spill/output/animations/oil_spill_simulation.mp4", fast=True)


if __name__ == "__main__":
    run()
