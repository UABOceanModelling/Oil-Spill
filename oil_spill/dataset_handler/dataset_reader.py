# stdlib
import glob
import yaml
import os

# 3rd party
import xarray as xr


class DatasetReader:
    def __read_single_file(self, path) -> xr.Dataset:
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found at path: {path}")
        ds = xr.open_dataset(path, engine="netcdf4")
        return ds

    def __read_multi_files(self, data_paths):
        datasets = {}

        for var, pattern in data_paths.items():
            paths = glob.glob(pattern)
            if not paths:
                raise FileNotFoundError(f"No files found for variable '{var}' with pattern '{pattern}'")
            datasets[var] = xr.open_mfdataset(paths, combine="by_coords", data_vars="all", decode_cf=False)

        return datasets

    def read_datasets(self, data_paths_dict: dict) -> dict:
        datasets = self.__read_multi_files(data_paths_dict)
        return datasets
