"""
BTPS Simulator IOC for unit and integration tests.
"""

import dataclasses
from typing import cast

from caproto import ChannelData
from caproto.server import AsyncLibraryLayer, PVGroup, SubGroup, pvproperty

from ..db.btps import BtpsMotorsAndCameras, BtpsState, RangeComparison
from .utils import main


@dataclasses.dataclass
class SourceDestinationConfiguration:
    source: int
    destination: int

    linear: float
    rotary: float
    goniometer: float


# GVL_BTPS.fbDestinations[1](sName:='TMO IP1', fbDestinationValve:=GVL_BTS_VAC.fb_LD8_VGC);
# GVL_BTPS.fbDestinations[2](sName:='TMO IP2', fbDestinationValve:=GVL_BTS_VAC.fb_LD10_VGC);
# GVL_BTPS.fbDestinations[3](sName:='TMO IP3', fbDestinationValve:=GVL_BTS_VAC.fb_LD2_VGC);
# GVL_BTPS.fbDestinations[4](sName:='RIX qRIXS', fbDestinationValve:=GVL_BTS_VAC.fb_LD6_VGC);
# GVL_BTPS.fbDestinations[5](sName:='RIX ChemRIXS', fbDestinationValve:=GVL_BTS_VAC.fb_LD4_VGC);
# GVL_BTPS.fbDestinations[6](sName:='XPP', fbDestinationValve:=GVL_BTS_VAC.fb_LD14_VGC);
# GVL_BTPS.fbDestinations[7](sName:='Laser Lab', fbDestinationValve:=GVL_BTS_VAC.fb_LD9_VGC);

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
        for source in [1, 3, 4]
    ),
    []
)


class BtpsSimulator(PVGroup):
    """
    A simulator for BTPS motors, cameras, and range logic.

    Listed PVs do not include the default "SIM:" prefix.
    """

    motors: BtpsMotorsAndCameras = SubGroup(BtpsMotorsAndCameras, prefix="")
    state: BtpsState = SubGroup(BtpsState, prefix="LTLHN:BTPS:")
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
