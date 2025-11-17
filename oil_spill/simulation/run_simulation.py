# stdlib
from typing import List
from datetime import datetime, timedelta

import numpy as np
import xarray as xr

# opendrift
import opendrift
from opendrift.models.openoil import OpenOil
from opendrift.readers.reader_netCDF_CF_generic import Reader

# local
from oil_spill.config import ConfigReader
from oil_spill.utils import set_configuration, create_directory, file_exists


def run_simulation(readers: List[Reader], config: ConfigReader, o: OpenOil):
    o.add_reader(readers)

    set_configuration(o)
    
    seeding_config = config.opendrift.seeding.copy()
    levels = np.arange(0, config.opendrift.seeding["z"], -1)
    if len(levels) == 0:
        levels = [config.opendrift.seeding["z"]]
    particles_per_level = config.opendrift.seeding["number"] // len(levels)
    z = np.repeat(levels, particles_per_level)

    seeding_config['z'] = z

    o.seed_elements(**seeding_config)

    directory = config.output.directory
    lat = config.opendrift.seeding["lat"]
    lon = config.opendrift.seeding["lon"]
    oil_type = config.opendrift.seeding["oil_type"]
    number_of_particles = config.opendrift.seeding["number"]
    radius = config.opendrift.seeding["radius"]
    z_file = config.opendrift.seeding["z"]
    start_time = config.opendrift.seeding["time"]
    end_time = config.opendrift.end_time
    time_step = config.opendrift.time_step

    output_directory = create_directory(
        directory
        + "simulations/"
        + f"{start_time}-{end_time}/"
        + f"lat_{lat}_lon_{lon}/"
        + f"{oil_type}/"
        + f"{z_file}_m_depth/"
        + f"particles_{number_of_particles}-radius_{radius}_m"
    )

    outfile_path = create_directory(output_directory + "/ncfiles") + "/" + config.output.files["netcdf"]

    o.run(end_time=end_time, time_step=timedelta(minutes=time_step), outfile=outfile_path)
    return o
