from dataclasses import dataclass
from pathlib import Path
import yaml


@dataclass
class OpenDrift:
    dataset: dict
    log_level: int
    end_time: str
    time_step: int
    seeding: dict


@dataclass
class Output:
    directory: str
    files: dict


@dataclass
class Xarray:
    datasets: dict


@dataclass
class Experiment:
    name: str
    description: str
    date: str


@dataclass
class Transformation:
    renaming_mappings: dict
    attributes_to_add: dict
    variables_to_drop: list
    datasets_to_format_time: list


@dataclass
class ConfigReader:
    experiment: Experiment
    input: dict
    output: Output
    xarray: Xarray
    opendrift: OpenDrift
    transformation: Transformation

    @classmethod
    def from_yaml(cls, path: str):
        path = Path(path)
        with open(path, "r") as f:
            data = yaml.safe_load(f)

        return cls(
            experiment=Experiment(**data["experiment"]),
            opendrift=OpenDrift(**data["opendrift"]),
            input=data["input"],
            output=Output(**data["output"]),
            xarray=Xarray(**data["xarray"]),
            transformation=Transformation(**data["transformation"]),
        )
