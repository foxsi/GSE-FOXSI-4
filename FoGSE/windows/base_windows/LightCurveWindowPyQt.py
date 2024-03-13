"""
A demo to walk through an existing CdTe raw file.
"""

import numpy as np

from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication, QSizePolicy, QVBoxLayout, QWidget
import pyqtgraph as pg

from FoGSE.read_raw_to_refined.readRawToRefinedTimepix import TimepixReader
        

class LightCurve(QWidget):
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
    def __init__(self, reader=None, name="light curve", colour="b", parent=None):
        pg.setConfigOption('background', (255,255,255, 0)) # needs to be first

        QWidget.__init__(self, parent)

        self.reader = reader

        self.detw, self.deth = 400, 150
        self.aspect_ratio = self.detw / self.deth
        # self.resize(self.detw, self.deth)

        self.graphPane = pg.PlotWidget()
        # self.graphPane.setMinimumSize(QtCore.QSize(self.detw, self.deth))
        # self.graphPane.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)

        self.layoutMain = QVBoxLayout()
        self.layoutMain.addWidget(self.graphPane)

        self.layoutMain.setContentsMargins(0, 0, 0, 0)
        self.layoutMain.setSpacing(0)

        self.graphPane.setBackground('w')
        self.graphPane.showGrid(x=True, y=True)

        self.plot_data_ys = np.array([0]).astype(float)
        self.plot_data_xs = np.array([0]).astype(float)
        self._remove_first = True

        self.plot_line = self.plot(self.graphPane, [], [], 
                                   color=colour, plotname=name, symbol="+", 
                                   symbolPen=pg.mkPen(color=(0, 0, 0), width=1), symbolSize=10, symbolBrush=pg.mkBrush(0, 0, 0, 255))

        self.keep_entries = 60 # entries

        # Disable interactivity
        self.graphPane.setMouseEnabled(x=False, y=False)  # Disable mouse panning & zooming

        self.setLayout(self.layoutMain)
        
        self.counter = 1

    def manage_plotting_ranges(self):
        # plot the newly updated x and ys
        _no_nans = ~np.isnan(self.plot_data_ys) #avoid plotting nans
        if len(self.plot_data_ys[_no_nans])>1:
            #pyqtgraph won't plot 1 data-point and throws an error instead :|
            self.plot_line.clear()
            self.plot_line.setData(self.plot_data_xs[_no_nans], self.plot_data_ys[_no_nans])
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
        self.plot_data_xs = np.append(self.plot_data_xs, self.plot_data_xs[-1]+1) if new_data_x is None else np.append(self.plot_data_xs, new_data_x)

        self._remove_first_artificial_point()
        self._replace_values(replace)
        
        if len(self.plot_data_ys)>self.keep_entries:
            self.plot_data_ys = self.plot_data_ys[-self.keep_entries:]
            self.plot_data_xs = self.plot_data_xs[-self.keep_entries:]

        self._minmax_y = np.array([np.nanmin(self.plot_data_ys), np.nanmax(self.plot_data_ys)])
        self.graphPane.plotItem.vb.setLimits(yMin=np.nanmin(self._minmax_y[0])*0.95)
        self.graphPane.plotItem.vb.setLimits(yMax=np.nanmax(self._minmax_y[1])*1.05)

        self._minmax_x = np.array([np.nanmin(self.plot_data_xs), np.nanmax(self.plot_data_xs)])
        self.graphPane.plotItem.vb.setLimits(xMin=np.nanmin(self._minmax_x[0]))
        self.graphPane.plotItem.vb.setLimits(xMax=np.nanmax(self._minmax_x[1])+1)

    def plot(self, graph_widget, x, y, color, plotname='', **kwargs):
        pen = pg.mkPen(color=color, width=5)
        return graph_widget.plot(x, y, name=plotname, pen=pen, **kwargs)

    def set_labels(self, graph_widget, xlabel="", ylabel="", title="", font_size="20pt", title_font_size="25pt"):
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
        if title_font_size!="0pt":
            graph_widget.setTitle(title, color='k', size=title_font_size)

        # Set label for both axes
        styles = {'color':'k', 'font-size':font_size, 'padding-top': '5px', 'padding-right': '5px', 'display': 'block'} 
        graph_widget.setLabel('bottom', xlabel, **styles)
        graph_widget.setLabel('left', ylabel, **styles)

    def resizeEvent(self,event):
        """ Define how the widget can be resized and keep the same apsect ratio. """
        super().resizeEvent(event)
        
        if event is None:
            return 
        
        new_size = QtCore.QSize(self.detw, int(self.detw / self.aspect_ratio)) #width, height/(width/height)
        new_size.scale(event.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio)

        self.resize(new_size)

class MultiLightCurve(QWidget):
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
    def __init__(self, reader=None, name="multi light curve", ids=["first"], colours=["b"], names=None, parent=None):
        pg.setConfigOption('background', (255,255,255, 0)) # needs to be first
        QWidget.__init__(self, parent)

        self.reader = reader

        self.detw, self.deth = 400, 150
        self.aspect_ratio = self.detw / self.deth

        self.layoutMain = QVBoxLayout()

        self.layoutMain.setContentsMargins(0, 0, 0, 0)
        self.layoutMain.setSpacing(0)

        self.plot_data_ys = [np.array([0]).astype(float)]*len(ids)
        self.plot_data_xs = [np.array([0]).astype(float)]*len(ids)
        self._remove_firsts = [True]*len(ids)

        self.graphPane = pg.PlotWidget()
        self.graphPane.addLegend(offset=-0.5, labelTextSize='10pt',labelTextColor='k', **{'background-color':'w'}) 
        self.layoutMain.addWidget(self.graphPane)

        colours = colours if len(colours)==len(ids) else colours*len(ids)
        names = ids if names is None else names
        self.plot_lines = []
        for p in range(len(names)):
            self.plot_lines.append(self.plot(self.graphPane, [], [], 
                                             color=colours[p], plotname=names[p], symbol="+", 
                                             symbolPen=pg.mkPen(color=(0, 0, 0), width=1), symbolSize=10, symbolBrush=pg.mkBrush(0, 0, 0, 255)))
            
        self.graphPane.setBackground('w')
        self.graphPane.showGrid(x=True, y=True)
        # Disable interactivity
        self.graphPane.setMouseEnabled(x=False, y=False)  # Disable mouse panning & zooming

        self.keep_entries = 30 # entries

        self.setLayout(self.layoutMain)
        
        self.counter = 1

    def manage_plotting_ranges(self):
        # plot the newly updated x and ys
        _add_counter = True
        for p in range(len(self.plot_data_ys)):
            _no_nans = ~np.isnan(self.plot_data_ys[p]) #avoid plotting nans
            if len(self.plot_data_ys[p][_no_nans])>1:
                #pyqtgraph won't plot 1 data-point and throws an error instead :|
                self.plot_lines[p].clear()
                self.plot_lines[p].setData(self.plot_data_xs[p][_no_nans], self.plot_data_ys[p][_no_nans])

                self.counter = self.counter+1 if _add_counter else self.counter
                _add_counter = False

    def _remove_first_artificial_point(self):
        """ 
        First point is artificial since PlotWidget object won't plot 
        a single datapoint by itself.
        
        The check is we still have that entry there (`_remove_first`), 
        and if there are at least two real data points, the just remove 
        the artificial one.
        """
        for p in range(len(self.plot_data_ys)):
            if self._remove_firsts[p] and len(self.plot_data_ys[p])>=3:
                self._remove_firsts[p] = False
                self.plot_data_ys[p] = self.plot_data_ys[p][1:]
                self.plot_data_xs[p] = self.plot_data_xs[p][1:]

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
        
        for p in range(len(self.plot_data_ys)):
            if len(self.plot_data_ys[p])>=3:
                if len(replace["this"])!=len(replace["with"]):
                    print("`replace` 'this' and 'with' keys do not have lists the same length.")

                for t, w in zip(replace["this"],replace["with"]):
                    self.plot_data_ys[p][self.plot_data_ys[p]==t] = w

    def add_plot_data(self, new_data_ys, new_data_xs=None, replace=None):
        """ Adds the new data to the array to be plotted. """

        for p in range(len(self.plot_data_ys)):
            self.plot_data_ys[p] = np.append(self.plot_data_ys[p], new_data_ys[p])
            # print("kjy",new_data_xs)
            # print("dsfgs",self.plot_data_xs)
            # print(new_data_xs[p])
            # print(self.plot_data_xs[p])
            self.plot_data_xs[p] = np.append(self.plot_data_xs[p], self.plot_data_xs[p][-1]+1) if new_data_xs is None else np.append(self.plot_data_xs[p], new_data_xs)

        self._remove_first_artificial_point()
        self._replace_values(replace)
        
        for p in range(len(self.plot_data_ys)):
            if len(self.plot_data_ys[p])>self.keep_entries:
                self.plot_data_ys[p] = self.plot_data_ys[p][-self.keep_entries:]
                self.plot_data_xs[p] = self.plot_data_xs[p][-self.keep_entries:]

        _ymins, _ymaxs, _xmins, _xmaxs = [], [], [], []
        for p in range(len(self.plot_data_ys)):
            _ymins.append(np.nanmin(self.plot_data_ys[p]))
            _ymaxs.append(np.nanmax(self.plot_data_ys[p]))
            _xmins.append(np.nanmin(self.plot_data_xs[p]))
            _xmaxs.append(np.nanmax(self.plot_data_xs[p]))

        self.graphPane.plotItem.vb.setLimits(yMin=np.nanmin(_ymins)*0.95)
        self.graphPane.plotItem.vb.setLimits(yMax=np.nanmax(_ymaxs)*1.05)
        self.graphPane.plotItem.vb.setLimits(xMin=np.nanmin(_xmins))
        self.graphPane.plotItem.vb.setLimits(xMax=np.nanmax(_xmaxs)+1)

    def plot(self, graph_widget, x, y, color, plotname='', **kwargs):
        pen = pg.mkPen(color=color, width=5)
        return graph_widget.plot(x, y, name=plotname, pen=pen, **kwargs)
    
    def set_labels(self, graph_widget, xlabel="", ylabel="", title="", font_size="20pt", title_font_size="25pt"):
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
        if title_font_size!="0pt":
            graph_widget.setTitle(title, color='k', size=title_font_size)

        # Set label for both axes
        styles = {'color':'k', 'font-size':font_size, 'padding-top': '5px', 'padding-right': '5px', 'display': 'block'} 
        graph_widget.setLabel('bottom', xlabel, **styles)
        graph_widget.setLabel('left', ylabel, **styles)

    def resizeEvent(self,event):
        """ Define how the widget can be resized and keep the same apsect ratio. """
        super().resizeEvent(event)

        if event is None:
            return 
        
        new_size = QtCore.QSize(self.detw, int(self.detw / self.aspect_ratio)) #width, height/(width/height)
        new_size.scale(event.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio)

        self.resize(new_size)


class LightCurveExample(QWidget):
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