#!/usr/bin/env python3
from typing import Any, Dict, Optional, cast

import caproto
from caproto.server import (AsyncLibraryLayer, PVGroup, SubGroup,
                            get_pv_pair_wrapper, pvproperty)
from caproto.server.records import MotorFields, register_record
from caproto.server.server import PvpropertyDouble

from .utils import pvproperty_with_rbv


async def broadcast_precision_to_fields(record):
    """Update precision of all fields to that of the given record."""

    precision = record.precision
    for field, prop in record.field_inst.pvdb.items():
        if hasattr(prop, 'precision'):
            await prop.write_metadata(precision=precision)


async def motor_record_simulator(
    instance: PvpropertyDouble,
    async_lib: AsyncLibraryLayer,
    defaults: Optional[Dict[str, Any]] = None,
    tick_rate_hz: float = 10.0,
):
    """
    A simple motor record simulator.

    Parameters
    ----------
    instance : pvproperty (ChannelDouble)
        Ensure you set ``record='motor'`` in your pvproperty first.

    async_lib : AsyncLibraryLayer

    defaults : dict, optional
        Defaults for velocity, precision, acceleration, limits, and resolution.

    tick_rate_hz : float, optional
        Update rate in Hz.
    """
    if defaults is None:
        defaults = dict(
            position=0.0,
            velocity=0.1,
            precision=3,
            acceleration=1.0,
            resolution=1e-6,
            tick_rate_hz=10.,
            user_limits=(0.0, 100.0),
            egu="mm",
        )

    fields = cast(MotorFields, instance.field_inst)
    have_new_position = False

    async def value_write_hook(fields, value):
        nonlocal have_new_position
        # This happens when a user puts to `motor.VAL`
        # print("New position requested!", value)
        have_new_position = True

    fields.value_write_hook = value_write_hook

    await instance.write_metadata(precision=defaults["precision"])
    await broadcast_precision_to_fields(instance)

    units = defaults.get("egu", "mm")
    await fields.user_readback_value.write(defaults["position"], units=units)
    await instance.write(defaults["position"], units=units)
    await fields.velocity.write(defaults["velocity"])
    await fields.seconds_to_velocity.write(defaults["acceleration"])
    await fields.motor_step_size.write(defaults["resolution"])
    await fields.user_low_limit.write(defaults["user_limits"][0])
    await fields.user_high_limit.write(defaults["user_limits"][1])
    await fields.engineering_units.write(units)

    while True:
        dwell = 1. / tick_rate_hz
        target_pos = instance.value
        diff = (target_pos - fields.user_readback_value.value)
        # compute the total movement time based an velocity
        total_time = abs(diff / fields.velocity.value)
        # compute how many steps, should come up short as there will
        # be a final write of the return value outside of this call
        num_steps = int(total_time // dwell)
        if abs(diff) < 1e-9 and not have_new_position:
            if fields.stop.value != 0:
                await fields.stop.write(0)
            await async_lib.library.sleep(dwell)
            continue

        if fields.stop.value != 0:
            await fields.stop.write(0)

        await fields.done_moving_to_value.write(0)
        await fields.motor_is_moving.write(1)

        readback = fields.user_readback_value.value
        step_size = diff / num_steps if num_steps > 0 else 0.0
        resolution = max((fields.motor_step_size.value, 1e-10))

        for _ in range(num_steps):
            if fields.stop.value != 0:
                await fields.stop.write(0)
                await instance.write(readback)
                break
            if fields.stop_pause_move_go.value == "Stop":
                await instance.write(readback)
                break

            readback += step_size
            raw_readback = readback / resolution
            await fields.user_readback_value.write(readback)
            await fields.dial_readback_value.write(readback)
            await fields.raw_readback_value.write(raw_readback)
            await async_lib.library.sleep(dwell)
        else:
            # Only executed if we didn't break
            await fields.user_readback_value.write(target_pos)

        await fields.motor_is_moving.write(0)
        await fields.done_moving_to_value.write(1)
        have_new_position = False


class Motor(PVGroup):
    motor = pvproperty(value=0.0, name='', record='motor', precision=3)

    def __init__(self, *args,
                 position=0.0,
                 velocity=1.0,
                 precision=3,
                 acceleration=1.0,
                 resolution=1e-6,
                 user_limits=(0.0, 100.0),
                 tick_rate_hz=10.,
                 egu="mm",
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.tick_rate_hz = tick_rate_hz
        self.defaults = {
            "position": position,
            "velocity": velocity,
            "precision": precision,
            "acceleration": acceleration,
            "resolution": resolution,
            "user_limits": tuple(user_limits),
            "egu": "mm",
        }

    @property
    def fields(self) -> MotorFields:
        """Fields of the motor record."""
        return self.motor.field_inst

    @property
    def user_setpoint_position(self) -> float:
        """User setpoint position."""
        return self.motor.value

    @property
    def user_readback_position(self) -> float:
        """User readback position of the motor."""
        return self.fields.user_readback_value.value

    @motor.startup
    async def motor(self, instance, async_lib):
        # Start the simulator:
        await motor_record_simulator(
            self.motor, async_lib, self.defaults,
            tick_rate_hz=self.tick_rate_hz,
        )


class SmarActMotor(Motor):
    ptype = pvproperty_with_rbv(name=":PTYPE", value=0, doc="Positioner type")
    step_voltage = pvproperty(
        name=":STEP_VOLTAGE", value=0.0, doc="Voltage for sawtooth (0-100V)"
    )
    # Frequency of steps
    step_freq = pvproperty(name=":STEP_FREQ", value=0.0, doc="Sawtooth drive frequency")
    # Number of steps per step forward, backward command
    jog_step_size = pvproperty(
        name=":STEP_COUNT", value=0, doc="Number of steps per FWD/BWD command"
    )
    # Jog forward
    jog_fwd = pvproperty(name=":STEP_FORWARD", value=0, doc="Jog the stage forward")
    # Jog backward
    jog_rev = pvproperty(name=":STEP_REVERSE", value=0, doc="Jog the stage backward")
    # Total number of steps counted
    total_step_count = pvproperty(
        name=":TOTAL_STEP_COUNT",
        value=0,
        doc="Current open loop step count",
        read_only=True,
    )
    # Reset steps ("home")
    step_clear_cmd = pvproperty(
        name=":CLEAR_COUNT", value=0, doc="Clear the current step count"
    )
    # Scan move
    scan_pos = pvproperty(
        name=":SCAN_POS", value=0, doc="Set current piezo voltage (in 16 bit ADC steps)"
    )
    scan_move = pvproperty(
        name=":SCAN_MOVE",
        value=0,
        doc="Set current piezo voltage (in 16 bit ADC steps)",
    )


class BeckhoffAxisPLC(PVGroup):
    status = pvproperty(value='No error', name='sErrorMessage_RBV')
    err_code = pvproperty(value=0, name='nErrorId_RBV')
    cmd_err_reset = pvproperty(value=0, name='bReset')
    cmd_err_reset_rbv = pvproperty(value=0, name='bReset_RBV')


pvproperty_with_rbv = get_pv_pair_wrapper(setpoint_suffix='',
                                          readback_suffix='_RBV')


class TwinCATStateConfigOne(PVGroup):
    state_name = pvproperty(dtype=str, name='NAME_RBV')
    setpoint = pvproperty_with_rbv(dtype=float, name='SETPOINT')
    delta = pvproperty_with_rbv(dtype=float, name='DELTA')
    velo = pvproperty_with_rbv(dtype=float, name='VELO')
    accl = pvproperty_with_rbv(dtype=float, name='ACCL')
    dccl = pvproperty_with_rbv(dtype=float, name='DCCL')
    move_ok = pvproperty(value=0, name='MOVE_OK_RBV')
    locked = pvproperty(value=0, name='LOCKED_RBV')
    valid = pvproperty(value=0, name='VALID_RBV')


class TwinCATStateConfigAll(PVGroup):
    state01 = SubGroup(TwinCATStateConfigOne, prefix='01:')
    state02 = SubGroup(TwinCATStateConfigOne, prefix='02:')
    state03 = SubGroup(TwinCATStateConfigOne, prefix='03:')
    state04 = SubGroup(TwinCATStateConfigOne, prefix='04:')
    state05 = SubGroup(TwinCATStateConfigOne, prefix='05:')
    state06 = SubGroup(TwinCATStateConfigOne, prefix='06:')
    # state07 = SubGroup(TwinCATStateConfigOne, prefix='07:')
    # state08 = SubGroup(TwinCATStateConfigOne, prefix='08:')
    # state09 = SubGroup(TwinCATStateConfigOne, prefix='09:')
    # state10 = SubGroup(TwinCATStateConfigOne, prefix='10:')
    # state11 = SubGroup(TwinCATStateConfigOne, prefix='11:')
    # state12 = SubGroup(TwinCATStateConfigOne, prefix='12:')
    # state13 = SubGroup(TwinCATStateConfigOne, prefix='13:')
    # state14 = SubGroup(TwinCATStateConfigOne, prefix='14:')
    # state15 = SubGroup(TwinCATStateConfigOne, prefix='15:')


class TwinCATStatePositioner(PVGroup):
    _delay = 0.2

    state_get = pvproperty(value=0, name='GET_RBV')
    state_set = pvproperty(value=0, name='SET')
    error = pvproperty(value=0.0, name='ERR_RBV')
    error_id = pvproperty(value=0, name='ERRID_RBV')
    error_message = pvproperty(dtype=str, name='ERRMSG_RBV')
    busy = pvproperty(value=0, name='BUSY_RBV')
    done = pvproperty(value=0, name='DONE_RBV')
    reset_cmd = pvproperty_with_rbv(dtype=int, name='RESET')
    config = SubGroup(TwinCATStateConfigAll, prefix='')

    @state_set.startup
    async def state_set(self, instance, async_lib):
        self.async_lib = async_lib
        # Start as "out" and not unknown
        await self.state_get.write(1)

    @state_set.putter
    async def state_set(self, instance, value):
        await self.busy.write(1)
        await self.state_get.write(0)
        await self.async_lib.library.sleep(self._delay)
        await self.state_get.write(value)
        await self.busy.write(0)
        await self.done.write(1)


class BeckhoffAxis(PVGroup):
    plc = SubGroup(BeckhoffAxisPLC, prefix=':PLC:')
    state = SubGroup(TwinCATStatePositioner, prefix=':STATE:')
    motor = SubGroup(Motor, velocity=2, prefix='')


@register_record
class XpsMotorFields(MotorFields):
    _record_type = 'xps8p'

    stop_pause_go = pvproperty(
        name='SPG',
        value='GO',
        dtype=caproto.ChannelType.ENUM,
        enum_strings=['STOP', 'PAUSE', 'GO'],
        doc='PCDS stop-pause-go variant of SPMG',
        read_only=False)


class XpsMotor(Motor):
    motor = pvproperty(value=0.0, name='', record='xps8p', precision=3)

    # TODO: caproto bug
    motor.startup(Motor.motor.pvspec.startup)


@register_record
class ImsMotorFields(MotorFields):
    _record_type = 'ims'

    stop_pause_go = pvproperty(
        name='SPG',
        value='GO',
        dtype=caproto.ChannelType.ENUM,
        enum_strings=['STOP', 'PAUSE', 'GO'],
        doc='PCDS stop-pause-go variant of SPMG',
        read_only=False
    )

    # Custom IMS bit fields
    reinit_command = pvproperty(
        name='RINI',
        value=0,
        doc='Reinitialize command',
        read_only=False,
    )

    # Custom IMS bit fields
    part_number = pvproperty(
        name='PN',
        value='',
        doc='Part number',
        read_only=True,
        report_as_string=True,
    )


class ImsMotor(Motor):
    motor = pvproperty(value=0.0, name='', record='ims', precision=3)
    seq_seln = pvproperty(value=0, name=':SEQ_SELN', record='longout')

    # TODO: caproto bug
    motor.startup(Motor.motor.pvspec.startup)


class AerotechMotor(Motor):
    """
    Aerotech motor record + additional records.

    Pairs with :class:`hxrsnd.aerotech.AeroBase`.

    May not be entirely accurate with respect to record types.
    """

    axis_status = pvproperty(
        name=":AXIS_STATUS",
        read_only=True,
        value=0,
    )

    axis_fault = pvproperty(
        name=":AXIS_FAULT",
        read_only=True,
        value=0,
    )
    clear_error = pvproperty(
        name=":CLEAR",
        read_only=False,
        value=0,
        record='bo',
    )
    config = pvproperty(
        name=":CONFIG",
        read_only=False,
        value=0,
    )
    zero_all_proc = pvproperty(
        name=":ZERO_P",
        record='bo',
        read_only=False,
        value=0,
    )


class AttocubeMotor(PVGroup):
    """
    Not a motor record. Pairs with :class:`hxrsnd.attocube.EccBase`.

    May not be entirely accurate with respect to record types.
    """
    # position
    user_readback = pvproperty(value=0.0, read_only=True, name=":POSITION")
    user_setpoint = pvproperty(value=0.0, name=":CMD:TARGET", record='ai')

    # limits
    # upper_ctrl_limit = pvproperty(name=':CMD:TARGET.HOPR')
    # lower_ctrl_limit = pvproperty(name=':CMD:TARGET.LOPR')

    # configuration
    motor_egu = pvproperty(value='mm', read_only=True, name=":UNIT")
    motor_amplitude = pvproperty(value=0.0, name=":CMD:AMPL")
    motor_dc = pvproperty(value=0.0, name=":CMD:DC")
    motor_frequency = pvproperty(value=0.0, name=":CMD:FREQ")

    # motor status
    motor_connected = pvproperty(value=True, read_only=True,
                                 name=":ST_CONNECT")
    motor_enabled = pvproperty(value=True, read_only=True, name=":ST_ENABLED")
    motor_referenced = pvproperty(value=True, read_only=True,
                                  name=":ST_REFVAL")
    motor_error = pvproperty(value=False, read_only=True, name=":ST_ERROR")
    motor_is_moving = pvproperty(value=False, read_only=True,
                                 name=":RD_MOVING")
    motor_done_move = pvproperty(value=False, read_only=True,
                                 name=":RD_INRANGE")
    high_limit_switch = pvproperty(value=False, name=":ST_EOT_FWD")
    low_limit_switch = pvproperty(value=False, name=":ST_EOT_BWD")
    motor_reference_position = pvproperty(value=0.0, read_only=True,
                                          name=":REF_POSITION")

    # commands
    motor_stop = pvproperty(value=0, name=":CMD:STOP")
    motor_reset = pvproperty(value=0, name=":CMD:RESET.PROC")
    motor_enable = pvproperty(value=True, name=":CMD:ENABLE")

    @user_setpoint.startup
    async def user_setpoint(self, instance, async_lib):
        """
        Startup hook for user_setpoint.
        """
        await self.user_setpoint.field_inst.low_operating_range.write(
            value=-10)
        await self.user_setpoint.field_inst.high_operating_range.write(
            value=10)

    @user_setpoint.putter
    async def user_setpoint(self, instance, value):
        await self.user_readback.write(value=value)
