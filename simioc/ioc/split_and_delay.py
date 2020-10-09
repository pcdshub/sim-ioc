from caproto.server import PVGroup, SubGroup

from ..db.motor import AerotechMotor
from .utils import main


class SplitAndDelayIOC(PVGroup):
    """
    A stand-in split and delay IOC, including:

    * Aerotech stages
    * The rest is TODO
    """

    default_velo = 3.
    default_prec = 2

    t1_tth = SubGroup(
        AerotechMotor,
        velocity=default_velo,
        precision=default_prec,
        prefix=':T1:TTH'
    )

    t1_th1 = SubGroup(
        AerotechMotor,
        velocity=default_velo,
        precision=default_prec,
        prefix=':T1:TH1'
    )

    t1_th2 = SubGroup(
        AerotechMotor,
        velocity=default_velo,
        precision=default_prec,
        prefix=':T1:TH2'
    )

    t1_x = SubGroup(
        AerotechMotor,
        velocity=default_velo,
        precision=default_prec,
        prefix=':T1:X'
    )

    t1_l = SubGroup(
        AerotechMotor,
        velocity=default_velo,
        precision=default_prec,
        prefix=':T1:L'
    )

    t4_tth = SubGroup(
        AerotechMotor,
        velocity=default_velo,
        precision=default_prec,
        prefix=':T4:TTH'
    )

    t4_th1 = SubGroup(
        AerotechMotor,
        velocity=default_velo,
        precision=default_prec,
        prefix=':T4:TH1'
    )

    t4_th2 = SubGroup(
        AerotechMotor,
        velocity=default_velo,
        precision=default_prec,
        prefix=':T4:TH2'
    )

    t4_x = SubGroup(
        AerotechMotor,
        velocity=default_velo,
        precision=default_prec,
        prefix=':T4:X'
    )

    t4_l = SubGroup(
        AerotechMotor,
        velocity=default_velo,
        precision=default_prec,
        prefix=':T4:L'
    )

    t2_th = SubGroup(
        AerotechMotor,
        velocity=default_velo,
        precision=default_prec,
        prefix=':T2:TH'
    )

    t2_x = SubGroup(
        AerotechMotor,
        velocity=default_velo,
        precision=default_prec,
        prefix=':T2:X'
    )

    t3_th = SubGroup(
        AerotechMotor,
        velocity=default_velo,
        precision=default_prec,
        prefix=':T3:TH'
    )

    t3_x = SubGroup(
        AerotechMotor,
        velocity=default_velo,
        precision=default_prec,
        prefix=':T3:X'
    )

    dia_di_x = SubGroup(
        AerotechMotor,
        velocity=default_velo,
        precision=default_prec,
        prefix=':DIA:DI:X'
    )

    dia_dd_x = SubGroup(
        AerotechMotor,
        velocity=default_velo,
        precision=default_prec,
        prefix=':DIA:DD:X'
    )

    dia_dd_y = SubGroup(
        AerotechMotor,
        velocity=default_velo,
        precision=default_prec,
        prefix=':DIA:DD:Y'
    )

    dia_do_x = SubGroup(
        AerotechMotor,
        velocity=default_velo,
        precision=default_prec,
        prefix=':DIA:DO:X'
    )

    dia_dci_x = SubGroup(
        AerotechMotor,
        velocity=default_velo,
        precision=default_prec,
        prefix=':DIA:DCI:X'
    )

    dia_dcc_x = SubGroup(
        AerotechMotor,
        velocity=default_velo,
        precision=default_prec,
        prefix=':DIA:DCC:X'
    )

    dia_dcc_y = SubGroup(
        AerotechMotor,
        velocity=default_velo,
        precision=default_prec,
        prefix=':DIA:DCC:Y'
    )

    dia_dco_x = SubGroup(
        AerotechMotor,
        velocity=default_velo,
        precision=default_prec,
        prefix=':DIA:DCO:X'
    )


if __name__ == '__main__':
    main(cls=SplitAndDelayIOC, default_prefix='PREFIX')
