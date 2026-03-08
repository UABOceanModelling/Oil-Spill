import xarray as xr
import pandas as pd
import re
from oil_spill.config import ConfigReader


class DatasetFormatter:
    def __init__(self, config: ConfigReader):
        self.renaming_mappings = config.transformation.renaming_mappings
        self.attributes_to_add = config.transformation.attributes_to_add
        self.variables_to_drop = config.transformation.variables_to_drop
        self.datasets_to_format_time = config.transformation.datasets_to_format_time

    def __rename_variables(self, ds_name: str, ds: xr.Dataset):
        variables_to_remove = []
        if ds_name not in self.renaming_mappings:
            return ds

        variables_to_rename = self.renaming_mappings[ds_name]
        renaming_map = variables_to_rename

        for var in variables_to_rename:
            if (var not in ds) and (var not in ds.coords) and (var not in ds.dims):
                print(f"WARNING: Variable '{var}' not found in dataset for renaming. Skipping...")
                variables_to_remove.append(var)

        for var in variables_to_remove:
            renaming_map.pop(var)

        return ds.rename(renaming_map)

    def __add_attributes(self, ds_name: str, ds: xr.Dataset):
        if ds_name not in self.attributes_to_add:
            return ds

        variable_attributes_dict = self.attributes_to_add[ds_name]

        for variable, attributes in variable_attributes_dict.items():
            if variable in ds:
                ds[variable] = ds[variable].assign_attrs(attributes)

        return ds

    def __format_time(self, ds_name: str, ds: xr.Dataset, paths: list):
        if ds_name not in self.datasets_to_format_time:
            return ds

        years = [int(re.search(r"(?<=y)\d{4}", path).group()) for path in paths]
        start_time = pd.Timestamp(year=min(years), month=1, day=1)
        total_hours = ds.sizes["time"]
        times = pd.date_range(start=start_time, periods=total_hours, freq="1H")

        return ds.assign_coords(time=times)

    def __drop_variables(self, ds_name: str, ds: xr.Dataset):
        if ds_name not in self.variables_to_drop:
            return ds

        variables_to_drop = self.variables_to_drop[ds_name]
        return ds.drop_vars(variables_to_drop)

    # TODO: temporary method to fix hdf5 reading issues
    def __remove_time_counter_dimension_from_variables_that_are_equal_along_this_dimension(self, ds: xr.Dataset):
        ds["lat"] = ds["lat"].isel(time_counter=0)
        ds["lon"] = ds["lon"].isel(time_counter=0)
        ds["mbathy"] = ds["mbathy"].isel(time_counter=0).squeeze()
        ds["tmask"] = ds["tmask"].isel(time_counter=0)

        return ds

    def __squeeze_ds(self, ds: xr.Dataset):
        return ds.squeeze()

    def transform_data(self, ds_name: str, ds: xr.Dataset, paths: list) -> xr.Dataset:
        ds = self.__rename_variables(ds_name, ds)
        ds = self.__add_attributes(ds_name, ds)
        ds = self.__drop_variables(ds_name, ds)
        # ds = self.__remove_time_counter_dimension_from_variables_that_are_equal_along_this_dimension(ds)
        ds = self.__squeeze_ds(ds)
        ds = self.__format_time(ds_name, ds, paths)

        return ds
