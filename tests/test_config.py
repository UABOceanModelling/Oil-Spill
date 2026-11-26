import textwrap

import pytest

from oil_spill.config import ConfigError, ConfigReader

VALID = """
experiment:
  name: "My Exp"
input:
  nemo: data/a.nc
opendrift:
  seeding:
    lat: 80
    lon: -100
    number: 10
    radius: 50
    oil_type: "GENERIC DIESEL"
"""


def write(tmp_path, text):
    path = tmp_path / "exp.yaml"
    path.write_text(textwrap.dedent(text))
    return path


def test_minimal_config_gets_defaults(tmp_path):
    cfg = ConfigReader.from_yaml(write(tmp_path, VALID))
    assert cfg.opendrift.log_level == 20
    assert cfg.output.directory == "output/"
    assert cfg.output.files["netcdf"] == "oil_spill.nc"
    assert cfg.transformation.renaming_mappings == {}


def test_partial_output_files_keep_other_defaults(tmp_path):
    text = VALID + "output:\n  files:\n    plot: custom.png\n"
    cfg = ConfigReader.from_yaml(write(tmp_path, text))
    assert cfg.output.files["plot"] == "custom.png"
    assert cfg.output.files["animation"] == "oil_spill.mp4"


def test_unquoted_date_becomes_string(tmp_path):
    text = VALID.replace('name: "My Exp"', 'name: x\n  date: 2006-01-01')
    assert ConfigReader.from_yaml(write(tmp_path, text)).experiment.date == "2006-01-01"


def test_run_directory_is_safe_and_unique_per_experiment(tmp_path):
    cfg = ConfigReader.from_yaml(write(tmp_path, VALID))
    parts = cfg.run_directory().parts
    assert "My_Exp" in parts
    assert "GENERIC_DIESEL" in parts
    assert parts[-1] == "particles_10-radius_50_m"


@pytest.mark.parametrize(
    "text, message",
    [
        ("- not a mapping", "top level"),
        ("experiment: {name: x}\nopendrift: {seeding: {lat: 1, lon: 1}}", "'input'"),
        ("experiment: {name: x}\ninput: {a: b}", "'opendrift'"),
        ("experiment: {name: x}\ninput: {a: b}\nopendrift: {seeding: {lat: 1}}", "lon"),
        (VALID + "extra: 1\n", None),  # unknown top-level keys are tolerated
        (VALID.replace("experiment:", "experiment:\n  bogus: 1"), "unknown keys"),
        (VALID + "transformation:\n  renaming_mappings:\n    a: b\n", "renaming_mappings"),
    ],
)
def test_invalid_configs(tmp_path, text, message):
    path = write(tmp_path, text)
    if message is None:
        ConfigReader.from_yaml(path)
        return
    with pytest.raises(ConfigError, match=message):
        ConfigReader.from_yaml(path)


def test_error_message_mentions_file(tmp_path):
    path = write(tmp_path, "experiment: {name: x}")
    with pytest.raises(ConfigError, match="exp.yaml"):
        ConfigReader.from_yaml(path)
