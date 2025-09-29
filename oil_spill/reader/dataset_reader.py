import xarray as xr
import glob

class DatasetReader:
    def __init__(self):
        pass

    def read(self):
        U_paths = glob.glob("/mnt/storage7/myers/NEMO/ANHA4-EPM520/ANHA4-EPM520_y2006m01d**_gridU.nc")
        V_paths = glob.glob("/mnt/storage7/myers/NEMO/ANHA4-EPM520/ANHA4-EPM520_y2006m01d**_gridV.nc")
        T_paths = glob.glob("/mnt/storage7/myers/NEMO/ANHA4-EPM520/ANHA4-EPM520_y2006m01d**_gridT.nc")
        W_paths = glob.glob("/mnt/storage7/myers/NEMO/ANHA4-EPM520/ANHA4-EPM520_y2006m01d**_gridW.nc")

        # U_paths = "/mnt/storage7/myers/NEMO/ANHA4-EPM520/ANHA4-EPM520_y2006m01d05_gridU.nc"
        # V_paths = "/mnt/storage7/myers/NEMO/ANHA4-EPM520/ANHA4-EPM520_y2006m01d05_gridV.nc"
        # T_paths = "/mnt/storage7/myers/NEMO/ANHA4-EPM520/ANHA4-EPM520_y2006m01d05_gridT.nc"
        # W_paths = "/mnt/storage7/myers/NEMO/ANHA4-EPM520/ANHA4-EPM520_y2006m01d05_gridW.nc"

        ds_U = xr.open_mfdataset(U_paths, combine="by_coords", data_vars="all")
        ds_V = xr.open_mfdataset(V_paths, combine="by_coords", data_vars="all")
        ds_T = xr.open_mfdataset(T_paths, combine="by_coords", data_vars="all")
        ds_W = xr.open_mfdataset(W_paths, combine="by_coords", data_vars="all")

        # ds_U = xr.open_dataset(U_paths)
        # ds_V = xr.open_dataset(V_paths)
        # ds_T = xr.open_dataset(T_paths)
        # ds_W = xr.open_dataset(W_paths)

        return ds_U, ds_V, ds_T, ds_W
