import logging
from pathlib import Path
from typing import Dict, Mapping

import xarray as xr

logger = logging.getLogger(__name__)


class DatasetReader:
    def __init__(self, engine: str = "netcdf4"):
        self.engine = engine

    def _read_single_file(self, path: str) -> xr.Dataset:
        path = Path(path).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"File not found at path: {path}")
        logger.info("Opening dataset %s", path)
        return xr.open_dataset(path, engine=self.engine)

    def read_datasets(self, data_paths: Mapping[str, str]) -> Dict[str, xr.Dataset]:
        """Open every dataset in `data_paths` ({name: file path})."""
        datasets: Dict[str, xr.Dataset] = {}
        try:
            for name, path in data_paths.items():
                datasets[name] = self._read_single_file(path)
        except Exception:
            close_datasets(datasets)
            raise
        return datasets


def close_datasets(datasets: Mapping[str, xr.Dataset]) -> None:
    for ds in datasets.values():
        ds.close()
