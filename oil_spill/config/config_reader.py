"""Experiment configuration: YAML loading and validation."""

from __future__ import annotations

import re
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any, Dict

import yaml

DEFAULT_OUTPUT_FILES = {
    "netcdf": "oil_spill.nc",
    "plot": "oil_spill.png",
    "animation": "oil_spill.mp4",
    "log": "oil_spill.log",
}


class ConfigError(ValueError):
    """Raised when an experiment YAML file is malformed or incomplete."""


def _slug(value: Any) -> str:
    """Make a string safe to use as a directory name."""
    return re.sub(r"[^A-Za-z0-9._-]+", "_", str(value)).strip("_") or "unnamed"


def _is_mapping_of(value: Any, depth: int) -> bool:
    """True if `value` is a dict nested `depth` levels deep with string keys."""
    if not isinstance(value, dict) or not all(isinstance(k, str) for k in value):
        return False
    if depth == 1:
        return True
    return all(_is_mapping_of(v, depth - 1) for v in value.values())


@dataclass
class Experiment:
    name: str
    description: str = ""
    date: str = ""

    def __post_init__(self):
        # YAML turns an unquoted `2006-01-01` into a date object.
        self.date = str(self.date)


@dataclass
class OpenDrift:
    seeding: dict
    dataset: dict = field(default_factory=dict)
    log_level: int = 20

    def __post_init__(self):
        if not isinstance(self.seeding, dict):
            raise ConfigError("'opendrift.seeding' must be a mapping")
        missing = [key for key in ("lat", "lon") if key not in self.seeding]
        if missing:
            raise ConfigError(f"'opendrift.seeding' is missing required keys: {missing}")


@dataclass
class Output:
    directory: str = "output/"
    files: dict = field(default_factory=dict)

    def __post_init__(self):
        self.files = {**DEFAULT_OUTPUT_FILES, **(self.files or {})}


@dataclass
class Transformation:
    """Per-dataset transformations, keyed by the dataset name used in `input`.

    renaming_mappings: {dataset: {old_name: new_name}}
    attributes_to_add: {dataset: {variable: {attribute: value}}}
    """

    renaming_mappings: dict = field(default_factory=dict)
    attributes_to_add: dict = field(default_factory=dict)

    def __post_init__(self):
        self.renaming_mappings = self.renaming_mappings or {}
        self.attributes_to_add = self.attributes_to_add or {}
        if not _is_mapping_of(self.renaming_mappings, 2) or not all(
            isinstance(new, str)
            for mapping in self.renaming_mappings.values()
            for new in mapping.values()
        ):
            raise ConfigError(
                "'transformation.renaming_mappings' must look like "
                "{dataset: {old_name: new_name}}"
            )
        if not _is_mapping_of(self.attributes_to_add, 3):
            raise ConfigError(
                "'transformation.attributes_to_add' must look like "
                "{dataset: {variable: {attribute: value}}}"
            )


def _section(data: dict, key: str, required: bool = False) -> dict:
    value = data.get(key)
    if value is None:
        if required:
            raise ConfigError(f"missing required section '{key}'")
        return {}
    if not isinstance(value, dict):
        raise ConfigError(f"section '{key}' must be a mapping")
    return value


def _build(cls, section: str, values: dict):
    allowed = {f.name for f in fields(cls)}
    unknown = sorted(set(values) - allowed)
    if unknown:
        raise ConfigError(
            f"unknown keys in section '{section}': {unknown} (allowed: {sorted(allowed)})"
        )
    try:
        return cls(**values)
    except TypeError as exc:
        raise ConfigError(f"invalid section '{section}': {exc}") from exc


@dataclass
class ConfigReader:
    experiment: Experiment
    input: Dict[str, str]
    output: Output
    opendrift: OpenDrift
    transformation: Transformation

    @classmethod
    def from_yaml(cls, path: str | Path) -> "ConfigReader":
        path = Path(path)
        with open(path, "r") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise ConfigError(f"{path}: expected a YAML mapping at the top level")

        try:
            input_ = _section(data, "input", required=True)
            if not input_ or not all(isinstance(p, str) for p in input_.values()):
                raise ConfigError("'input' must map dataset names to file paths")

            return cls(
                experiment=_build(Experiment, "experiment", _section(data, "experiment", True)),
                input=input_,
                output=_build(Output, "output", _section(data, "output")),
                opendrift=_build(OpenDrift, "opendrift", _section(data, "opendrift", True)),
                transformation=_build(
                    Transformation, "transformation", _section(data, "transformation")
                ),
            )
        except ConfigError as exc:
            raise ConfigError(f"{path}: {exc}") from exc

    def run_directory(self) -> Path:
        """Directory where everything produced by this experiment is written.

        Includes the experiment name so that experiments that share the same
        seeding parameters do not overwrite each other.
        """
        seeding = self.opendrift.seeding
        return (
            Path(self.output.directory)
            / _slug(self.experiment.name)
            / f"lat_{seeding['lat']}_lon_{seeding['lon']}"
            / _slug(seeding.get("oil_type", "default"))
            / f"particles_{seeding.get('number', 'default')}-radius_{seeding.get('radius', 'default')}_m"
        )
