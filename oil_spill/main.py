# stdlib
import os
import time
from pprint import pprint

# opendrift
import opendrift
from opendrift.models.openoil import OpenOil
from opendrift.readers.reader_netCDF_CF_generic import Reader

# local
from oil_spill.dataset_handler import DatasetReader
from oil_spill.dataset_handler import DatasetFormatter
from oil_spill.plotter import Plotter
from oil_spill.config import ConfigReader
from oil_spill.simulation import run_simulation


def plot_results(config, o: OpenOil):
    plotter = Plotter(config, o)
    plotter.plot_main()
    plotter.plot_property("z")
    plotter.plot_oil_budget()
    # plotter.create_animation()
    # plotter.animate_vertical_distribution()


def main(file: str):
    s_time = time.time()

    print("Running simulation with parameters from file:", file)

    config = ConfigReader.from_yaml(os.path.join(file))
    pprint(config)

    dr = DatasetReader(config)
    file_paths = dr.get_file_paths()
    datasets_config_dict = config.xarray.datasets
    df = DatasetFormatter(config)

    readers = []
    for name, paths in file_paths.items():
        if name not in datasets_config_dict:
            raise ValueError(f"{name} not found in xarray configuration")

        params = datasets_config_dict[name]["open_dataset_params"]
        read_data_mode = datasets_config_dict[name]["read_data_mode"]
        if read_data_mode == "together":
            ds = dr.read_multi_files(paths, params)
            ds = df.transform_data(name, ds, paths)
            readers.append(Reader(ds, name=name))
            ds.close()
        elif read_data_mode == "separately":
            # for path in paths:
            #     ds = dr.read_single_file(path, params)
            #     ds = df.transform_data(name, ds, [path])
            #     readers.append(Reader(ds, name=path))
            #     ds.close()
            raise ValueError(
                f"Unknown read data mode {read_data_mode}. Options are: together, separately."
            )
        else:
            raise ValueError(
                f"Unknown read data mode {read_data_mode}. Options are: together, separately."
            )

    o = OpenOil(loglevel=config.opendrift.log_level)
    # o = opendrift.open("/home/caion/projects/rrg-pmyers-ad/caio/Oil-Spill/old_library-output/simulations/2002-07-01 12:00:00-2003-07-01 12:00:00/lat_68_lon_-114/GENERIC DIESEL/0_m_depth/particles_5000-radius_100_m/ncfiles/oil_spill.nc")
    o = run_simulation(readers, config, o)
    # plot_results(config, o)

    print(f"Simulation for file {file} finished")

    e_time = time.time()
    duration = (e_time - s_time) / 60
    print(f"Execution took {duration} minutes.")
