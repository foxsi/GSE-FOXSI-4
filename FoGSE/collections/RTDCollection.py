"""
RTD collection to handle the read-in RTD data.
"""

# from copy import copy 

import numpy as np
# from numpy.lib import recfunctions as rfn
# import matplotlib.pyplot as plt

from FoGSE.parsers.temp_parser import numpy_struct


class RTDCollection:
    """
    A container for RTD data after being parsed.
    
    Can be used to generate time series plots.
    
    Paramters
    ---------
    parsed_data : `tuple`, length 2
            Contains `df_values, `df_errors` as returned from the parser.

    parsed_data : `int`, `float`
            The last time of the last data point previously extracted and 
            used. Default is `0` and so should take all data.
            Default: 0
            
    Example
    -------
    ...
    """
    
    def __init__(self, parsed_data, old_data_time=0):
        # bring in the parsed data
        self.event, _ = parsed_data

        # filter data to only include the new stuff
        self.last_data_time = old_data_time
        self.new_entries = self.event['ti']>self.last_data_time
        self.last_data_time = self.event['ti'][-1]

        # collect new data
        self.new_data = self.slice_numpy_struct(self.event, self.new_entries)

    def slice_numpy_struct(self, old_struct, bool_indices):
        """
        Function to indexlice a numpy structured array.
        
        Parameters
        ----------
        old_struct : `numpy.ndarray`
            The structured array with all data.

        bool_indices : `list` of `bool`
            List of indices to keep. Same length as `old_struct`.

        Returns
        -------
        `numpy.ndarray` : 
            Filtered down `old_struct`.
        """

        df = numpy_struct(sensor_value_fmt='f4', num=np.sum(bool_indices))

        for t in df.dtype.names:
            df[t] = old_struct[t][bool_indices]

        return df