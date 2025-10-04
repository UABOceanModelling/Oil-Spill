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

    def select_subset_of_data(self, ds: xr.Dataset) -> xr.Dataset:
        variables_mapping = {key: slice(start, end) for key, (start, end) in self.region_of_interest.items()}
        ds = ds.isel(
            **variables_mapping,
        )

        return ds

    def add_mask(self, ds: xr.Dataset) -> xr.Dataset:
        tahya_mask = "/mnt/storage4/tahya/runoff/runoff_comp_regions.nc"
        mask_ds = xr.open_dataset(tahya_mask)
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
            attrs={"standard_name": "land_binary_mask"}
        )

        ds["land_binary_mask"] = mask_broadcasted
        ds["land_binary_mask"] = ds["land_binary_mask"].fillna(0).astype(int)

        return ds

    def clean_dataset(self, ds: xr.Dataset) -> xr.Dataset:
        vars_to_drop = [v for v in ds.data_vars if v not in self.vars_to_keep]
        ds = ds.drop_vars(vars_to_drop)

        coords_to_drop = [c for c in ds.coords if c not in self.coords_to_keep]
        ds = ds.drop_vars(coords_to_drop)

        return ds

    def interpolate(self, data_array: xr.DataArray, dimension_slice_start: dict, dimension_slice_end: dict) -> xr.DataArray:
        d_array = 0.5 * (data_array.isel(**dimension_slice_start) + data_array.isel(**dimension_slice_end))

        return d_array

    def interpolate_w(self, dataset: xr.Dataset, deptht) -> xr.DataArray:
        W_on_T_data = 0.5 * (dataset['vovecrtz'].isel({"grid_W_3D_inner": slice(0, -1)}).data +
                            dataset['vovecrtz'].isel({"grid_W_3D_inner": slice(1, None)}).data)

        W_on_T_data = np.concatenate([W_on_T_data, np.full((W_on_T_data.shape[0], 1, W_on_T_data.shape[2], W_on_T_data.shape[3]), np.nan)], axis=1)
        W_on_T = xr.DataArray(
            W_on_T_data,
            dims=('time_counter', "deptht", 'y', 'x'),
            coords={
                'time_counter': dataset['time_counter'],
                'deptht': deptht,
                'y': dataset['y'],
                'x': dataset['x']
            },
            attrs=dataset['vovecrtz'].attrs,
            name="w",
        )

        W_on_T = W_on_T.rename({'y': "Y", 'x': "X"})

        return W_on_T


    def __add_nan_column(self, arr: xr.DataArray, dimension: str) -> xr.DataArray:
        print(dimension)
        raise
        last_col = arr.isel(**{dimension: -1})
        
        print(arr)
        arr = xr.concat([arr, last_col], dim=dimension)
        print(arr)
        raise

        return arr

    def __add_atributes(self, ds: xr.Dataset) -> xr.Dataset:
        for attr, value in self.file_attributes.items():
            ds.attrs[attr] = value

        for var, attrs in self.variable_attributes.items():
            if var in ds:
                for attr, value in attrs.items():
                    ds[var].attrs[attr] = value

        return ds
        
    def create_combined_dataset(self, datasets: List[xr.Dataset]) -> xr.Dataset:
        for var, ds in datasets.items():
            print(self.variables[var].source_var)
            raise
            variable_dimension, target_dimension = self.dimensions[var].items()
            print(variable_dimension)
            print(target_dimension)
            raise
            if not var == self.target_grid:
                interpolated_data_array = self.interpolate(
                    data_array=ds[self.variables[var]],
                    dimension_slice_start={self.dimensions[var]: slice(0, -1)},
                    dimension_slice_end={self.dimensions[var]: slice(1, None)},
                )
                if var == "W":
                    print(interpolated_data_array)
                    raise

                # print(datasets[self.target_grid][self.variables[self.target_grid]].size)
                interpolated_data_array = self.__add_nan_column(interpolated_data_array, self.dimensions[var])

                datasets[var][self.variables[var]] = interpolated_data_array
            
        raise
        for var, rename_map in self.renaming.items():
            # NOTE: FIX FOR W VARIABLE
            # if not var == "W":
                if var in datasets:
                    datasets[var] = datasets[var].rename(rename_map)

        # NOTE: FIX FOR W VARIABLE
        datasets["W"]["vovecrtz"] = self.interpolate_w(datasets["W"], datasets["T"]["deptht"])

        target_dataset = datasets[self.target_grid]
        for var, dataset in datasets.items():
            if not var == self.target_grid:
                target_dataset[var.lower()] = dataset[self.variables[var]]

        ds = self.__add_atributes(target_dataset)

        return ds