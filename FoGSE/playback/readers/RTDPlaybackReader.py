"""
Create a class that will read the LOG file containing raw binary data received from 
the RTDs
"""

import numpy as np
from PyQt6.QtCore import QTimer

from FoGSE.readers.RTDReader import RTDReader

from FoGSE.readBackwards import BackwardsReader
from FoGSE.utils import get_frame_size

class RTDPlaybackReader(RTDReader):
    """
    Reader for the RTD readout.
    """

    def __init__(self, datafile, parent=None):
        """
        Raw : binary
        Parsed : human readable
        Collected : organised by intrumentation
        """
        RTDReader.__init__(self, datafile, parent)
        self.timer.stop()

        # 4 CdTe, 2 CMOS, 1 Timepix, 1 HK, so each gets 1/8 s
        delay = 7*125
        call_interval = 1_000
        self.delay_timer(delay, call_interval)
        
        self.frame_size = get_frame_size("housekeeping", "rtd")*2 # 84 bytes
        self.frame_counter = 0

        self.define_buffer_size(size=0) # read whole file
        self.call_interval(1000)

    def file_modified_check(self):
        """ 
        No need to check for file updates.
        Just skip this from `FoGSE.readers.BaseReader.BaseReader`.
        """
        return True
    
    def delay_timer(self, delay, call_interval):
        """ 
        Handles a delay in starting the `QTimer` to simulate data for 
        the readers coming in at different rates.

        Parameters
        ----------
        delay : `int`
            The delay before the new timer will start in milliseconds.

        call_interval : `int`
            The new timer's call interval.
        """
        self._delay_timer = QTimer()
        self._delay_timer.setSingleShot(True)
        self._delay_timer.setInterval(delay)
        self._delay_timer.timeout.connect(lambda : self.call_interval(call_interval))
        self._delay_timer.start()
    
    def extract_raw_data_rtd(self):
        """
        Method to extract the CdTe data from `self.data_file` and return the 
        desired data.

        Returns
        -------
        `tuple` :
            (x, y) The new x and y coordinates read from `self.data_file`.
        """
        if self.frame_counter==0:
            try:
                with BackwardsReader(file=self.data_file, blksize=self.buffer_size, forward=True) as f:
                    datalist = f.read_block()

                if self._old_data==datalist:
                    return self.return_empty() 
            except FileNotFoundError:
                return self.return_empty() 
            
            self.datalist = datalist
            self.frame_counter += 1
            return self.datalist[:self.frame_size]
        
        next_frame = self.datalist[self.frame_size*self.frame_counter:self.frame_size*(self.frame_counter+1)]
        self.frame_counter += 1
        return next_frame

    