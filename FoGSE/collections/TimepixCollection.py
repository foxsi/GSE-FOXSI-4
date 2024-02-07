"""
Timepix collection to handle the read-in RTD data.
"""


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
    ...
    """
    
    def __init__(self, parsed_data, old_data_time=0):
        # bring in the parsed data
        self.mean_tot, self.flux, self.flags = parsed_data

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
        return self.flags