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


def check_U_data(ds: xr.Dataset):
    # ds = ds.isel(
    #     y_grid_U=slice(530, 750),
    #     x_grid_U=slice(120, 430),
    # )

    ds71 = ds.isel(
        # x_grid_U=71,
        x_grid_U=191,
        # y_grid_U=87,
        y_grid_U=617,
        time_counter=0
    )
    print(ds71["vozocrtx"].values)
    print("length", len(ds71["vozocrtx"].values))

    ds72 = ds.isel(
        x_grid_U=192,
        y_grid_U=617,
        time_counter=0
    )
    print(ds72["vozocrtx"].values)
    print("length", len(ds72["vozocrtx"].values))

def check_data(ds: xr.Dataset):
    da = ds["nav_lat_grid_T"]
    subset = ds.where((ds.nav_lat_grid_T == 78) & (ds.nav_lon_grid_T == 127))
    non_nan_count = np.sum(~np.isnan(subset["votemper"].values))
    print(non_nan_count)
    raise
    print(da.isel(nav_lat_grid_T=0, nav_lon_grid_T=0))

    raise


def select_subset_data(ds: xr.Dataset):
    lon = -33
    lat = 84
    dist = np.sqrt(
        (ds["nav_lat_grid_T"] - lat) ** 2 +
        (ds["nav_lon_grid_T"] - lon) ** 2
    )

    iy, ix = np.unravel_index(dist.argmin(), dist.shape)

    dados_ponto = ds.isel(Y=iy, X=ix)

    print(dados_ponto["nav_lat_grid_T"].values)
    print(dados_ponto["nav_lon_grid_T"].values)
    # print(dados_ponto['u'])
    # print(dados_ponto['v'])
    # print(dados_ponto['w'])
    # print(dados_ponto['votemper'])
    # print(dados_ponto['vosaline'])
    raise
    ds = ds.isel(
        X=71,
        Y=87,
        # deptht=20,
        time_counter=0
    )

    # print("temp component:")
    # print(ds["votemper"].values)

    # print("sal component:")
    # print(ds["vosaline"].values)

    print("U component:")
    print(ds["u"].values)

    # print("V component:")
    # print(ds["v"].values)

    # print("W component:")
    # print(ds["w"].values)
    # raise
    # ds.to_netcdf("subset.nc")

def replace_values(ds: xr.Dataset):
    ds['u'] = ds['u'].where(ds['u'] != 0, 0.5)
    ds['v'] = ds['v'].where(ds['v'] != 0, -0.5)
    ds['w'] = ds['w'].where(ds['w'] != 0, 0.5)
    ds['votemper'] = ds['votemper'].where(ds['votemper'] != 0, 0.5)
    ds['vosaline'] = ds['vosaline'].where(ds['vosaline'] != 0, 0.5)

    return ds

if __name__ == "__main__":
    run()
