from dataclasses import dataclass
from pathlib import Path
import yaml


@dataclass
class AncillaryPaths:
    mask: str


@dataclass
class InputData:
    data_paths: dict
    ancillary_paths: AncillaryPaths

@dataclass
class VariableConfig:
    source_var: str
    dims_mapping: dict

@dataclass
class Interpolation:
    target_grid: str
    variables: dict[str, VariableConfig]

@dataclass
class AttributesToAdd:
    file: dict
    variables: dict

@dataclass
class Slicing:
    region_of_interest: dict

@dataclass
class Keep:
    variables: list
    coords: list

@dataclass
class Transformations:
    interpolation: Interpolation
    renaming: dict
    attributes_to_add: AttributesToAdd
    slicing: Slicing
    keep: Keep


@dataclass
class Reader:
    combine: str
    data_vars: str


@dataclass
class XarrayParameters:
    engine: str
    reader: Reader


@dataclass
class Dataset:
    name: str


# @dataclass
# class Seeding:
#     lon: float
#     lat: float
#     number: int
#     radius: float
#     z: float
#     time: str
#     oil_type: str


@dataclass
class OpenDrift:
    dataset: Dataset
    seeding: dict
    log_level: str


@dataclass
class Files:
    netcdf: str
    plot: str
    animation: str
    log: str


@dataclass
class Output:
    directory: str
    files: Files


@dataclass
class Experiment:
    name: str
    description: str
    date: str


@dataclass
class ConfigReader:
    experiment: Experiment
    input_data: InputData
    transformations: Transformations
    xarray_parameters: XarrayParameters
    opendrift: OpenDrift
    output: Output

    @classmethod
    def from_yaml(cls, path: str):
        path = Path(path)
        with open(path, "r") as f:
            data = yaml.safe_load(f)

        variables = {
            k: VariableConfig(**v) for k, v in data["transformations"]["interpolation"]["variables"].items()
        }

        return cls(
            experiment=Experiment(**data["experiment"]),
            input_data=InputData(
                data_paths=data["input_data"]["data_paths"],
                ancillary_paths=AncillaryPaths(**data["input_data"]["ancillary_paths"]),
            ),
            transformations=Transformations(
                interpolation=Interpolation(data["transformations"]["interpolation"]["target_grid"], variables),
                renaming=data["transformations"]["renaming"],
                attributes_to_add=AttributesToAdd(**data["transformations"]["attributes_to_add"]),
                slicing=Slicing(**data["transformations"]["slicing"]),
                keep=Keep(**data["transformations"]["keep"]),
            ),
            xarray_parameters=XarrayParameters(
                engine=data["xarray"]["engine"],
                reader=Reader(**data["xarray"]["reader"]),
            ),
            opendrift=OpenDrift(
                dataset=Dataset(**data["opendrift"]["dataset"]),
                log_level=data["opendrift"]["log_level"],
                seeding=data["opendrift"]["seeding"],
            ),
            output=Output(
                directory=data["output"]["directory"],
                files=Files(**data["output"]["files"]),
            ),
        )
