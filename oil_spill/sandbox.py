import xarray as xr

ds_U = xr.open_dataset("/mnt/storage7/myers/NEMO/ANHA4-EPM520/ANHA4-EPM520_y2006m01d05_gridU.nc")
ds_V = xr.open_dataset("/mnt/storage7/myers/NEMO/ANHA4-EPM520/ANHA4-EPM520_y2006m01d05_gridV.nc")
ds_T = xr.open_dataset("/mnt/storage7/myers/NEMO/ANHA4-EPM520/ANHA4-EPM520_y2006m01d05_gridT.nc")
ds_W = xr.open_dataset("/mnt/storage7/myers/NEMO/ANHA4-EPM520/ANHA4-EPM520_y2006m01d05_gridW.nc")
ds_icemod = xr.open_dataset("/mnt/storage7/myers/NEMO/ANHA4-EPM520/ANHA4-EPM520_y2006m01d05_icemod.nc")


def print_U_grid():
    print("--------------- GRID U ---------------")
    print(list(ds_U.variables))
    print(ds_U["nav_lat_grid_U"].values)

def print_V_grid():
    print("--------------- GRID V ---------------")
    print(ds_V)
    print(list(ds_V.variables))
    print(ds_V["vomecrty"])

def print_T_grid():
    print("--------------- GRID T ---------------")
    # print(ds_T)
    # print(list(ds_T.variables))
    da = ds_T["nav_lon_grid_T"].isel(
        y_grid_T = 0,
        x_grid_T = 0
    )
    print(da.values)

def print_W_grid():
    print("--------------- GRID W ---------------")
    print(ds_W)
    print(list(ds_W.variables))
    print(ds_W["vovecrtz"])

def print_ice_mod():
    print("--------------- ICE MOD ---------------")
    print(ds_icemod)
    print(list(ds_icemod.variables))


def print_variables():
    print("----------- Variables in ds_u ---------------")
    print(list(ds_U.variables))
    print("----------- Variables in ds_v ---------------")
    print(list(ds_V.variables))
    print("----------- Variables in ds_t ---------------")
    print(list(ds_T.variables))
    print("----------- Variables in ds_w ---------------")
    print(list(ds_W.variables))
    print("----------- Variables in ds_icemod ---------------")
    print(list(ds_icemod.variables))


# print_variables()
# print_U_grid()
# print_V_grid()
print_T_grid()
# print_W_grid()
# print_ice_mod()


# ds_n = xr.open_dataset("/mnt/storage6/caio/manual_pkgs/opendrift/tests/test_data/14Jan2016_NorKyst_z_3d/NorKyst-800m_ZDEPTHS_his_00_3Dsubset.nc")

# print("--------------- NORKYST ---------------")
# print(ds_n)