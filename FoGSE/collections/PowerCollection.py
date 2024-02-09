"""
Power collection to handle the read-in power data.
"""

import numpy as np
import matplotlib.pyplot as plt


class PowerCollection:
    """
    A container for power data after being parsed.
    
    Parameters
    ---------
    parsed_data : `tuple`, length 2
            Contains `error`, `data`, as returned from the parser.

    old_data_time : `int`, `float`
            The last time of the last data point previously extracted and 
            used. Default is `0` and so should take all data.
            Default: 0
            
    Example
    -------
    with BackwardsReader(file=self.data_file, blksize=self.buffer_size, forward=True) as f:
        data = f.read_block()
        error, data = Powerparser(raw_data)
        
    power_data = PowerCollection((error, data))
    
    plt.figure()
    power_data.plot_trace()
    plt.show()
    """
    
    def __init__(self, parsed_data, old_data_time=0):
        # bring in the parsed data
        self.error, self.data = parsed_data
        
        # used in the filter to only consider data with times > than this
        self.last_data_time = old_data_time
        if self.data["unixtime"][-1] > self.last_data_time:
            self.last_data_time = self.data["unixtime"][-1]

        # if not self.new_array():
        #     self._image = self.empty()

    def empty(self):
        """ Define what an empty return should be. """
        return np.zeros((16,))
    
    def new_array(self):
        """ Check if the array is new or a repeat. """
        if self.data["unixtime"][-1] > self.last_data_time:
            return True
        return False
    
    def image_array(self):
        """
        Method to return the image array of the parser output.

        Returns
        -------
        `np.ndarray` :
            The image array.
        """
        return self._image