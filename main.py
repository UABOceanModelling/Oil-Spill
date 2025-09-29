from datetime import timedelta
from opendrift.models import openoil
import xarray as xr
import numpy as np

from opendrift.models.openoil import OpenOil
from opendrift.readers.reader_netCDF_CF_generic import Reader

from oil_spill.nemo_converter import NemoConverter
from oil_spill.reader import DatasetReader


def adapt_dataset(ds_U: xr.Dataset, ds_V: xr.Dataset, ds_T: xr.Dataset, ds_W: xr.Dataset):
    nc = NemoConverter()
    # ds_T = ds_T.rename({"nav_lon_grid_T": "lon", "nav_lat_grid_T": "lat"})

    # X_coord, Y_coord = nc.convert_lat_lon_to_meters(ds_T["lon"], ds_T["lat"])

    ds_T = ds_T.rename(
        {
            "x_grid_T": "X",
            "y_grid_T": "Y",
        }
    )

    # ds_T = ds_T.assign_coords(X=X_coord, Y=Y_coord)

    # ds_T["X"].attrs = {
    #     "units": "m",
    #     "standard_name": "projection_x_coordinate",
    #     "axis": "X",
    # }
    # ds_T["Y"].attrs = {
    #     "units": "m",
    #     "standard_name": "projection_y_coordinate",
    #     "axis": "Y",
    # }

    # ds_T["lon"] = (("Y", "X"), ds_T["lon"].values)
    # ds_T["lat"] = (("Y", "X"), ds_T["lat"].values)

    u = nc.interpolate(
        data_array=ds_U["vozocrtx"],
        dimension_slice_start={"x_grid_U": slice(0, -1)},
        dimension_slice_end={"x_grid_U": slice(1, None)},
        dimension_to_add_nan="x_grid_U",
        map_rename={"x_grid_U": "X", "y_grid_U": "Y", "depthu": "deptht"},
    )
    v = nc.interpolate(
        data_array=ds_V["vomecrty"],
        dimension_slice_start={"y_grid_V": slice(0, -1)},
        dimension_slice_end={"y_grid_V": slice(1, None)},
        dimension_to_add_nan="y_grid_V",
        map_rename={"x_grid_V": "X", "y_grid_V": "Y", "depthv": "deptht"},
    )
    w = nc.interpolate_w(ds_W, ds_T["deptht"])
    # w = nc.interpolate(
    #     data_array=ds_W["vovecrtz"],
    #     dimension_slice_start={"grid_W_3D_inner": slice(0, -1)},
    #     dimension_slice_end={"grid_W_3D_inner": slice(1, None)},
    #     dimension_to_add_nan="grid_W_3D_inner",
    #     map_rename={"grid_W_3D_inner": "deptht"},
    # )

    ds_T["u"] = u
    ds_T["v"] = v
    ds_T["w"] = w
    ds_T["deptht"].attrs["standard_name"] = "depth"
    ds_T["u"].attrs["standard_name"] = "x_sea_water_velocity"
    ds_T["v"].attrs["standard_name"] = "y_sea_water_velocity"

    return ds_T


def select_subset_of_data(ds: xr.Dataset, variables_mapping: dict) -> xr.Dataset:
    ds = ds.isel(
        **variables_mapping,
    )

    return ds

def set_configuration(o: OpenOil):
    o.set_config("environment:fallback:x_wind", 3)
    o.set_config("environment:fallback:y_wind", 7)
    o.set_config("drift:vertical_mixing", True)
    o.set_config("seed:droplet_size_distribution", "uniform")
    o.set_config("seed:droplet_diameter_min_subsea", 0.0001)
    o.set_config("seed:droplet_diameter_max_subsea", 0.0005)

def add_mask(ds: xr.Dataset) -> xr.Dataset:
    tahya_mask = "/mnt/storage4/tahya/runoff/runoff_comp_regions.nc"
    mask_ds = xr.open_dataset(tahya_mask)

    mask = mask_ds["tmask"].isel(t=0)
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

    return ds

def clean_dataset(ds: xr.Dataset) -> xr.Dataset:
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

def run():
    output_nc_file = "oil_spill_simulation.nc"

    o = OpenOil(loglevel=0)
    dr = DatasetReader()
    ds_U, ds_V, ds_T, ds_W = dr.read()

    combined_ds = adapt_dataset(ds_U, ds_V, ds_T, ds_W)

    combined_ds = add_mask(combined_ds)

    combined_ds = clean_dataset(combined_ds)

    combined_ds = select_subset_of_data(combined_ds, {"Y": slice(530, 750), "X": slice(120, 430)})

    T_reader = Reader(combined_ds, name="NEMO dataset")
    print(T_reader)
    raise

    o.add_reader([T_reader])

    set_configuration(o)

    o.seed_elements(
        lon=-60, lat=75, number=10, radius=10, time=T_reader.start_time, oil_type="GENERIC DIESEL"
    )

    o.run(outfile=output_nc_file)

    o.animation("oil_spill_simulation.mp4")


if __name__ == "__main__":
    run()
