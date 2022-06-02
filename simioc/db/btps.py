"""
BTPS Simulator "database" PVGroups for reuse.
"""

from caproto.server import PVGroup, SubGroup

from ..db.areadetector import StatsPlugin
from ..db.motor import Motor
from ..db.utils import pvproperty_from_pytmc


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

    The following *will be* sourced from plc-las-bts:

    LSS Shutter Request
        LTLHN:LS1:LST:REQ (ioc-las-lhn-bhc-05 -> ioc-las-bts)
        LTLHN:LS5:LST:REQ (ioc-las-lhn-bhc-05 -> ioc-las-bts)
        LTLHN:LS8:LST:REQ (ioc-las-lhn-bhc-05 -> ioc-las-bts)

    LSS Shutter State - Open
        LTLHN:LS1:LST:OPN (ioc-las-lhn-bhc-05 -> ioc-las-bts)
        LTLHN:LS5:LST:OPN (ioc-las-lhn-bhc-05 -> ioc-las-bts)
        LTLHN:LS8:LST:OPN (ioc-las-lhn-bhc-05 -> ioc-las-bts)

    LSS Shutter State - Closed
        LTLHN:LS1:LST:CLS (ioc-las-lhn-bhc-05 -> ioc-las-bts)
        LTLHN:LS5:LST:CLS (ioc-las-lhn-bhc-05 -> ioc-las-bts)
        LTLHN:LS8:LST:CLS (ioc-las-lhn-bhc-05 -> ioc-las-bts)
    """

    # Linear motors (ioc-las-bts-mcs1)
    m1 = SubGroup(Motor, prefix="LAS:BTS:MCS2:01:m1", user_limits=(0, 0))
    m4 = SubGroup(Motor, prefix="LAS:BTS:MCS2:01:m4", user_limits=(0, 2000))
    m7 = SubGroup(
        Motor, prefix="LAS:BTS:MCS2:01:m7", position=405.0, user_limits=(400, 1446.53)
    )

    # Rotary motors
    m2 = SubGroup(Motor, prefix="LAS:BTS:MCS2:01:m2", user_limits=(0, 0))
    m6 = SubGroup(Motor, prefix="LAS:BTS:MCS2:01:m6", user_limits=(-95, 95))
    m8 = SubGroup(Motor, prefix="LAS:BTS:MCS2:01:m8", user_limits=(-300, 300))

    # Goniometers
    m3 = SubGroup(Motor, prefix="LAS:BTS:MCS2:01:m3", user_limits=(0, 0))
    m5 = SubGroup(Motor, prefix="LAS:BTS:MCS2:01:m5", user_limits=(0, 0))
    m9 = SubGroup(Motor, prefix="LAS:BTS:MCS2:01:m9", user_limits=(0, 0))

    nf_cam_bay1 = SubGroup(StatsPlugin, prefix="LAS:LHN:BAY1:CAM:01:Stats2:")
    nf_cam_bay3 = SubGroup(StatsPlugin, prefix="LAS:LHN:BAY3:CAM:01:Stats2:")
    nf_cam_bay4 = SubGroup(StatsPlugin, prefix="LAS:LHN:BAY4:CAM:01:Stats2:")

    ff_cam_bay1 = SubGroup(StatsPlugin, prefix="LAS:LHN:BAY1:CAM:02:Stats2:")
    ff_cam_bay3 = SubGroup(StatsPlugin, prefix="LAS:LHN:BAY3:CAM:02:Stats2:")
    ff_cam_bay4 = SubGroup(StatsPlugin, prefix="LAS:LHN:BAY4:CAM:02:Stats2:")


class RangeComparison(PVGroup):
    """BTPS single value range comparison check."""

    value = pvproperty_from_pytmc(
        name="Value", io="input", doc="Current value from the control system",
    )
    in_range = pvproperty_from_pytmc(
        name="InRange", io="input", doc="Is the value currently in range?",
    )
    input_valid = pvproperty_from_pytmc(
        name="Valid", io="input", doc="Is the value considered valid?",
    )

    # Configuration settings:
    low = pvproperty_from_pytmc(
        name="Low", io="io", doc="Configurable lower bound for the value range",
    )
    nominal = pvproperty_from_pytmc(name="Nominal", io="io", doc="The nominal value",)
    high = pvproperty_from_pytmc(
        name="High", io="io", doc="Configurable upper bound for the value range",
    )
    inclusive = pvproperty_from_pytmc(
        name="Inclusive",
        io="io",
        doc="Is the value comparison exclusive or inclusive?",
    )


class CentroidConfig(PVGroup):
    """BTPS camera centroid range comparison."""

    centroid_x = SubGroup(RangeComparison, prefix="CenterX:", doc="Centroid X range")
    centroid_y = SubGroup(RangeComparison, prefix="CenterY:", doc="Centroid Y range")


class SourceConfig(PVGroup):
    """BTPS per-(source, destination) configuration settings and state."""

    name_ = pvproperty_from_pytmc(
        name="Name", io="input", doc="Source name", value="name", max_length=255,
    )
    far_field = SubGroup(CentroidConfig, prefix="FF", doc="Far field centroid")
    near_field = SubGroup(CentroidConfig, prefix="NF", doc="Near field centroid")
    goniometer = SubGroup(RangeComparison, prefix="Goniometer:", doc="Goniometer stage")
    linear = SubGroup(RangeComparison, prefix="Linear:", doc="Linear stage")
    rotary = SubGroup(RangeComparison, prefix="Rotary:", doc="Rotary stage")
    entry_valve_ready = pvproperty_from_pytmc(
        name="EntryValveReady", io="input", doc="Entry valve is open and ready",
    )

    checks_ok = pvproperty_from_pytmc(name="ChecksOK", io="input", doc="Check summary")
    data_valid = pvproperty_from_pytmc(
        name="Valid", io="input", doc="Data validity summary"
    )


class DestinationConfig(PVGroup):
    """BTPS per-destination configuration settings and state."""

    name_ = pvproperty_from_pytmc(
        name="Name", io="input", doc="Destination name", value="name", max_length=255,
    )
    source1 = SubGroup(SourceConfig, prefix="SRC:01:", doc="Settings for source 1")
    source3 = SubGroup(SourceConfig, prefix="SRC:03:", doc="Settings for source 3")
    source4 = SubGroup(SourceConfig, prefix="SRC:04:", doc="Settings for source 4")
    # exit_valve = SubGroup(VGC, prefix="DestValve", doc="Exit valve for the destination")
    exit_valve_ready = pvproperty_from_pytmc(
        name="ExitValveReady", io="input", doc="Exit valve is open and ready",
    )


class GlobalConfig(PVGroup):
    """BTPS global configuration settings."""

    max_frame_time = pvproperty_from_pytmc(
        name="MaxFrameTime",
        io="io",
        doc=(
            "Maximum time between frame updates in seconds to be considered "
            "'valid' data"
        ),
    )

    min_centroid_change = pvproperty_from_pytmc(
        name="MinPixelChange",
        io="io",
        doc=(
            "Minimal change (in pixels) for camera image sum to be "
            "considered valid"
        ),
    )


class ShutterSafety(PVGroup):
    """BTPS per-source shutter safety status."""

    open_request = pvproperty_from_pytmc(
        name="UserOpen", io="io", doc="User request to open/close shutter",
    )

    latched_error = pvproperty_from_pytmc(
        name="Error", io="input", doc="Latched error",
    )

    acknowledge = pvproperty_from_pytmc(
        name="Acknowledge", io="io", doc="User acknowledgement of latched fault",
    )

    override = pvproperty_from_pytmc(
        name="Override", io="io", doc="BTPS advanced override mode",
    )

    lss_open_request = pvproperty_from_pytmc(
        name="LSS:OpenRequest", io="input", doc="Output request to LSS open shutter",
    )

    safe_to_open = pvproperty_from_pytmc(
        name="Safe", io="input", doc="BTPS safe to open indicator",
    )


class BtpsState(PVGroup):
    """
    Beam Transport Protection System (BTPS) State
    """

    config = SubGroup(GlobalConfig, prefix="Config:", doc="Global configuration")

    shutter1 = SubGroup(ShutterSafety, prefix="Shutter:01:", doc="Source Shutter 1")
    shutter3 = SubGroup(ShutterSafety, prefix="Shutter:03:", doc="Source Shutter 3")
    shutter4 = SubGroup(ShutterSafety, prefix="Shutter:04:", doc="Source Shutter 4")

    dest1 = SubGroup(DestinationConfig, prefix="DEST:01:", doc="Destination 1")
    dest2 = SubGroup(DestinationConfig, prefix="DEST:02:", doc="Destination 2")
    dest3 = SubGroup(DestinationConfig, prefix="DEST:03:", doc="Destination 3")
    dest4 = SubGroup(DestinationConfig, prefix="DEST:04:", doc="Destination 4")
    dest5 = SubGroup(DestinationConfig, prefix="DEST:05:", doc="Destination 5")
    dest6 = SubGroup(DestinationConfig, prefix="DEST:06:", doc="Destination 6")
    dest7 = SubGroup(DestinationConfig, prefix="DEST:07:", doc="Destination 7")
