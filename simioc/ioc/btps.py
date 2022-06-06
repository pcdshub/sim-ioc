"""
BTPS Simulator IOC for unit and integration tests.
"""

from caproto import ChannelData
from caproto.server import AsyncLibraryLayer, PVGroup, SubGroup, pvproperty

from ..db.btps import BtpsMotorsAndCameras, BtpsState
from .utils import main


class BtpsSimulator(PVGroup):
    """
    A simulator for BTPS motors, cameras, and range logic.

    Listed PVs do not include the default "SIM:" prefix.
    """

    motors = SubGroup(BtpsMotorsAndCameras, prefix="")
    state = SubGroup(BtpsState, prefix="LTLHN:BTPS:")
    load_config = pvproperty(name="LTLHN:BTPS:Sim:LoadConfig", value=0)

    @load_config.startup
    async def load_config(self, instance: ChannelData, async_lib: AsyncLibraryLayer):
        ...


if __name__ == "__main__":
    main(cls=BtpsSimulator, default_prefix="SIM:")
