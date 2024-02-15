"""
Timepix collection to handle the read-in RTD data.
"""

import numpy as np

class TimepixCollection:
    """
    A container for Timepix data after being parsed.
    
    Can be used to generate time series plots.
    
    Paramters
    ---------
    parsed_data : `tuple`, length 2
            Contains `df_values, `df_errors` as returned from the parser.

    old_data_time : `int`, `float`
            The last time of the last data point previously extracted and 
            used. Default is `0` and so should take all data.
            Default: 0
            NOT USED
            
    Example
    -------
    from FoGSE.parsers.Timepixparser import timepix_parser
    from FoGSE.collections.TimepixCollection import TimepixCollection

    # get the raw data and parse it
    tot, flx, flgs = timepix_parser(raw_data)

    # set to a single variable
    parsed_data = (tot, flx, flgs)

    # pass the parsed data to the collection
    col = TimepixCollection(parsed_data, 0)

    # to get the mean time-over-threshold, e.g., for the parsed data
    col.get_mean_tot()
    """
    
    def __init__(self, parsed_data, old_data_time=0):
        # bring in the parsed data
        self.mean_tot, self.flux, self.flags = parsed_data
        self.flags = []
        # # filter data to only include the new stuff
        # self.last_data_time = old_data_time
        # self.new_entries = self.event['ti']>self.last_data_time
        # self.last_data_time = self.event['ti'][-1]

    def get_mean_tot(self):
        """ Return the mean time-over-threshold. """
        return self.mean_tot
    
    def get_flux(self):
        """ Return the flux. """
        return self.flux

    def get_flags(self):
        """ Return the flags. """
        # assume no flags
        _flags_status = np.zeros(8).astype(int)

        # set the flag indices, if any, then set to one
        if len(self.flags)>0:
            _flags_status[np.array(self.flags)-1] = 1
            
        return '-'.join(map(str, self.flags))