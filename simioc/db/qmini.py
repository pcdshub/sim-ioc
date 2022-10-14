from caproto import ChannelType
from caproto.server import PVGroup, pvproperty

from .utils import pvproperty_with_rbv


class QminiSpectrometer(PVGroup):
    status = pvproperty(
        name=":STATUS",
        value=0,
        doc="",
        dtype=ChannelType.ENUM,
        enum_strings=[
            "Idle",
            "Waiting For Trig",
            "TakingSpectrum",
            "Waiting for Temp",
            "Not Ready",
            "Busy",
            "Error",
            "Closed",
        ],
        read_only=True,
    )
    temperature = pvproperty(
        name=":TEMP", value=0.0, doc="", precision=0, read_only=True
    )
    exposure_setpoint = pvproperty(name=":SET_EXPOSURE_TIME", value=0, doc="")
    exposure = pvproperty(name=":GET_EXPOSURE_TIME", value=0, doc="")
    trig_mode = pvproperty_with_rbv(
        name=":TRIG_MODE",
        value=0,
        doc="",
        dtype=ChannelType.ENUM,
        enum_strings=["Trigger On Start", "Trigger On End"],
    )
    trig_delay_setpoint = pvproperty(name=":SET_TRIG_DELAY", value=0, doc="")
    trig_delay = pvproperty(name=":GET_TRIG_DELAY", value=0, doc="")
    trig_pin_setpoint = pvproperty(
        name=":SET_TRIG_PIN",
        value=0,
        doc="",
        dtype=ChannelType.ENUM,
        enum_strings=["Pin 0", "Pin 1", "Pin 2", "Pin 3"],
    )
    trig_pin = pvproperty(
        name=":TRIG_PIN_RBV",
        value=0,
        doc="",
        dtype=ChannelType.ENUM,
        enum_strings=["Pin 0", "Pin 1", "Pin 2", "Pin 3"],
    )
    trig_edge_setpoint = pvproperty(
        name=":SET_TRIG_EDGE",
        value=0,
        doc="",
        dtype=ChannelType.ENUM,
        enum_strings=["Falling", "Rising"],
    )
    trig_edge = pvproperty(
        name=":TRIG_EDGE_RBV",
        value=0,
        doc="",
        dtype=ChannelType.ENUM,
        enum_strings=["Falling", "Rising"],
    )
    trig_enable_setpoint = pvproperty(
        name=":SET_TRIG_ENABLE",
        value=0,
        doc="",
        dtype=ChannelType.ENUM,
        enum_strings=["No", "Yes"],
    )
    trig_enable = pvproperty(
        name=":GET_TRIG_ENABLE",
        value=0,
        doc="",
        dtype=ChannelType.ENUM,
        enum_strings=["No", "Yes"],
    )
    scan_rate = pvproperty(name=":GET_SPECTRUM.SCAN", value=0, doc="")
    reset = pvproperty(name=":CLEAR_SPECTROMETER", value=0, doc="")
    spectrum = pvproperty(
        name=":SPECTRUM",
        value=[0],
        doc="",
        dtype=ChannelType.FLOAT,
        max_length=2500,
        read_only=True,
    )
    wavelengths = pvproperty(
        name=":WAVELENGTHS",
        value=[0],
        doc="",
        dtype=ChannelType.FLOAT,
        max_length=2500,
        read_only=True,
    )
    model = pvproperty(name=":MODEL_CODE", value=0, doc="", read_only=True)
    serial_number = pvproperty(name=":SERIAL_NUMBER", value=0, doc="", read_only=True)
    adjust_offset = pvproperty(
        name=":ADJUST_OFFSET",
        value=0,
        doc="",
        dtype=ChannelType.ENUM,
        enum_strings=["No", "Yes"],
    )
    correct_nonlinearity = pvproperty(
        name=":CORRECT_NONLINEARITY",
        value=0,
        doc="",
        dtype=ChannelType.ENUM,
        enum_strings=["No", "Yes"],
    )
    remove_bad_pixels = pvproperty(
        name=":REMOVE_BAD_PIXELS",
        value=0,
        doc="",
        dtype=ChannelType.ENUM,
        enum_strings=["No", "Yes"],
    )
    subtract_dark = pvproperty(
        name=":SUBTRACT_DARK",
        value=0,
        doc="",
        dtype=ChannelType.ENUM,
        enum_strings=["No", "Yes"],
    )
    remove_temp_bad_pixels = pvproperty(
        name=":REMOVE_TEMP_BAD_PIXELS",
        value=0,
        doc="",
        dtype=ChannelType.ENUM,
        enum_strings=["No", "Yes"],
    )
    normalize_exposure = pvproperty(
        name=":NORMALIZE_EXPOSURE",
        value=0,
        doc="",
        dtype=ChannelType.ENUM,
        enum_strings=["No", "Yes"],
    )
    sensitivity_cal = pvproperty(
        name=":SENSITIVITY_CAL",
        value=0,
        doc="",
        dtype=ChannelType.ENUM,
        enum_strings=["No", "Yes"],
    )
    correct_prnu = pvproperty(
        name=":CORRECT_PRNU",
        value=0,
        doc="",
        dtype=ChannelType.ENUM,
        enum_strings=["No", "Yes"],
    )
    additional_filtering = pvproperty(
        name=":ADDITIONAL_FILTERING",
        value=0,
        doc="",
        dtype=ChannelType.ENUM,
        enum_strings=["No", "Yes"],
    )
    scale_to_16_bit = pvproperty(
        name=":SCALE_TO_16BIT",
        value=0,
        doc="",
        dtype=ChannelType.ENUM,
        enum_strings=["No", "Yes"],
    )
    set_processing_steps = pvproperty(name=":SET_PROCESSING_STEPS", value=0, doc="")
    get_processing_steps = pvproperty(
        name=":GET_PROCESSING_STEPS", value=0, doc="", read_only=True
    )
    fit_on = pvproperty(
        name=":FIT_ON",
        value=0,
        doc="",
        dtype=ChannelType.ENUM,
        enum_strings=["No", "Yes"],
    )
    fit_width = pvproperty(name=":WIDTH", value=0, doc="")
    w0_guess = pvproperty(name=":W0_GUESS", value=0.0, doc="", precision=0)
    w0_fit = pvproperty(name=":W0_FIT", value=0.0, doc="", precision=0, read_only=True)
    fit_fwhm = pvproperty(name=":FWHM", value=0.0, doc="", precision=0, read_only=True)
    fit_amplitude = pvproperty(
        name=":AMPLITUDE", value=0.0, doc="", precision=0, read_only=True
    )
    fit_stdev = pvproperty(
        name=":STDEV", value=0.0, doc="", precision=0, read_only=True
    )
    fit_chisq = pvproperty(
        name=":CHISQ", value=0.0, doc="", precision=0, read_only=True
    )


class QminiWithEvr(QminiSpectrometer, PVGroup):
    event_code_setpoint = pvproperty(
        name="{evr_pv}:TRIG{evr_ch}:EC_RBV", value=0, doc=""
    )
    event_code = pvproperty(name="{evr_pv}:TRIG{evr_ch}:EC_RBV", value=0, doc="")
    evr_width_setpoint = pvproperty(
        name="{evr_pv}:TRIG{evr_ch}:BW_TWIDCALC", value=0, doc=""
    )
    evr_width = pvproperty(name="{evr_pv}:TRIG{evr_ch}:BW_TWIDCALC", value=0, doc="")
    evr_delay_setpoint = pvproperty(
        name="{evr_pv}:TRIG{evr_ch}:BW_TDES", value=0, doc=""
    )
    evr_delay = pvproperty(name="{evr_pv}:TRIG{evr_ch}:BW_TDES", value=0, doc="")
