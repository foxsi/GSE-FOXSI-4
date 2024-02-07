"""
A demo to walk through an existing CdTe raw file.
"""

import numpy as np

from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication, QSizePolicy, QVBoxLayout, QWidget
import pyqtgraph as pg

from FoGSE.read_raw_to_refined.readRawToRefinedTimepix import TimepixReader

    
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

        self.graphPane_mean_tot = pg.PlotWidget()
        self.graphPane_mean_tot.setMinimumSize(QtCore.QSize(800,350))
        self.graphPane_mean_tot.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        self.graphPane_flux = pg.PlotWidget()
        self.graphPane_flux.setMinimumSize(QtCore.QSize(800,350))
        self.graphPane_flux.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)

        self.layoutMain = QVBoxLayout()
        self.layoutMain.setContentsMargins(0, 0, 0, 0)
        self.layoutMain.setSpacing(0)
        self.layoutMain.addWidget(self.graphPane_mean_tot)
        self.layoutMain.addWidget(self.graphPane_flux)

        self.graphPane_mean_tot.setBackground('w')
        self.graphPane_mean_tot.showGrid(x=True, y=True)
        self.graphPane_flux.setBackground('w')
        self.graphPane_flux.showGrid(x=True, y=True)

        self.sensor_plot_data_mean_tot = np.array([0])
        self.sensor_plot_data_flux = np.array([0])

        self.sensor_plots_mean_tot = self.plot(self.graphPane_mean_tot, [0,0], [0,0], color="b", plotname="Mean ToT")
        self.sensor_plots_flux = self.plot(self.graphPane_flux, [0,0], [0,0], color="purple", plotname="Flux")

        # set title and labels
        self.set_labels(self.graphPane_mean_tot, xlabel="", ylabel="Mean ToT", title=" ")
        self.set_labels(self.graphPane_flux, xlabel="Time (entry)", ylabel="Flux", title=" ")

        self.keep_entries = 30 # entries

        self.reader.value_changed_collection.connect(self.update_plot)

        # Disable interactivity
        self.graphPane_mean_tot.setMouseEnabled(x=False, y=False)  # Disable mouse panning & zooming
        self.graphPane_flux.setMouseEnabled(x=False, y=False)  # Disable mouse panning & zooming

        self.setLayout(self.layoutMain)
        
        self.counter = 1

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
        self.add_plot_data_mean_tot(new_mean_tot)
        self.add_plot_data_flux(new_flux)

        # plot the newly updated x and ys
        _no_nans = ~np.isnan(self.sensor_plot_data_mean_tot) #avoid plotting nans
        if len(self.sensor_plot_data_mean_tot[_no_nans])>1:
            #pyqtgraph won't plot 1 data-point and throws an error instead :|
            self.sensor_plots_mean_tot.clear()
            _xs = np.arange(len(self.sensor_plot_data_mean_tot[_no_nans]))
            xs = _xs+self.counter if self.counter>self.keep_entries else _xs
            print(xs, self.sensor_plot_data_mean_tot[_no_nans])
            self.sensor_plots_mean_tot.setData(xs, self.sensor_plot_data_mean_tot[_no_nans])

        _no_nans = ~np.isnan(self.sensor_plot_data_flux) #avoid plotting nans
        if len(self.sensor_plot_data_flux[_no_nans])>1:
            #pyqtgraph won't plot 1 data-point and throws an error instead :|
            self.sensor_plots_flux.clear()
            _xs = np.arange(len(self.sensor_plot_data_mean_tot[_no_nans]))
            xs = _xs+self.counter if self.counter>self.keep_entries else _xs
            self.sensor_plots_flux.setData(xs, self.sensor_plot_data_flux[_no_nans])

        self.counter += 1

    def add_plot_data_mean_tot(self, new_data):
        """ Adds the new data to the array to be plotted. """

        # self.sensor_plot_data_mean_tot.append(new_data)
        self.sensor_plot_data_mean_tot = np.append(self.sensor_plot_data_mean_tot, new_data)
        
        if len(self.sensor_plot_data_mean_tot)>self.keep_entries:
            self.sensor_plot_data_mean_tot = self.sensor_plot_data_mean_tot[-30:]

        minmax = np.array([np.min(self.sensor_plot_data_mean_tot), np.max(self.sensor_plot_data_mean_tot)])
        
        if (not np.isnan(minmax[0])):
            self.graphPane_mean_tot.plotItem.vb.setLimits(yMin=np.nanmin(minmax[0])*0.95)
        if (not np.isnan(minmax[1])):
            self.graphPane_mean_tot.plotItem.vb.setLimits(yMax=np.nanmax(minmax[1])*1.05)

        minx = self.counter-self.keep_entries if len(self.sensor_plot_data_mean_tot)>self.keep_entries else 0
        self.graphPane_mean_tot.plotItem.vb.setLimits(xMin=minx, xMax=self.counter+1)
        
    def add_plot_data_flux(self, new_data):
        """ Adds the new data to the array to be plotted. """

        # self.sensor_plot_data_flux.append(new_data)
        self.sensor_plot_data_flux = np.append(self.sensor_plot_data_flux, new_data)
        
        if len(self.sensor_plot_data_flux)>self.keep_entries:
            self.sensor_plot_data_flux = self.sensor_plot_data_flux[-30:]

        minmax = np.array([np.min(self.sensor_plot_data_flux), np.max(self.sensor_plot_data_flux)])
        
        if (not np.isnan(minmax[0])):
            self.graphPane_flux.plotItem.vb.setLimits(yMin=np.nanmin(minmax[0])*0.95)
        if (not np.isnan(minmax[1])):
            self.graphPane_flux.plotItem.vb.setLimits(yMax=np.nanmax(minmax[1])*1.05)
            
        minx = self.counter-self.keep_entries if len(self.sensor_plot_data_flux)>self.keep_entries else 0
        self.graphPane_flux.plotItem.vb.setLimits(xMin=minx, xMax=self.counter+1)
        

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
        graph_widget.setTitle(title, color='k', size='25pt')

        # Set label for both axes
        styles = {'color':'k', 'font-size':'20pt'} 
        graph_widget.setLabel('bottom', xlabel, **styles)
        graph_widget.setLabel('left', ylabel, **styles)

    def plot(self, graph_widget, x, y, color, plotname=''):
        pen = pg.mkPen(color=color, width=5)
        return graph_widget.plot(x, y, name=plotname, pen=pen)

    

if __name__=="__main__":
    # package top-level
    import os
    DATAFILE = os.path.dirname(os.path.realpath(__file__)) + "/../../../fake_temperatures.txt"
    DATAFILE = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/timepix/for_Kris/fake_data_for_parser/example_timepix_frame.bin"

    def initiate_gui():
        app = QApplication([])

        # R = TimepixFileReader(DATAFILE)
        R = TimepixReader(DATAFILE)

        f0 = TimepixWindow(reader=R)

        f0.show()
        app.exec()

    # def initiate_fake_Timepixs():
    #     from FoGSE.fake_foxsi.fake_Timepixs import fake_Timepixs

    #     # generate fake data and save to `datafile`
    #     fake_Timepixs(DATAFILE, loops=1_000_000)

    # from multiprocessing import Process

    # fake temps
    # p1 = Process(target = initiate_fake_Timepixs)
    # p1.start()
    # live plot
    # p2 = Process(target = initiate_gui)
    # p2.start()
    # p2.join()

    initiate_gui()