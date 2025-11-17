# stdlib
import glob
import yaml
import os

# 3rd party
import xarray as xr

from oil_spill.utils import file_exists


class DatasetReader:
    def __init__(self, config):
        self.data_paths = config.input
        self.datasets_config_dict = config.xarray.datasets

    def read_multi_files(self, data_paths_list: list, params: dict) -> xr.Dataset:
        return xr.open_mfdataset(data_paths_list, **params)

    def read_single_file(self, path, additional_params):
        return xr.open_dataset(path, **additional_params)

    def get_file_paths(self):
        paths_dict = {}
        for var, pattern in self.data_paths.items():
            paths = sorted(glob.glob(pattern))
            if not paths:
                raise FileNotFoundError(f"No files found for variable '{var}' with pattern '{pattern}'")
            paths_dict[var] = paths
        return paths_dict
