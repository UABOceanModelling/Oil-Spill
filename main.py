# stdlib
from datetime import timedelta
from pprint import pprint

# opendrift
from opendrift.models.openoil import OpenOil
from opendrift.readers.reader_netCDF_CF_generic import Reader

# 3rd party
import xarray as xr
from typing import List
import numpy as np
from matplotlib import pyplot as plt

# local
from oil_spill.dataset_utils import DatasetHandler
from oil_spill.reader import DatasetReader
from oil_spill.utils import set_configuration
from oil_spill.config import ConfigReader
from oil_spill.plotter import Plotter


def read_data(config: ConfigReader):
    dr = DatasetReader(
        xarray_parameters=config.xarray_parameters,
    )
    dh = DatasetHandler(
        interpolation=config.transformations.interpolation,
        renaming=config.transformations.renaming,
        attributes_to_add=config.transformations.attributes_to_add,
        slicing=config.transformations.slicing,
        keep=config.transformations.keep,
    )
    datasets = dr.read_multi_files(config.input_data.data_paths)
    mask_ds = dr.read_single_file(config.input_data.ancillary_paths.mask)
    return dh, datasets, mask_ds


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

    Plotter.plot_result(config, o)


def run():
    config = ConfigReader.from_yaml("parameters.yaml")

    dh, datasets, mask_ds = read_data(config)

    combined_ds = dh.create_combined_dataset(datasets, mask_ds)

    T_reader = Reader(combined_ds, name="NEMO dataset")

    run_simulation(T_reader, config)


if __name__ == "__main__":
    run()
