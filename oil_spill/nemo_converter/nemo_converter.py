import xarray as xr
import numpy as np
import pyproj

class NemoConverter:
    def interpolate(self, data_array: xr.DataArray, dimension_slice_start: dict, dimension_slice_end: dict, dimension_to_add_nan: str, map_rename: dict=None) -> xr.DataArray:
        d_array = 0.5 * (data_array.isel(**dimension_slice_start) + data_array.isel(**dimension_slice_end))

        d_array = self.add_nan_column(d_array, dimension_to_add_nan)

        d_array = d_array.rename(map_rename)

        return d_array

    def interpolate_w(self, dataset: xr.Dataset, deptht) -> xr.DataArray:
        W_on_T_data = 0.5 * (dataset['vovecrtz'].isel({"grid_W_3D_inner": slice(0, -1)}).data +
                            dataset['vovecrtz'].isel({"grid_W_3D_inner": slice(1, None)}).data)

        W_on_T_data = np.concatenate([W_on_T_data, np.full((W_on_T_data.shape[0], 1, W_on_T_data.shape[2], W_on_T_data.shape[3]), np.nan)], axis=1)
        # z_old = dataset['grid_W_3D_inner'].values
        # z_new = 0.5 * (z_old[:-1] + z_old[1:])
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


    def add_nan_column(self, arr: xr.DataArray, dimension: str) -> xr.DataArray:
        nan_col = xr.full_like(arr.isel(**{dimension: 0}), np.nan)
        arr = xr.concat([arr, nan_col], dim=dimension)

        return arr
    
    def drop_dims(self, dims_list: list, dataset: xr.Dataset) -> xr.Dataset:
        ds = dataset.drop_dims(dims_list)
        return ds

    def rename_dims(self, dataset: xr.Dataset, map_rename: dict) -> xr.Dataset:
        ds = dataset.rename(map_rename)
        return ds

    def convert_lat_lon_to_meters(self, lon: xr.DataArray, lat: xr.DataArray) -> tuple[xr.DataArray, xr.DataArray]:
        proj = pyproj.Proj(proj="stere", lat_0=90, lon_0=-45, lat_ts=70, ellps="WGS84")

        X_m, Y_m = proj(lon, lat)
        X_coord = X_m[0, :]
        Y_coord = Y_m[:, 0]

        return X_coord, Y_coord
