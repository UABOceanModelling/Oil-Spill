from dataclasses import dataclass
from pathlib import Path
import yaml
from typing import Any, Dict


@dataclass
class OpenDrift:
    dataset: dict
    seeding: dict
    log_level: int


@dataclass
class Output:
    directory: str
    files: dict


@dataclass
class Experiment:
    name: str
    description: str
    date: str

@dataclass
class Transformation:
    renaming_mappings: dict
    attributes_to_add: dict

@dataclass
class ConfigReader:
    experiment: Experiment
    input: dict
    output: Output
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
            transformation=Transformation(**data["transformation"]),
        )
