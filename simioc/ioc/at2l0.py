from caproto.server import PVGroup, SubGroup

from ..db.attenuator import BladeGroup
from .utils import main


class IOCMain(PVGroup):
    """AT2L0 motion simulator IOC."""

    # beam = SubGroup(EVGroup, prefix='LCLS:HXR:BEAM:')
    # pmps = SubGroup(PMPSGroup, prefix='PMPS:AT2L0:')
    attenuator = SubGroup(BladeGroup, prefix='AT2L0:XTES:')


if __name__ == '__main__':
    main(IOCMain)
