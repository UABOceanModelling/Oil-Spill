# stdlib
import os
from typing import List

# opendrift
from opendrift.models.openoil import OpenOil
from opendrift.readers.reader_netCDF_CF_generic import Reader

# local
from oil_spill.dataset_handler import DatasetReader
from oil_spill.dataset_handler import DatasetFormatter
from oil_spill.config import ConfigReader
from oil_spill.plotter import Plotter
from oil_spill.utils import set_configuration


def read_data(config: ConfigReader):
    dr = DatasetReader()
    datasets = dr.read_datasets(config.input)

    return datasets


def transform_data(config: ConfigReader, datasets: dict) -> dict:
    df = DatasetFormatter(config)
    df.transform_data(datasets)

    return datasets


def run_simulation(readers: List[Reader], config: ConfigReader, o: OpenOil):
    o.add_reader(readers)

    set_configuration(o)

    seeding_config = {
        "time": readers[0].start_time,
    }
    seeding_config.update(config.opendrift.seeding)

    o.seed_elements(**seeding_config)

    o.run()


def plot_results(config, o):
    plotter = Plotter(config, o)
    plotter.plot_main()
    plotter.plot_property("z")
    plotter.plot_oil_budget()
    plotter.create_animation()


def main(config_folder: str):
    parameters_files = os.listdir(config_folder)

    for file in parameters_files:
        print("Running simulation with parameters from file:", file)

        config = ConfigReader.from_yaml(os.path.join(config_folder, file))

        datasets = read_data(config)
        datasets = transform_data(config, datasets)

        readers = [Reader(ds, name=name) for name, ds in datasets.items()]

        o = OpenOil(loglevel=config.opendrift.log_level)
        run_simulation(readers, config, o)
        plot_results(config, o)

        print(f"Simulation for file {file} finished")
