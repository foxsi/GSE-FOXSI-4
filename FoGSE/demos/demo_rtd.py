"""
A demo to walk through an existing CdTe raw file.
"""

import numpy as np
import sys

from PyQt6 import QtCore#, QtWidgets
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
import pyqtgraph as pg

from FoGSE.demos.readRawToRefined_rtd import RTDFileReader

    
class IndividualWindowRTD(QWidget):
    """
    An individual window to display RTD data read from a file.

    Parameters
    ----------
    reader : `FoGSE.demos.readRawToRefined_rtd.RTDFileReader()`
        The class in charge of using the RTD parser and containing the result.
    """
    def __init__(self, reader, parent=None):

        QWidget.__init__(self, parent)

        self.reader = reader
        self.graphPane = pg.PlotWidget(self)
        self.graphPane.setMinimumSize(QtCore.QSize(500,500))

        self.layoutCenter = QVBoxLayout()
        self.layoutCenter.addWidget(self.graphPane)

        # should match the data, big problems if not
        self.temp_sensors = ['ts0', 'ts1', 'ts2', 'ts3', 'ts4', 'ts5', 'ts6', 'ts7', 'ts8', 'ts9', 'ts10', 'ts11', 'ts12', 'ts13', 'ts14', 'ts15', 'ts16', 'ts17']
        self.colors       = ['b',   'g',   'r',   'c',   'y',   'm',  'brown', 'k',  'purple','b',  'g',   'r',    'c',    'y',    'm',    'brown','k',    'purple']

        # self.sensor_plot_data = dict.fromkeys(['ti', *self.temp_sensors], [])
        self.sensor_plot_data = dict(zip(['ti', *self.temp_sensors], [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]))
        self.sensor_plots = dict()
        for c,t in enumerate(self.temp_sensors):
            self.sensor_plots[t] = self.plot([], [], color=self.colors[c], plotname=t)

        # set title and labels
        self.set_labels(self.graphPane, xlabel="Time (UNIX)", ylabel="Temperature (C)", title="RTD Temperatures")

        self.setLayout(self.layoutCenter)

        self.reader.value_changed_collections.connect(self.update_plot)

        # Disable interactivity
        self.graphPane.setMouseEnabled(x=False, y=False)  # Disable mouse panning & zooming
        

    def update_plot(self):
        """
        Defines how the plot window is updated for time series.

        In subclass define methods: 
        *`get_data` to extract the new image frame from `self.data_file`, 
        *`update_image` to define how the new image affects the current one,
        *`process_data` to perform any last steps before updating the plot.
        """
        
        new_data = self.reader.collections.new_data

        # just average over some coordinates fto reduce the number of points being plotted
        # separated_data = self.process_data(new_data)
        # print(new_data['ti'],new_data['ts0'])

        # defined how to add/append onto the new data arrays
        self.add_plot_data(new_data)
        print("plotted",self.sensor_plot_data['ti'])

        # plot the newly updated x and ys
        for c,t in enumerate(self.temp_sensors):
            self.sensor_plots[t] = self.plot(self.sensor_plot_data['ti'], self.sensor_plot_data[t], color=self.colors[c], plotname=t)

        # self.update()

    def add_plot_data(self, separated_data):
        _keep = 30
        _from = -_keep if len(self.sensor_plot_data['ti'])>_keep else 0
        for t in self.temp_sensors:
            self.sensor_plot_data[t] = self.sensor_plot_data[t][_from:] + list(separated_data[t])
        self.sensor_plot_data['ti'] = self.sensor_plot_data['ti'][_from:] + list(separated_data['ti'])
        self.graphPane.plotItem.vb.setLimits(xMin=self.sensor_plot_data['ti'][0], 
                                             xMax=self.sensor_plot_data['ti'][-1])
        

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

    def plot(self, x, y, color, plotname):
        pen = pg.mkPen(color=color, width=5)
        return self.graphPane.plot(x, y, name=plotname, pen=pen)

    

import os
from FoGSE.demos.fake_rtds import fake_rtds
# package top-level
DATAFILE = os.path.dirname(os.path.realpath(__file__)) + "/../../fake_temperatures.txt"

def initiate_gui():
    app = QApplication([])

    R = RTDFileReader(DATAFILE)

    f0 = IndividualWindowRTD(R)

    f0.show()
    sys.exit(app.exec())

def initiate_fake_rtds():

    # generate fake data and save to `datafile`
    fake_rtds(DATAFILE, loops=1_000_000)

if __name__=="__main__":

    from multiprocessing import Process

    # layout
    p1 = Process(target = initiate_gui)
    p1.start()
    # fake FOXSI
    p2 = Process(target = initiate_fake_rtds)
    p2.start()
    p2.join()