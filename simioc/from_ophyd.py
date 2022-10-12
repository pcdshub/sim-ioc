"""
Helper which takes a Python module with ophyd Devices and converts them to
caproto PVGroups.
"""
from __future__ import annotations

import argparse
import importlib
import inspect
import logging
from typing import Any, Dict, Generator, List, Optional, Type, cast

import lark
import ophyd
import whatrecord
from ophyd.signal import EpicsSignalRO

try:
    from pcdsdevices.signal import PytmcSignalRO, SignalRO
except ImportError:
    ro_signal_classes = (EpicsSignalRO,)
else:
    ro_signal_classes = (EpicsSignalRO, SignalRO, PytmcSignalRO)


logger = logging.getLogger(__name__)


DESCRIPTION = __doc__


def convert_signal(
    cpt: ophyd.Component,
    attr: str,
    pvname: str,
    setpoint_pvname: Optional[str],
    signal: ophyd.signal.EpicsSignalBase,
    value: Optional[Any] = 0,
    **kwargs,
) -> Generator[str, None, None]:
    """
    Take an ophyd component and an instantiated signal and return caproto
    PVGroup-compatible pvproperty code.

    Parameters
    ----------
    cpt : ophyd.Component
        The ophyd component for the attribute.

    attr : str
        The attribute name to use.

    pvname : str
        The PV name.

    setpoint_pvname : str, optional
        An optional setpoint PV name.

    signal : EpicsSignal
        The instantiated signal

    value : any, optional
        The initial value.

    **kwargs :
        Keyword arguments for the pvproperty.
    """
    cls = "pvproperty"
    if setpoint_pvname and setpoint_pvname != pvname:
        if f"{setpoint_pvname}_RBV" == pvname:
            # We handle pvproperty-with-RBV here directly:
            cls = "pvproperty_with_rbv"
            pvname = setpoint_pvname
        else:
            # But other cases get their own signal entirely:
            yield from convert_signal(
                cpt=cpt,
                attr=f"{attr}_setpoint",
                pvname=setpoint_pvname,
                setpoint_pvname=None,
                signal=signal,
                value=value,
                **kwargs
            )

    doc = cpt.doc or ""
    if "Component attribute" in doc:
        doc = ""

    if isinstance(signal, ro_signal_classes) and cls == "pvproperty":
        kwargs["read_only"] = True

    if kwargs:
        kwarg_str = ", " + ", ".join(f"{key}={value}" for key, value in kwargs.items())
    else:
        kwarg_str = ""

    yield f"""    {attr} = {cls}(name="{pvname}", value={value}, doc={doc!r}{kwarg_str})"""


def find_record_by_suffix(
    db: whatrecord.db.Database,
    suffix: str,
    all_pvnames: List[str]
) -> Optional[whatrecord.db.RecordInstance]:
    """
    Get the most-likely matching record from a provided Database.

    Parameters
    ----------
    db : Database
        The whatrecord database.

    suffix : str
        The PV suffix.

    all_pvnames : str
        Other PV suffixes that may be used to determine the most likely
        record.
    """
    by_prefix = {}
    for pv in all_pvnames:
        for name, instance in db.records.items():
            if name.endswith(pv):
                prefix = name[: -len(pv)]
                by_prefix.setdefault(prefix, {})[pv] = instance

    items = list(by_prefix.items())
    items.sort(key=lambda kv: len(kv[1]), reverse=True)

    # Pick the most likely one based on other matching PVs
    for prefix, match_to_instance in items:
        if suffix in match_to_instance:
            return match_to_instance[suffix]


def info_from_db(
    db: whatrecord.db.Database,
    suffix: str,
    all_pvnames: List[str]
) -> Dict[str, Any]:
    """
    Get pvproperty instantiation information from a whatrecord database.

    Parameters
    ----------
    db : Database
        The whatrecord database.

    suffix : str
        The PV suffix.

    all_pvnames : str
        Other PV suffixes that may be used to determine the most likely
        record.
    """
    record = find_record_by_suffix(db, suffix, all_pvnames)
    if not record:
        return dict(value=0)

    def get_fields(field_names: List[str]):
        result = []
        for field in field_names:
            if field in record.fields:
                field = cast(whatrecord.db.RecordField, record.fields[field])
                result.append(field.value)
            else:
                result.append("")

        while result and result[-1] == "":
            result = result[:-1]
        return result

    # read_only =
    if record.record_type in ("bi", "bo"):
        return dict(
            value=0,
            dtype="ChannelType.ENUM",
            enum_strings=list(get_fields(["ZNAM", "ONAM"])),
        )

    if record.record_type in ("mbbi", "mbbo"):
        return dict(
            value=0,
            dtype="ChannelType.ENUM",
            enum_strings=get_fields(
                "ZRST ONST TWST THST FRST FVST SXST SVST EIST NIST TEST ELST TVST TTST FTST FFST".split()
            ),
        )

    if record.record_type in ("ai", "ao"):
        (precision,) = get_fields(["PREC"]) or ["0"]
        return dict(value=0.0, precision=precision)

    if record.record_type in ("stringin", "stringout"):
        return dict(value='""', max_length=40)

    if record.record_type in ("waveform",):
        ftvl, nelm = get_fields(["FTVL", "NELM"])
        if ftvl == "CHAR":
            return dict(
                value='""',
                max_length=nelm if nelm else 40,
            )

        return dict(
            value='[0]',
            dtype=f"ChannelType.{ftvl}",
            max_length=nelm if nelm else 40,
        )

    return dict(value=0)


def convert_class(db: whatrecord.db.Database, cls: Type[ophyd.Device]):
    """
    Convert an ophyd class to a caproto PVGroup given an EPICS database.

    Parameters
    ----------
    db : Database
        The parsed whatrecord database.

    cls : ophyd.Device class
        The ophyd device class to convert.
    """
    try:
        inst = cls(prefix="{{prefix}}", name="")
    except Exception as ex:
        logger.warning(f"Can't convert: {cls.__name__}: {ex}")
        return

    ignored_bases = [
        "LightpathMixin",
        "Positioner",
        "InOutPositioner",
        "InOutPVStatePositioner",
    ]
    bases = list(
        base.__name__ for base in cls.__bases__ if base.__name__ not in ignored_bases
    )
    if "Device" in bases:
        idx = bases.index("Device")
        bases[idx] = "PVGroup"
    else:
        bases.append("PVGroup")

    base_names = ", ".join(bases)
    print(f"\n\nclass {cls.__name__}({base_names}):")
    for dev in inst._sub_devices:
        print(dev)
        raise RuntimeError("TODO")

    all_pvnames = [
        sig.pvname.replace("{{prefix}}", "")
        for sig in inst._signals.values()
        if hasattr(sig, "pvname")
    ]

    non_inherited_components = {
        attr for attr, cpt in cls.__dict__.items() if isinstance(cpt, ophyd.Component)
    }

    converted_signals = []
    signals_to_convert = [
        (attr, sig, sig.pvname.replace("{{prefix}}", ""))
        for attr, sig in inst._signals.items()
        if hasattr(sig, "pvname") and attr in non_inherited_components
    ]

    for attr, sig, pvname in signals_to_convert:
        setpoint_pvname = getattr(sig, "setpoint_pvname", None)
        if setpoint_pvname is not None:
            setpoint_pvname = setpoint_pvname.replace("{{prefix}}", "")
        cpt = getattr(cls, attr)
        db_info = info_from_db(db, pvname, all_pvnames)
        converted_signals.extend(
            list(
                convert_signal(
                    cpt,
                    attr,
                    pvname,
                    setpoint_pvname,
                    sig,
                    **db_info
                )
            )
        )

    if not converted_signals:
        print("    ...")
    else:
        print("\n".join(converted_signals))


def convert_from_ophyd(import_name: str, database_name: str):
    """
    Takes a Python module name with ophyd Devices, import it, and converts the
    found Devices to caproto PVGroups.

    Parameters
    ----------
    import_name : str
        The module name.

    database_name : str
        Path to an EPICS database file.
    """
    print("# Automatically converted from: ")
    print(f"# Module: {import_name}")
    print(f"# Database: {database_name}")
    print()
    print("from caproto import ChannelType")
    print("from caproto.server import PVGroup, SubGroup, pvproperty")
    print()
    print("from .utils import pvproperty_with_rbv")

    module = importlib.import_module(import_name)

    try:
        db = cast(
            whatrecord.Database,
            whatrecord.parse(database_name),
        )
    except lark.exceptions.UnexpectedToken:
        logger.debug("Falling back to interpret the database as an EPICS v3 database...")
        db = cast(
            whatrecord.Database,
            whatrecord.parse(database_name, v3=True),
        )

    seen = set()
    to_check = list(
        obj for _, obj in inspect.getmembers(module) if inspect.isclass(obj)
    )
    classes = []

    while to_check:
        cls = to_check.pop(0)
        if cls in seen:
            continue

        if cls is not ophyd.Device and issubclass(cls, ophyd.Device):
            seen.add(cls)
            for base in cls.__bases__:
                to_check.append(base)
            classes.append(cls)

    converted = set()

    def recursively_convert(cls):
        if cls in converted:
            return

        for base in cls.__bases__:
            if base in classes:
                recursively_convert(base)

        if cls in converted:
            return

        converted.add(cls)
        convert_class(db, cls)

    for cls in classes:
        recursively_convert(cls)


def create_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("import_name", type=str, help="Full import name")
    parser.add_argument(
        "database_name", type=str, help="Sample database file with similar components"
    )
    return parser


def main():
    parser = create_arg_parser()
    args = parser.parse_args()
    convert_from_ophyd(args.import_name, args.database_name)


if __name__ == "__main__":
    main()
