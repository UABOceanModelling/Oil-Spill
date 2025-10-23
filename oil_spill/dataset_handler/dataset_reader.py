# stdlib
import glob
import yaml
import os

# 3rd party
import xarray as xr


class DatasetReader:
    def __read_multi_files(self, data_paths):
        datasets = {}

        for var, pattern in data_paths.items():
            paths = glob.glob(pattern)
            if not paths:
                raise FileNotFoundError(f"No files found for variable '{var}' with pattern '{pattern}'")
            datasets[var] = xr.open_mfdataset(
                paths,
                combine="by_coords", 
                data_vars="all", 
                decode_cf=False, 
                # chunks={"time_counter": 10}
            )
            datasets[var].attrs["source_files"] = [os.path.basename(p) for p in paths]

        return datasets

    def read_datasets(self, data_paths_dict: dict) -> dict:
        datasets = self.__read_multi_files(data_paths_dict)
        return datasets
