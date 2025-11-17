import time
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
import xarray as xr
from matplotlib.colors import ListedColormap


def __set_up_map():
    proj = ccrs.NorthPolarStereo()
    proj_lonlat = ccrs.PlateCarree()
    fig, ax = plt.subplots(subplot_kw={"projection": proj}, figsize=(10, 10))
    lonmin, lonmax, latmin, latmax = -150, -120, 70, 90
    ax.set_extent([lonmin, lonmax, latmin, latmax])
    ax.gridlines(color="gray", linestyle="--", linewidth=0.5, draw_labels=True, zorder=20)
    return proj, proj_lonlat, fig, ax


def run_plots(mask_ds):
    proj, proj_lonlat, fig, ax = __set_up_map()
    lon = mask_ds["nav_lon"]
    lat = mask_ds["nav_lat"]
    mask = mask_ds["tmask"].isel(t=0, z=0)
    cmap = ListedColormap(["#999999", (0, 0, 0, 0)])
    ax.pcolormesh(lon, lat, mask, cmap=cmap, shading="nearest", transform=proj_lonlat, zorder=10)
    plt.savefig(f"output/figures/fig_{time.time()}.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    mask_file = "/home/caion/projects/rrg-pmyers-ad/ANHA4-I/ANHA4_mesh_mask.nc"
    mask_ds = xr.open_dataset(mask_file)
    run_plots(mask_ds)