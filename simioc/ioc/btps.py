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


# Bottom destinations (rough top centers, inside chamber)
BOTTOM_PORTS = [
    1,
    2,
    3,
    4,
    5,
    6,
    7,
]
TOP_PORTS = [
    8,
    9,
    10,
    11,
    12,
    13,
    14,
]


def guess_position_for_port(dest: int) -> float:
    """
    Make a guess at a linear stage position given the destination port number.

    Parameters
    ----------
    dest : int
        The destination port number.

    Returns
    -------
    float
        Linear stage position guess.
    """
    # 8.5" spacing per side
    # 215.9 mm port-to-port
    port_spacing_mm = 215.9
    top_start = 30.0000
    bottom_start = top_start + port_spacing_mm / 2

    if dest in TOP_PORTS:
        port_index = TOP_PORTS.index(dest)
        start = top_start
    else:
        port_index = BOTTOM_PORTS.index(dest)
        start = bottom_start

    return start + port_index * port_spacing_mm


sample_config = sum(
    (
        [
            # TMO IP1 (LD8)
            SourceDestinationConfiguration(
                source=source,
                destination=8,
                linear=guess_position_for_port(8),
                rotary=-89.7,
                goniometer=0.0,
            ),
            # TMO IP2 (LD10)
            SourceDestinationConfiguration(
                source=source,
                destination=10,
                linear=guess_position_for_port(10),
                rotary=-89.0,
                goniometer=0.0,
            ),
            # TMO IP3 (LD2)
            SourceDestinationConfiguration(
                source=source,
                destination=2,
                linear=guess_position_for_port(2),
                rotary=-89.0,
                goniometer=0.0,
            ),
            # qRIXS (LD6)
            SourceDestinationConfiguration(
                source=source,
                destination=6,
                linear=guess_position_for_port(6),
                rotary=-89.0,
                goniometer=0.0,
            ),
            # ChemRIXS (LD4)
            SourceDestinationConfiguration(
                source=source,
                destination=4,
                linear=guess_position_for_port(4),
                rotary=-89.0,
                goniometer=0.0,
            ),
            # XPP (LD14)
            SourceDestinationConfiguration(
                source=source,
                destination=14,
                linear=guess_position_for_port(14),
                rotary=-89.0,
                goniometer=0.0,
            ),
            # Laser lab (LD9)
            SourceDestinationConfiguration(
                source=source,
                destination=9,
                linear=guess_position_for_port(9),
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
                await range_.set_nominal(nominal, atol=5.0)


if __name__ == "__main__":
    main(cls=BtpsSimulator, default_prefix="SIM:")
