import pytest
import xarray as xr

from oil_spill.dataset_handler import DatasetReader, close_datasets
from oil_spill.utils import create_directory, find_config_files


def test_find_config_files_filters_and_sorts(tmp_path):
    for name in ("b.yaml", "a.yml", "notes.txt", ".DS_Store"):
        (tmp_path / name).write_text("")
    assert [p.name for p in find_config_files(tmp_path)] == ["a.yml", "b.yaml"]


def test_find_config_files_single_file(tmp_path):
    f = tmp_path / "x.yaml"
    f.write_text("")
    assert find_config_files(f) == [f]


def test_find_config_files_errors(tmp_path):
    with pytest.raises(FileNotFoundError):
        find_config_files(tmp_path / "missing")
    with pytest.raises(FileNotFoundError):
        find_config_files(tmp_path)  # empty folder


def test_create_directory_nested_and_idempotent(tmp_path):
    target = tmp_path / "a" / "b"
    assert create_directory(target) == str(target.resolve())
    assert create_directory(target) == str(target.resolve())


def test_reader_reads_and_reports_missing(tmp_path):
    path = tmp_path / "d.nc"
    xr.Dataset({"v": ("t", [1, 2])}).to_netcdf(path)

    reader = DatasetReader()
    datasets = reader.read_datasets({"d": str(path)})
    assert "v" in datasets["d"]
    close_datasets(datasets)

    with pytest.raises(FileNotFoundError):
        reader.read_datasets({"d": str(path), "bad": str(tmp_path / "nope.nc")})
