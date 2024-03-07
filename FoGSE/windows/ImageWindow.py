"""
A class to help handle displaying a matplotlib image in a PyQt window.
"""

import numpy as np
from matplotlib import transforms

from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication, QSizePolicy, QVBoxLayout, QWidget
import pyqtgraph as pg

from FoGSE.windows.mpl.MPLCanvas import MPLCanvas

# from FoGSE.read_raw_to_refined.readRawToRefinedTimepix import TimepixReader
        

class Image(QWidget):
    """
    An individual window to display Timepix data read from a file.

    Parameters
    ----------
    """

    mpl_click_signal = QtCore.pyqtSignal()
    mpl_axes_enter_signal = QtCore.pyqtSignal()
    mpl_axes_leave_signal = QtCore.pyqtSignal()

    def __init__(self, name="image", colour="b", rotation=0, parent=None):
        pg.setConfigOption('background', (255,255,255, 0)) # needs to be first

        QWidget.__init__(self, parent)

        self.detw, self.deth = 400, 400
        self.aspect_ratio = self.detw / self.deth
        # self.resize(self.detw, self.deth)

        self.graphPane = MPLCanvas(self)

        self.layoutMain = QVBoxLayout()
        self.layoutMain.addWidget(self.graphPane)

        self.layoutMain.setContentsMargins(0, 0, 0, 0)
        self.layoutMain.setSpacing(0)

        # self.graphPane.setBackground('w')
        # self.graphPane.showGrid(x=True, y=True)
        self._plot_ref = None

        self.plot_data_ys = np.array([0]).astype(float)
        self.plot_data_xs = np.array([0]).astype(float)
        self._remove_first = True

        tr = transforms.Affine2D().rotate_deg(rotation) #rotation_in_degrees
        # Create the pcolormesh plot
        self.graphPane.axes.pcolormesh(x_values, y_values, data_matrix, cmap='viridis', transform=tr + self.graphPane.axes.transData)
        self.graphPane.axes.set_aspect('equal')  # Maintain aspect ratio (optional)

        # self.plot_line = self.plot(self.graphPane, [], [], 
        #                            color=colour, plotname=name, symbol="+", 
        #                            symbolPen=pg.mkPen(color=(0, 0, 0), width=1), symbolSize=10, symbolBrush=pg.mkBrush(0, 0, 0, 255))
        plot_refs = self.graphPane.axes.plot(self.plot_data_xs, self.plot_data_ys, colour, marker="o", ms=6)
        self._plot_ref = plot_refs[0]

        self.keep_entries = 60 # entries

        # Disable interactivity
        # self.graphPane.setMouseEnabled(x=False, y=False)  # Disable mouse panning & zooming

        self.setLayout(self.layoutMain)
        
        self.graphPane.mpl_connect("button_press_event", self.on_click)
        self.graphPane.mpl_connect("axes_enter_event", self.on_enter)
        self.graphPane.mpl_connect("axes_leave_event", self.on_leave)
        
        self.counter = 1

    def on_click(self,event):
        """ 
        The matplotlib way needs a method to shout when it is interacted with. 
        """
        self.mpl_click_signal.emit()

    def on_enter(self, event):
        # https://stackoverflow.com/questions/7908636/how-to-add-hovering-annotations-to-a-plot
        # connection: https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.pyplot.connect.html
        self.mpl_axes_enter_signal.emit()

    def on_leave(self, event):
        # https://stackoverflow.com/questions/7908636/how-to-add-hovering-annotations-to-a-plot
        # connection: https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.pyplot.connect.html
        self.mpl_axes_leave_signal.emit()

    def manage_plotting_ranges(self):
        # plot the newly updated x and ys
        _no_nans = ~np.isnan(self.plot_data_ys) #avoid plotting nans
        if len(self.plot_data_ys[_no_nans])>1:
            #pyqtgraph won't plot 1 data-point and throws an error instead :|
            # self.plot_line.clear()
            # self.plot_line.setData(self.plot_data_xs[_no_nans], self.plot_data_ys[_no_nans])
            self.plot(self, self.plot_data_xs[_no_nans], self.plot_data_ys[_no_nans])
            self.counter += 1

    def _remove_first_artificial_point(self):
        """ 
        First point is artificial since PlotWidget object won't plot 
        a single datapoint by itself.
        
        The check is we still have that entry there (`_remove_first`), 
        and if there are at least two real data points, the just remove 
        the artificial one.
        """
        if self._remove_first and len(self.plot_data_ys)>=3:
            self._remove_first = False
            self.plot_data_ys = self.plot_data_ys[1:]
            self.plot_data_xs = self.plot_data_xs[1:]

    def _replace_values(self, replace):
        """
        Given a dictionary, replace the entries with values "this" with 
        the value indicated by "with" in `self.plot_data_ys`.

        E.g., replace = {"this":[0, 500, 453], "with":[np.nan, 475, 450]}
        would mean to replace all 0s, 500s, and 453s in `self.plot_data_ys` 
        with np.nan, 475, and 450, respectively.
        """
        if replace is None:
            return
        
        if len(self.plot_data_ys)>=3:
            if len(replace["this"])!=len(replace["with"]):
                print("`replace` 'this' and 'with' keys do not have lists the same length.")

            for t, w in zip(replace["this"],replace["with"]):
                self.plot_data_ys[np.where(self.plot_data_ys==t)] = w

    def add_plot_data(self, new_data_y, new_data_x=None, replace=None):
        """ Adds the new data to the array to be plotted. """

        # self.sensor_plot_data_mean_tot.append(new_data)
        self.plot_data_ys = np.append(self.plot_data_ys, new_data_y)
        # self.plot_data_xs = np.append(self.plot_data_xs, self.plot_data_xs[-1]+1) if new_data_x is None else np.append(self.plot_data_xs, new_data_x)
        self.plot_data_xs = np.append(self.plot_data_xs, self.plot_data_xs[-1]+1) if new_data_x is None else np.append(self.plot_data_xs, new_data_x)

        self._remove_first_artificial_point()
        self._replace_values(replace)
        
        if len(self.plot_data_ys)>self.keep_entries:
            self.plot_data_ys = self.plot_data_ys[-self.keep_entries:]
            self.plot_data_xs = self.plot_data_xs[-self.keep_entries:]

        self._minmax_y = np.array([np.nanmin(self.plot_data_ys), np.nanmax(self.plot_data_ys)])
        # self.graphPane.plotItem.vb.setLimits(yMin=np.nanmin(self._minmax_y[0])*0.95)
        # self.graphPane.plotItem.vb.setLimits(yMax=np.nanmax(self._minmax_y[1])*1.05)
        self.graphPane.axes.set_ylim([np.nanmin(self._minmax_y[0])*0.95, np.nanmax(self._minmax_y[1])*1.05])

        self._minmax_x = np.array([np.nanmin(self.plot_data_xs), np.nanmax(self.plot_data_xs)])
        # self.graphPane.plotItem.vb.setLimits(xMin=np.nanmin(self._minmax_x[0]))
        # self.graphPane.plotItem.vb.setLimits(xMax=np.nanmax(self._minmax_x[1])+1)
        self.graphPane.axes.set_xlim([np.nanmin(self._minmax_x[0]), np.nanmax(self._minmax_x[1])+1])

    def plot(self, graph_widget, x, y, color="r", plotname='', **kwargs):
        # pen = pg.mkPen(color=color, width=5)
        # return graph_widget.plot(x, y, name=plotname, pen=pen, **kwargs)
        graph_widget._plot_ref.set_data(x, y)
        self.graphPane.draw()

    def set_labels(self, graph_widget, xlabel="", ylabel="", title="", fontsize=9, ticksize=9, titlesize=10, offsetsize=1):
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
        # if title_font_size!="0pt":
        #     graph_widget.axes.set_title(title, color='k', size=title_font_size)
        graph_widget.axes.set_title(title, size=titlesize)#, **styles)

        # Set label for both axes
        # styles = {'color':'k', 'font-size':font_size, 'padding-top': '5px', 'padding-right': '5px', 'display': 'block'} 
        graph_widget.axes.set_xlabel(xlabel, size=fontsize)#, **styles)
        graph_widget.axes.set_ylabel(ylabel, size=fontsize)#, **styles)

        graph_widget.axes.tick_params(axis='both', which='major', labelsize=ticksize)
        graph_widget.axes.tick_params(axis='both', which='minor', labelsize=ticksize)

        # this handles the exponent, if the data is in 1e10 then it is 
        # usually plotted in smaller numbers with 1e10 off to the side.
        # `get_offset_text` controls the "1e10"
        t = graph_widget.axes.xaxis.get_offset_text()
        t.set_size(offsetsize)

    def resizeEvent(self,event):
        """ Define how the widget can be resized and keep the same apsect ratio. """
        super().resizeEvent(event)
        
        if event is None:
            return 
        
        new_size = QtCore.QSize(self.detw, int(self.detw / self.aspect_ratio)) #width, height/(width/height)
        new_size.scale(event.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio)

        self.resize(new_size)


class ImageExample(QWidget):
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

        self.lc = LightCurve(reader=self.reader, name="Mean ToT")
        self.mlc = MultiLightCurve(reader=self.reader, name="Mean ToT", ids=["first", "second"], colours=["b", "k"], names=["1","2"])

        self.lc.set_labels(self.lc.graphPane, xlabel="", ylabel="Some Light Curve", title=" ")
        self.mlc.set_labels(self.mlc.graphPane, xlabel="", ylabel="Multi Light Curve", title=" ")

        self.reader.value_changed_collection.connect(self.update_plot)

        self.layoutMain = QVBoxLayout()
        self.layoutMain.setContentsMargins(0, 0, 0, 0)
        self.layoutMain.setSpacing(0)
        self.layoutMain.addWidget(self.lc)
        self.layoutMain.addWidget(self.mlc)
        self.setLayout(self.layoutMain)

        self.detw, self.deth = self.lc.detw, self.lc.deth*2
        self.aspect_ratio = self.detw / self.deth

        self.setMinimumSize(self.detw, self.deth)
        self.resize(self.detw, self.deth)

    def update_plot(self):
        """
        Defines how the plot window is updated for time series.

        In subclass define methods: 
        *`get_data` to extract the new image frame from `self.data_file`, 
        *`update_image` to define how the new image affects the current one,
        *`process_data` to perform any last steps before updating the plot.
        """
        
        new_mean_tot = self.reader.collection.get_mean_tot()
        
        # defined how to add/append onto the new data arrays
        self.lc.add_plot_data(new_mean_tot)
        self.mlc.add_plot_data([new_mean_tot, new_mean_tot-100])

        # plot the newly updated x and ys
        self.lc.manage_plotting_ranges()
        self.mlc.manage_plotting_ranges()

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
    # package top-level
    import os
    DATAFILE = os.path.dirname(os.path.realpath(__file__)) + "/../../../fake_temperatures.txt"
    DATAFILE = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/timepix/for_Kris/fake_data_for_parser/example_timepix_frame.bin"
    DATAFILE = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/timepix/for_Kris/fake_data_for_parser/example_timepix_frame_writing.bin"

    def initiate_gui():
        app = QApplication([])

        # R = TimepixFileReader(DATAFILE)
        R = TimepixReader(DATAFILE)

        f0 = LightCurveExample(reader=R)

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