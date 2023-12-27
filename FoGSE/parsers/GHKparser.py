
def adcparser(bytes_to_parse: bytearray):
    """
    Parse ADC measurements of voltage and current into a `numpy.ndarray`.

    Paramaters
    ----------
    bytes_to_parse : `bytearray`
        A raw data frame output by the Housekeeping board. Raw data is 16 
        2-byte long samples concatenated (32 bytes total, or a multiple of 32).
        Data is taken from the AD7490 multiplexed ADC: 
        https://www.analog.com/en/products/ad7490.html.
        First 4 bytes are channel number. Next 12 bytes are raw data.

    Returns
    -------
    `numpy.ndarray` : 
        an n-by-16 block of raw data. First 4 columns are voltage
        measurements, next 12 are current measurements. Header describes
        physical measurement.
    """

    frame_size = 32
    if len(bytes_to_parse) % frame_size != 0:
        print("Housekeeping ADC frames are 32 bytes long! Cannot parse from a smaller block size.")
        except IndexError

    frame_count = len(bytes_to_parse) // frame_size

    for i in range(frame_count):
        for j in range(0, frame_size, 2):
            # index into the raw data:
            raw_index = j + i*frame_size

            # get a pair of bytes for a single channel's sample:
            this_raw_16b = int(bytes_to_parse[raw_index:raw_index+1], 16)
            # get channel number from the sample:
            this_channel = this_raw_16b >> 12
            # get measured voltage from the sample:
            this_measured_voltage = 5.0 * (this_raw_16b & 0x0fff) / 0x0fff
            # convert measured voltage to original physical quantity:
            this_physical = convert_to_physical(this_channel, this_measured_voltage)

            # todo:
            # would like to drop this into a dataframe or structured array now.
            
def convert_to_physical(channel: int, raw_value: float) -> float: 
    """
    Function to take a physical voltage measurement on an ADC channel
    and convert to a current or voltage value.
    
    Parameters
    ----------
    channel : `int`
        The channel number on the AD7490 that produced `raw_value`.
    
    raw_value: `float`
        The raw measurement (units voltage) from measured on the AD7490 pin.
        This value should already be normalized to ADC bit range and voltage 
        bounds.

    Returns
    -------
    `float` : 
        The source signal current or voltage value. This accounts for upstream 
        resistor dividers and Hall-effect sensors on the channel.
    """

    # the voltage-sensing channels each have a specific resistor divider to 
    # transform the source voltage into the ADC's measurement range.
    # These coefficients let you back-convert to the source voltage from
    # normalized ADC measurement.
    voltage_coefficients = [9.2, 4.0, 4.0, 1.68]

    if channel > 3:
        # the current-sensing channels
        return 5.0*(raw_value - 2.5)
    else:
        # the voltage-sensing channels
        return voltage_coefficients[channel]*raw_value
