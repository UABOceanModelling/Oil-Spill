import xarray as xr
import numpy as np

class DatasetHandler:
    def __init__(self):
        pass

    def select_subset_of_data(self, ds: xr.Dataset, variables_mapping: dict) -> xr.Dataset:
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
        keep_vars = [
            "u",
            "v",
            "w",
            "votemper",
            "vosaline",
            "sossheig",
            "land_binary_mask"
        ]

        keep_coords = [
            "X", "Y", "deptht", "time_counter", "nav_lon_grid_T", "nav_lat_grid_T"
        ]

        vars_to_drop = [v for v in ds.data_vars if v not in keep_vars]
        ds = ds.drop_vars(vars_to_drop)

        coords_to_drop = [c for c in ds.coords if c not in keep_coords]
        ds = ds.drop_vars(coords_to_drop)

        return ds