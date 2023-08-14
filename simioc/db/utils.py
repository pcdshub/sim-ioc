from typing import Any

import numpy as np

from caproto import ChannelData, ChannelEnum
from caproto.server import get_pv_pair_wrapper

pvproperty_with_rbv = get_pv_pair_wrapper(
    setpoint_suffix="",
    readback_suffix="_RBV"
)


async def write_if_differs(data: ChannelData, value: Any) -> bool:
    """
    Write ``value`` to ``data`` if it differs from the existing value.
    """
    if value is None:
        return False

    try:
        value = data.preprocess_value(value)
    except Exception:
        ...

    if isinstance(data, ChannelEnum) and isinstance(value, int):
        value = data.enum_strings[value]

    if np.shape(value) or np.shape(data.value):
        if np.shape(value) == np.shape(data.value) and np.all(value == data.value):
            return False

        await data.write(value)
        return True

    if value != data.value:
        await data.write(value)
        return True
    return False
