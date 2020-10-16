from caproto.server import PVGroup, SubGroup

from ..db.ccm import CCMCalcGroup, CCMMotorGroup, CCMXGroup, CCMYGroup
from ..db.motor import Motor
from .utils import main


class CCM(PVGroup):
    """
    A simulated CCM IOC.

    May require some customization when using a custom prefix.

    ::

        pcdsdevices.ccm.CCMCalc.energy_request.suffix = 'sim:{hutch}'

        ccm = pcdsdevices.ccm.CCM(**{
            'in_pos': 3.3,
            'out_pos': 13.18,
            'theta0': 0.2311318654103,
            'name': 'xcs_ccm',
            'alio_prefix': 'sim:XCS:MON:MPZ:01',
            'chi2_prefix': 'sim:XCS:MON:PIC:06',
            'theta2coarse_prefix': 'sim:XCS:MON:PIC:05',
            'theta2fine_prefix': 'sim:XCS:MON:MPZ:02',
            'x_down_prefix': 'sim:XCS:MON:MMS:24',
            'x_up_prefix': 'sim:XCS:MON:MMS:25',
            'y_down_prefix': 'sim:XCS:MON:MMS:26',
            'y_up_north_prefix': 'sim:XCS:MON:MMS:27',
            'y_up_south_prefix': 'sim:XCS:MON:MMS:28',
        })

    """

    calc = SubGroup(CCMCalcGroup, prefix='')
    theta2fine = SubGroup(CCMMotorGroup, prefix='{{theta2fine_prefix}}')
    theta2coarse = SubGroup(Motor, prefix='{{theta2coarse_prefix}}')
    chi2 = SubGroup(Motor, prefix='{{chi2_prefix}}')
    x = SubGroup(CCMXGroup, prefix='')
    y = SubGroup(CCMYGroup, prefix='')


if __name__ == '__main__':
    main(
        cls=CCM, default_prefix='sim:',
        macros={
            'hutch': 'XCS',
            'chi2_prefix': 'XCS:MON:PIC:06',
            'alio_prefix': 'XCS:MON:MPZ:01',
            'theta2coarse_prefix': 'XCS:MON:PIC:05',
            'theta2fine_prefix': 'XCS:MON:MPZ:02',
            'x_down_prefix': 'XCS:MON:MMS:24',
            'x_up_prefix': 'XCS:MON:MMS:25',
            'y_down_prefix': 'XCS:MON:MMS:26',
            'y_up_north_prefix': 'XCS:MON:MMS:27',
            'y_up_south_prefix': 'XCS:MON:MMS:28'
        },
    )
