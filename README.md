# oil_spill

Oil spill simulations with [OpenDrift](https://github.com/OpenDrift/opendrift)
(`OpenOil`) using NEMO ocean data (e.g. ANHA4) or other NetCDF datasets.
Each experiment is described by a YAML file; the program runs the simulation,
saves the NetCDF result and produces plots and an animation.

## Requirements

- Python >= 3.10
- OpenDrift. If you use a local checkout of OpenDrift, install it in editable
  mode, for example:

  ```bash
  pip install -e . --config-settings editable_mode=strict
  ```
- `ffmpeg` (needed to write the `.mp4` animation)

## Installation

```bash
pip install -e ".[dev]"      # or: make install
```

## Usage

Put the input NetCDF files under `data/` and describe the experiment in a YAML
file inside `experiments/` (see `experiments/open_oil_simulation.yaml`). Run
from the repository root, because the paths in the YAML are relative:

```bash
python app.py                                   # every .yaml/.yml in experiments/
python app.py experiments/open_oil_simulation.yaml   # a single experiment
python app.py some/other/folder                 # another folder
make run                                        # same as `python app.py`
make run-bg                                     # in the background, log in output.txt
```

A failing experiment is logged and the remaining ones still run; the exit code
is `1` if any experiment failed.

## Configuration

| Section | Purpose |
| --- | --- |
| `experiment` | `name` (required), `description`, `date`. |
| `input` | Dataset name -> NetCDF path. Each entry becomes an OpenDrift reader named after the key. |
| `output` | `directory` (default `output/`) and `files` (`netcdf`, `plot`, `animation`, `log`; defaults are `oil_spill.*`). |
| `opendrift` | `seeding` (required, at least `lat` and `lon`; the rest is passed to `seed_elements`), `log_level`, `dataset`. |
| `transformation` | Optional, **per dataset** (use the same names as in `input`): `renaming_mappings: {dataset: {old: new}}` and `attributes_to_add: {dataset: {variable: {attr: value}}}`. |

Unknown keys and malformed sections are rejected with an error that names the
file and the section.

## Output

Everything for one experiment goes in a single folder:

```
<output.directory>/<experiment.name>/lat_<lat>_lon_<lon>/<oil_type>/particles_<n>-radius_<r>_m/
├── oil_spill.nc          # simulation result (OpenDrift output)
├── oil_spill.log         # log of this run
├── <config>.yaml         # copy of the configuration that produced it
├── plots/                # trajectory plot, properties/z.png, budget/oil_budget.png
└── animations/
```

## Development

```bash
make test        # or: python -m pytest
```

The tests do not require OpenDrift. Input/output handling lives in
`oil_spill/dataset_handler`, configuration in `oil_spill/config`, plotting in
`oil_spill/plotter` and the OpenDrift setup in `oil_spill/utils/set_configuration.py`.
