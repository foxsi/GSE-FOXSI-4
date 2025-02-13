"""
Create a class that will read the LOG file containing raw binary data received from 
Formatter Ping messages
"""

from FoGSE.readers.BaseReader import BaseReader

from FoGSE.readBackwards import BackwardsReader
from FoGSE.telemetry_tools.parsers.Pingparser import pingparser
from FoGSE.telemetry_tools.collections.PingCollection import PingCollection
from FoGSE.utils import get_frame_size, get_system_value

class PingReader(BaseReader):
    """
    Reader for Formatter Ping messages.
    """

    def __init__(self, datafile, parent=None):
        """
        Raw : binary
        Parsed : human readable
        Collected : organised by intrumentation
        """
        BaseReader.__init__(self, datafile, parent)
        
        self.define_buffer_size(size=get_frame_size("housekeeping", "ping")) # 46 bytes
        self.call_interval(get_system_value("gse", "display_settings", "housekeeping", "pow", "readers", "read_interval"))

    def extract_raw_data(self):
        """
        Method to extract the data from `self.data_file` and return the 
        desired data.
        """
        return self.extract_raw_data_ping()
    
    def extract_raw_data_ping(self):
        """
        Method to extract the Ping data from `self.data_file` and return the 
        desired data.
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
            Output from the parser.
        """
        # return or set human readable data
        # do stuff with the raw data and return nice, human readable data
        try:
            output, error_flag = pingparser(raw_data)
        except ValueError:
            # no data from parser so pass nothing on with a time of -1
            print("No data from Pingparser.")
            output, error_flag = ({'unixtime':None, 'global_errors_int': None,
                                   0:None, 1:None, 2:None, 3:None, 4:None, 5:None, 6:None, 7:None, 
                                   8:None, 9:None, 10:None, 11:None, 12:None, 13:None, 14:None, 15:None},
                                   None)
        return output, error_flag

    def parsed_2_collection(self, parsed_data):
        """
        Method to move the parsed data to the relevant collection.

        Parameters
        ----------
        parsed_data : `tuple`
            Output from the Ping parser.

        Returns
        -------
        `FoGSE.telemetry_tools.collections.PingCollection.PingCollection` :
            The Ping collection.
        """
        # take human readable and convert and set to 
        # CdTeCollection(), TimePixCollection(), CMOSCollection()
        col = PingCollection(parsed_data, self.old_data_time)
        # if col.last_data_time>self.old_data_time:
        #     self.old_data_time = col.last_data_time
        # if not hasattr(self,"data_start_time"):
        #     self.data_start_time = col.output['unixtime'][0]
        return col