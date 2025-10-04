# stdlib
from datetime import timedelta
from pprint import pprint

# opendrift
from opendrift.models.openoil import OpenOil
from opendrift.readers.reader_netCDF_CF_generic import Reader

# 3rd party
import xarray as xr
from typing import List

# local
from oil_spill.dataset_utils import DatasetHandler
from oil_spill.reader import DatasetReader
from oil_spill.utils import set_configuration
from oil_spill.config import ConfigReader


def read_data(config: ConfigReader):
    dr = DatasetReader(data_paths=config.input_data.data_paths, xarray_parameters=config.xarray_parameters)
    dh = DatasetHandler(
        interpolation=config.transformations.interpolation,
        renaming=config.transformations.renaming,
        attributes_to_add=config.transformations.attributes_to_add,
        slicing=config.transformations.slicing,
        keep=config.transformations.keep,
    )
    datasets = dr.read_multi_files()
    return datasets, dh

def transform_data(datasets: List[xr.Dataset], dh: DatasetHandler) -> xr.Dataset:
    combined_ds = dh.create_combined_dataset(datasets)
    raise

    combined_ds = dh.add_mask(combined_ds)

    combined_ds = dh.clean_dataset(combined_ds)

    combined_ds = dh.select_subset_of_data(combined_ds)

    return combined_ds

def run_simulation(T_reader: Reader, config: ConfigReader):
    o = OpenOil(loglevel=config.opendrift.log_level)
    o.add_reader([T_reader])

    set_configuration(o)

    seeding_config = {
        "time": T_reader.start_time,
    }
    seeding_config.update(config.opendrift.seeding)

    o.seed_elements(**seeding_config)

    o.run()

    directory = config.output.directory
    plot = config.output.files.plot
    animation = config.output.files.animation
    o.plot(filename=directory+plot, linecolor="z")

    o.animation(filename=directory+animation, fast=True)

def run():
    config = ConfigReader.from_yaml("parameters.yaml")

    datasets, dh = read_data(config)

    combined_ds = transform_data(datasets, dh)

    T_reader = Reader(combined_ds, name="NEMO dataset")

    run_simulation(T_reader, config)


if __name__ == "__main__":
    run()
