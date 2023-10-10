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
from sys import getsizeof
from copy import copy 

import numpy as np
import matplotlib.pyplot as plt
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout

from FoGSE.readBackwards import BackwardsReader, read_raw_cdte
from FoGSE.parsers.CdTerawalldata2parser import CdTerawalldata2parser
from FoGSE.parsers.CdTerawalldata2parser_test import CdTerawalldata2parser_test

import pyqtgraph as pg

class Reader(QWidget):
    # need to be class variable to connect
    value_changed_collections = QtCore.pyqtSignal()

    def __init__(self, datafile, parent=None):
        """
        Raw : binary
        Parsed : human readable
        Collected : organised by intrumentation
        """
        QWidget.__init__(self, parent)

        self._collections = []

        # stand-in log file
        self.data_file = datafile
        self._old_data = 0
        self.old_data_time = 0

        # for timing tests
        self.start = time.time()

        # default is update plot every 100 ms
        self.call_interval()
        # read 50,000 bytes from the end of `self.data_file` at a time
        self.define_buffer_size(size=50_000)

        self.setup_and_start_timer()

    def define_buffer_size(self, size):
        if size%4!=0:
            new_size = int(int(size/4)*4)
            print(f"Buffer size must be divisable by 4 for parser code, changing to {new_size}.")
            self.buffer_size = new_size
        self.buffer_size = size

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
        return self.extract_raw_data_cdte()
    
    def extract_raw_data_cdte(self):
        """
        Method to extract the CdTe data from `self.data_file` and return the 
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
        col = CdTeCollection(parsed_data, self.old_data_time)
        self.old_data_time = col.last_data_time
        return col

    def raw_2_collected(self):
        raw = self.extract_raw_data()

        # might need in future: `if raw!=self.return_empty():``
        parsed = self.raw_2_parsed(raw)

        # assign the collected data and trigger the `emit`
        self.collections = self.parsed_2_collections(parsed)


class CdTeCollection:
    """
    A container for CdTe data after being parsed.
    
    Can be used to generate spectrograms or images.
    
    Paramters
    ---------
    parsed_data : `tuple`, length 3
            Contains `Flags`, `event_df`, `all_hkdicts` as returned from 
            the parser.

    parsed_data : `int`, `float`
            The last time of the last data point previously extracted and 
            used. Default is `0` and so should take all data.
            Default: 0
            
    Example
    -------
    with readBackwards.BackwardsReader(file=directory+raw_file, blksize=20_000_000, forward=True) as f:
        iterative_unpack=struct.iter_unpack("<I",f.read_block())
        datalist=[]
        for ndata,data in enumerate(iterative_unpack):
            datalist.append(data[0])
        Flags, event_df, all_hkdicts = CdTerawalldata2parser_new.CdTerawalldata2parser(datalist)
        
    cdte_data = CdTeCollection((Flags, event_df, all_hkdicts))
    
    plt.figure(figsize=(12,8))
    cdte_data.plot_spectrogram(v=210, remap=True, cmn_sub=True)
    plt.show()
    
    plt.figure(figsize=(8,8))
    cdte_data.plot_image(remap=True, area_correction=True, true_pixel_size=True)
    plt.show()
    """
    
    def __init__(self, parsed_data, old_data_time=0):
        # bring in the parsed data
        _, self.event_dataframe, _ = parsed_data
        
        # define all the strip sizes in CdTe detectors
        self.strip_bins, self.side_strip_bins, self.adc_bins = self.channel_bins()
        
        # for easy remapping of channels
        self.channel_map = self.remap_strip_dict()

        # used in the filter to only consider data with times > than this
        self.last_data_time = old_data_time

        # filter the counts somehow, go for crude single strip right now
        self.f_data = self.filter_counts(event_dataframe=self.event_dataframe)
        
        # get more physical information about detector geometry
        self.strip_width_edges = self.strip_widths()
        self.pixel_area = self.pixel_areas()

    def single_event(self, adc_values_pt, adc_values_al, style:str="simple1"):
        """
        Hosts a number of ways to filter the data and get single count 
        events.

        Paramters
        ---------
        adc_values_pt, adc_values_al : `np.ndarray`, `np.ndarray`
                Contains `Flags`, `event_df`, `all_hkdicts` as returned 
                from the parser.
                
        style : `str`
                Sets the style to be used to obtain single count events.
                Default: 'simple1'

        Returns
        -------
        `tuple`:
            (pt_lower,al_lower), ADC values greater than these entries 
            will be considered for single event selection.
        """
        
        if style=="simple0":
            # not great :(
            pt_min_adc = np.min(adc_values_pt, axis=0)
            al_min_adc = np.min(adc_values_al, axis=0)
            filter_scalar = 0.9
            return filter_scalar*abs(pt_min_adc), filter_scalar*abs(al_min_adc)
        elif style=="simple1":
            # seems to work well and is probably the normal way to do it
            pos_pt = adc_values_pt[adc_values_pt>0]
            pt_min_adc = np.median(pos_pt) + np.std(pos_pt)
            pos_al = adc_values_al[adc_values_al>0]
            al_min_adc = np.median(pos_al) + np.std(pos_al)
            return pt_min_adc, al_min_adc
        elif style=="simple2":
            # takes ages for some reason
            pt_min_adc = np.std(adc_values_pt[adc_values_pt])
            al_min_adc = np.std(adc_values_al[adc_values_al])
            return pt_min_adc, al_min_adc
        elif style=="simple3":
            # same as oldest selection
            return self.get_pt_cmn(), self.get_al_cmn()
        else:
            return 0, 0

    def filter_counts(self, event_dataframe):
        """
        Function to filer the count data.

        Paramters
        ---------
        event_dataframe : numpy structured array
                The numpy structured array returned from the parser 
                containing the CdTe data.

        Returns
        -------
        `dict`:
            Dictionary of the times, adc value, and strip number of all 
            filtered data.
        """

        new = event_dataframe['ti']>self.last_data_time
        
        if np.all(~new):
            return {'times':np.array([]), 
                    'pt_strip_adc':np.array([]), 
                    'al_strip_adc':np.array([]), 
                    'pt_strips':np.array([]), 
                    'al_strips':np.array([])}

        trig_times = event_dataframe['ti'][new]
        pt = event_dataframe['index_pt'][new]
        al = event_dataframe['index_al'][new]+128
        pt_adc = event_dataframe['adc_cmn_pt'][new]
        al_adc = event_dataframe['adc_cmn_al'][new]

        pt_min_adc, al_min_adc = self.single_event(pt_adc, al_adc, style="simple1")
    
        pt_selection = ((pt<59) | (pt>68)) & (pt_adc>pt_min_adc) & (pt_adc<800)
        al_selection = ((al>131) & (al<252)) & (al_adc>al_min_adc) & (al_adc<800)
        
        # choose single strip events
        single = [True if np.sum(pts)==np.sum(als)==1 else False for pts,als in zip(pt_selection,al_selection)]
        single_trig_times = trig_times[single]
        single = np.array(single)[:,None]

        pt_strip = pt[pt_selection & single]
        al_strip = al[al_selection & single]
        pt_value = pt_adc[pt_selection & single]
        al_value = al_adc[al_selection & single]
        
        self.last_data_time = event_dataframe['ti'][-1]
        return {'times':single_trig_times, 
                'pt_strip_adc':pt_value, 
                'al_strip_adc':al_value, 
                'pt_strips':pt_strip, 
                'al_strips':al_strip-128}
    
    def channel_bins(self):
        """ Define the strip and ADC bins. """
        strip_bins = np.arange(257)-0.5
        side_strip_bins = np.arange(129)-0.5
        adc_bins = np.arange(1025)-0.5

        return strip_bins, side_strip_bins, adc_bins

    def get_pt_cmn(self):
        """ 
        Put all common modes for the Pt side  into the same structure as 
        the ADC-cmn values.
        
        E.g., the cmn are all 'per ASIC' (so 2 for Al for every event) 
        but want structure to give the common mode for each ADC value.
        """
        ptcmn = self.event_dataframe['cmn_pt']
        num = len(ptcmn[:,0])
        return np.concatenate((np.resize(ptcmn[:,0],(64,num)),np.resize(ptcmn[:,1],(64,num))), axis=0).T
    
    def get_al_cmn(self):
        """ 
        Put all common modes for the Al side  into the same structure as 
        the ADC-cmn values.
        
        E.g., the cmn are all 'per ASIC' (so 2 for Pt for every event) 
        but want structure to give the common mode for each ADC value.
        """
        alcmn = self.event_dataframe['cmn_al']
        num = len(alcmn[:,0])
        return np.concatenate((np.resize(alcmn[:,0],(64,num)),np.resize(alcmn[:,1],(64,num))), axis=0).T

    def add_cmn(self):
        """ 
        The ADC values from the parser where the common mode has been 
        added back in for reference.
        """
        cmn01 = self.get_pt_cmn()
        
        cmn23 = self.get_al_cmn()
        
        add_cmn_pt = self.event_dataframe['adc_cmn_pt']+cmn01
        add_cmn_al = self.event_dataframe['adc_cmn_al']+cmn23
        
        return np.ndarray.flatten(add_cmn_pt), np.ndarray.flatten(add_cmn_al)
    
    def spectrogram(self, cmn_sub:bool=False):
        """ 
        Spectrogram? 
        
        In space, not time though. Don't think that matters but will 
        someone get annoyed though? 
        
        Parameters
        ----------
            
        cmn_sub : `bool`
            Defines whether the common mode subtraction should be done 
            for the ADC values.
            Default: False

        Returns
        -------
        `np.ndarray`, _, _ :
            Array of the binned histogram.
        """
        pt_strips = np.ndarray.flatten(self.event_dataframe['index_pt'])
        al_strips = np.ndarray.flatten(self.event_dataframe['index_al'])+128
        all_strips = np.concatenate((pt_strips, al_strips))
        
        if cmn_sub:
            pt_adc = np.ndarray.flatten(self.event_dataframe['adc_cmn_pt'])
            al_adc = np.ndarray.flatten(self.event_dataframe['adc_cmn_al'])
        else:
            pt_adc, al_adc = self.add_cmn()
        all_adc = np.concatenate((pt_adc, al_adc))
        
        self.adc_counts_arr, _, _ = np.histogram2d(all_strips, all_adc, 
                                                   bins=[self.strip_bins,
                                                         self.adc_bins])
        
    def plot_spectrogram(self, v:(float,int)=None, remap:bool=False, nan_zeros:bool=False, cmn_sub:bool=False):
        """
        Method to plot the spectrogram of the CdTe file.

        Parameters
        ----------
        v : `float`, `int`
            Maximum value for the histrogram colourbar.
            
        remap : `bool`
            Set to `True` to remap the strip channels to their physical 
            orientation.
            Default: False
            
        nan_zeros : `bool`
            Defines whether zeros should be replaced with NaNs.
            Default: False
            
        cmn_sub : `bool`
            Defines whether the common mode subtraction should be done 
            for the ADC values.
            Default: False

        Returns
        -------
        `matplotlib.collections.QuadMesh` :
            The object which hold the plot.
        """
        
        self.spectrogram(cmn_sub=cmn_sub)
        
        counts = self.remap_strips(counts=self.adc_counts_arr) if remap else self.adc_counts_arr
        
        v = 0.8*np.max(counts) if v is None else v
        
        counts[counts<=0] = np.nan if nan_zeros else counts[counts<=0]
        
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
    
    def image(self, remap:bool=True):
        """
        Method to return the image array of the parser output.

        Parameters
        ----------
        remap : `bool`
            Set to `True` to remap the strip channels to their physical 
            orientation.
            Default: True

        Returns
        -------
        `np.ndarray` :
            The image array.
        """
        
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
        """ Remap the strip values to their physical location. """
        rpt_strips, ral_strips = [],[]
        for c in range(len(pt_strips)):
            rpt_strips.append(self.channel_map[pt_strips[c]])
            ral_strips.append(self.channel_map[al_strips[c]+128])
        return np.array(rpt_strips), np.array(ral_strips)-128
    
    def _area_correction(self, image):
        """ 
        Correct the image counts array for strip-pixel collecting 
        area. 
        """
        image /= self.pixel_area
        return image
    
    def image_array(self, remap:bool=True, area_correction:bool=True):
        """ obtain the image array with the wanted corrections. """
        im = self.image(remap=remap)
        if area_correction:
            return self._area_correction(im)
        return im
    
    def plot_image(self, remap:bool=True, area_correction:bool=True, true_pixel_size:bool=True):
        """
        Method to plot the image of the CdTe file.

        Parameters
        ----------
            
        remap : `bool`
            Set to `True` to remap the strip channels to their physical 
            orientation.
            Default: True
            
        area_correction : `bool`
            Defines whether the map is corrected for the true, 
            non-uniform strip-pixel collection areas.
            Default: True
            
        true_pixel_size : `bool`
            Defines whether 'pixels' are plotted uniformly (False) or 
            non-uniformly (True).
            Default: True

        Returns
        -------
        `matplotlib.collections.QuadMesh` or `matplotlib.pyplot.imshow`:
            The object which holds the plot depending if 
            `true_pixel_size=True` or `False`, respectivley.
        """

        im = self.image_array(remap=remap, area_correction=area_correction)
        
        if true_pixel_size:
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
        """ 
        Define dictionary for easy remapping of channels to physical 
        location. 
        """
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
        """ Reverse the rows of a 2D numpy array. """
        return arr[::-1,:]

    def remap_strips(self, counts):
        """ Remap a 2D numpy array of the strip data. """
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
        """ 
        Function to define the physical sizes of the different pitch 
        widths and what to do as they transition. 
        
        Pitch widths are 100, 80, 60 um and the spaced between are 90 
        and 70 um (100/2+80/2 and 80/2+60/2, respectively).
        """
        C = np.arange(29)*100 # ignore channel 28 just now

        B = np.arange(20)*80 

        A = np.arange(16)*60
        
        new_b = B + C[-1] + 50 + 40 # add last value from (C) then half a bin in (C) and half one in (B)
        
        new_a = A + new_b[-1] + 40 + 30
        
        right_a = A[:-1] + new_a[-1] + 60
        right_b = B + right_a[-1] + 30 + 40
        right_c = C + right_b[-1] + 40 + 50
        
        edges = np.concatenate((C,new_b,new_a,right_a,right_b,right_c))
        
        return edges
    
    def pixel_areas(self):
        """ From the pitch widths, get the strip-pixel areas. """
        return np.diff(self.strip_width_edges)[:,None]@np.diff(self.strip_width_edges)[None,:]
    

class CdTeFileReader(Reader):
    """ A reader for a CdTe data file already obtained. """
    def __init__(self, datafile, parent=None):
        """
        Raw : binary
        Parsed : human readable
        Collected : organised by intrumentation
        """
        
        Reader.__init__(self, datafile, parent)
        self.define_buffer_size(size=25_000)
        self._read_counter = 0#28983837-self.buffer_size#-0

    def extract_raw_data_cdte(self):
        """
        Mocl method to extract the CdTe data from `self.data_file` and return the 
        desired data.

        This just reads in the whole file but then iterates through the file.

        Returns
        -------
        `tuple` :
            (x, y) The new x and y coordinates read from `self.data_file`.
        """
        # read the file `self.bufferSize` bytes from the end and extract the lines
        # forward=True: reads buffer from the back but doesn't reverse the data 
        if not hasattr(self,"data_unpack"):
            try:
                with open(self.data_file, 'rb') as f:
                    iterative_unpack=struct.iter_unpack("<I",f.read())
                self.data_unpack = []
                for i,data in enumerate(iterative_unpack):
                    self.data_unpack.append(data[0])
                self.data_len = i
            except FileNotFoundError:
                return self.return_empty() 
        
        if self._read_counter>self.data_len:
            return self.return_empty() 
        
        if (self._read_counter+self.buffer_size)<=self.data_len:
            datalist = self.data_unpack[self._read_counter:(self._read_counter+self.buffer_size)]
        else:
            datalist = self.data_unpack[self._read_counter:]
        
        # pretend 50% of the buffer size has been written since last read
        self._read_counter += int(self.buffer_size*0.5) 
        return datalist
    
    def raw_2_parsed(self, raw_data):
        """ 
        Since `extract_raw_data_cdte` is re-defined then this points 
        to a _slightly_ different parser that will not break if half an 
        event/trigger is in raw data. 
        """
        # return or set human readable data
        # do stuff with the raw data and return nice, human readable data
        try:
            flags, event_df, all_hkdicts = CdTerawalldata2parser_test(raw_data)
        except ValueError:
            # no data from parser so pass nothing on with a time of -1
            print("No data from parser.")
            flags, event_df, all_hkdicts = (None,{'ti':-1},None)
        return flags, event_df, all_hkdicts
    
    
class fake_window_cdte(QWidget):
    def __init__(self, reader, parent=None):

        QWidget.__init__(self, parent)

        self.reader = reader
        self.graphPane = pg.PlotWidget(self)
        self.graphPane.setMinimumSize(QtCore.QSize(500,500))

        self.layoutCenter = QVBoxLayout()
        self.layoutCenter.addWidget(self.graphPane)

        # set all rgba info (e.g., mode rgb or rgba, indices for red green blue, etc.)
        self.colour_mode = "rgba"
        self.channel = {"red":0, "green":1, "blue":2}
        # alpha index
        self.alpha = 3
        # colours range from 0->255 in RGBA
        self.min_val, self.max_val = 0, 255

        self.fade_out = 25

        # create QImage from numpy array 
        self.deth, self.detw = 128, 128
        self.numpy_format = np.uint8
        self.set_image_ndarray()
        q_image = pg.QtGui.QImage(self.my_array, self.deth, self.detw, self.cformat)

        # send image to fram and add to plot
        self.img = QtWidgets.QGraphicsPixmapItem(pg.QtGui.QPixmap(q_image))
        self.graphPane.addItem(self.img)

        # set title and labels
        self.set_labels(self.graphPane, xlabel="X", ylabel="Y", title="Image")

        self.image_colour = "green"

        self.setLayout(self.layoutCenter)

        self.reader.value_changed_collections.connect(self.update_plot)
        

    def update_plot(self):
        """
        Defines how the plot window is updated for a 2D image.

        In subclass define methods: 
        *`get_data` to extract the new image frame from `self.data_file`, 
        *`update_image` to define how the new image affects the current one,
        *`process_data` to perform any last steps before updating the plot.
        """
        
        # get the new frame
        new_frame = self.reader.collections.image_array(area_correction=False)

        # update current plotted data with new frame
        self.update_image(existing_frame=self.my_array, new_frame=new_frame)
        
        # define self.qImageDetails for this particular image product
        self.process_data()

        # # new image
        qImage = pg.QtGui.QImage(*self.qImageDetails)#Format.Format_RGBA64

        # faster long term to remove pervious frame and replot new one
        self.graphPane.removeItem(self.img)
        self.img = QtWidgets.QGraphicsPixmapItem(pg.QtGui.QPixmap(qImage))
        self.graphPane.addItem(self.img)
        self.update()

    def update_image(self, existing_frame, new_frame):
        """
        Add new frame to the current frame while recording the newsest hits in the `new_frame` image. Use 
        the new hits to control the alpha channel via `self.fade_control` to allow old counts to fade out.
        
        Only using the blue and alpha channels at the moment.

        Parameters
        ----------
        existing_frame : `numpy.ndarray`
            This is the RGB (`self.colour_mode='rgb'`) or RGBA (`self.colour_mode='rgba'`) array of shape 
            (`self.detw`,`self.deth`,3) or (`self.detw`,`self.deth`,4), respectively.

        new_frame : `numpy.ndarray`
            This is a 2D array of the new image frame created from the latest data of shape (`self.detw`,`self.deth`).
        """

        # if new_frame is a list then it's empty and so no new frame, make all 0s
        if type(new_frame)==list:
            new_frame = np.zeros((self.deth, self.detw))
        
        # what pixels have a brand new hit? (0 = False, not 0 = True)
        new_hits = new_frame.astype(bool) 
        
        self.fade_control(new_hits_array=new_hits)#, control_with=self.image_colour)

        # add the new frame to the blue channel values and update the `self.my_array` to be plotted
        self.my_array[:,:,self.channel[self.image_colour]] = existing_frame[:,:,self.channel[self.image_colour]] + new_frame

    def fade_control(self, new_hits_array, control_with="alpha"):
        """
        Fades out pixels that haven't had a new count in steps of `self.max_val//self.fade_out` until a pixel has not had an 
        event for `self.fade_out` frames. If a pixel has not had a detection in `self.fade_out` frames then reset the colour 
        channel to zero and the alpha channel back to `self.max_val`.

        Parameters
        ----------
        new_frame : `numpy.ndarray`, `bool`
            This is a 2D boolean array of shape (`self.detw`,`self.deth`) which shows True if the pixel has just detected 
            a new count and False if it hasn't.
        """

        # reset counter if pixel has new hit
        self.no_new_hits_counter_array[new_hits_array] = 0

        # add to counter if pixel has no hits
        self.no_new_hits_counter_array += ~new_hits_array

        if (control_with=="alpha") and (self.colour_mode=="rgba"):
            # set alpha channel, fade by decreasing steadily over `self.fade_out` steps 
            # (a step for every frame the pixel has not detected an event)
            index = self.alpha
            self.my_array[:,:,index] = self.max_val - (self.max_val//self.fade_out)*self.no_new_hits_counter_array

            # find where alpha is zero (completely faded)
            turn_off_colour = (self.my_array[:,:,self.alpha]==0)

            # now set the colour back to zero and return alhpa to max, ready for new counts
            for k in self.channel.keys():
                self.my_array[:,:,self.channel[k]][turn_off_colour] = 0

            # reset alpha
            self.my_array[:,:,self.alpha][turn_off_colour] = self.max_val

        elif control_with in ["red", "green", "blue"]:
            index = self.channel[control_with]
            self.my_array[:,:,index] = self.my_array[:,:,index] - (self.my_array[:,:,index]/self.fade_out)*self.no_new_hits_counter_array
        
        # reset the no hits counter when max is reached
        self.no_new_hits_counter_array[self.no_new_hits_counter_array==self.fade_out] = 0

    def process_data(self):
        """
        An extra processing step for the data before it is plotted.
        """

        # make sure everything is normalised between 0--255
        norm = np.max(self.my_array, axis=(0,1))
        norm[norm==0] = 1 # can't divide by 0
        uf = self.max_val*self.my_array//norm

        # allow this all to be looked at if need be
        self.qImageDetails = [uf.astype(self.numpy_format), self.deth, self.detw, self.cformat]

    def set_labels(self, graph_widget, xlabel="", ylabel="", title=""):
        """
        Method just to easily set the x, y-label andplot title without having to write all lines below again 
        and again.

        [1] https://stackoverflow.com/questions/74628737/how-to-change-the-font-of-axis-label-in-pyqtgraph

        arameters
        ----------
        graph_widget : `PyQt6 PlotWidget`
            The widget for the labels

        xlabel, ylabel, title : `str`
            The strings relating to each label to be set.
        """

        graph_widget.setTitle(title)

        # Set label for both axes
        graph_widget.setLabel('bottom', xlabel)
        graph_widget.setLabel('left', ylabel)

    def set_image_ndarray(self):
        """
        Set-up the numpy array and define colour format from `self.colour_mode`.
        """
        # colours range from 0->255 in RGBA8888 and RGB888
        # do we want alpha channel or not
        if self.colour_mode == "rgba":
            self.my_array = np.zeros((self.deth, self.detw, 4))
            self.cformat = pg.QtGui.QImage.Format.Format_RGBA8888
            # for all x and y, turn alpha to max
            self.my_array[:,:,3] = self.max_val 
        if self.colour_mode == "rgb":
            self.my_array = np.zeros((self.deth, self.detw, 3))
            self.cformat = pg.QtGui.QImage.Format.Format_RGB888

        # define array to keep track of the last hit to each pixel
        self.no_new_hits_counter_array = (np.zeros((self.deth, self.detw))).astype(self.numpy_format)


if __name__=="__main__":
    app = QApplication([])

    # different data files to try
    # datafile = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/CdTeImages/no2022_03/NiFoilAm241/10min/test_20230609a_det03_00012_001"
    datafile = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/berkeley/prototype_vibe_test/fromBerkeley_postVibeCheckFiles/Am241/test_berk_20230803_proto_Am241_1min_postvibe2_00006_001"
    # datafile = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/berkeley/prototype_vibe_test/fromBerkeley_postVibeCheckFiles/Fe55/test_berk_20230803_proto_Fe55_1min__postvibe2_00008_001"
    # datafile = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/CdTeImages/no2021_05/Am241/1min/test_berk_20230728_det05_00005_001"
    # datafile = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/CdTeImages/no2021_05/Fe55/1min/test_berk_20230728_det05_00006_001"
    # datafile = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/CdTeImages/no2021_05/Cr51/1min/test_berk_20230728_det05_00007_001"

    R = CdTeFileReader(datafile)

    f0 = fake_window_cdte(R)
    # print(R.collections)
    f0.show()
    app.exec()