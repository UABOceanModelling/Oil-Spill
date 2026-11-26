import logging
from typing import Dict

import xarray as xr

logger = logging.getLogger(__name__)


class DatasetFormatter:
    """Applies the `transformation` section of the config to each dataset.

    Both mappings are keyed by dataset name (the keys of `input` in the YAML):
      renaming_mappings: {dataset: {old_name: new_name}}
      attributes_to_add: {dataset: {variable: {attribute: value}}}
    """

    def __init__(self, config):
        self.renaming_mappings = config.transformation.renaming_mappings
        self.attributes_to_add = config.transformation.attributes_to_add

    def _rename_variables(self, name: str, ds: xr.Dataset) -> xr.Dataset:
        mapping = {}
        for old, new in self.renaming_mappings.get(name, {}).items():
            if old == new:
                continue
            if old not in ds.variables and old not in ds.dims:
                logger.warning(
                    "Dataset '%s': '%s' not found, skipping rename to '%s'", name, old, new
                )
                continue
            mapping[old] = new
        return ds.rename(mapping) if mapping else ds

    def _add_attributes(self, name: str, ds: xr.Dataset) -> xr.Dataset:
        for var, attrs in self.attributes_to_add.get(name, {}).items():
            if var not in ds.variables:
                logger.warning("Dataset '%s': variable '%s' not found, skipping attributes", name, var)
                continue
            ds[var].attrs.update(attrs)
        return ds

    def transform_data(self, datasets: Dict[str, xr.Dataset]) -> Dict[str, xr.Dataset]:
        """Return a new dict with the transformed datasets (input dict is untouched)."""
        configured = set(self.renaming_mappings) | set(self.attributes_to_add)
        for unused in sorted(configured - set(datasets)):
            logger.info("Transformation configured for '%s' but no such input dataset; ignored", unused)

        transformed = {}
        for name, ds in datasets.items():
            ds = self._rename_variables(name, ds)
            transformed[name] = self._add_attributes(name, ds)
        return transformed
