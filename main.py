# stdlib
from datetime import timedelta
from pprint import pprint

# opendrift
from opendrift.models.openoil import OpenOil
from opendrift.readers.reader_netCDF_CF_generic import Reader

# local
from oil_spill.dataset_utils import DatasetHandler
from oil_spill.reader import DatasetReader
from oil_spill.utils import set_configuration
from oil_spill.config import ConfigReader


def run():
    # Load configuration
    config = ConfigReader.from_yaml("parameters.yaml")

    o = OpenOil(loglevel=config.opendrift.log_level)

    dr = DatasetReader(data_paths=config.input_data.data_paths, xarray_parameters=config.xarray_parameters)
    dh = DatasetHandler(
        interpolation=config.transformations.interpolation,
        renaming=config.transformations.renaming,
        attributes_to_add=config.transformations.attributes_to_add,
        slicing=config.transformations.slicing,
        keep=config.transformations.keep,
    )
    datasets = dr.read_multi_files()

    combined_ds = dh.create_combined_dataset(datasets)

    combined_ds = dh.add_mask(combined_ds)

    combined_ds = dh.clean_dataset(combined_ds)

    combined_ds = dh.select_subset_of_data(combined_ds)
    print(combined_ds)
    raise

    T_reader = Reader(combined_ds, name="NEMO dataset")

    o.add_reader([T_reader])

    set_configuration(o)

    o.seed_elements(lon=-100, lat=81, number=1000, radius=10000, time=T_reader.start_time, oil_type="GENERIC DIESEL")

    o.run()
    o.plot(filename="oil_spill/output/plots/oil_spill_simulation.png", linecolor="z")

    o.animation(filename="oil_spill/output/animations/oil_spill_simulation.mp4", fast=True)


if __name__ == "__main__":
    run()
