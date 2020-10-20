#!/usr/bin/env python3

from caproto.server import PVGroup, SubGroup

from ..db.heartbeat import HeartbeatGroup
from ..db.undulator import BeamParametersGroup
from .utils import main


class BeamlineGroup(PVGroup):
    heartbeat = SubGroup(HeartbeatGroup, prefix='')
    beam_params = SubGroup(BeamParametersGroup, prefix='')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        params = self.params
        lower_gap, upper_gap = params['gap_range']
        self.beam_params.gap._data.update(
            lower_ctrl_limit=lower_gap,
            upper_ctrl_limit=upper_gap,
            value=lower_gap,
        )

        lower_energy, upper_energy = params['electron_energy_range']
        self.beam_params.electron_energy._data.update(
            lower_ctrl_limit=lower_energy,
            upper_ctrl_limit=upper_energy,
            value=lower_energy,
        )

        und_info = self.beam_params.undulator_info
        for param in ('k0', 'a', 'b', 'period'):
            getattr(und_info, param)._data['value'] = params[param]


class HxuBeamlineGroup(BeamlineGroup):
    # hxu assuming copper line (SCRF line is slightly different, gap-wise)
    params = dict(
        k0=9.471,
        a=-5.131,
        b=1.878,
        period=26.,
        gap_range=(7.2, 19),
        electron_energy_range=(2.5, 15.0),
    )


class SxuBeamlineGroup(BeamlineGroup):
    params = dict(
        k0=13.997,
        a=-5.131,
        b=1.878,
        period=39.,
        gap_range=(7.2, 20),
        electron_energy_range=(3.6, 4.0),
    )


class AcceleratorGroup(PVGroup):
    """Accelerator IOC simulator for PMPS."""
    hxu = SubGroup(HxuBeamlineGroup)
    sxu = SubGroup(SxuBeamlineGroup)


if __name__ == '__main__':
    main(cls=AcceleratorGroup, default_prefix='PREFIX:')
