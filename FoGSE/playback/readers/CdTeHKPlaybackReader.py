"""
Create a class that will read the LOG file containing raw binary data received from 
FOXSI and parse the data to be readyfor the GUI plotting windows. 

Can read:
    * CdTe
"""

from FoGSE.readers.CdTeHKReader import CdTeHKReader

from FoGSE.readBackwards import BackwardsReader
from FoGSE.utils import get_frame_size

class CdTeHKPlaybackReader(CdTeHKReader):
    """
    Reader for the FOXSI CdTe instrument.
    """

    def __init__(self, datafile, parent=None):
        """
        Raw : binary
        Parsed : human readable
        Collected : organised by intrumentation
        """

        if datafile is None:
            return

        CdTeHKReader.__init__(self, datafile, parent)

        self.frame_size = get_frame_size("cdte1", "hk") # 796 bytes
        self.frame_counter = 0

        self.define_buffer_size(size=0) # read whole file
        self.call_interval(1000)

    def file_modified_check(self):
        """ 
        No need to check for file updates.
        Just skip this from `FoGSE.readers.BaseReader.BaseReader`.
        """
        return True
    
    def extract_raw_data_cdtehk(self):
        """
        Method to extract the CdTe data from `self.data_file` and return the 
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
