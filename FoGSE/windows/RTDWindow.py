"""
A demo to walk through an existing CdTe raw file.
"""

import numpy as np

from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication, QSizePolicy, QVBoxLayout, QWidget
import pyqtgraph as pg

from FoGSE.read_raw_to_refined.readRawToRefinedRTD import RTDReader
from FoGSE.windows.LightCurveWindow import MultiLightCurve

from FoGSE.widgets.layout_tools.stretch import unifrom_layout_stretch
from FoGSE.widgets.layout_tools.spacing import set_all_spacings


class RTDWindow(QWidget):
    """
    An individual window to display RTD data read from a file.

    Parameters
    ----------
    data_file : `str` 
        The file to be passed to `FoGSE.read_raw_to_refined.readRawToRefinedRTD.RTDReader()`.
        If given, takes priority over `reader` input.
        Default: None

    reader : instance of `FoGSE.read_raw_to_refined.readRawToRefinedBase.ReaderBase()`
        The reader already given a file.
        Default: None
    """
    def __init__(self, data_file=None, reader=None, parent=None, name="RTD"):

        pg.setConfigOption('background', (255,255,255, 0)) # needs to be first

        QWidget.__init__(self, parent)

        # decide how to read the data
        if data_file is not None:
            # probably the main way to use it
            self.reader = RTDReader(data_file)
        elif reader is not None:
            # useful for testing and if multiple windows need to share the same file
            self.reader = reader
        else:
            print("How do I read the Timepix data?")

        self.chip1_ids     = ['ts0',  'ts1',        'ts2',  'ts3',  'ts4',    'ts5',     'ts6',      'ts7',  'ts8']
        self.chip1_names   = ['LN2',  'POS2',       'POS3', 'POS4', 'POS5',   '5.5 V',   'MICRO',    '???',  'TIMEPIX']
        self.chip1_colours = ['blue', 'lightgreen', 'red',  'cyan', 'gold',   'magenta', 'darkGrey', 'pink', 'k']

        self.chip2_ids     = ['ts9',         'ts10',       'ts11',   'ts12',    'ts13',    'ts14',    'ts15',     'ts16',     'ts17']
        self.chip2_names   = ['OPTIC PLATE', 'A FRONT',    'A BACK', 'B FRONT', 'C FRONT', 'C BACK',  'D FRONT',  'D MIDDLE', 'D BACK']
        self.chip2_colours = ['blue',        'lightgreen', 'red',    'cyan',    'gold',    'magenta', 'darkGrey', 'pink',     'k']

        self.chip1 = MultiLightCurve(ids=self.chip1_ids, colours=self.chip1_colours, names=self.chip1_names)
        self.chip2 = MultiLightCurve(ids=self.chip2_ids, colours=self.chip2_colours, names=self.chip2_names)

        self.chip1.set_labels(xlabel="", ylabel="T (C)", title="", fontsize=5, ticksize=5, titlesize=0, offsetsize=1)
        self.chip2.set_labels(xlabel="Time (Unixtime)", ylabel="T (C)", title="", fontsize=5, ticksize=5, titlesize=0, offsetsize=1)
        
        self.reader.value_changed_collection.connect(self.update_plot)

        self.layoutMain = QVBoxLayout()
        self.layoutMain.setContentsMargins(0, 0, 0, 0)
        self.layoutMain.setSpacing(0)
        self.layoutMain.addWidget(self.chip1)
        self.layoutMain.addWidget(self.chip2)

        set_all_spacings(self.layoutMain)
        unifrom_layout_stretch(self.layoutMain)

        self.setLayout(self.layoutMain)

        self.detw, self.deth = self.chip1.detw, self.chip1.deth+self.chip2.deth
        self.aspect_ratio = self.detw / self.deth

    # def _separate_chips(self, new_data):
    #     """ Return the values for chip1 and 2. """
    #     chip1_values, chip2_values = [], []
    #     for ids1 in self.chip1_ids:
    #         chip1_values.append(list(new_data[ids1]))
    #     for ids2 in self.chip1_ids:
    #         chip2_values.append(list(new_data[ids2]))
    #     return chip1_values, chip2_values

    def update_plot(self):
        """
        Defines how the plot window is updated for time series.

        In subclass define methods: 
        *`get_data` to extract the new image frame from `self.data_file`, 
        *`update_image` to define how the new image affects the current one,
        *`process_data` to perform any last steps before updating the plot.
        """
        
        chip1_values = self.reader.collection.chip1_data()
        chip2_values = self.reader.collection.chip2_data()
        
        # chip1_values = [chip1_values[0], [0,8], [6,9], [15,80], [6,8], [6,8], [6,8], [6,8], [6,8], [6,8]]
        # chip2_values = [chip2_values[0], [0,8], [6,9], [15,80], [6,8], [6,8], [6,8], [6,8], [6,8], [6,8]]
        
        # defined how to add/append onto the new data arrays
        self.chip1.add_plot_data(chip1_values[1:], new_data_xs=chip1_values[0], replace={"this":[np.nan], "with":[0]})
        self.chip2.add_plot_data(chip2_values[1:], new_data_xs=chip2_values[0], replace={"this":[0], "with":[np.nan]})

        # plot the newly updated x and ys
        self.chip1.manage_plotting_ranges()
        self.chip2.manage_plotting_ranges()

    def resizeEvent(self,event):
        """ Define how the widget can be resized and keep the same apsect ratio. """
        super().resizeEvent(event)
        # Create a square base size of 10x10 and scale it to the new size
        # maintaining aspect ratio.
        # image_resize = QtCore.QSize(int(event.size().width()*0.6), int(event.size().height()*0.6))
        # self.image.resize(image_resize)
        # ped_resize = QtCore.QSize(int(event.size().width()*0.6), int(event.size().height()*0.4))
        # self.ped.resize(ped_resize)
        if event is None:
            return 
        
        new_size = QtCore.QSize(self.detw, int(self.detw / self.aspect_ratio)) #width, height/(width/height)
        new_size.scale(event.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio)

        self.resize(new_size)


if __name__=="__main__":
    
    import os
    DATAFILE = os.path.dirname(os.path.realpath(__file__)) + "/../../../fake_temperatures.txt"
    DATAFILE = "/Users/kris/Downloads/housekeeping.log"
    # DATAFILE = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/GSE-FOXSI-4/logs/received/1-2-2024_9-16-23/housekeeping_rtd.log"
    DATAFILE = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/usingGSECodeForDetAnalysis/feb3/run19/gse/housekeeping.log"

    def initiate_gui():
        app = QApplication([])

        # R = RTDFileReader(DATAFILE)
        R = RTDReader(DATAFILE)

        f0 = RTDWindow(reader=R)

        f0.show()
        app.exec()

    # from multiprocessing import Process

    # fake temps
    # p1 = Process(target = initiate_fake_Timepixs)
    # p1.start()
    # live plot
    # p2 = Process(target = initiate_gui)
    # p2.start()
    # p2.join()

    initiate_gui()
