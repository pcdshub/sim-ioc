from caproto import ChannelType
from caproto.server import PVGroup, pvproperty

from .utils import pvproperty_with_rbv


class Stopper(PVGroup):
    open_limit = pvproperty(
        name=":OPEN",
        value=0,
        doc="Reads 1 if the stopper is out, at the open limit.",
        read_only=True,
    )
    closed_limit = pvproperty(
        name=":CLOSE",
        value=0,
        doc="Reads 1 if the stopper is in, at the closed limit.",
        read_only=True,
    )
    command = pvproperty(
        name=":CMD", value=0, doc="Put here to command a stopper move.", read_only=False
    )


class GateValve(Stopper, PVGroup):
    open_limit = pvproperty(name=":OPN_DI", value=0, doc="", read_only=True)
    closed_limit = pvproperty(name=":CLS_DI", value=0, doc="", read_only=True)
    command = pvproperty(
        name=":OPN_SW",
        value=0,
        doc="",
        read_only=False,
        dtype=ChannelType.ENUM,
        enum_strings=["CLOSE", "OPEN"],
    )
    interlock = pvproperty(name=":OPN_OK", value=0, doc="", read_only=True)


class PPSStopper(PVGroup):
    state = pvproperty(
        name="",
        value=0,
        doc="Stopper state summary PV that tells us if it is in, out, or inconsistent.",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "TRUE"],
    )


class VCN(PVGroup):
    position_readback = pvproperty(
        name=":POS_RDBK_RBV", value=0, doc="valve position readback", read_only=True
    )
    position_control = pvproperty_with_rbv(
        name=":POS_REQ",
        value=0,
        doc="requested positition to control the valve 0-100%",
        read_only=False,
    )
    upper_limit = pvproperty_with_rbv(
        name=":Limit",
        value=0,
        doc="max upper limit position to open the valve 0-100%",
        read_only=False,
    )
    interlock_ok = pvproperty(
        name=":ILK_OK_RBV",
        value=0,
        doc="interlock ok status",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["NOT OK", "OK"],
    )
    open_command = pvproperty_with_rbv(
        name=":OPN_SW",
        value=0,
        doc="Epics command to Open valve",
        read_only=False,
        dtype=ChannelType.ENUM,
        enum_strings=["CLOSE", "OPEN"],
    )
    state = pvproperty_with_rbv(
        name=":STATE",
        value=0,
        doc="Valve state",
        read_only=False,
        dtype=ChannelType.ENUM,
        enum_strings=[
            "Vented",
            "At Vacuum",
            "Differential Pressure",
            "Lost Vacuum",
            "Ext Fault",
            "AT Vacuum",
            "Triggered",
            "Vacuum Fault",
            "Close Timeout",
            "Open Timeout",
        ],
    )
    pos_ao = pvproperty(name=":POS_AO_RBV", value=0, doc="", read_only=True)


class VFS(PVGroup):
    valve_position = pvproperty(
        name=":POS_STATE_RBV",
        value=0,
        doc="Ex: OPEN, CLOSED, MOVING, INVALID, OPEN_F",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["OPEN", "CLOSED", "MOVING", "INVALID", "OPEN_F"],
    )
    vfs_state = pvproperty(
        name=":STATE_RBV",
        value=0,
        doc="Fast Shutter Current State",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=[
            "Vented",
            "At Vacuum",
            "Differential Pressure",
            "Lost Vacuum",
            "Ext Fault",
            "AT Vacuum",
            "Triggered",
            "Vacuum Fault",
            "Close Timeout",
            "Open Timeout",
        ],
    )
    request_close = pvproperty_with_rbv(
        name=":CLS_SW",
        value=0,
        doc="Request Fast Shutter to Close. When both closeand open are requested, VFS will close.",
        read_only=False,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "CLOSE"],
    )
    request_open = pvproperty_with_rbv(
        name=":OPN_SW",
        value=0,
        doc="Request Fast Shutter to Open. Requires a risingEPICS signal to open. When both close andopen are requested, VFS will close.",
        read_only=False,
        dtype=ChannelType.ENUM,
        enum_strings=["CLOSE", "OPEN"],
    )
    reset_vacuum_fault = pvproperty_with_rbv(
        name=":ALM_RST",
        value=0,
        doc="Reset Fast Shutter Vacuum Faults: fastsensor triggered, fast sensor turned off.To open VFS, this needs to be reset to TRUEafter a vacuum event.",
        read_only=False,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "TRUE"],
    )
    override_mode = pvproperty_with_rbv(
        name=":OVRD_ON",
        value=0,
        doc="Epics Command to set Override mode",
        read_only=False,
        dtype=ChannelType.ENUM,
        enum_strings=["Override OFF", "Override ON"],
    )
    override_force_open = pvproperty_with_rbv(
        name=":FORCE_OPN",
        value=0,
        doc="Epics Command to force openthe valve in override mode",
        read_only=False,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "FORCE OPEN"],
    )
    gfs_name = pvproperty(
        name=":GFS_RBV",
        value="",
        doc="Gauge Fast Sensor Name",
        read_only=True,
        max_length=80,
    )
    gfs_trigger = pvproperty(
        name=":TRIG_RBV",
        value=0,
        doc="Gauge Fast Sensor Input Trigger",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["TRIG_OFF", "TRIG_ON"],
    )
    position_close = pvproperty(
        name=":CLS_DI_RBV",
        value=0,
        doc="Fast Shutter Closed Valve Position",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "CLOSE"],
    )
    position_open = pvproperty(
        name=":OPN_DI_RBV",
        value=0,
        doc="Fast Shutter Open Valve Position",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "OPEN"],
    )
    vac_fault_ok = pvproperty(
        name=":VAC_FAULT_OK_RBV",
        value=0,
        doc="Fast Shutter Vacuum Fault OK Readback",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["FAULT", "FAULT OK"],
    )
    mps_ok = pvproperty(
        name=":MPS_FAULT_OK_RBV",
        value=0,
        doc="Fast Shutter Fast Fault Output OK",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["MPS FAULT", "MPS OK"],
    )
    veto_device = pvproperty(
        name=":VETO_DEVICE_RBV",
        value=0,
        doc="Name of device that can veto this VFS",
        read_only=True,
    )


class ValveBase(PVGroup):
    open_command = pvproperty_with_rbv(
        name=":OPN_SW",
        value=0,
        doc="Epics command to Open valve",
        read_only=False,
        dtype=ChannelType.ENUM,
        enum_strings=["CLOSE", "OPEN"],
    )
    interlock_ok = pvproperty(
        name=":OPN_OK_RBV",
        value=0,
        doc="Valve is OK to Open interlock ",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["OPN ILK NOT OK", "OPN ILK OK"],
    )
    open_do = pvproperty(
        name=":OPN_DO_RBV",
        value=0,
        doc="PLC Output to Open valve, 1 means 24V on command cable",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "TRUE"],
    )
    error_reset = pvproperty_with_rbv(
        name=":ALM_RST",
        value=0,
        doc="Reset Error state to valid by toggling this",
        read_only=False,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "TRUE"],
    )


class VVC(ValveBase, PVGroup):
    open_command = pvproperty_with_rbv(
        name=":OPN_SW",
        value=0,
        doc="Epics command to Open valve",
        read_only=False,
        dtype=ChannelType.ENUM,
        enum_strings=["CLOSE", "OPEN"],
    )
    interlock_ok = pvproperty(
        name=":OPN_OK_RBV",
        value=0,
        doc="Valve is OK to Open interlock ",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["OPN ILK NOT OK", "OPN ILK OK"],
    )
    open_do = pvproperty(
        name=":OPN_DO_RBV",
        value=0,
        doc="PLC Output to Open valve, 1 means 24V on command cable",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "TRUE"],
    )
    error_reset = pvproperty_with_rbv(
        name=":ALM_RST",
        value=0,
        doc="Reset Error state to valid by toggling this",
        read_only=False,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "TRUE"],
    )
    override_status = pvproperty(
        name=":OVRD_ON_RBV",
        value=0,
        doc="Epics Readback on Override mode",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["Override OFF", "Override ON"],
    )
    override_force_open = pvproperty_with_rbv(
        name=":FORCE_OPN",
        value=0,
        doc="Epics Command to force open the valve inoverride mode",
        read_only=False,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "FORCE OPEN"],
    )


class VRC(VVC, PVGroup):
    open_command = pvproperty_with_rbv(
        name=":OPN_SW",
        value=0,
        doc="Epics command to Open valve",
        read_only=False,
        dtype=ChannelType.ENUM,
        enum_strings=["CLOSE", "OPEN"],
    )
    interlock_ok = pvproperty(
        name=":OPN_OK_RBV",
        value=0,
        doc="Valve is OK to Open interlock ",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["OPN ILK NOT OK", "OPN ILK OK"],
    )
    open_do = pvproperty(
        name=":OPN_DO_RBV",
        value=0,
        doc="PLC Output to Open valve, 1 means 24V on command cable",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "TRUE"],
    )
    error_reset = pvproperty_with_rbv(
        name=":ALM_RST",
        value=0,
        doc="Reset Error state to valid by toggling this",
        read_only=False,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "TRUE"],
    )
    override_status = pvproperty(
        name=":OVRD_ON_RBV",
        value=0,
        doc="Epics Readback on Override mode",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["Override OFF", "Override ON"],
    )
    override_force_open = pvproperty_with_rbv(
        name=":FORCE_OPN",
        value=0,
        doc="Epics Command to force open the valve inoverride mode",
        read_only=False,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "FORCE OPEN"],
    )
    state = pvproperty(
        name=":STATE_RBV",
        value=0,
        doc="Valve state",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=[
            "Vented",
            "At Vacuum",
            "Differential Pressure",
            "Lost Vacuum",
            "Ext Fault",
            "AT Vacuum",
            "Triggered",
            "Vacuum Fault",
            "Close Timeout",
            "Open Timeout",
        ],
    )
    open_limit = pvproperty(
        name=":OPN_DI_RBV",
        value=0,
        doc="Open limit switch digital input",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "OPEN"],
    )
    closed_limit = pvproperty(
        name=":CLS_DI_RBV",
        value=0,
        doc="Closed limit switch digital input",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "CLOSE"],
    )


class VGC(VRC, PVGroup):
    open_command = pvproperty_with_rbv(
        name=":OPN_SW",
        value=0,
        doc="Epics command to Open valve",
        read_only=False,
        dtype=ChannelType.ENUM,
        enum_strings=["CLOSE", "OPEN"],
    )
    interlock_ok = pvproperty(
        name=":OPN_OK_RBV",
        value=0,
        doc="Valve is OK to Open interlock ",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["OPN ILK NOT OK", "OPN ILK OK"],
    )
    open_do = pvproperty(
        name=":OPN_DO_RBV",
        value=0,
        doc="PLC Output to Open valve, 1 means 24V on command cable",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "TRUE"],
    )
    error_reset = pvproperty_with_rbv(
        name=":ALM_RST",
        value=0,
        doc="Reset Error state to valid by toggling this",
        read_only=False,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "TRUE"],
    )
    override_status = pvproperty(
        name=":OVRD_ON_RBV",
        value=0,
        doc="Epics Readback on Override mode",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["Override OFF", "Override ON"],
    )
    override_force_open = pvproperty_with_rbv(
        name=":FORCE_OPN",
        value=0,
        doc="Epics Command to force open the valve inoverride mode",
        read_only=False,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "FORCE OPEN"],
    )
    state = pvproperty(
        name=":STATE_RBV",
        value=0,
        doc="Valve state",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=[
            "Vented",
            "At Vacuum",
            "Differential Pressure",
            "Lost Vacuum",
            "Ext Fault",
            "AT Vacuum",
            "Triggered",
            "Vacuum Fault",
            "Close Timeout",
            "Open Timeout",
        ],
    )
    open_limit = pvproperty(
        name=":OPN_DI_RBV",
        value=0,
        doc="Open limit switch digital input",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "OPEN"],
    )
    closed_limit = pvproperty(
        name=":CLS_DI_RBV",
        value=0,
        doc="Closed limit switch digital input",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "CLOSE"],
    )
    diff_press_ok = pvproperty(
        name=":DP_OK_RBV",
        value=0,
        doc="Differential pressure interlock ok",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["DP NOT OK", "DP OK"],
    )
    ext_ilk_ok = pvproperty(
        name=":EXT_ILK_OK_RBV",
        value=0,
        doc="External interlock ok",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["NOT OK", "OK"],
    )
    at_vac_setpoint = pvproperty_with_rbv(
        name=":AT_VAC_SP", value=0.0, doc="AT VAC Set point value", read_only=False
    )
    setpoint_hysterisis = pvproperty_with_rbv(
        name=":AT_VAC_HYS", value=0.0, doc="AT VAC Hysteresis", read_only=False
    )
    at_vac = pvproperty(
        name=":AT_VAC_RBV",
        value=0,
        doc="at vacuum setpoint is reached",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["NOT AT VAC", "AT VAC"],
    )
    error = pvproperty(
        name=":ERROR_RBV",
        value=0,
        doc="Error Present",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["NO ERROR", "ERROR PRESENT"],
    )
    mps_state = pvproperty(
        name=":MPS_FAULT_OK_RBV",
        value=0,
        doc="individual valve MPS state for debugging",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["MPS FAULT", "MPS OK"],
    )
    interlock_device_upstream = pvproperty(
        name=":ILK_DEVICE_US_RBV",
        value="",
        doc="Upstream vacuum device used forinterlocking this valve",
        read_only=True,
        max_length=80,
    )
    interlock_device_downstream = pvproperty(
        name=":ILK_DEVICE_DS_RBV",
        value="",
        doc="Downstream vacuum device used forinterlocking this valve",
        read_only=True,
        max_length=80,
    )


class VGCLegacy(ValveBase, PVGroup):
    open_command = pvproperty_with_rbv(
        name=":OPN_SW",
        value=0,
        doc="Epics command to Open valve",
        read_only=False,
        dtype=ChannelType.ENUM,
        enum_strings=["CLOSE", "OPEN"],
    )
    interlock_ok = pvproperty(
        name=":OPN_OK_RBV",
        value=0,
        doc="Valve is OK to Open interlock ",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["OPN ILK NOT OK", "OPN ILK OK"],
    )
    open_do = pvproperty(
        name=":OPN_DO_RBV",
        value=0,
        doc="PLC Output to Open valve, 1 means 24V on command cable",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "TRUE"],
    )
    error_reset = pvproperty_with_rbv(
        name=":ALM_RST",
        value=0,
        doc="Reset Error state to valid by toggling this",
        read_only=False,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "TRUE"],
    )
    open_limit = pvproperty(
        name=":OPN_DI_RBV",
        value=0,
        doc="Open limit switch digital input",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "OPEN"],
    )
    closed_limit = pvproperty(
        name=":CLS_DI_RBV",
        value=0,
        doc="Closed limit switch digital input",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "CLOSE"],
    )


class VGC_2S(VRC, PVGroup):
    open_command = pvproperty_with_rbv(
        name=":OPN_SW",
        value=0,
        doc="Epics command to Open valve",
        read_only=False,
        dtype=ChannelType.ENUM,
        enum_strings=["CLOSE", "OPEN"],
    )
    interlock_ok = pvproperty(
        name=":OPN_OK_RBV",
        value=0,
        doc="Valve is OK to Open interlock ",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["OPN ILK NOT OK", "OPN ILK OK"],
    )
    open_do = pvproperty(
        name=":OPN_DO_RBV",
        value=0,
        doc="PLC Output to Open valve, 1 means 24V on command cable",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "TRUE"],
    )
    error_reset = pvproperty_with_rbv(
        name=":ALM_RST",
        value=0,
        doc="Reset Error state to valid by toggling this",
        read_only=False,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "TRUE"],
    )
    override_status = pvproperty(
        name=":OVRD_ON_RBV",
        value=0,
        doc="Epics Readback on Override mode",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["Override OFF", "Override ON"],
    )
    override_force_open = pvproperty_with_rbv(
        name=":FORCE_OPN",
        value=0,
        doc="Epics Command to force open the valve inoverride mode",
        read_only=False,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "FORCE OPEN"],
    )
    state = pvproperty(
        name=":STATE_RBV",
        value=0,
        doc="Valve state",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=[
            "Vented",
            "At Vacuum",
            "Differential Pressure",
            "Lost Vacuum",
            "Ext Fault",
            "AT Vacuum",
            "Triggered",
            "Vacuum Fault",
            "Close Timeout",
            "Open Timeout",
        ],
    )
    open_limit = pvproperty(
        name=":OPN_DI_RBV",
        value=0,
        doc="Open limit switch digital input",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "OPEN"],
    )
    closed_limit = pvproperty(
        name=":CLS_DI_RBV",
        value=0,
        doc="Closed limit switch digital input",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "CLOSE"],
    )
    diff_press_ok = pvproperty(
        name=":DP_OK_RBV",
        value=0,
        doc="Differential pressure interlock ok",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["DP NOT OK", "DP OK"],
    )
    ext_ilk_ok = pvproperty(
        name=":EXT_ILK_OK_RBV",
        value=0,
        doc="External interlock ok",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["NOT OK", "OK"],
    )
    at_vac_setpoint_us = pvproperty_with_rbv(
        name=":AT_VAC_SP",
        value=0.0,
        doc="AT VAC Set point value for the upstream gauge",
        read_only=False,
    )
    setpoint_hysterisis_us = pvproperty_with_rbv(
        name=":AT_VAC_HYS",
        value=0.0,
        doc="AT VAC Hysteresis for the upstream setpoint",
        read_only=False,
    )
    at_vac_setpoint_ds = pvproperty_with_rbv(
        name=":AT_VAC_SP_DS",
        value=0,
        doc="AT VAC Set point value for the downstream gauge",
        read_only=False,
    )
    setpoint_hysterisis_ds = pvproperty_with_rbv(
        name=":AT_VAC_HYS_DS",
        value=0,
        doc="AT VAC Hysteresis for the downstream setpoint",
        read_only=False,
    )
    at_vac = pvproperty(
        name=":AT_VAC_RBV",
        value=0,
        doc="at vacuum setpoint is reached",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["NOT AT VAC", "AT VAC"],
    )
    error = pvproperty(
        name=":ERROR_RBV",
        value=0,
        doc="Error Present",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["NO ERROR", "ERROR PRESENT"],
    )
    mps_state = pvproperty(
        name=":MPS_FAULT_OK_RBV",
        value=0,
        doc="individual valve MPS state for debugging",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["MPS FAULT", "MPS OK"],
    )
    interlock_device_upstream = pvproperty(
        name=":ILK_DEVICE_US_RBV",
        value="",
        doc="Upstream vacuum device used forinterlocking this valve",
        read_only=True,
        max_length=80,
    )
    interlock_device_downstream = pvproperty(
        name=":ILK_DEVICE_DS_RBV",
        value="",
        doc="Downstream vacuum device used forinterlocking this valve",
        read_only=True,
        max_length=80,
    )


class VRCClsLS(VVC, PVGroup):
    open_command = pvproperty_with_rbv(
        name=":OPN_SW",
        value=0,
        doc="Epics command to Open valve",
        read_only=False,
        dtype=ChannelType.ENUM,
        enum_strings=["CLOSE", "OPEN"],
    )
    interlock_ok = pvproperty(
        name=":OPN_OK_RBV",
        value=0,
        doc="Valve is OK to Open interlock ",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["OPN ILK NOT OK", "OPN ILK OK"],
    )
    open_do = pvproperty(
        name=":OPN_DO_RBV",
        value=0,
        doc="PLC Output to Open valve, 1 means 24V on command cable",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "TRUE"],
    )
    error_reset = pvproperty_with_rbv(
        name=":ALM_RST",
        value=0,
        doc="Reset Error state to valid by toggling this",
        read_only=False,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "TRUE"],
    )
    override_status = pvproperty(
        name=":OVRD_ON_RBV",
        value=0,
        doc="Epics Readback on Override mode",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["Override OFF", "Override ON"],
    )
    override_force_open = pvproperty_with_rbv(
        name=":FORCE_OPN",
        value=0,
        doc="Epics Command to force open the valve inoverride mode",
        read_only=False,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "FORCE OPEN"],
    )
    state = pvproperty(
        name=":STATE_RBV",
        value=0,
        doc="Valve state",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=[
            "Vented",
            "At Vacuum",
            "Differential Pressure",
            "Lost Vacuum",
            "Ext Fault",
            "AT Vacuum",
            "Triggered",
            "Vacuum Fault",
            "Close Timeout",
            "Open Timeout",
        ],
    )
    closed_limit = pvproperty(
        name=":CLS_DI_RBV",
        value=0,
        doc="Closed limit switch digital input",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "CLOSE"],
    )


class VVCNO(PVGroup):
    close_command = pvproperty_with_rbv(
        name=":CLS_SW",
        value=0,
        doc="Epics command to close valve",
        read_only=False,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "CLOSE"],
    )
    close_override = pvproperty_with_rbv(
        name=":FORCE_CLS",
        value=0,
        doc="Epics Command for open the valve in override mode",
        read_only=False,
    )
    override_on = pvproperty_with_rbv(
        name=":OVRD_ON",
        value=0,
        doc="Epics Command to set/reset Override mode",
        read_only=False,
        dtype=ChannelType.ENUM,
        enum_strings=["Override OFF", "Override ON"],
    )
    close_ok = pvproperty(
        name=":CLS_OK_RBV", value=0, doc="used for normally open valves", read_only=True
    )
    close_do = pvproperty(
        name=":CLS_DO_RBV", value=0, doc="PLC Output to close valve", read_only=True
    )


class VRCNO(VVCNO, PVGroup):
    close_command = pvproperty_with_rbv(
        name=":CLS_SW",
        value=0,
        doc="Epics command to close valve",
        read_only=False,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "CLOSE"],
    )
    close_override = pvproperty_with_rbv(
        name=":FORCE_CLS",
        value=0,
        doc="Epics Command for open the valve in override mode",
        read_only=False,
    )
    override_on = pvproperty_with_rbv(
        name=":OVRD_ON",
        value=0,
        doc="Epics Command to set/reset Override mode",
        read_only=False,
        dtype=ChannelType.ENUM,
        enum_strings=["Override OFF", "Override ON"],
    )
    close_ok = pvproperty(
        name=":CLS_OK_RBV", value=0, doc="used for normally open valves", read_only=True
    )
    close_do = pvproperty(
        name=":CLS_DO_RBV", value=0, doc="PLC Output to close valve", read_only=True
    )
    state = pvproperty(
        name=":STATE_RBV",
        value=0,
        doc="Valve state",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=[
            "Vented",
            "At Vacuum",
            "Differential Pressure",
            "Lost Vacuum",
            "Ext Fault",
            "AT Vacuum",
            "Triggered",
            "Vacuum Fault",
            "Close Timeout",
            "Open Timeout",
        ],
    )
    error_reset = pvproperty_with_rbv(
        name=":ALM_RST",
        value=0,
        doc="Reset Error state to valid by toggling this",
        read_only=False,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "TRUE"],
    )
    open_limit = pvproperty(
        name=":OPN_DI_RBV",
        value=0,
        doc="Open limit switch digital input",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "OPEN"],
    )
    closed_limit = pvproperty(
        name=":CLS_DI_RBV",
        value=0,
        doc="Closed limit switch digital input",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "CLOSE"],
    )


class VRCDA(VRC, VRCNO, PVGroup):
    close_command = pvproperty_with_rbv(
        name=":CLS_SW",
        value=0,
        doc="Epics command to close valve",
        read_only=False,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "CLOSE"],
    )
    close_override = pvproperty_with_rbv(
        name=":FORCE_CLS",
        value=0,
        doc="Epics Command for open the valve in override mode",
        read_only=False,
    )
    override_on = pvproperty_with_rbv(
        name=":OVRD_ON",
        value=0,
        doc="Epics Command to set/reset Override mode",
        read_only=False,
        dtype=ChannelType.ENUM,
        enum_strings=["Override OFF", "Override ON"],
    )
    close_ok = pvproperty(
        name=":CLS_OK_RBV", value=0, doc="used for normally open valves", read_only=True
    )
    close_do = pvproperty(
        name=":CLS_DO_RBV", value=0, doc="PLC Output to close valve", read_only=True
    )
    state = pvproperty(
        name=":STATE_RBV",
        value=0,
        doc="Valve state",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=[
            "Vented",
            "At Vacuum",
            "Differential Pressure",
            "Lost Vacuum",
            "Ext Fault",
            "AT Vacuum",
            "Triggered",
            "Vacuum Fault",
            "Close Timeout",
            "Open Timeout",
        ],
    )
    error_reset = pvproperty_with_rbv(
        name=":ALM_RST",
        value=0,
        doc="Reset Error state to valid by toggling this",
        read_only=False,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "TRUE"],
    )
    open_limit = pvproperty(
        name=":OPN_DI_RBV",
        value=0,
        doc="Open limit switch digital input",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "OPEN"],
    )
    closed_limit = pvproperty(
        name=":CLS_DI_RBV",
        value=0,
        doc="Closed limit switch digital input",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "CLOSE"],
    )
    open_command = pvproperty_with_rbv(
        name=":OPN_SW",
        value=0,
        doc="Epics command to Open valve",
        read_only=False,
        dtype=ChannelType.ENUM,
        enum_strings=["CLOSE", "OPEN"],
    )
    interlock_ok = pvproperty(
        name=":OPN_OK_RBV",
        value=0,
        doc="Valve is OK to Open interlock ",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["OPN ILK NOT OK", "OPN ILK OK"],
    )
    open_do = pvproperty(
        name=":OPN_DO_RBV",
        value=0,
        doc="PLC Output to Open valve, 1 means 24V on command cable",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "TRUE"],
    )
    override_status = pvproperty(
        name=":OVRD_ON_RBV",
        value=0,
        doc="Epics Readback on Override mode",
        read_only=True,
        dtype=ChannelType.ENUM,
        enum_strings=["Override OFF", "Override ON"],
    )
    override_force_open = pvproperty_with_rbv(
        name=":FORCE_OPN",
        value=0,
        doc="Epics Command to force open the valve inoverride mode",
        read_only=False,
        dtype=ChannelType.ENUM,
        enum_strings=["FALSE", "FORCE OPEN"],
    )
