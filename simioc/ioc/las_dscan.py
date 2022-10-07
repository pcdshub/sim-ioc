from caproto.server import PVGroup, SubGroup

from ..db.motor import Motor
from ..db.qmini import QminiSpectrometer
from .utils import main


class LaserDscanIOC(PVGroup):
    """
    A simulation IOC used for the laser dispersion scan GUI.
    """

    spectrometer = SubGroup(QminiSpectrometer, prefix='{spectrometer}')
    motor = SubGroup(Motor, prefix='{motor}')


if __name__ == '__main__':
    main(
        cls=LaserDscanIOC,
        default_prefix='IOC:TST:',
        macros={
            'spectrometer': 'DScan:Qmini',
            'motor': 'DScan:m1',
        },
    )
