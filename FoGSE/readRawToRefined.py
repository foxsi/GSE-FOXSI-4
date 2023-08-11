"""
Create a class that will read the LOG file containing raw binary data received from 
FOXSI and parse the data to be readyfor the GUI plotting windows. 

There will be two main operations of this class with the class managing the communication 
between them.

1. The class will read the LOG file with the raw binary data collected from FOXSI and pass 
the raw data to the instrument parsers which return the data as physical units in a human 
readable format.

2. Take the human readable data format (event lists, arrays, etc.) and organise the data 
into general instrument collections (i.e., one for all CdTe data, one for TimePix, one for 
CMOS). Individual GUI display windows, to which this class will be passed to, will monitor 
their relevant collections (being connected through `QtCore.pyqtSignal`) and request these 
collection objects to be displayed.

One class is assigned to do both jobs since (at this time) we will always want to go from raw
binary data to a collected, human readable form for investigation and analysis.
"""

import time
import struct

import numpy as np
from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication, QWidget

from FoGSE.readBackwards import BackwardsReader, read_raw_cdte
from FoGSE.parsers.CdTerawalldata2parser import CdTerawalldata2parser

class Reader(QWidget):
    # need to be class variable to connect
    value_changed_collections = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        """
        Raw : binary
        Parsed : human readable
        Collected : organised by intrumentation
        """
        QWidget.__init__(self, parent)

        # self._raw_data = []
        # self._parsed_data = []

        self._collections = []

        # stand-in log file
        self.data_file = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/minami-raw2parser/am241_1hr_20230612c_det01_00006_001"
        self._old_data = 0

        # for timing tests
        self.start = time.time()

        # default is update plot every 100 ms
        self.call_interval()
        # read 50,000 bytes from the end of `self.data_file` at a time
        self.buffer_size = 50_000

        self.setup_and_start_timer()

    def call_interval(self,call_interval=1000):
        self._call_interval = call_interval
        if hasattr(self,"timer"):
            self.timer.stop()
        self.setup_and_start_timer()

    def setup_and_start_timer(self):
        self.timer = QtCore.QTimer()
        self.timer.setInterval(self._call_interval) # fastest is every millisecond here, with a value of 1
        self.timer.timeout.connect(self.raw_2_collected) # call self.update_plot_data every cycle
        self.timer.start()

    @property
    def collections(self):
        return self._collections

    @collections.setter
    def collections(self, new_collections):
        self._collections = new_collections
        self.value_changed_collections.emit()

    def check_enough_data(self, lines):
        """
        Method to check if there is enough data in the file to continue.

        Parameters
        ----------
        lines : list of strings
            The lines from the content of `self.data_file` obtained using 
            `FoGSE.readBackwards.BackwardsReader`.

        Returns
        -------
        `bool` :
            Boolean where True means there is enough data to plot and False 
            means there is not.
        """
        if (lines==[]) or (len(lines)<3):
            return False # empty x, y
        return True

    def return_empty(self):
        """
        Define what should take the place of the data if the file is either 
        empty or doesn't have anything new to plot.
        """
        return []

    def extract_raw_data(self):
        """
        Method to extract the data from `self.data_file` and return the 
        desired data.

        Returns
        -------
        `tuple` :
            (x, y) The new x and y coordinates read from `self.data_file`.
        """
        # read the file `self.bufferSize` bytes from the end and extract the lines
        # forward=True: reads buffer from the back but doesn't reverse the data 
        try:
            with BackwardsReader(file=self.data_file, blksize=self.buffer_size, forward=True) as f:
                iterative_unpack=struct.iter_unpack("<I",f.read_block())
                datalist=[]
                for _,data in enumerate(iterative_unpack):

                    datalist.append(data[0])
            if self._old_data==datalist:
                return self.return_empty() 
        except FileNotFoundError:
            return self.return_empty() 
        
        self._old_data = datalist
        return datalist

    def raw_2_parsed(self, raw_data):
        # return or set human readable data
        # do stuff with the raw data and return nice, human readable data
        flags, event_df, all_hkdicts = CdTerawalldata2parser(raw_data)
        return flags, event_df, all_hkdicts

    def parsed_2_collections(self, parsed_data):
        # take human readable and convert and set to 
        # CdTeCollection(), TimePixCollection(), CMOSCollection()
        return CdTeCollection(parsed_data)

    def raw_2_collected(self):
        raw = self.extract_raw_data()

        if raw!=self.return_empty():
            parsed = self.raw_2_parsed(raw)

            # assign the collected data and trigger the `emit`
            self.collections = self.parsed_2_collections(parsed)


class CdTeCollection:
    def __init__(self, parsed_data):
        _, self.event_dataframe, _ = parsed_data
        
        self.strip_bins, self.side_strip_bins, self.adc_bins = self.channel_bins()
        
        self.channel_map = self.remap_strip_dict()
        
        self.f_data = self.filter_(event_dataframe=self.event_dataframe)
        
        self.strip_width_edges = self.strip_widths()
        self.pixel_area = self.pixel_areas()

        self.last_data_time = 0

    def filter_(self, event_dataframe):
        trig_times = []
        pt_strip_adc, al_strip_adc = [], []
        pt_strips, al_strips = [], []
        for i in range(len(event_dataframe['index_pt'])):

            time = event_dataframe['time'][i][0]
            if (time<=self.last_data_time):
                continue

            pt = np.array(event_dataframe['index_pt'][i])
            al = np.array(event_dataframe['index_al'][i])+128
            pt_adc = np.array(event_dataframe['adc_cmn_pt'][i])
            al_adc = np.array(event_dataframe['adc_cmn_al'][i])

            pt_min_adc = np.min(pt_adc)
            al_min_adc = np.min(al_adc)
            
            pt_selection = ((pt<59) | (pt>68)) & (pt_adc>2*abs(pt_min_adc))
            al_selection = ((al>131) & (al<252)) & (al_adc>2*abs(al_min_adc))
            
            pt_strip = pt[pt_selection]
            al_strip = al[al_selection]
            pt_value = pt_adc[pt_selection]
            al_value = al_adc[al_selection]

            # choose single strip events
            if ((len(pt_strip))==(len(al_strip))==1):
                trig_times.append(time)
                pt_strip_adc.append(pt_value)
                al_strip_adc.append(al_value)
                pt_strips.append(pt_strip[0])
                al_strips.append(al_strip[0])
                # print(trig_times, pt_adc, al_adc, pt_strips, al_strips)
        
        self.last_data_time = trig_times[-1]
        return {'times':trig_times, 
                'pt_strip_adc':pt_strip_adc, 
                'al_strip_adc':al_strip_adc, 
                'pt_strips':np.array(pt_strips), 
                'al_strips':np.array(al_strips)-128}
    
    def channel_bins(self):
        strip_bins = np.arange(257)-0.5
        side_strip_bins = np.arange(129)-0.5
        adc_bins = np.arange(1025)-0.5

        return strip_bins, side_strip_bins, adc_bins
    
    def spectrogram(self):
        """ 
        Spectrogram? 
        
        In space, not time though. Don't think that matters but will 
        someone get annoyed though? 
        """
        pt_strips = np.ndarray.flatten(self.event_dataframe['index_pt'])
        al_strips = np.ndarray.flatten(self.event_dataframe['index_al'])+128
        all_strips = np.concatenate((pt_strips, al_strips))
        
        pt_adc = np.ndarray.flatten(self.event_dataframe['adc_cmn_pt'])
        al_adc = np.ndarray.flatten(self.event_dataframe['adc_cmn_al'])
        all_adc = np.concatenate((pt_adc, al_adc))
        
        self.adc_counts_arr, _, _ = np.histogram2d(all_strips, all_adc, 
                                                   bins=[self.strip_bins,
                                                         self.adc_bins])
        
    def plot_spectrogram(self, v:(float,int)=None, remap:bool=False):
        """
        Method to plot the spectrogram of the CdTe file.

        Parameters
        ----------
        v : `float`, `int`
            Maximum value for the histrogram colourbar.
            
        v : `bool`
            Set to `True` to remap the strip channels to their physical 
            orientation.

        Returns
        -------
        `matplotlib.collections.QuadMesh` :
            The object which hold the plot.
        """
        
        self.spectrogram()
        
        counts = self.remap_strips(counts=self.adc_counts_arr) if remap else self.adc_counts_arr
        
        v = 0.8*np.max(counts) if v is None else v
        
        counts[counts<=0] = np.nan
        
        pc = plt.pcolormesh(self.strip_bins, 
                            self.adc_bins, 
                            counts.T, 
                            vmin=0, 
                            vmax=v)
        plt.ylabel("ADC [common mode subtracted]")
        plt.xlabel("Strip [Pt: 0-127, Al: 128-255]")
        plt.colorbar(label="Counts")
        plt.title(f"Spectrogram: CMN Subtracted, Re-map={remap}")
        
        return pc
    
    def image(self, remap=True):
        pt_strips = self.f_data.get('pt_strips', None)
        al_strips = self.f_data.get('al_strips', None)
        
        if remap:
            pt_strips, al_strips = self._remap_strip_values(pt_strips, al_strips)
        
        im, _, _ = np.histogram2d(pt_strips, 
                                  al_strips, 
                                  bins=[self.side_strip_bins,
                                        self.side_strip_bins])
        return im
    
    def _remap_strip_values(self, pt_strips, al_strips):
        rpt_strips, ral_strips = [],[]
        for c in range(len(pt_strips)):
            rpt_strips.append(self.channel_map[pt_strips[c]])
            ral_strips.append(self.channel_map[al_strips[c]+128])
        return np.array(rpt_strips), np.array(ral_strips)-128
    
    def _area_correction(self, image, area_correction):
        image /= self.pixel_area
        return image
    
    def image_array(self, area_correction=True):

        im = self.image(remap=remap)
        if area_correction:
            return self._area_correction(im, area_correction=area_correction)
        return im
    
    def plot_image(self, remap=True, area_correction=True, non_uniform_pixels=True):

        im = self.image_array(area_correction=area_correction)
        
        if non_uniform_pixels:
            i = plt.pcolormesh(self.strip_width_edges, 
                               self.strip_width_edges, 
                               im, 
                               rasterized=True)
            u = " [$\mu$m]"
        else:
            i = plt.imshow(im, 
                           rasterized=True, 
                           origin="lower")
            u = " [strip]"
        plt.xlabel("Al"+u)
        plt.ylabel("Pt"+u)
        plt.title(f"Image: Counts, Re-map={remap}")
        
        return i
    
    def remap_strip_dict(self):
        """ May be removed. """
        original_channels = np.arange(256)

        new_channels = copy(original_channels)

        asic0_inds = original_channels<64
        asic1_inds = (64<=original_channels)&(original_channels<128)
        asic2_inds = (128<=original_channels)&(original_channels<192)
        asic3_inds = 192<=original_channels

        new_channels[asic0_inds] = original_channels[asic0_inds][::-1]
        new_channels[asic1_inds] = original_channels[asic1_inds][::-1]
        new_channels[asic2_inds] = original_channels[asic3_inds][::-1]
        new_channels[asic3_inds] = original_channels[asic2_inds][::-1]

        return dict(zip(original_channels, new_channels))
    
    def reverse_rows(self, arr):
        return arr[::-1,:]

    def remap_strips(self, counts):
        asic0 = counts[:64,:]
        asic1 = counts[64:128,:]
        asic2 = counts[128:192,:]
        asic3 = counts[192:,:]

        asic0_rmap = self.reverse_rows(asic0)
        asic1_rmap = self.reverse_rows(asic1)
        asic2_rmap = self.reverse_rows(asic2)
        asic3_rmap = self.reverse_rows(asic3)

        return np.concatenate((asic0_rmap, asic1_rmap, asic3_rmap, asic2_rmap), axis=0)
    
    def strip_widths(self):
        C = np.arange(29)*100 # ignore channel 28 just now

        B = np.arange(20)*80 

        A = np.arange(16)*60
        
        new_B = B + C[-1] + 50 + 40 # add last value from (C) then half a bin in (C) and half one in (B)
        
        new_A = A + new_B[-1] + 40 + 30
        
        right_A = A[:-1] + new_A[-1] + 60
        right_B = B + right_A[-1] + 30 + 40
        right_C = C + right_B[-1] + 40 + 50
        
        edges = np.concatenate((C,new_B,new_A,right_A,right_B,right_C))
        
        return edges
    
    def pixel_areas(self):
        return np.diff(self.strip_width_edges)[:,None]@np.diff(self.strip_width_edges)[None,:]
    


    
    
class fake_window:
    def __init__(self, i, reader):

        self.reader = reader

        self.reader.value_changed_collections.connect(self.check_reader)

        self.i = i

    def check_reader(self):
        # stand-in for update plot window method
        # connect as self.reader.value_changed_collections.connect(self.check_reader)
        print(self.i, self.reader.collections, "\n\n")


if __name__=="__main__":
    app = QApplication([])

    R = Reader()

    f0 = fake_window("f0", R)

    app.exec()