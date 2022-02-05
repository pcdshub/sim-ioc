"""
BTPS Simulator IOC for unit and integration tests.
"""

import random
from caproto.server import PVGroup, SubGroup, pvproperty

from ..db.motor import Motor
from .utils import main


class StatsPlugin(PVGroup):
    """
    Minimal AreaDetector stats plugin stand-in.

    BTPS will check the array counter update rate and centroid values.
    """
    enable = pvproperty(value=1, name="SimEnable")
    array_counter = pvproperty(value=0, name="ArrayCounter_RBV")
    centroid_x = pvproperty(value=0.0, name="CentroidX_RBV")
    centroid_y = pvproperty(value=0.0, name="CentroidY_RBV")

    @enable.scan(period=1)
    async def enable(self, instance, async_lib):
        if self.enable.value == 0:
            return
       
        await self.array_counter.write(value=self.array_counter.value + 1)
        await self.centroid_x.write(value=random.random())
        await self.centroid_y.write(value=random.random())


class BtpsPrototypeSimulator(PVGroup):
    """
    A simulator for key BTPS PVs in the control system.

    Listed PVs do not include the default "SIM:" prefix.

    PVs
    ---
    Motor - Linear
    LAS:BTS:MCS2:01:m1 (ioc-las-bts-mcs1)
    LAS:BTS:MCS2:01:m4 (ioc-las-bts-mcs1)
    LAS:BTS:MCS2:01:m7 (ioc-las-bts-mcs1)

    Motor - Rotary
    LAS:BTS:MCS2:01:m2 (ioc-las-bts-mcs1)
    LAS:BTS:MCS2:01:m6 (ioc-las-bts-mcs1)
    LAS:BTS:MCS2:01:m8 (ioc-las-bts-mcs1)

    Motor - Goniometer
    LAS:BTS:MCS2:01:m3 (ioc-las-bts-mcs1)
    LAS:BTS:MCS2:01:m5 (ioc-las-bts-mcs1)
    LAS:BTS:MCS2:01:m9 (ioc-las-bts-mcs1)

    Source Gate Valve
    LTLHN:LS1:VGC:01  (plc-las-bts)
    LTLHN:LS5:VGC:01  (plc-las-bts)
    LTLHN:LS8:VGC:01  (plc-las-bts)

    LSS Shutter Request
    LTLHN:LS1:LST:REQ (ioc-las-lhn-bhc-05)
    LTLHN:LS5:LST:REQ (ioc-las-lhn-bhc-05)
    LTLHN:LS8:LST:REQ (ioc-las-lhn-bhc-05)

    LSS Shutter State - Open
    LTLHN:LS1:LST:OPN (ioc-las-lhn-bhc-05)
    LTLHN:LS5:LST:OPN (ioc-las-lhn-bhc-05)
    LTLHN:LS8:LST:OPN (ioc-las-lhn-bhc-05)

    LSS Shutter State - Closed
    LTLHN:LS1:LST:CLS (ioc-las-lhn-bhc-05)
    LTLHN:LS5:LST:CLS (ioc-las-lhn-bhc-05)
    LTLHN:LS8:LST:CLS (ioc-las-lhn-bhc-05)

    NF Camera
    LAS:LHN:BAY1:CAM:01 (ioc-lhn-bay1-nf-01)
    LAS:LHN:BAY3:CAM:01 (?, assumed)
    LAS:LHN:BAY4:CAM:01 (ioc-lhn-bay4-nf-01)

    FF Camera
    LAS:LHN:BAY1:CAM:02 (ioc-lhn-bay1-ff-01)
    LAS:LHN:BAY3:CAM:02 (?, assumed)
    LAS:LHN:BAY4:CAM:02 (ioc-lhn-bay4-ff-01)

    Destination Gate Valve PV
    LTLHN:LD8:VGC:01 (ioc-las-bts) - TMO - IP1
    LTLHN:LD10:VGC:01 (ioc-las-bts) - TMO - IP2
    LTLHN:LD2:VGC:01 (ioc-las-bts) - TMO - IP3
    LTLHN:LD6:VGC:01 (ioc-las-bts) - RIX - qRIXS
    LTLH:LD4:VGC:01 (ioc-las-bts) - RIX - ChemRIXS
    LTLHN:LD14:VGC:01 (ioc-las-bts) - XPP
    LTLHN:LD9:VGC:01 (ioc-las-bts) - Laser Lab
    """

    # Linear motors (ioc-las-bts-mcs1)
    m1 = SubGroup(Motor, prefix="LAS:BTS:MCS2:01:m1", user_limits=(0, 0))
    m4 = SubGroup(Motor, prefix="LAS:BTS:MCS2:01:m4", user_limits=(0, 2000))
    m7 = SubGroup(Motor, prefix="LAS:BTS:MCS2:01:m7", position=405.0, user_limits=(400, 1446.53))

    # Rotary motors
    m2 = SubGroup(Motor, prefix="LAS:BTS:MCS2:01:m2", user_limits=(0, 0))
    m6 = SubGroup(Motor, prefix="LAS:BTS:MCS2:01:m6", user_limits=(-95, 95))
    m8 = SubGroup(Motor, prefix="LAS:BTS:MCS2:01:m8", user_limits=(-300, 300))

    # Rotary motors
    m3 = SubGroup(Motor, prefix="LAS:BTS:MCS2:01:m3", user_limits=(0, 0))
    m5 = SubGroup(Motor, prefix="LAS:BTS:MCS2:01:m5", user_limits=(0, 0))
    m9 = SubGroup(Motor, prefix="LAS:BTS:MCS2:01:m9", user_limits=(0, 0))

    nf_cam_bay1 = SubGroup(StatsPlugin, prefix="LAS:LHN:BAY1:CAM:01:Stats1:")
    nf_cam_bay3 = SubGroup(StatsPlugin, prefix="LAS:LHN:BAY3:CAM:01:Stats1:")
    nf_cam_bay4 = SubGroup(StatsPlugin, prefix="LAS:LHN:BAY4:CAM:01:Stats1:")

    ff_cam_bay1 = SubGroup(StatsPlugin, prefix="LAS:LHN:BAY1:CAM:02:Stats1:")
    ff_cam_bay3 = SubGroup(StatsPlugin, prefix="LAS:LHN:BAY3:CAM:02:Stats1:")
    ff_cam_bay4 = SubGroup(StatsPlugin, prefix="LAS:LHN:BAY4:CAM:02:Stats1:")


if __name__ == "__main__":
    main(cls=BtpsPrototypeSimulator, default_prefix="SIM:")
