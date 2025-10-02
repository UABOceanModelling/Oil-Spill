# stdlib
import glob
import yaml
import os

# 3rd party
import xarray as xr


class DatasetReader:
    def __init__(self, data_paths: dict, xarray_parameters: dict):
        self.data_paths = data_paths
        self.xarray_parameters = xarray_parameters

    def read_multi_files(self):
        datasets = {}
        reader_params = self.xarray_parameters.reader
        combine = reader_params.combine
        data_vars = reader_params.data_vars

        for var, pattern in self.data_paths.items():
            paths = glob.glob(pattern)
            if not paths:
                raise FileNotFoundError(f"No files found for variable '{var}' with pattern '{pattern}'")
            datasets[var] = xr.open_mfdataset(paths, combine=combine, data_vars=data_vars)

        return datasets
