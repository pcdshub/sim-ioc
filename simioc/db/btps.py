"""
BTPS Simulator "database" PVGroups for reuse.
"""

from __future__ import annotations

from typing import Dict, cast

import caproto
from caproto import ChannelType
from caproto.server import PVGroup, SubGroup, pvproperty

from .areadetector import StatsPlugin
from .motor import Motor
from .utils import pvproperty_with_rbv, write_if_differs
from .valve import VGC


class BtpsMotorsAndCameras(PVGroup):
    """
    A simulator for key motion and camera PVs in the control system.

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

    NF Camera
        LAS:LHN:BAY1:CAM:01 (ioc-lhn-bay1-nf-01)
        LAS:LHN:BAY3:CAM:01 (?, assumed)
        LAS:LHN:BAY4:CAM:01 (ioc-lhn-bay4-nf-01)

    FF Camera
        LAS:LHN:BAY1:CAM:02 (ioc-lhn-bay1-ff-01)
        LAS:LHN:BAY3:CAM:02 (?, assumed)
        LAS:LHN:BAY4:CAM:02 (ioc-lhn-bay4-ff-01)
    """

    # Linear motors (ioc-las-bts-mcs1)
    m1: Motor = SubGroup(Motor, prefix="LAS:BTS:MCS2:01:m1", user_limits=(0, 0))
    m4: Motor = SubGroup(Motor, prefix="LAS:BTS:MCS2:01:m4", user_limits=(0, 2000))
    m7: Motor = SubGroup(
        Motor,
        prefix="LAS:BTS:MCS2:01:m7",
        position=405.0,
        user_limits=(400, 1446.53),
    )

    # Rotary motors
    m2: Motor = SubGroup(Motor, prefix="LAS:BTS:MCS2:01:m2", user_limits=(0, 0))
    m6: Motor = SubGroup(Motor, prefix="LAS:BTS:MCS2:01:m6", user_limits=(-95, 95))
    m8: Motor = SubGroup(Motor, prefix="LAS:BTS:MCS2:01:m8", user_limits=(-300, 300))

    # Goniometers
    m3: Motor = SubGroup(Motor, prefix="LAS:BTS:MCS2:01:m3", user_limits=(0, 0))
    m5: Motor = SubGroup(Motor, prefix="LAS:BTS:MCS2:01:m5", user_limits=(0, 0))
    m9: Motor = SubGroup(Motor, prefix="LAS:BTS:MCS2:01:m9", user_limits=(0, 0))

    nf1: StatsPlugin = SubGroup(StatsPlugin, prefix="LAS:LHN:BAY1:CAM:01:Stats2:")
    nf3: StatsPlugin = SubGroup(StatsPlugin, prefix="LAS:LHN:BAY3:CAM:01:Stats2:")
    nf4: StatsPlugin = SubGroup(StatsPlugin, prefix="LAS:LHN:BAY4:CAM:01:Stats2:")

    ff1: StatsPlugin = SubGroup(StatsPlugin, prefix="LAS:LHN:BAY1:CAM:02:Stats2:")
    ff3: StatsPlugin = SubGroup(StatsPlugin, prefix="LAS:LHN:BAY3:CAM:02:Stats2:")
    ff4: StatsPlugin = SubGroup(StatsPlugin, prefix="LAS:LHN:BAY4:CAM:02:Stats2:")


class RangeComparison(PVGroup):
    """BTPS single value range comparison check."""

    value = pvproperty(
        name="Value_RBV",
        value=0.0,
        doc="Current value from the control system",
        precision=3,
    )
    in_range = pvproperty(
        name="InRange_RBV",
        doc="Is the value currently in range?",
        dtype=ChannelType.ENUM,
        enum_strings=["Out of range", "In range"],
    )
    input_valid = pvproperty(
        name="Valid_RBV",
        doc="Is the value considered valid?",
        dtype=ChannelType.ENUM,
        enum_strings=["Data Invalid", "Data Valid"],
    )

    # Configuration settings:
    low = pvproperty_with_rbv(
        name="Low",
        value=0.0,
        doc="Configurable lower bound for the value range",
        precision=3,
    )
    nominal = pvproperty_with_rbv(
        name="Nominal",
        value=0.0,
        doc="The nominal value",
        precision=3,
    )
    high = pvproperty_with_rbv(
        name="High",
        value=0.0,
        doc="Configurable upper bound for the value range",
        precision=3,
    )
    inclusive = pvproperty_with_rbv(
        name="Inclusive",
        value=0.0,
        doc="Is the value comparison exclusive or inclusive?",
    )

    async def set_nominal(self, value: float, atol: float = 0.1):
        """Set the nominal value to ``value`` with tolerance ``atol``."""
        await self.nominal.readback.write(value)
        await self.low.readback.write(value - atol)
        await self.high.readback.write(value + atol)

    async def simulate(self, data_valid: bool = True):
        """Simulate and update state."""
        await write_if_differs(self.input_valid, int(data_valid))

        low = self.low.readback.value
        high = self.high.readback.value
        if not self.input_valid.value or high < low:
            in_range = False
        elif self.inclusive.readback.value:
            in_range = low <= self.value.value <= high
        else:
            in_range = low < self.value.value < high

        await write_if_differs(self.in_range, in_range)


class CentroidConfig(PVGroup):
    """BTPS camera centroid range comparison."""
    centroid_x: RangeComparison = SubGroup(
        RangeComparison,
        prefix="CenterX:",
        doc="Centroid X range",
    )
    centroid_y: RangeComparison = SubGroup(
        RangeComparison,
        prefix="CenterY:",
        doc="Centroid Y range",
    )

    async def simulate(self, data_valid: bool = True):
        for check in [self.centroid_x, self.centroid_y]:
            await check.simulate()


class SourceConfig(PVGroup):
    """BTPS per-(source, destination) configuration settings and state."""

    name_ = pvproperty(
        name="Name_RBV",
        doc="Source name",
        value="name",
        max_length=255,
    )
    far_field: CentroidConfig = SubGroup(
        CentroidConfig, prefix="FF", doc="Far field centroid"
    )
    near_field: CentroidConfig = SubGroup(
        CentroidConfig, prefix="NF", doc="Near field centroid"
    )
    goniometer: RangeComparison = SubGroup(
        RangeComparison, prefix="Goniometer:", doc="Goniometer stage"
    )
    linear: RangeComparison = SubGroup(
        RangeComparison, prefix="Linear:", doc="Linear stage"
    )
    rotary: RangeComparison = SubGroup(
        RangeComparison, prefix="Rotary:", doc="Rotary stage"
    )
    entry_valve_ready = pvproperty(
        name="EntryValveReady_RBV",
        doc="Entry valve is open and ready",
        dtype=ChannelType.ENUM,
        enum_strings=["Not ready", "Ready"],
    )

    checks_ok = pvproperty(
        name="ChecksOK_RBV",
        doc="Check summary",
        dtype=ChannelType.ENUM,
        enum_strings=["Failed", "Passed"],
    )
    data_valid = pvproperty(
        name="Valid_RBV",
        doc="Data validity summary",
        dtype=ChannelType.ENUM,
        enum_strings=["Data Invalid", "Data Valid"],
    )

    async def simulate(
        self,
        state: BtpsState,
        motors: BtpsMotorsAndCameras,
        destination: DestinationConfig,
    ):
        """Simulate and update state."""
        for check in [self.linear, self.rotary, self.goniometer]:
            check = cast(RangeComparison, check)
            await check.simulate()

        for centroid in [self.near_field, self.far_field]:
            centroid = cast(CentroidConfig, centroid)
            await centroid.simulate()


class DestinationConfig(PVGroup):
    """BTPS per-destination configuration settings and state."""

    name_ = pvproperty(
        name="Name_RBV",
        doc="Destination name",
        value="name",
        max_length=255,
    )
    source1: SourceConfig = SubGroup(
        SourceConfig,
        prefix="SRC:01:",
        doc="Settings for source 1"
    )
    source3: SourceConfig = SubGroup(
        SourceConfig,
        prefix="SRC:03:",
        doc="Settings for source 3"
    )
    source4: SourceConfig = SubGroup(
        SourceConfig,
        prefix="SRC:04:",
        doc="Settings for source 4"
    )
    # exit_valve = SubGroup(VGC, prefix="DestValve", doc="Exit valve for the destination")
    exit_valve_ready = pvproperty(
        name="ExitValveReady_RBV",
        doc="Exit valve is open and ready",
        dtype=ChannelType.ENUM,
        enum_strings=["Not ready", "Ready"],
    )

    @property
    def sources(self) -> Dict[int, SourceConfig]:
        """Destination configurations."""
        return {
            1: self.source1,
            3: self.source3,
            4: self.source4,
        }

    async def simulate(self, state: BtpsState, motors: BtpsMotorsAndCameras):
        """Simulate and update state."""
        for source in self.sources.values():
            await source.simulate(state, motors, self)


class GlobalConfig(PVGroup):
    """BTPS global configuration settings."""

    system_override = pvproperty_with_rbv(
        name="SystemOverride",
        value=0.0,
        doc="System override for when BTPS gets in the way",
    )

    max_frame_time = pvproperty_with_rbv(
        name="MaxFrameTime",
        value=0.0,
        doc=(
            "Maximum time between frame updates in seconds to be considered "
            "'valid' data"
        ),
    )

    min_pixel_sum_change = pvproperty_with_rbv(
        name="MinPixelChange",
        value=0.0,
        doc=(
            "Minimal change (in pixels) for camera image sum to be "
            "considered valid"
        ),
    )


class ShutterSafety(PVGroup):
    """BTPS per-source shutter safety status."""

    open_request = pvproperty_with_rbv(
        name="UserOpen",
        doc="User request to open/close shutter",
        dtype=ChannelType.ENUM,
        enum_strings=["Close", "Open"],
    )

    latched_error = pvproperty(
        name="Error_RBV",
        doc="Latched error",
        dtype=ChannelType.ENUM,
        enum_strings=["No error", "Error"],
    )

    acknowledge = pvproperty_with_rbv(
        name="Acknowledge",
        doc="User acknowledgement of latched fault",
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "TRUE"],
    )

    override = pvproperty_with_rbv(
        name="Override",
        doc="BTPS advanced override mode",
        dtype=ChannelType.ENUM,
        enum_strings=["Normal mode", "Override mode"],
    )

    lss_open_request = pvproperty(
        name="LSS:OpenRequest_RBV",
        doc="Output request to LSS open shutter",
        dtype=ChannelType.ENUM,
        enum_strings=["Request close", "Request open"],
    )

    safe_to_open = pvproperty(
        name="Safe_RBV",
        doc="BTPS safe to open indicator",
        dtype=ChannelType.ENUM,
        enum_strings=["Unsafe", "Safe"],
    )

    async def simulate(self, state: BtpsState, motors: BtpsMotorsAndCameras):
        """Simulate and update state."""


class BtpsCameraStatus(PVGroup):
    """pytmc-linked checks of camera state in the PLC."""
    frame_time = pvproperty(
        name="FrameTime_RBV",
        doc="Frame time as calculated by the PLC",
    )

    is_updating = pvproperty(
        name="IsUpdating_RBV",
        doc="Frame time as calculated by the PLC",
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "TRUE"],
    )


class BtpsAllCameraStatus(PVGroup):
    """pytmc-linked checks of camera state in the PLC."""

    nf1 = SubGroup(BtpsCameraStatus, prefix="NF1:")
    nf3 = SubGroup(BtpsCameraStatus, prefix="NF3:")
    nf4 = SubGroup(BtpsCameraStatus, prefix="NF4:")
    ff1 = SubGroup(BtpsCameraStatus, prefix="FF1:")
    ff3 = SubGroup(BtpsCameraStatus, prefix="FF3:")
    ff4 = SubGroup(BtpsCameraStatus, prefix="FF4:")


class LssShutter(PVGroup):
    """Beam transport system shutter interface via ioc-las-bts."""

    async def _put_request(self, instance, value: str):
        value = self.readback.enum_strings.index(value)
        await self.parent.opened.write(bool(value))
        await self.parent.closed.write(not bool(value))
        await self.readback.write(bool(value))

    request = pvproperty_with_rbv(
        name="REQ",
        value=0,
        doc="User request to open",
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "TRUE"],
        put=_put_request,
    )
    opened = pvproperty(
        name="OPN_RBV",
        value=0,
        doc="Open status",
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "TRUE"],
    )
    closed = pvproperty(
        name="CLS_RBV",
        value=0,
        doc="Closed status",
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "TRUE"],
    )
    permission = pvproperty(
        name="LSS_RBV",
        value=0,
        doc="LSS Permission status",
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "TRUE"],
    )


class BtsGateValves(PVGroup):
    """
    Gate valves (VGC, non-legacy)

    The following are sourced from plc-las-bts:

    Source Gate Valve
        LTLHN:LS1:VGC:01 (ioc-las-bts)
        LTLHN:LS5:VGC:01 (ioc-las-bts)
        LTLHN:LS8:VGC:01 (ioc-las-bts)

    Destination Gate Valve PV
        LTLHN:LD8:VGC:01 (ioc-las-bts) - TMO - IP1
        LTLHN:LD10:VGC:01 (ioc-las-bts) - TMO - IP2
        LTLHN:LD2:VGC:01 (ioc-las-bts) - TMO - IP3
        LTLHN:LD6:VGC:01 (ioc-las-bts) - RIX - qRIXS
        LTLHN:LD4:VGC:01 (ioc-las-bts) - RIX - ChemRIXS
        LTLHN:LD14:VGC:01 (ioc-las-bts) - XPP
        LTLHN:LD9:VGC:01 (ioc-las-bts) - Laser Lab
    """
    source1 = SubGroup(VGC, prefix="LTLHN:LS1:VGC:01")
    source3 = SubGroup(VGC, prefix="LTLHN:LS5:VGC:01")
    source4 = SubGroup(VGC, prefix="LTLHN:LS8:VGC:01")

    dest1 = SubGroup(VGC, prefix="LTLHN:LD8:VGC:01")  # TMO - IP1
    dest2 = SubGroup(VGC, prefix="LTLHN:LD10:VGC:01")  # TMO - IP2
    dest3 = SubGroup(VGC, prefix="LTLHN:LD2:VGC:01")  # TMO - IP3
    dest4 = SubGroup(VGC, prefix="LTLHN:LD6:VGC:01")  # RIX - qRIXS
    dest5 = SubGroup(VGC, prefix="LTLHN:LD4:VGC:01")  # RIX - ChemRIXS
    dest6 = SubGroup(VGC, prefix="LTLHN:LD14:VGC:01")  # XPP
    dest7 = SubGroup(VGC, prefix="LTLHN:LD9:VGC:01")  # Laser Lab


class LssShutters(PVGroup):
    """
    Shutter readback status and request status.

    LSS Shutter Request
        LTLHN:LS1:LST:REQ_RBV (ioc-las-bts)
        LTLHN:LS5:LST:REQ_RBV (ioc-las-bts)
        LTLHN:LS8:LST:REQ_RBV (ioc-las-bts)

    LSS Shutter State - Open
        LTLHN:LS1:LST:OPN_RBV (ioc-las-bts)
        LTLHN:LS5:LST:OPN_RBV (ioc-las-bts)
        LTLHN:LS8:LST:OPN_RBV (ioc-las-bts)

    LSS Shutter State - Closed
        LTLHN:LS1:LST:CLS_RBV (ioc-las-bts)
        LTLHN:LS5:LST:CLS_RBV (ioc-las-bts)
        LTLHN:LS8:LST:CLS_RBV (ioc-las-bts)

    LSS Permission
        LTLHN:LS1:LST:LSS_RBV (ioc-las-bts)
        LTLHN:LS5:LST:LSS_RBV (ioc-las-bts)
        LTLHN:LS8:LST:LSS_RBV (ioc-las-bts)
    """
    source1 = SubGroup(LssShutter, prefix="LTLHN:LS1:LST:")
    source3 = SubGroup(LssShutter, prefix="LTLHN:LS5:LST:")
    source4 = SubGroup(LssShutter, prefix="LTLHN:LS8:LST:")


class BtpsState(PVGroup):
    """
    Beam Transport Protection System (BTPS) State
    """

    config = SubGroup(GlobalConfig, prefix="Config:", doc="Global configuration")

    shutter1: ShutterSafety = SubGroup(
        ShutterSafety,
        prefix="Shutter:01:",
        doc="Source Shutter 1",
    )
    shutter3: ShutterSafety = SubGroup(
        ShutterSafety,
        prefix="Shutter:03:",
        doc="Source Shutter 3",
    )
    shutter4: ShutterSafety = SubGroup(
        ShutterSafety,
        prefix="Shutter:04:",
        doc="Source Shutter 4",
    )

    dest1: DestinationConfig = SubGroup(
        DestinationConfig,
        prefix="DEST:01:",
        doc="Destination 1",
    )
    dest2: DestinationConfig = SubGroup(
        DestinationConfig,
        prefix="DEST:02:",
        doc="Destination 2",
    )
    dest3: DestinationConfig = SubGroup(
        DestinationConfig,
        prefix="DEST:03:",
        doc="Destination 3",
    )
    dest4: DestinationConfig = SubGroup(
        DestinationConfig,
        prefix="DEST:04:",
        doc="Destination 4",
    )
    dest5: DestinationConfig = SubGroup(
        DestinationConfig,
        prefix="DEST:05:",
        doc="Destination 5",
    )
    dest6: DestinationConfig = SubGroup(
        DestinationConfig,
        prefix="DEST:06:",
        doc="Destination 6",
    )
    dest7: DestinationConfig = SubGroup(
        DestinationConfig,
        prefix="DEST:07:",
        doc="Destination 7",
    )

    sim_enable = pvproperty(value=1, name="SimEnable", record="bo")
    camera_times: BtpsAllCameraStatus = SubGroup(BtpsAllCameraStatus, prefix="Chk:")

    @sim_enable.scan(period=1, use_scan_field=True)
    async def sim_enable(
        self,
        instance: caproto.ChannelInteger,
        async_lib: caproto.server.AsyncLibraryLayer,
    ):
        if self.sim_enable.value == 0:
            return

        if self.parent is None:
            return

        try:
            motors: BtpsMotorsAndCameras = self.parent.motors
        except AttributeError:
            raise RuntimeError(
                "To enable simulations, include a BtpsMotorsAndCameras SubGroup "
                "in the IOC named 'motors'."
            ) from None

        for shutter in self.shutters.values():
            await shutter.simulate(self, motors)

        for dest in self.destinations.values():
            await dest.simulate(self, motors)

    @property
    def shutters(self) -> Dict[int, ShutterSafety]:
        """Source shutters."""
        return {1: self.shutter1, 3: self.shutter3, 4: self.shutter4}

    @property
    def destinations(self) -> Dict[int, DestinationConfig]:
        """Destination configurations."""
        return {
            1: self.dest1,
            2: self.dest2,
            3: self.dest3,
            4: self.dest4,
            5: self.dest5,
            6: self.dest6,
            7: self.dest7,
        }
