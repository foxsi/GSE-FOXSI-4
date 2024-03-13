"""
Create a class that will read the LOG file containing raw binary data received from 
FOXSI and parse the data to be readyfor the GUI plotting windows. 

Can read:
    * Timepix
"""
from FoGSE.readers.BaseReader import BaseReader

from FoGSE.readBackwards import BackwardsReader
from FoGSE.parsers.Timepixparser import timepix_parser
from FoGSE.collections.TimepixCollection import TimepixCollection
from FoGSE.utils import get_frame_size, get_system_value

class TimepixReader(BaseReader):
    """
    Reader for the FOXSI Timepix instrument.
    """

    def __init__(self, datafile, parent=None):
        """
        Raw : binary
        Parsed : human readable
        Collected : organised by intrumentation
        """
        BaseReader.__init__(self, datafile, parent)
        
        self.define_buffer_size(size=5) # bytes, get_frame_size("timepix", "tpx")
        self.call_interval(get_system_value("gse", "display_settings", "timepix", "tpx", "readers", "read_interval"))

    def extract_raw_data(self):
        """
        Method to extract the data from `self.data_file` and return the 
        desired data.

        Returns
        -------
        `list` :
            Data read from `self.data_file`.
        """
        return self.extract_raw_data_timepix()
    
    def extract_raw_data_timepix(self):
        """
        Method to extract the CdTe data from `self.data_file` and return the 
        desired data.

        Returns
        -------
        `list` :
            Data read from `self.data_file`.
        """
        # read the file `self.bufferSize` bytes from the end and extract the lines
        # forward=True: reads buffer from the back but doesn't reverse the data 
        try:
            with BackwardsReader(file=self.data_file, blksize=self.buffer_size, forward=True) as f:
                datalist = f.read_block()
                
            if self._old_data==datalist:
                return self.return_empty() 
        except FileNotFoundError:
            return self.return_empty() 
        
        self._old_data = datalist
        return datalist

    def raw_2_parsed(self, raw_data):
        """
        Method to check if there is enough data in the file to continue.

        Parameters
        ----------
        raw_data : list of strings
            The lines from the content of `self.data_file` obtained using 
            `FoGSE.readBackwards.BackwardsReader`.

        Returns
        -------
        `tuple` :
            Output from the CdTe parser.
        """
        # return or set human readable data
        # do stuff with the raw data and return nice, human readable data
        try:
            tot, flx, flgs = timepix_parser(raw_data)
        except ValueError:
            # no data from parser so pass nothing on with a time of -1
            print("No data from parser.")
            tot, flx, flgs = (None,None,None)
        return tot, flx, flgs

    def parsed_2_collection(self, parsed_data):
        """
        Method to move the parsed data to the relevant collection.

        Parameters
        ----------
        parsed_data : `tuple`
            Output from the CdTe parser.

        Returns
        -------
        `FoGSE.detector_collections.CdTeCollection.CdTeCollection` :
            The CdTe collection.
        """
        # take human readable and convert and set to 
        # CdTeCollection(), TimePixCollection(), CMOSCollection()
        col = TimepixCollection(parsed_data, 0)#self.old_data_time) #replace the old data time with 0 to allow even old data trhough if it gets to this stage (come back to this!)

        # if col.last_data_time>self.old_data_time:
        #     self.old_data_time = col.last_data_time
        return col