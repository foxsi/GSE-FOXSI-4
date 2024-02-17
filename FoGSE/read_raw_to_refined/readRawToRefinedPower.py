"""
Create a class that will read the LOG file containing raw binary data received from 
FOXSI and parse the data to be readyfor the GUI plotting windows. 

Can read:
    * Power
"""

from FoGSE.read_raw_to_refined.readRawToRefinedBase import ReaderBase

from FoGSE.readBackwards import BackwardsReader
from FoGSE.parsers.Powerparser import adcparser
from FoGSE.collections.PowerCollection import PowerCollection


class PowerReader(ReaderBase):
    """
    Reader for the FOXSI power system.
    """

    def __init__(self, datafile, parent=None):
        """
        Raw : binary
        Parsed : human readable
        Collected : organised by intrumentation
        """
        ReaderBase.__init__(self, datafile, parent)
        # The magic number for Power is 38.
        self.define_buffer_size(size=38*2)
        self.call_interval(500)

    def extract_raw_data(self):
        """
        Method to extract the data from `self.data_file` and return the 
        desired data.

        Returns
        -------
        `list` :
            Data read from `self.data_file`.
        """
        return self.extract_raw_data_power()
    
    def extract_raw_data_power(self):
        """
        Method to extract the power data from `self.data_file` and return the 
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
                data = f.read_block()
            if self._old_data==data:
                print("found old!")
                return self.return_empty() 
        except FileNotFoundError:
            return self.return_empty() 
        
        self._old_data = data
        print(data.hex())
        return data

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
            Output from the power parser.
        """
        # return or set human readable data
        # do stuff with the raw data and return nice, human readable data
        try:
            error, data = adcparser(raw_data)
        except ValueError:
            # no data from parser so pass nothing on with a time of -1
            print("No data from parser.")
            error, data = (1,None)
        return error, data

    def parsed_2_collection(self, parsed_data):
        """
        Method to move the parsed data to the relevant collection.

        Parameters
        ----------
        parsed_data : `tuple`
            Output from the Power parser.

        Returns
        -------
        `FoGSE.detector_collections.PowerCollection.PowerCollection` :
            The Power collection.
        """
        # take human readable and convert and set to 
        # CdTeCollection(), TimePixCollection(), CMOSCollection()
        col = PowerCollection(parsed_data, self.old_data_time)
        if col.last_data_time != self.old_data_time:
            self.old_data_time = col.last_data_time
        return col