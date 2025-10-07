from typing import List
import xarray as xr
import numpy as np


class DatasetHandler:
    def __init__(self, interpolation, renaming, attributes_to_add, slicing, keep):
        self.target_grid = interpolation.target_grid
        self.variables = interpolation.variables
        self.renaming = renaming
        self.region_of_interest = slicing.region_of_interest
        self.vars_to_keep = keep.variables
        self.coords_to_keep = keep.coords
        self.file_attributes = attributes_to_add.file
        self.variable_attributes = attributes_to_add.variables
        self.region_of_interest = slicing.region_of_interest

    def __select_subset_of_data(self, ds: xr.Dataset) -> xr.Dataset:
        variables_mapping = {key: slice(start, end) for key, (start, end) in self.region_of_interest.items()}
        ds = ds.isel(
            **variables_mapping,
        )

        return ds

    def __add_mask(self, ds: xr.Dataset, mask_ds: xr.Dataset) -> xr.Dataset:
        mask = mask_ds["tmask"].fillna(0).astype(int)

        time_len = ds["time_counter"].size
        depth_len = ds["deptht"].size
        Y_len = ds["Y"].size
        X_len = ds["X"].size

        mask_broadcasted = xr.DataArray(
            np.broadcast_to(mask.values, (time_len, depth_len, Y_len, X_len)),
            dims=["time_counter", "deptht", "Y", "X"],
            coords={
                "time_counter": ds["time_counter"],
                "deptht": ds["deptht"],
                "Y": ds["Y"],
                "X": ds["X"],
            },
            attrs={"standard_name": "land_binary_mask"},
        )

        ds["land_binary_mask"] = mask_broadcasted
        ds["land_binary_mask"] = ds["land_binary_mask"].fillna(0).astype(int)

        return ds

    def __clean_dataset(self, ds: xr.Dataset) -> xr.Dataset:
        vars_to_drop = [v for v in ds.data_vars if v not in self.vars_to_keep]
        ds = ds.drop_vars(vars_to_drop)

        coords_to_drop = [c for c in ds.coords if c not in self.coords_to_keep]
        ds = ds.drop_vars(coords_to_drop)

        return ds

    def interpolate(self, data_array: xr.DataArray, dimension_slice_start: dict, dimension_slice_end: dict) -> xr.DataArray:
        d_array = 0.5 * (data_array.isel(**dimension_slice_start) + data_array.isel(**dimension_slice_end))

        return d_array

    def __fill_values(self, arr: xr.DataArray, dimension: str, target_dim_size: int) -> xr.DataArray:
        times_to_add = target_dim_size - arr[dimension].size

        if times_to_add <= 0:
            return arr

        last_col = arr.isel({dimension: -1})
        repeats = [last_col] * times_to_add
        arr = xr.concat([arr, *repeats], dim=dimension)

        if dimension in arr.coords:
            arr = arr.drop_vars(dimension)

        return arr

    def __add_atributes(self, ds: xr.Dataset) -> xr.Dataset:
        for attr, value in self.file_attributes.items():
            ds.attrs[attr] = value

        for var, attrs in self.variable_attributes.items():
            if var in ds:
                for attr, value in attrs.items():
                    ds[var].attrs[attr] = value

        return ds

    def __rename_variables(self, datasets: List[xr.Dataset]) -> xr.Dataset:
        for var, rename_map in self.renaming.items():
            if var in datasets:
                datasets[var] = datasets[var].rename(rename_map)

    def __join_datasets(self, datasets: List[xr.Dataset]) -> xr.Dataset:
        target_ds = datasets[self.target_grid]
        for var, dataset in datasets.items():
            if not var == self.target_grid:
                target_ds[var.lower()] = dataset[self.variables[var].source_var]
        return target_ds

    def __run_interpolation(self, datasets: List[xr.Dataset]):
        target_ds = datasets[self.target_grid]
        for var, ds in datasets.items():
            if not var == self.target_grid:
                variable_dim, target_dim = next(iter(self.variables[var].dims_mapping.items()))
                dimension_slice_start = {variable_dim: slice(0, -1)}
                dimension_slice_end = {variable_dim: slice(1, None)}

                interpolated_data_array = self.interpolate(
                    data_array=ds[self.variables[var].source_var],
                    dimension_slice_start=dimension_slice_start,
                    dimension_slice_end=dimension_slice_end,
                )

                target_dim_size = target_ds[target_dim].size
                interpolated_data_array = self.__fill_values(interpolated_data_array, variable_dim, target_dim_size)

                datasets[var][self.variables[var].source_var] = interpolated_data_array

    def create_combined_dataset(self, datasets: List[xr.Dataset], mask_ds: xr.Dataset) -> xr.Dataset:

        self.__run_interpolation(datasets)

        self.__rename_variables(datasets)

        ds = self.__join_datasets(datasets)

        ds = self.__add_atributes(ds)

        ds = self.__add_mask(ds, mask_ds)

        ds = self.__clean_dataset(ds)

        ds = self.__select_subset_of_data(ds)

        return ds
