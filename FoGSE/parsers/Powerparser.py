
import os.path
import numpy as np
# todo: possibly roll raw MAX7317 readout into this raw stream as well?

def adcparser(bytes_to_parse: bytes):
    """
    Parse ADC measurements of voltage and current into a `numpy.ndarray`.

    Paramaters
    ----------
    bytes_to_parse : `bytes`
        A raw data frame output by the Housekeeping board. Raw data is 6 bytes 
        of header data, followed by 16 2-byte long samples concatenated 
        (38 bytes total, or a multiple of 38).
        Data is taken from the AD7490 multiplexed ADC: 
        https://www.analog.com/en/products/ad7490.html.
        First 4 bits are channel number. Next 12 bits are raw data for that channel.

    Returns
    -------
    `numpy.ndarray` : 
        an n-by-16 block of raw data. First 4 columns are voltage
        measurements, next 12 are current measurements. Header describes
        physical measurement.
    """
    
    frame_size = 38
    frame_count = len(bytes_to_parse) // frame_size
    error = False
    dt = np.dtype({'names':('source', 'unixtime', 'adc_channel', 'measurement'),
                   'formats':('u1', 'u4', '(16,)u1', '(16,)f4')}) # u1==np.uint8,u4==np.uint32,i4==int32,f4==float32
    df = np.zeros(frame_count, dtype=dt)

    if len(bytes_to_parse) % frame_size != 0:
        print("Housekeeping power frames are 38 bytes long! Cannot parse from a different block size.")
        error = True
        return error, df

    frames = [bytes_to_parse[i:i+frame_size] for i in range(0,len(bytes_to_parse), frame_size)]

    for i,frame in enumerate(frames):
        source_system = frame[0]
        format_time = int.from_bytes(frame[2:6], "big")
        channel_data = [int.from_bytes(frame[i:i+2], "big") for i in range(6,len(frame), 2)]

        raw_5v_src = int.from_bytes(frame[12:14], "big", signed=False)
        channel_5v = raw_5v_src >> 12
        if channel_5v != 0x03:
            print("5 V measurement channel is in the wrong place! Got ", hex(channel_5v))
            error = True
            return error, df
        
        ref_5v = 5.0        # [V] reference input voltage for ADC scale
        current_gain = 0.2  # [V/A] current-to-voltage gain for Hall-effect sensors
        
        # note that last measured on-board, as-built value was 5.36 V for 5 V supply. This 
        # matches nicely with a coefficient of 1.68.
        divider_coefficients = [9.2, 4.0, 4.0, 1.68]
        measured_5v = divider_coefficients[3] * ref_5v * (raw_5v_src & 0x0fff) / 0x0fff
        
        channel_numbers = [0]*len(channel_data)
        channel_measurements = [0.0]*len(channel_data)
        for raw in channel_data:
            ch = raw >> 12
            channel_numbers[ch] = ch
            this_ratiometric = ref_5v * (raw & 0x0fff) / 0x0fff
            if ch < 4:
                if ch == 0x03:
                    channel_measurements[ch] = measured_5v
                else:
                    channel_measurements[ch] = divider_coefficients[ch] * this_ratiometric
            else:
                channel_measurements[ch] = (this_ratiometric - measured_5v/2) / current_gain

        df[i]["source"] = source_system
        df[i]["unixtime"] = format_time
        df[i]["adc_channel"] = channel_numbers
        df[i]["measurement"] = channel_measurements
    
    # print(df)
    return error,df

if __name__ == "__main__":
    testfile = "logs/received/23-1-2024_10:32:8/housekeeping_pow.log"
    with open(testfile, "rb") as f:
        data = f.read()
        adcparser(data)