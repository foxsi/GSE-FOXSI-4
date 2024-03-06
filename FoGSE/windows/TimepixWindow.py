"""
A demo to walk through an existing CdTe raw file.
"""

import numpy as np

from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication, QSizePolicy, QVBoxLayout, QWidget
import pyqtgraph as pg

from FoGSE.read_raw_to_refined.readRawToRefinedTimepix import TimepixReader
from FoGSE.windows.LightCurveWindow import LightCurve

from FoGSE.widgets.layout_tools.stretch import unifrom_layout_stretch
from FoGSE.widgets.layout_tools.spacing import set_all_spacings


class TimepixWindow(QWidget):
    """
    An individual window to display Timepix data read from a file.

    Parameters
    ----------
    data_file : `str` 
        The file to be passed to `FoGSE.read_raw_to_refined.readRawToRefinedTimepix.TimepixReader()`.
        If given, takes priority over `reader` input.
        Default: None

    reader : instance of `FoGSE.read_raw_to_refined.readRawToRefinedBase.ReaderBase()`
        The reader already given a file.
        Default: None
    """
    def __init__(self, data_file=None, reader=None, parent=None, name="Timepix"):

        pg.setConfigOption('background', (255,255,255, 0)) # needs to be first

        QWidget.__init__(self, parent)

        # decide how to read the data
        if data_file is not None:
            # probably the main way to use it
            self.reader = TimepixReader(data_file)
        elif reader is not None:
            # useful for testing and if multiple windows need to share the same file
            self.reader = reader
        else:
            print("How do I read the Timepix data?")

        self.mean_tot = LightCurve(reader=self.reader, name="Mean ToT")
        self.flux = LightCurve(reader=self.reader, name="Flux", colour="purple")

        self.mean_tot.set_labels(self.mean_tot.graphPane, xlabel="", ylabel="Mean ToT", title=" ")
        self.flux.set_labels(self.flux.graphPane, xlabel="Time (frame #)", ylabel="Flux", title="")

        self.reader.value_changed_collection.connect(self.update_plot)

        self.layoutMain = QVBoxLayout()
        self.layoutMain.setContentsMargins(0, 0, 0, 0)
        self.layoutMain.setSpacing(0)
        self.layoutMain.addWidget(self.mean_tot)
        self.layoutMain.addWidget(self.flux)

        set_all_spacings(self.layoutMain)
        unifrom_layout_stretch(self.layoutMain)

        self.setLayout(self.layoutMain)

        self.detw, self.deth = self.mean_tot.detw, self.mean_tot.deth+self.flux.deth
        self.aspect_ratio = self.detw / self.deth

        # self.setMinimumSize(self.detw, self.deth)
        # self.resize(self.detw, self.deth)

    def update_plot(self):
        """
        Defines how the plot window is updated for time series.

        In subclass define methods: 
        *`get_data` to extract the new image frame from `self.data_file`, 
        *`update_image` to define how the new image affects the current one,
        *`process_data` to perform any last steps before updating the plot.
        """
        
        new_mean_tot = self.reader.collection.get_mean_tot()
        new_flux = self.reader.collection.get_flux()
        
        # defined how to add/append onto the new data arrays
        self.mean_tot.add_plot_data(new_mean_tot, replace={"this":[0], "with":[np.nan]})
        self.flux.add_plot_data(new_flux, replace={"this":[0], "with":[np.nan]})

        # plot the newly updated x and ys
        self.mean_tot.manage_plotting_ranges()
        self.flux.manage_plotting_ranges()

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
    
    DATAFILE = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/timepix/for_Kris/fake_data_for_parser/example_timepix_frame.bin"
    DATAFILE = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/timepix/for_Kris/fake_data_for_parser/example_timepix_frame_writing.bin"

    def initiate_gui():
        app = QApplication([])

        # R = TimepixFileReader(DATAFILE)
        R = TimepixReader(DATAFILE)

        f0 = TimepixWindow(reader=R)

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
