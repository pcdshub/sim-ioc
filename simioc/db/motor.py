#!/usr/bin/env python3
import caproto
from caproto.server import PVGroup, SubGroup, get_pv_pair_wrapper, pvproperty
from caproto.server.records import MotorFields, register_record


async def broadcast_precision_to_fields(record):
    """Update precision of all fields to that of the given record."""

    precision = record.precision
    for field, prop in record.field_inst.pvdb.items():
        if hasattr(prop, 'precision'):
            await prop.write_metadata(precision=precision)


class Motor(PVGroup):
    motor = pvproperty(value=0.0, name='', record='motor',
                       precision=3)

    def __init__(self, *args,
                 velocity=0.1,
                 precision=3,
                 acceleration=1.0,
                 resolution=1e-6,
                 tick_rate_hz=10.,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self._have_new_position = False
        self.tick_rate_hz = tick_rate_hz
        self.defaults = {
            'velocity': velocity,
            'precision': precision,
            'acceleration': acceleration,
            'resolution': resolution,
        }

    @motor.putter
    async def motor(self, instance, value):
        self._have_new_position = True
        return value

    @motor.startup
    async def motor(self, instance, async_lib):
        self.async_lib = async_lib

        await self.motor.write_metadata(precision=self.defaults['precision'])
        await broadcast_precision_to_fields(self.motor)

        fields = self.motor.field_inst  # type: MotorFields
        await fields.velocity.write(self.defaults['velocity'])
        await fields.seconds_to_velocity.write(self.defaults['acceleration'])
        await fields.motor_step_size.write(self.defaults['resolution'])

        while True:
            dwell = 1. / self.tick_rate_hz
            target_pos = self.motor.value
            diff = (target_pos - fields.user_readback_value.value)
            # compute the total movement time based an velocity
            total_time = abs(diff / fields.velocity.value)
            # compute how many steps, should come up short as there will
            # be a final write of the return value outside of this call
            num_steps = int(total_time // dwell)
            if abs(diff) < 1e-9 and not self._have_new_position:
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
                    await self.motor.write(readback)
                    break
                if fields.stop_pause_move_go.value == 'Stop':
                    await self.motor.write(readback)
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
            self._have_new_position = False


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
