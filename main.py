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

    directory = config.output.directory
    plot = config.output.files.plot
    animation = config.output.files.animation
    o.plot(filename=directory + "plots/" + plot, linecolor="z")

    # o.animation(filename=directory + "animations/" + animation, fast=True)

    


def run():
    config = ConfigReader.from_yaml("parameters.yaml")

    import matplotlib.pyplot as plt
    dh, datasets, mask_ds = read_data(config)

    combined_ds = dh.create_combined_dataset(datasets, mask_ds)
    # combined_ds["land_binary_mask"].isel(time_counter=0, deptht=0).plot()
    # import matplotlib.pyplot as plt
    # plt.show()
    # raise

    T_reader = Reader(combined_ds, name="NEMO dataset")

    run_simulation(T_reader, config)

    # netcdf = config.output.files.netcdf
    # directory = config.output.directory
    # combined_ds.to_netcdf(directory + netcdf)


if __name__ == "__main__":
    run()
