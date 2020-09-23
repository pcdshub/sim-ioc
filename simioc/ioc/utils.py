import typing
from textwrap import dedent

from caproto.server import PVGroup, ioc_arg_parser, run


def main(cls: typing.Type[PVGroup], default_prefix='sim:') -> PVGroup:
    """
    Boilerplate for running a simple IOC.

    Expects a usable docstring on the class.

    Parameters
    ----------
    cls : PVGroup class
        The top-level PVGroup.

    default_prefix : str, optional
        The default prefix.

    Returns
    -------
    ioc : PVGroup
        The instantiated PVGroup, after the IOC runs.
    """
    ioc_options, run_options = ioc_arg_parser(
        default_prefix=default_prefix,
        desc=dedent(cls.__doc__)
    )
    ioc = cls(**ioc_options)
    run(ioc.pvdb, **run_options)
    return ioc
