import random

import caproto.server
from caproto.server import PVGroup, pvproperty


class StatsPlugin(PVGroup):
    """
    Minimal AreaDetector stats plugin stand-in.

    BTPS will check the array counter update rate and centroid values.
    """

    enable = pvproperty(value=1, name="SimEnable")
    array_counter = pvproperty(value=0, name="ArrayCounter_RBV")
    centroid_x = pvproperty(value=0.0, name="CentroidX_RBV")
    centroid_y = pvproperty(value=0.0, name="CentroidY_RBV")
    total = pvproperty(value=0.0, name="Total_RBV")

    @enable.scan(period=1)
    async def enable(
        self,
        instance: caproto.ChannelInteger,
        async_lib: caproto.server.AsyncLibraryLayer,
    ):
        if self.enable.value == 0:
            return

        await self.array_counter.write(value=self.array_counter.value + 1)
        await self.centroid_x.write(value=random.random())
        await self.centroid_y.write(value=random.random())
        await self.total.write(value=random.random())
