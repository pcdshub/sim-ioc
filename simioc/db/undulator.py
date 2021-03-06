#!/usr/bin/env python3
import numpy as np
from caproto.server import PVGroup, SubGroup, pvproperty


def calculate_k(k0, a, b, period, gap):
    '''
    Calculate undulator strength, K.

    Parameters
    ----------
    k0 : float
        Tuning parameter
    a : float
        Tuning parameter
    b : float
        Tuning parameter
    period : float
        Undulator period, in mm
    gap : float, np.array
        Undulator gap, in mm
    '''
    return k0 * np.exp(a * (gap / period) + b * (gap / period) ** 2)


def calculate_photon_energy(electron_energy, period, k):
    '''
    Estimate the energy of photons generated by an undulator (given period and
    K) with electrons at the given energy.

    Parameters
    ----------
    electron_energy : float
        Electron energy in GeV
    period : float
        Undulator period, in mm
    k : float
        Undulator K parameter (strength), unitless
    '''
    m_e = 0.0005109989461  # GeV [electron rest mass/energy]
    h = 6.62607004e-34  # Js [Planck's constant]
    e = 1.6021766208e-19  # C [electron charge]
    c = 299792458  # m/s, speed of light
    return ((2. * (electron_energy / m_e) ** 2 * h * c) /
            (e * period * 1e-3 * (1 + k ** 2 / 2.))
            )


class UndulatorInfoGroup(PVGroup):
    k0 = pvproperty(value=0.0, read_only=True)
    a = pvproperty(value=0.0, read_only=True)
    b = pvproperty(value=0.0, read_only=True)
    period = pvproperty(value=0, read_only=True)

    def calculate_k(self, gap):
        'Calculate K, given an undulator gap'
        return calculate_k(
            k0=self.k0.value,
            a=self.a.value,
            b=self.b.value,
            period=self.period.value,
            gap=gap
        )


class BeamParametersGroup(PVGroup):
    undulator_info = SubGroup(UndulatorInfoGroup, prefix='')

    rate = pvproperty(
        value=10,
        doc='Repetition rate',
        units='Hz'
    )

    charge = pvproperty(
        value=10,
        record='longin',
        units='pC',
        doc='Bunch charge'
    )

    async def _recalculate(self, instance, value):
        await self.k.write(self.undulator_info.calculate_k(self.gap.value))
        await self.photon_energy.write(
            calculate_photon_energy(electron_energy=self.electron_energy.value,
                                    period=self.undulator_info.period.value,
                                    k=self.k.value)
        )

    gap = pvproperty(
        value=10.,
        doc='Undulator gap',
        record='ai',
        units='mm',
        put=_recalculate,
    )

    k = pvproperty(
        value=0.,
        doc='Undulator strength (K)',
        record='ai',
        units='n/a',
    )

    electron_energy = pvproperty(
        value=0.0,
        doc='Electron energy',
        units='GeV',
        precision=4,
        put=_recalculate,
    )

    photon_energy = pvproperty(
        value=0.0,
        doc='Photon energy',
        read_only=True,
        precision=4,
    )

    @gap.startup
    async def gap(self, instance, async_lib):
        # Ensure k/photon energy is calculated on startup
        await instance.write(instance.value)
