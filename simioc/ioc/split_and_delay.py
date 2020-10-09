from caproto.server import PVGroup, SubGroup, pvproperty

from ..db.motor import AerotechMotor, AttocubeMotor
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

    t1_y1 = SubGroup(AttocubeMotor, prefix=':T1:Y1')
    t1_y2 = SubGroup(AttocubeMotor, prefix=':T1:Y2')
    t1_chi1 = SubGroup(AttocubeMotor, prefix=':T1:CHI1')
    t1_chi2 = SubGroup(AttocubeMotor, prefix=':T1:CHI2')
    t1_dh = SubGroup(AttocubeMotor, prefix=':T1:DH')
    t4_y1 = SubGroup(AttocubeMotor, prefix=':T4:Y1')
    t4_y2 = SubGroup(AttocubeMotor, prefix=':T4:Y2')
    t4_chi1 = SubGroup(AttocubeMotor, prefix=':T4:CHI1')
    t4_chi2 = SubGroup(AttocubeMotor, prefix=':T4:CHI2')
    t4_dh = SubGroup(AttocubeMotor, prefix=':T4:DH')

    n2_t1_gps = pvproperty(name=':N2:T1:GPS', value=1.0)
    n2_t1_vgp = pvproperty(name=':N2:T1:VGP', value=1.0)
    n2_t4_gps = pvproperty(name=':N2:T4:GPS', value=1.0)
    n2_t4_vgp = pvproperty(name=':N2:T4:VGP', value=1.0)
    t1_n2_t1_gps = pvproperty(name=':T1:N2:T1:GPS', value=1.0)
    t4_n2_t4_gps = pvproperty(name=':T4:N2:T4:GPS', value=1.0)
    vac_gps = pvproperty(name=':VAC:GPS', value=1.0)
    vac_vgp = pvproperty(name=':VAC:VGP', value=1.0)

    # TODO: standins for the areadetector components


if __name__ == '__main__':
    main(cls=SplitAndDelayIOC, default_prefix='PREFIX')
