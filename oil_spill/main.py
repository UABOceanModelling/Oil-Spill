# stdlib
from datetime import timedelta
from pprint import pprint
import os

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
from oil_spill.utils import check_existing_file
from oil_spill.utils import create_directory


def read_data(config: ConfigReader):
    dr = DatasetReader(
        xarray_parameters=config.xarray_parameters,
    )
    dh = DatasetHandler(
        interpolation=config.transformations.interpolation,
        combination=config.transformations.combination,
        renaming=config.transformations.renaming,
        attributes_to_add=config.transformations.attributes_to_add,
        coords_to_add=config.transformations.coords_to_add,
        slicing=config.transformations.slicing,
        keep=config.transformations.keep,
    )
    datasets = dr.read_multi_files(config.input_data.data_paths)
    return dh, datasets


def run_simulation(T_reader: Reader, config: ConfigReader, o: OpenOil):

    o.add_reader([T_reader])

    set_configuration(o)

    seeding_config = {
        "time": T_reader.start_time,
    }
    seeding_config.update(config.opendrift.seeding)

    o.seed_elements(**seeding_config)

    simulation_path = create_directory("oil_spill/data/simulations/")
    o.run(outfile=simulation_path + "/output_simulation.nc")


def plot_results(config, o):
    plotter = Plotter(config, o)
    plotter.plot_main()
    plotter.plot_property("z")
    plotter.plot_oil_budget()
    plotter.create_animation()

def main(parameters_folder: str):
    parameters_files = os.listdir(parameters_folder)

    for file in parameters_files:
        print("Running simulation with parameters from file:", file)

        config = ConfigReader.from_yaml(os.path.join(parameters_folder, file))

        # is_dataset_already_processed = check_existing_file(os.getcwd() + "/oil_spill/data/processed/combined_dataset.nc")
        is_dataset_already_processed = False
        if is_dataset_already_processed:
            print("Using already processed dataset...")
            combined_ds = xr.open_dataset("oil_spill/data/processed/combined_dataset.nc")
        else:
            dh, datasets = read_data(config)
            combined_ds = dh.create_combined_dataset(datasets)

        T_reader = Reader(combined_ds, name="NEMO dataset")

        o = OpenOil(loglevel=config.opendrift.log_level)
        run_simulation(T_reader, config, o)
        plot_results(config, o)

        print(f"Simulation for file {file} finished")