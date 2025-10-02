# stdlib
import glob
import yaml
import os

# 3rd party
import xarray as xr


class DatasetReader:
    def __init__(self):
        base_dir = os.path.dirname(__file__)
        self.config_file_path = os.path.join(base_dir, "../../parameters.yaml")

    def __read_config_file(self):
        try:
            with open(self.config_file_path, "r") as file:
                self.file = yaml.safe_load(file)
        except FileNotFoundError:
            print(f"Config file not found: {self.config_file_path}")
            raise
        except yaml.YAMLError as e:
            print(f"Invalid YAML format in {self.config_file_path}: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error reading config file {self.config_file_path}: {e}")
            raise

    def __validate_config(self):
        required_data_paths = ["U", "V", "T", "W"]
        data_paths = self.file.get("data_paths")

        if not data_paths:
            raise ValueError("Missing 'data_paths' section in config file.")

        for key in required_data_paths:
            if key not in data_paths:
                raise ValueError(f"Missing path for '{key}' in config file.")

        xarray_params = self.file.get("xarray_parameters")
        if not xarray_params:
            raise ValueError("Missing 'xarray_parameters' section in config file.")

        reader_params = xarray_params.get("reader_parameters")
        if not reader_params:
            raise ValueError("Missing 'reader_parameters' inside 'xarray_parameters'.")

        if "combine" not in reader_params or "data_vars" not in reader_params:
            raise ValueError("Missing required keys in 'reader_parameters'.")

    def read(self):
        self.__read_config_file()
        self.__validate_config()
        variables_paths = ["U", "V", "T", "W"]

        U_paths, V_paths, T_paths, W_paths = [glob.glob(self.file.get("data_paths").get(var)) for var in variables_paths]

        xarray_params = self.file.get("xarray_parameters")
        combine = xarray_params.get("reader_parameters").get("combine")
        data_vars = xarray_params.get("reader_parameters").get("data_vars")

        ds_U, ds_V, ds_T, ds_W = [xr.open_mfdataset(paths, combine=combine, data_vars=data_vars) for paths in [U_paths, V_paths, T_paths, W_paths]]

        return ds_U, ds_V, ds_T, ds_W
