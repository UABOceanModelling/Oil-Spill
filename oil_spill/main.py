import argparse
import logging
import shutil
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import xarray as xr

# opendrift
from opendrift.models.openoil import OpenOil
from opendrift.readers.reader_netCDF_CF_generic import Reader

# local
from oil_spill.config import ConfigReader
from oil_spill.dataset_handler import DatasetFormatter, DatasetReader, close_datasets
from oil_spill.plotter import Plotter
from oil_spill.utils import create_directory, find_config_files
from oil_spill.utils.set_configuration import set_configuration

logger = logging.getLogger("oil_spill")

DEFAULT_CONFIG_PATH = "experiments/"
LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"


def read_data(config: ConfigReader) -> Dict[str, xr.Dataset]:
    return DatasetReader().read_datasets(config.input)


def transform_data(config: ConfigReader, datasets: Dict[str, xr.Dataset]) -> Dict[str, xr.Dataset]:
    return DatasetFormatter(config).transform_data(datasets)


def run_simulation(
    readers: List[Reader],
    config: ConfigReader,
    o: OpenOil,
    outfile: Optional[Path] = None,
):
    o.add_reader(readers)

    set_configuration(o)

    seeding_config = {
        "time": readers[0].start_time,
    }
    seeding_config.update(config.opendrift.seeding)

    o.seed_elements(**seeding_config)

    if outfile is not None:
        o.run(outfile=str(outfile))
    else:
        o.run()


def plot_results(config: ConfigReader, o: OpenOil):
    plotter = Plotter(config, o)
    try:
        plotter.plot_main()
        plotter.plot_property("z")
        plotter.plot_oil_budget()
        plotter.create_animation()
    finally:
        plt.close("all")


@contextmanager
def _file_logging(log_path: Path):
    """Also write this package's log records to `log_path` while inside the block."""
    handler = logging.FileHandler(log_path)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(handler)
    try:
        yield
    finally:
        logger.removeHandler(handler)
        handler.close()


def run_experiment(config_path: Path):
    config = ConfigReader.from_yaml(config_path)

    run_dir = Path(create_directory(config.run_directory()))
    with _file_logging(run_dir / config.output.files["log"]):
        logger.info("Experiment '%s' (config: %s)", config.experiment.name, config_path)
        logger.info("Outputs will be written to %s", run_dir)
        # Keep the exact config next to the results.
        shutil.copy2(config_path, run_dir / config_path.name)

        datasets = read_data(config)
        try:
            datasets = transform_data(config, datasets)

            readers = [Reader(ds, name=name) for name, ds in datasets.items()]

            o = OpenOil(loglevel=config.opendrift.log_level)
            run_simulation(readers, config, o, outfile=run_dir / config.output.files["netcdf"])
            plot_results(config, o)
        finally:
            close_datasets(datasets)


def main(config_path: str = DEFAULT_CONFIG_PATH) -> int:
    """Run every experiment found at `config_path` (a YAML file or a folder).

    A failing experiment is logged and does not stop the others. Returns the
    process exit code: 0 if all succeeded, 1 otherwise.
    """
    failed = []
    for path in find_config_files(config_path):
        logger.info("Running simulation with parameters from file: %s", path)
        try:
            run_experiment(path)
        except Exception:
            logger.exception("Simulation for file %s failed", path)
            failed.append(path)
        else:
            logger.info("Simulation for file %s finished", path)

    if failed:
        logger.error("%d experiment(s) failed: %s", len(failed), ", ".join(map(str, failed)))
        return 1
    return 0


def cli(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Run OpenDrift oil spill experiments.")
    parser.add_argument(
        "config",
        nargs="?",
        default=DEFAULT_CONFIG_PATH,
        help="experiment YAML file, or a folder of them (default: %(default)s)",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    sys.exit(main(args.config))
