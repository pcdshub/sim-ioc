from caproto.server import PVGroup, SubGroup

from ..db.motor import Motor, XpsMotor
from .utils import main


class MotorIOC(PVGroup):
    """
    A fake motor IOC, with 3 fake motors.

    PVs
    ---
    mtr1 (motor)
    mtr2 (motor)
    mtr3 (motor)
    """

    motor1 = SubGroup(Motor, velocity=1., precision=3, prefix='mtr1')
    motor2 = SubGroup(Motor, velocity=2., precision=2, prefix='mtr2')
    motor3 = SubGroup(Motor, velocity=3., precision=2, prefix='mtr3')
    xps_motor1 = SubGroup(XpsMotor, velocity=3., precision=2,
                          prefix='xps:mtr1')
    xps_motor2 = SubGroup(XpsMotor, velocity=3., precision=2,
                          prefix='xps:mtr2')
    xps_motor3 = SubGroup(XpsMotor, velocity=3., precision=2,
                          prefix='xps:mtr3')


if __name__ == '__main__':
    main(cls=MotorIOC, default_prefix='sim:')
