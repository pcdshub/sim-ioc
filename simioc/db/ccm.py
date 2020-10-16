#!/usr/bin/env python3
from caproto.server import PVGroup, SubGroup, pvproperty

from .motor import ImsMotor


class CCMMotorGroup(PVGroup):
    # done = pvproperty(name=None, dtype=int)
    setpoint = pvproperty(name=':POSITIONSET', dtype=float)
    readback = pvproperty(name=':POSITIONGET', dtype=float, read_only=True)

    @setpoint.putter
    async def setpoint(self, instance, value):
        await self.readback.write(value=value)


class BeamEnergyRequestGroup(PVGroup):
    # done = pvproperty(name=None, dtype=int)
    setpoint = pvproperty(name=':USER:MCC:EPHOT', dtype=float)


class CCMCalcGroup(PVGroup):
    # energy = SubGroup(PseudoSingleInterfaceGroup, prefix='None')
    # wavelength = SubGroup(PseudoSingleInterfaceGroup, prefix='None')
    # theta = SubGroup(PseudoSingleInterfaceGroup, prefix='None')
    # energy_with_vernier = SubGroup(PseudoSingleInterfaceGroup, prefix='None')
    alio = SubGroup(CCMMotorGroup, prefix='{{alio_prefix}}')
    energy_request = SubGroup(BeamEnergyRequestGroup, prefix='{{hutch}}')


class CCMXGroup(PVGroup):
    # pseudo = SubGroup(PseudoSingleInterfaceGroup, prefix='None')
    down = SubGroup(ImsMotor, prefix='{{x_down_prefix}}', velocity=10)
    up = SubGroup(ImsMotor, prefix='{{x_up_prefix}}', velocity=10)


class CCMYGroup(PVGroup):
    # pseudo = SubGroup(PseudoSingleInterfaceGroup, prefix='None')
    down = SubGroup(ImsMotor, prefix='{{y_down_prefix}}')
    up_north = SubGroup(ImsMotor, prefix='{{y_up_north_prefix}}')
    up_south = SubGroup(ImsMotor, prefix='{{y_up_south_prefix}}')
