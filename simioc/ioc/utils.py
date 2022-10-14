import pathlib
from textwrap import dedent
from typing import Dict, Optional, Type

from caproto.server import PVGroup, ioc_arg_parser, run

SIM_IOC_PATH = pathlib.Path(__file__).resolve().parent


def main(cls: Type[PVGroup],
         default_prefix: str = 'sim:',
         macros: Optional[Dict[str, str]] = None,
         ) -> PVGroup:
    """
    Boilerplate for running a simple IOC.

    Expects a usable docstring on the class.

    Parameters
    ----------
    cls : PVGroup class
        The top-level PVGroup.

    default_prefix : str, optional
        The default prefix.

    macros : dict, optional
        The macro options to pass to `ioc_arg_parser`.

    Returns
    -------
    ioc : PVGroup
        The instantiated PVGroup, after the IOC runs.
    """
    ioc_options, run_options = ioc_arg_parser(
        default_prefix=default_prefix,
        desc=dedent(cls.__doc__),
        macros=macros,
    )
    ioc = cls(**ioc_options)
    run(ioc.pvdb, **run_options)
    return ioc
