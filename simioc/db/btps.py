"""
BTPS Simulator "database" PVGroups for reuse.
"""

from __future__ import annotations

from typing import Dict, cast

import caproto
from caproto import ChannelType
from caproto.server import PVGroup, SubGroup, pvproperty

from .areadetector import StatsPlugin
from .motor import Motor, SmarActMotor
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
    m1: SmarActMotor = SubGroup(
        SmarActMotor,
        prefix="LAS:BTS:MCS2:01:m1",
        user_limits=(0, 0),
        velocity=100.0,
    )
    m4: SmarActMotor = SubGroup(
        SmarActMotor,
        prefix="LAS:BTS:MCS2:01:m4",
        user_limits=(0, 2000),
        velocity=100.0,
    )
    m7: SmarActMotor = SubGroup(
        SmarActMotor,
        prefix="LAS:BTS:MCS2:01:m7",
        position=405.0,
        user_limits=(400, 1446.53),
        velocity=100.0,
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
        valves: BtsGateValves,
        destination: DestinationConfig,
    ):
        """Simulate and update state."""
        # TODO: always ready
        await write_if_differs(self.entry_valve_ready, 1)

        for check in [self.linear, self.rotary, self.goniometer]:
            check = cast(RangeComparison, check)
            await check.simulate()

        for centroid in [self.near_field, self.far_field]:
            centroid = cast(CentroidConfig, centroid)
            await centroid.simulate()


class DestinationConfig(PVGroup):
    """BTPS per-destination configuration settings and state."""

    name_ = pvproperty(
        name="BTPS:Name_RBV",
        doc="Destination name",
        value="name",
        max_length=255,
    )
    ls1: SourceConfig = SubGroup(
        SourceConfig,
        prefix="LS1:BTPS:",
        doc="Settings for source LS1, bay 1"
    )
    ls5: SourceConfig = SubGroup(
        SourceConfig,
        prefix="LS5:BTPS:",
        doc="Settings for source LS5, bay 3"
    )
    ls8: SourceConfig = SubGroup(
        SourceConfig,
        prefix="LS8:BTPS:",
        doc="Settings for source LS8, bay 4"
    )
    # exit_valve = SubGroup(VGC, prefix="DestValve", doc="Exit valve for the destination")
    exit_valve_ready = pvproperty(
        name="BTPS:ExitValveReady_RBV",
        doc="Exit valve is open and ready",
        dtype=ChannelType.ENUM,
        enum_strings=["Not ready", "Ready"],
    )

    @property
    def sources(self) -> Dict[int, SourceConfig]:
        """Destination configurations."""
        return {
            1: self.ls1,
            5: self.ls5,
            8: self.ls8,
        }

    async def simulate(
        self, state: BtpsState, motors: BtpsMotorsAndCameras, valves: BtsGateValves
    ):
        """Simulate and update state."""
        # TODO: always ready
        await write_if_differs(self.exit_valve_ready, 1)

        for source in self.sources.values():
            await source.simulate(state, motors, valves, self)


class GlobalConfig(PVGroup):
    """BTPS global configuration settings."""

    system_override = pvproperty_with_rbv(
        name="SystemOverride",
        value="FALSE",
        doc="System override for when BTPS gets in the way",
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "TRUE"],
    )

    max_frame_time = pvproperty_with_rbv(
        name="MaxFrameTime",
        precision=2,
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

    async def simulate(
        self, state: BtpsState, motors: BtpsMotorsAndCameras, valves: BtsGateValves
    ):
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
        if self.parent.permission.value == "TRUE":
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
    ls1 = SubGroup(VGC, prefix="LTLHN:LS1:VGC:01")
    ls5 = SubGroup(VGC, prefix="LTLHN:LS5:VGC:01")
    ls8 = SubGroup(VGC, prefix="LTLHN:LS8:VGC:01")

    ld2 = SubGroup(VGC, prefix="LTLHN:LD2:VGC:01")  # TMO - IP3
    ld4 = SubGroup(VGC, prefix="LTLHN:LD4:VGC:01")  # RIX - ChemRIXS
    ld6 = SubGroup(VGC, prefix="LTLHN:LD6:VGC:01")  # RIX - qRIXS
    ld8 = SubGroup(VGC, prefix="LTLHN:LD8:VGC:01")  # TMO - IP1
    ld9 = SubGroup(VGC, prefix="LTLHN:LD9:VGC:01")  # Laser Lab
    ld10 = SubGroup(VGC, prefix="LTLHN:LD10:VGC:01")  # TMO - IP2
    ld14 = SubGroup(VGC, prefix="LTLHN:LD14:VGC:01")  # XPP

    @property
    def by_source(self) -> Dict[int, VGC]:
        return {
            1: self.ls1,
            5: self.ls5,
            8: self.ls8,
        }

    @property
    def by_destination(self) -> Dict[int, VGC]:
        return {
            2: self.ld2,
            4: self.ld4,
            6: self.ld6,
            8: self.ld8,
            9: self.ld9,
            10: self.ld10,
            14: self.ld14,

        }


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
    ls1 = SubGroup(LssShutter, prefix="LTLHN:LS1:LST:")
    ls5 = SubGroup(LssShutter, prefix="LTLHN:LS5:LST:")
    ls8 = SubGroup(LssShutter, prefix="LTLHN:LS8:LST:")


class BtpsState(PVGroup):
    """
    Beam Transport Protection System (BTPS) State
    """

    config = SubGroup(
        GlobalConfig,
        prefix="BTPS:Config:",
        doc="Global configuration settings for BTPS"
    )

    ls1: ShutterSafety = SubGroup(
        ShutterSafety,
        prefix="LS1:BTPS:",
        doc="Source Shutter LS1 (bay 1)",
    )
    ls5: ShutterSafety = SubGroup(
        ShutterSafety,
        prefix="LS5:BTPS:",
        doc="Source Shutter LS5 (bay 3)",
    )
    ls8: ShutterSafety = SubGroup(
        ShutterSafety,
        prefix="LS8:BTPS:",
        doc="Source Shutter LS8 (bay 4)",
    )

    ld1: DestinationConfig = SubGroup(
        DestinationConfig,
        prefix="LD1:",
        doc="Destination 1",
    )
    ld2: DestinationConfig = SubGroup(
        DestinationConfig,
        prefix="LD2:",
        doc="Destination 2",
    )
    ld3: DestinationConfig = SubGroup(
        DestinationConfig,
        prefix="LD3:",
        doc="Destination 3",
    )
    ld4: DestinationConfig = SubGroup(
        DestinationConfig,
        prefix="LD4:",
        doc="Destination 4",
    )
    ld5: DestinationConfig = SubGroup(
        DestinationConfig,
        prefix="LD5:",
        doc="Destination 5",
    )
    ld6: DestinationConfig = SubGroup(
        DestinationConfig,
        prefix="LD6:",
        doc="Destination 6",
    )
    ld7: DestinationConfig = SubGroup(
        DestinationConfig,
        prefix="LD7:",
        doc="Destination 7",
    )
    ld8: DestinationConfig = SubGroup(
        DestinationConfig,
        prefix="LD8:",
        doc="Destination 8",
    )
    ld9: DestinationConfig = SubGroup(
        DestinationConfig,
        prefix="LD9:",
        doc="Destination 9",
    )
    ld10: DestinationConfig = SubGroup(
        DestinationConfig,
        prefix="LD10:",
        doc="Destination 10",
    )
    ld11: DestinationConfig = SubGroup(
        DestinationConfig,
        prefix="LD11:",
        doc="Destination 11",
    )
    ld12: DestinationConfig = SubGroup(
        DestinationConfig,
        prefix="LD12:",
        doc="Destination 12",
    )
    ld13: DestinationConfig = SubGroup(
        DestinationConfig,
        prefix="LD13:",
        doc="Destination 13",
    )
    ld14: DestinationConfig = SubGroup(
        DestinationConfig,
        prefix="LD14:",
        doc="Destination 14",
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

        try:
            valves: BtsGateValves = self.parent.gate_valves
        except AttributeError:
            raise RuntimeError(
                "To enable simulations, include a BtsGateValves SubGroup "
                "in the IOC named 'gate_valves'."
            ) from None

        for valve in list(valves.by_source.values()) + list(valves.by_destination.values()):
            await valve.simulate()

        for shutter in self.shutters.values():
            await shutter.simulate(self, motors, valves)

        for dest in self.destinations.values():
            await dest.simulate(self, motors, valves)

    @property
    def shutters(self) -> Dict[int, ShutterSafety]:
        """Source shutters."""
        return {1: self.ls1, 5: self.ls5, 8: self.ls8}

    @property
    def destinations(self) -> Dict[int, DestinationConfig]:
        """Destination configurations."""
        return {
            1: self.ld1,
            2: self.ld2,
            3: self.ld3,
            4: self.ld4,
            5: self.ld5,
            6: self.ld6,
            7: self.ld7,
            8: self.ld8,
            9: self.ld9,
            10: self.ld10,
            11: self.ld11,
            12: self.ld12,
            13: self.ld13,
            14: self.ld14,
        }
