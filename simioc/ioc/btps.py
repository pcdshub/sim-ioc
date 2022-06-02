"""
BTPS Simulator IOC for unit and integration tests.
"""

from caproto.server import PVGroup, SubGroup

from ..db.btps import BtpsMotorsAndCameras, BtpsState
from .utils import main


class BtpsSimulator(PVGroup):
    """
    A simulator for BTPS motors, cameras, and range logic.

    Listed PVs do not include the default "SIM:" prefix.
    """

    motors = SubGroup(BtpsMotorsAndCameras, prefix="")
    state = SubGroup(BtpsState, prefix="LTLHN:BTPS:")


if __name__ == "__main__":
    main(cls=BtpsSimulator, default_prefix="SIM:")
