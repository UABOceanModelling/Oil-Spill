import numpy as np
import xarray as xr

from oil_spill.config.config_reader import Transformation
from oil_spill.dataset_handler import DatasetFormatter


class FakeConfig:
    def __init__(self, renaming=None, attributes=None):
        self.transformation = Transformation(renaming or {}, attributes or {})


def make_ds(var):
    return xr.Dataset({var: ("time", np.arange(3.0))}, coords={"time": [0, 1, 2]})


def test_rename_is_per_dataset_and_does_not_leak():
    cfg = FakeConfig(renaming={"x_wind": {"u_wind": "x_wind"}, "y_wind": {"v_wind": "y_wind"}})
    datasets = {"x_wind": make_ds("u_wind"), "y_wind": make_ds("v_wind")}

    out = DatasetFormatter(cfg).transform_data(datasets)

    assert "x_wind" in out["x_wind"] and "y_wind" in out["y_wind"]
    # config is not consumed: running again still works
    out2 = DatasetFormatter(cfg).transform_data(datasets)
    assert "y_wind" in out2["y_wind"]


def test_missing_variable_is_skipped_and_input_untouched():
    cfg = FakeConfig(renaming={"nemo": {"nope": "yes", "a": "b"}})
    datasets = {"nemo": make_ds("a")}

    out = DatasetFormatter(cfg).transform_data(datasets)

    assert "b" in out["nemo"]
    assert "a" in datasets["nemo"]  # original dict/dataset unchanged


def test_unconfigured_dataset_passes_through():
    cfg = FakeConfig(renaming={"other": {"a": "b"}})
    datasets = {"nemo": make_ds("a")}
    assert "a" in DatasetFormatter(cfg).transform_data(datasets)["nemo"]


def test_attributes_added_to_variables_and_coords():
    cfg = FakeConfig(
        attributes={"w": {"x_wind": {"standard_name": "x_wind"}, "time": {"standard_name": "time"}}}
    )
    out = DatasetFormatter(cfg).transform_data({"w": make_ds("x_wind")})["w"]
    assert out["x_wind"].attrs["standard_name"] == "x_wind"
    assert out["time"].attrs["standard_name"] == "time"
