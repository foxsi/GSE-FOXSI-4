"""
CMOS collection to handle the read-in CMOS data.
"""

import numpy as np
import matplotlib.pyplot as plt


class CMOSHKCollection:
    
    def __init__(self, parsed_data, old_data_time=0):
        # bring in the parsed data
        self.linetime, self.gain_pc, self.exposure_pc, self._image = parsed_data
        
        # used in the filter to only consider data with times > than this
        self.last_data_time = old_data_time

        if not self.new_array():
            self._image = self.empty()

    def empty(self):
        """ Define what an empty return should be. """
        return np.zeros((384,768))
    
    def new_array(self):
        """ Check if the array is new or a repeat. """
        return True
        # previously was
        # if self.linetime>self.last_data_time:
        #     return True
        # return False
    
    def image_array(self):
        """
        Method to return the image array of the parser output.

        Returns
        -------
        `np.ndarray` :
            The image array.
        """
        im = self._image
        return im
    
    def plot_image(self):
        """
        Method to plot the image of the CMOS file.

        Returns
        -------
        `matplotlib.pyplot.imshow`:
            The object which holds the plot.
        """

        i = plt.imshow(self.image_array(), 
                       rasterized=True, 
                       origin="lower")
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.title("CMOS Image")
        
        return i
    
    def get_exposure(self):
        """ Return the exposure time of PC image. """
        return self.exposure_pc
    
    def get_gain(self):
        """ Return the exposure time of PC image. """
        return self.gain_pc