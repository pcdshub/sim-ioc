from caproto.server import PVGroup, SubGroup

from .motor import BeckhoffAxis


class BladeGroup(PVGroup):
    """
    PV group for motion axes.
    """
    # Index   Blade Number 		Material	Thickness (um)	IN Beam
    # Position (mm)	OUT (mm)
    # 1	Mirror	- 	0	24
    # 2	Diamond (C)	1,280	0	24
    # 3	Diamond (C)	320	0	24
    # 4	Diamond (C)	640	0	24
    # 5	Diamond (C)	160	0	24
    # 6	Diamond (C)	80	0	24
    # 7	Diamond (C)	40	0	24
    # 8	Diamond (C)	20	0	24
    # 9	Diamond (C)	10	0	24
    # 10	Silicon (Si)	10,240	0	24
    # 11	Silicon (Si)	5,120	0	24
    # 12	Silicon (Si)	2,560	0	24
    # 13	Silicon (Si)	1,280	0	24
    # 14	Silicon (Si)	640	0	24
    # 15	Silicon (Si)	320	0	24
    # 16	Silicon (Si)	160	0	24
    # 17	Silicon (Si)	80	0	24
    # 18	Silicon (Si)	40	0	24
    # 19	Silicon (Si)	20	0	24
    locals().update(
        **{f'axis{axis:02d}': SubGroup(BeckhoffAxis,
                                       prefix=f'MMS:{axis:02d}')
           for axis in range(1, 20)
           }
    )
