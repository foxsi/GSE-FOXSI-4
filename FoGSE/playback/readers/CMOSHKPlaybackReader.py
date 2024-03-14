"""
Create a class that will read the LOG file containing raw binary data received from 
FOXSI and parse the data to be readyfor the GUI plotting windows. 

Can read:
    * CMOS PC
"""

import numpy as np
from PyQt6.QtCore import QTimer

from FoGSE.readers.CMOSHKReader import CMOSHKReader

from FoGSE.readBackwards import BackwardsReader
from FoGSE.utils import get_frame_size

class CMOSHKPlaybackReader(CMOSHKReader):
    """
    Reader for the FOXSI CMOS instrument.
    """

    def __init__(self, datafile, parent=None):
        """
        Raw : binary
        Parsed : human readable
        Collected : organised by intrumentation
        """

        if datafile is None:
            return
        
        CMOSHKReader.__init__(self, datafile, parent)
        self.timer.stop()

        # 4 CdTe, 2 CMOS, 1 Timepix, 1 HK, so each gets 1/8 s
        delay = np.random.randint(4,6)*125
        call_interval = 1_000
        self.delay_timer(delay, call_interval)

        self.frame_size = get_frame_size("cmos1", "hk") # 536 bytes
        self.frame_counter = 0
        
        self.define_buffer_size(size=0) # read whole file

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
    
    def extract_raw_data_cmos(self):
        """
        Method to extract the CMOS data from `self.data_file` and return the 
        desired data.

        Returns
        -------
        `list` :
            Data read from `self.data_file`.
        """
        if self.frame_counter==0:
            try:
                with BackwardsReader(file=self.data_file, blksize=self.buffer_size, forward=True) as f:
                    data = f.read_block()
                if self._old_data==data:
                    return self.return_empty() 
            except FileNotFoundError:
                return self.return_empty() 
        
            self.datalist = data
            self.frame_counter += 1
            return self.datalist[:self.frame_size]
        
        next_frame = self.datalist[self.frame_size*self.frame_counter:self.frame_size*(self.frame_counter+1)]
        self.frame_counter += 1
        return next_frame
