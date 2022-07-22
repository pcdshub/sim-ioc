"""
BTPS Simulator IOC for unit and integration tests.
"""

import dataclasses
from typing import cast

from caproto import ChannelData
from caproto.server import AsyncLibraryLayer, PVGroup, SubGroup, pvproperty

from ..db.btps import (BtpsMotorsAndCameras, BtpsState, BtsGateValves,
                       LssShutters, RangeComparison)
from .utils import main


@dataclasses.dataclass
class SourceDestinationConfiguration:
    source: int
    destination: int

    linear: float
    rotary: float
    goniometer: float


sample_config = sum(
    (
        [
            # TMO IP1
            SourceDestinationConfiguration(
                source=source,
                destination=1,
                linear=1357.0,
                rotary=-89.7,
                goniometer=0.0,
            ),
            # TMO IP2
            SourceDestinationConfiguration(
                source=source,
                destination=2,
                linear=1000.,
                rotary=-89.0,
                goniometer=0.0,
            ),
            # TMO IP3
            SourceDestinationConfiguration(
                source=source,
                destination=3,
                linear=750.,
                rotary=-89.0,
                goniometer=0.0,
            ),
            # qRIXS
            SourceDestinationConfiguration(
                source=source,
                destination=4,
                linear=500.,
                rotary=-89.0,
                goniometer=0.0,
            ),
            # ChemRIXS
            SourceDestinationConfiguration(
                source=source,
                destination=5,
                linear=250.,
                rotary=-89.0,
                goniometer=0.0,
            ),
            # XPP
            SourceDestinationConfiguration(
                source=source,
                destination=6,
                linear=59.0,
                rotary=-89.0,
                goniometer=0.0,
            ),
            # Laser lab
            SourceDestinationConfiguration(
                source=source,
                destination=7,
                linear=0.,
                rotary=-89.0,
                goniometer=0.0,
            ),
        ]
        for source in [1, 5, 8]
    ),
    []
)


class BtpsSimulator(PVGroup):
    """
    A simulator for BTPS motors, cameras, and range logic.

    Listed PVs do not include the default "SIM:" prefix.
    """

    motors: BtpsMotorsAndCameras = SubGroup(BtpsMotorsAndCameras, prefix="")
    state: BtpsState = SubGroup(BtpsState, prefix="LTLHN:")
    shutters: LssShutters = SubGroup(LssShutters, prefix="")
    gate_valves: BtsGateValves = SubGroup(BtsGateValves, prefix="")
    load_config = pvproperty(name="LTLHN:BTPS:Sim:LoadConfig", value=0)

    @load_config.startup
    async def load_config(self, instance: ChannelData, async_lib: AsyncLibraryLayer):
        print("Loading sample config...")
        for conf in sample_config:
            dest = self.state.destinations[conf.destination]
            source = dest.sources[conf.source]

            for range_, nominal in [
                (source.linear, conf.linear),
                (source.goniometer, conf.goniometer),
                (source.rotary, conf.rotary),
            ]:
                range_ = cast(RangeComparison, range_)
                await range_.set_nominal(nominal)


if __name__ == "__main__":
    main(cls=BtpsSimulator, default_prefix="SIM:")
