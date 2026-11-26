from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from oil_spill.utils import create_directory

if TYPE_CHECKING:
    from opendrift.models.openoil import OpenOil

    from oil_spill.config import ConfigReader


class Plotter:
    def __init__(self, config: "ConfigReader", o: "OpenOil"):
        self.o = o
        self.plot_name = config.output.files["plot"]
        self.animation_name = config.output.files["animation"]
        self.output_directory = Path(create_directory(config.run_directory()))

    def _target(self, *parts: str) -> str:
        """Path (as str, for OpenDrift) of a file below the run directory; creates its folder."""
        path = self.output_directory.joinpath(*parts)
        create_directory(path.parent)
        return str(path)

    def plot_main(self):
        self.o.plot(
            filename=self._target("plots", self.plot_name),
            linecolor="z",
        )

    def create_animation(self):
        self.o.animation(
            filename=self._target("animations", self.animation_name),
            color="z",
            fast=True,
        )

    def plot_property(self, property_name: str):
        self.o.plot_property(
            property_name,
            filename=self._target("plots", "properties", f"{property_name}.png"),
        )

    def plot_oil_budget(self):
        self.o.plot_oil_budget(
            filename=self._target("plots", "budget", "oil_budget.png"),
        )
